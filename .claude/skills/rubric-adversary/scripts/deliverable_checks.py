"""Read-only, deterministic checks of the LAAO lab deliverables.

Recomputes the measurable facts a grader would check, without trusting the
project's own check files:
  - inventory of candidate deliverables (.nrrd, .stl, .bdf, .pdf, ParaView files)
  - NRRD: file name vs case id, header keys that look like patient data,
    labels / voxel counts / volume / connected components, LA-device overlap
  - STL: triangles, open and non-manifold edges, closed volume, connected
    pieces, number of regions after a Fluent-style angle separation (30 deg)
  - BDF: tetra count, negative volumes, equivolume skewness distribution
  - PDF: page count, which page starts the references, body pages

Nothing is written inside the project. Output: JSON on stdout or --out FILE.

Usage (from the project folder, shared venv):
  ../mcp/.venv/Scripts/python.exe .claude/skills/rubric-adversary/scripts/deliverable_checks.py \
      --root . --out <scratchpad>/checks.json [--case-id 3] [--skip-bdf]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np

PHI_PATTERN = re.compile(
    r"patient|birth|0010\||0008\|0020|study.?date|institution|accession|physician|operator",
    re.IGNORECASE,
)
IGNORE_DIRS = {"archive", ".git", ".venv", "__pycache__", "node_modules"}


def walk(root: Path, suffixes: tuple[str, ...]) -> list[Path]:
    out = []
    for p in root.rglob("*"):
        if any(part in IGNORE_DIRS for part in p.relative_to(root).parts):
            continue
        if p.is_file() and p.name.lower().endswith(suffixes):
            out.append(p)
    return sorted(out)


def rel(p: Path, root: Path) -> str:
    return p.relative_to(root).as_posix()


# ---------------------------------------------------------------- NRRD
def nrrd_affine(h: dict) -> np.ndarray | None:
    dirs = h.get("space directions")
    org = h.get("space origin")
    if dirs is None or org is None:
        return None
    rows = [np.asarray(d, float) for d in dirs if d is not None and not (
        isinstance(d, float) and np.isnan(d)) and np.all(np.isfinite(np.asarray(d, float)))]
    if len(rows) != 3:
        return None
    A = np.eye(4)
    A[:3, :3] = np.stack(rows, axis=1)  # columns = index axes
    A[:3, 3] = np.asarray(org, float)
    return A


def check_nrrd(path: Path, root: Path, case_patterns: list[str]) -> dict:
    import nrrd
    from scipy import ndimage

    info: dict = {"file": rel(path, root), "size_MB": round(path.stat().st_size / 1e6, 1)}
    stem = path.name.lower()
    info["name_has_case_id"] = any(re.search(p, stem) for p in case_patterns)
    try:
        data, h = nrrd.read(str(path))
    except Exception as e:  # noqa: BLE001
        info["error"] = f"read failed: {e}"
        return info
    info["shape"] = list(data.shape)
    info["dtype"] = str(data.dtype)
    phi = {k: str(v)[:60] for k, v in h.items() if PHI_PATTERN.search(k)}
    info["header_keys_looking_like_patient_data"] = phi
    seg_names = {k: v for k, v in h.items() if re.match(r"Segment\d+_Name$", k)}
    if seg_names:
        info["segments"] = seg_names
    A = nrrd_affine(h)
    if A is not None:
        info["voxel_mm"] = [round(float(np.linalg.norm(A[:3, i])), 4) for i in range(3)]
        vox_ml = abs(np.linalg.det(A[:3, :3])) / 1000.0
    else:
        vox_ml = None
    looks_like_label = data.ndim == 3 and (data.dtype.kind in "ub" or np.issubdtype(data.dtype, np.integer)) \
        and len(np.unique(data[:: max(1, data.shape[0] // 64)])) < 32
    info["is_label_map"] = bool(looks_like_label)
    if looks_like_label:
        labels, counts = np.unique(data, return_counts=True)
        lab = {}
        for l, c in zip(labels.tolist(), counts.tolist()):
            if l == 0:
                continue
            m = data == l
            _, ncomp = ndimage.label(m)
            sizes = np.bincount(ndimage.label(m)[0].ravel())[1:] if ncomp else np.array([])
            lab[str(l)] = {
                "voxels": int(c),
                "volume_mL": round(c * vox_ml, 2) if vox_ml else None,
                "connected_components": int(ncomp),
                "largest_component_fraction": round(float(sizes.max() / sizes.sum()), 4) if ncomp else None,
                "components_under_50_voxels": int((sizes < 50).sum()) if ncomp else 0,
            }
        info["labels"] = lab
    info["_affine"] = A.tolist() if A is not None else None
    info["_path"] = str(path)
    return info


def overlap(la: dict, dev: dict) -> dict:
    """Voxels of the device mask that fall inside the LA mask (physical-space mapping)."""
    import nrrd

    if la.get("_affine") is None or dev.get("_affine") is None:
        return {"error": "missing geometry"}
    la_d, _ = nrrd.read(la["_path"])
    dv_d, _ = nrrd.read(dev["_path"])
    if dv_d.ndim == 4:
        dv_d = dv_d.any(axis=0)
    la_m = la_d > 0 if la_d.ndim == 3 else la_d.any(axis=0)
    idx = np.argwhere(dv_d > 0)
    if len(idx) == 0:
        return {"device_voxels": 0}
    A_dev, A_la = np.asarray(dev["_affine"]), np.asarray(la["_affine"])
    xyz = (A_dev @ np.c_[idx, np.ones(len(idx))].T)
    ijk = np.rint(np.linalg.inv(A_la) @ xyz).T[:, :3].astype(int)
    ok = np.all((ijk >= 0) & (ijk < np.array(la_m.shape)), axis=1)
    inside = la_m[tuple(ijk[ok].T)]
    return {
        "la_file": la["file"], "device_file": dev["file"],
        "device_voxels": int(len(idx)),
        "device_voxels_inside_LA_mask": int(inside.sum()),
        "fraction_inside": round(float(inside.sum() / len(idx)), 4),
    }


# ---------------------------------------------------------------- STL
def angle_regions(mesh, angle_deg: float = 30.0, to_mm: float = 1.0) -> list[dict]:
    """Flood-fill faces across edges whose dihedral angle is below angle_deg."""
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components

    faces = mesh.faces.reshape(-1, 4)[:, 1:]
    pts = mesh.points
    n = np.cross(pts[faces[:, 1]] - pts[faces[:, 0]], pts[faces[:, 2]] - pts[faces[:, 0]])
    area = 0.5 * np.linalg.norm(n, axis=1)
    nn = n / np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-30)
    e = np.sort(np.concatenate([faces[:, [0, 1]], faces[:, [1, 2]], faces[:, [2, 0]]]), axis=1)
    fid = np.tile(np.arange(len(faces)), 3)
    order = np.lexsort((e[:, 1], e[:, 0]))
    e, fid = e[order], fid[order]
    same = np.all(e[1:] == e[:-1], axis=1)
    a, b = fid[:-1][same], fid[1:][same]
    cosang = np.einsum("ij,ij->i", nn[a], nn[b])
    keep = cosang > np.cos(np.radians(angle_deg))
    g = coo_matrix((np.ones(keep.sum()), (a[keep], b[keep])), shape=(len(faces),) * 2)
    ncomp, lab = connected_components(g, directed=False)
    regions = []
    for r in range(ncomp):
        sel = lab == r
        A = area[sel].sum() * to_mm ** 2
        nrm = (nn[sel] * area[sel, None]).sum(0)
        flat = np.linalg.norm(nrm) / max(area[sel].sum(), 1e-30)  # 1 = perfectly planar
        regions.append({"faces": int(sel.sum()), "area_mm2": round(float(A), 1),
                        "eq_diameter_mm": round(float(2 * np.sqrt(A / np.pi)), 1),
                        "planarity": round(float(flat), 4)})
    regions.sort(key=lambda d: -d["area_mm2"])
    return regions


def check_stl(path: Path, root: Path) -> dict:
    import pyvista as pv

    info: dict = {"file": rel(path, root)}
    try:
        m = pv.read(str(path)).triangulate().clean()
    except Exception as e:  # noqa: BLE001
        info["error"] = f"read failed: {e}"
        return info
    info["triangles"] = int(m.n_cells)
    info["points"] = int(m.n_points)
    b = m.bounds
    info["extent"] = [round(b[1] - b[0], 2), round(b[3] - b[2], 2), round(b[5] - b[4], 2)]
    info["units_guess"] = "mm" if max(info["extent"]) > 1 else "m"
    to_mm = 1.0 if info["units_guess"] == "mm" else 1000.0
    fe = m.extract_feature_edges(boundary_edges=True, non_manifold_edges=False,
                                 feature_edges=False, manifold_edges=False)
    nm = m.extract_feature_edges(boundary_edges=False, non_manifold_edges=True,
                                 feature_edges=False, manifold_edges=False)
    info["open_edges"] = int(fe.n_cells)
    info["non_manifold_edges"] = int(nm.n_cells)
    conn = m.connectivity()
    info["connected_pieces"] = int(len(np.unique(conn["RegionId"]))) if m.n_cells else 0
    q = m.compute_cell_sizes(length=False, area=True, volume=False)
    info["degenerate_triangles(area<1e-6 mm2)"] = int((np.asarray(q["Area"]) * to_mm ** 2 < 1e-6).sum())
    if info["open_edges"] == 0:
        info["closed_volume_mL"] = round(float(m.volume) * to_mm ** 3 / 1000.0, 3)
    if m.n_cells < 400_000 and info["connected_pieces"] == 1:
        regs = angle_regions(m, 30.0, to_mm)
        info["angle_separation_30deg"] = {"regions": len(regs), "largest_8": regs[:8]}
        info["angle_separation_regions_at"] = {f"{a}deg": len(angle_regions(m, float(a), to_mm)) for a in (20, 40)}
    return info


# ---------------------------------------------------------------- BDF
_NUM = re.compile(r"^([+-]?\d*\.?\d*)([+-]\d+)$")


def nas_float(s: str) -> float:
    s = s.strip()
    try:
        return float(s)
    except ValueError:
        m = _NUM.match(s)  # Nastran short exponent 1.2-3
        if m:
            return float(f"{m.group(1)}e{m.group(2)}")
        raise


def check_bdf(path: Path, root: Path) -> dict:
    info: dict = {"file": rel(path, root), "size_MB": round(path.stat().st_size / 1e6, 1)}
    ids, xyz, tets, other = [], [], [], {}
    with open(path, "r", errors="replace") as f:
        for line in f:
            if line.startswith("GRID") and not line.startswith("GRID*"):
                if "," in line:
                    p = line.split(",")
                    ids.append(int(p[1])); xyz.append([nas_float(p[3]), nas_float(p[4]), nas_float(p[5])])
                else:
                    ids.append(int(line[8:16])); xyz.append([nas_float(line[24:32]), nas_float(line[32:40]), nas_float(line[40:48])])
            elif line.startswith("CTETRA"):
                p = line.split(",") if "," in line else line.split()
                tets.append([int(v) for v in p[3:7]])
            elif line[:1].isalpha():
                k = line.split()[0].rstrip(",") if line.split() else ""
                other[k] = other.get(k, 0) + 1
    info["nodes"] = len(ids)
    info["tetrahedra"] = len(tets)
    info["other_cards"] = {k: v for k, v in other.items() if k not in ("ENDDATA",)}
    info["under_500k"] = len(tets) < 500_000
    if not tets:
        return info
    lut = np.full(max(ids) + 1, -1, dtype=np.int64)
    lut[np.asarray(ids)] = np.arange(len(ids))
    P = np.asarray(xyz)
    T = lut[np.asarray(tets)]
    a, b, c, d = (P[T[:, i]] for i in range(4))
    vol = np.einsum("ij,ij->i", b - a, np.cross(c - a, d - a)) / 6.0
    info["negative_volume_tets"] = int((vol < 0).sum())
    info["zero_volume_tets(|V|<1e-12)"] = int((np.abs(vol) < 1e-12).sum())
    info["total_volume"] = round(float(np.abs(vol).sum()), 2)
    # equivolume skewness = (V_ideal - V) / V_ideal, V_ideal = regular tet with the same circumradius
    u, v, w = b - a, c - a, d - a
    num = (np.einsum("ij,ij->i", u, u)[:, None] * np.cross(v, w)
           + np.einsum("ij,ij->i", v, v)[:, None] * np.cross(w, u)
           + np.einsum("ij,ij->i", w, w)[:, None] * np.cross(u, v))
    den = 2.0 * np.einsum("ij,ij->i", u, np.cross(v, w))
    R = np.linalg.norm(num, axis=1) / np.maximum(np.abs(den), 1e-30)
    v_ideal = 8.0 * np.sqrt(3.0) / 27.0 * R ** 3
    skew = np.clip((v_ideal - np.abs(vol)) / np.maximum(v_ideal, 1e-30), 0, 1)
    info["equivolume_skewness"] = {
        "max": round(float(skew.max()), 4), "mean": round(float(skew.mean()), 4),
        "p99": round(float(np.percentile(skew, 99)), 4),
        "n_above_0.8": int((skew > 0.8).sum()), "n_above_0.9": int((skew > 0.9).sum()),
        "n_above_0.95": int((skew > 0.95).sum()),
    }
    return info


# ---------------------------------------------------------------- PDF
def check_pdf(path: Path, root: Path) -> dict:
    info: dict = {"file": rel(path, root)}
    try:
        import fitz  # PyMuPDF
    except ImportError:
        info["error"] = "PyMuPDF not available"
        return info
    doc = fitz.open(str(path))
    info["pages"] = doc.page_count
    ref_page = None
    texts = []
    for i, page in enumerate(doc):
        t = page.get_text()
        texts.append(t)
        if ref_page is None and re.search(r"^\s*(References|Bibliography)\s*$", t, re.MULTILINE | re.IGNORECASE):
            ref_page = i + 1
    info["references_heading_on_page"] = ref_page
    if ref_page:
        body_end = ref_page if not re.match(r"\s*(References|Bibliography)", texts[ref_page - 1].strip(), re.I) else ref_page - 1
        info["body_pages_before_references"] = body_end
    info["images_per_page"] = [len(p.get_images()) for p in doc]
    info["words_per_page"] = [len(t.split()) for t in texts]
    full = "\n".join(texts)
    info["mentions"] = {k: len(re.findall(k, full, re.I)) for k in
                        ["thrombus", "DRT", "no device-related thrombus", "risk", "Watchman", "Amulet",
                         "ParaView", "ECAP", "TAWSS", "OSI", "streamline", "mitral"]}
    return info


# ---------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=".")
    ap.add_argument("--out", default=None)
    ap.add_argument("--case-id", default="3")
    ap.add_argument("--skip-bdf", action="store_true")
    ap.add_argument("--skip-nrrd", action="store_true")
    args = ap.parse_args()
    root = Path(args.root).resolve()
    cid = args.case_id
    case_patterns = [rf"case[ _-]?0*{cid}(?!\d)"]

    res: dict = {"root": str(root), "case_id": cid}
    nrrds = walk(root / "1_segmentation", (".nrrd",)) if (root / "1_segmentation").exists() else []
    stls = walk(root, (".stl",))
    bdfs = walk(root, (".bdf",))
    pdfs = walk(root / "5_report", (".pdf",)) if (root / "5_report").exists() else []
    pv_dir = root / "6_paraview_package"
    res["inventory"] = {
        "nrrd": [rel(p, root) for p in nrrds],
        "stl": [rel(p, root) for p in stls],
        "bdf": [rel(p, root) for p in bdfs],
        "pdf_in_5_report": [rel(p, root) for p in pdfs],
    }
    if pv_dir.exists():
        files = [p for p in pv_dir.rglob("*") if p.is_file()]
        res["inventory"]["paraview_package"] = {
            "files": len(files), "size_GB": round(sum(p.stat().st_size for p in files) / 1e9, 2),
            "by_suffix": {s: sum(1 for p in files if p.suffix.lower() == s)
                          for s in sorted({p.suffix.lower() for p in files})},
        }

    if not args.skip_nrrd:
        res["nrrd"] = []
        for p in nrrds:
            if p.stat().st_size > 400e6:
                res["nrrd"].append({"file": rel(p, root), "skipped": "larger than 400 MB"})
                continue
            res["nrrd"].append(check_nrrd(p, root, case_patterns))
        las = [n for n in res["nrrd"] if n.get("is_label_map") and re.search(r"atri|LA|stl", n["file"], re.I)
               and "device" not in n["file"].lower() and "experiment" not in n["file"]]
        devs = [n for n in res["nrrd"] if n.get("is_label_map") and "device" in n["file"].lower()]
        res["la_device_overlap"] = [overlap(l, d) for l in las for d in devs]
        for n in res["nrrd"]:
            n.pop("_affine", None); n.pop("_path", None)

    res["stl"] = [check_stl(p, root) for p in stls if "archive" not in p.parts]
    if not args.skip_bdf:
        res["bdf"] = [check_bdf(p, root) for p in bdfs]
    res["pdf"] = [check_pdf(p, root) for p in pdfs]

    txt = json.dumps(res, indent=1, default=str)
    if args.out:
        Path(args.out).write_text(txt, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        print(txt)
    return 0


if __name__ == "__main__":
    sys.exit(main())
