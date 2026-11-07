"""LA segmentation v2 (06/11/2026): two fixes from the rubric review (docs/agents/reviews/rubric_review_06112026.md).
The original Hugo_Jal_left_atrium_segmentation.nrrd is only read, never changed.

C1-1 "pulmonary veins at least up to the first branch": the two inferior veins (RIPV, LIPV) stopped 5-8 mm before
     their first division. Each is extended with the same tools the LA was segmented with, threshold + mask:
     CT voxels at blood level (>= HU_MIN, just below the 1st percentile of the CT inside the LA mask) that are
     connected to the distal part of that vein (its voxels beyond the point nearest the old run6 mesh cap), lie beyond
     that point's plane, within 25 mm of it, and at most EXT_MM away along the lumen (geodesic distance through the
     thresholded voxels). This takes each vein end to (and a few mm past) its first division, and adds a ~1 voxel rim
     along the distal vein, where the original mask lay ~0.5 mm inside the lumen edge. Holes in the added part are
     closed (1 voxel).
C1-2 "excluding the device": the device (manual mask OR gamma v4 wireframe, dilated by 1 voxel) is removed from the
     LA. 16.7 % of the device voxels were inside the LA mask (a ~1 mm layer on the atrial face of the disc).
Only the largest connected component is kept; a 1-voxel morphological opening then removes 1-voxel bridges/spurs that
form small handles (genus 38 -> 0; a CFD surface must have genus 0). The segment is named "LA_Case3".
Output: Case3_LA_segmentation_HugoJal_06112026.seg.nrrd (+ .stl in LPS mm), stats JSON and QC images in this folder.
Usage (from the project folder): python 1_segmentation/la_v2_06112026/fix_la_segmentation.py"""
import os, json
import numpy as np, nrrd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy import ndimage as ndi
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
from skimage import measure

HERE = os.path.dirname(os.path.abspath(__file__)); SEG = os.path.dirname(HERE); ROOT = os.path.dirname(SEG)
OUT = os.path.join(HERE, "Case3_LA_segmentation_HugoJal_06112026.seg.nrrd")
HU_MIN, EXT_MM = 300.0, 10.0

m0, h = nrrd.read(os.path.join(SEG, "Hugo_Jal_left_atrium_segmentation.nrrd")); m0 = m0 > 0
ct, _ = nrrd.read(os.path.join(SEG, "5 DS_Coronaires  0.75  B26f  BestDiast 78 %.nrrd")); ct = ct.astype(np.float32)
dman, _ = nrrd.read(os.path.join(SEG, "device", "manual", "Device_manual.seg.nrrd"))
dgam, _ = nrrd.read(os.path.join(SEG, "device", "gamma", "Device_gamma_wire_v4_06112026.seg.nrrd"))
dev = (dman > 0) | (dgam > 0)
SP = np.diag(np.asarray(h["space directions"], float)); O = np.asarray(h["space origin"], float)
assert h.get("space") == "left-posterior-superior"
print(f"CT inside the LA mask: p1 {np.percentile(ct[m0], 1):.0f} HU, p5 {np.percentile(ct[m0], 5):.0f} HU; threshold {HU_MIN:.0f} HU")

def neighbours_graph(mask):
    pts = np.argwhere(mask); idx = -np.ones(mask.shape, np.int64); idx[tuple(pts.T)] = np.arange(len(pts))
    rows, cols, w = [], [], []
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for dz in (-1, 0, 1):
                if (dx, dy, dz) <= (0, 0, 0): continue
                q = pts + [dx, dy, dz]; ok = np.all((q >= 0) & (q < mask.shape), 1); q2 = q[ok]; inm = mask[tuple(q2.T)]
                rows.append(idx[tuple(pts[ok][inm].T)]); cols.append(idx[tuple(q2[inm].T)])
                w.append(np.full(inm.sum(), np.linalg.norm(np.array([dx, dy, dz]) * SP)))
    G = coo_matrix((np.concatenate(w), (np.concatenate(rows), np.concatenate(cols))), shape=(len(pts), len(pts))).tocsr()
    return pts, idx, G

# geodesic distance inside the LA mask from the centre of the body (to find the far end of each vein)
pts, idx, G = neighbours_graph(m0)
seed = np.unravel_index(np.argmax(ndi.distance_transform_edt(m0, sampling=SP)), m0.shape)
geo = dijkstra(G, directed=False, indices=idx[seed]); P = O + pts * SP

# vein ends: the PV caps of the run6 mesh (model frame) mapped back to LPS; inferior veins = caps 3 (right) and 4 (left)
TR = json.load(open(os.path.join(ROOT, "2_mesh", "run8_07112026", "transform_LPS_to_model.json"))); R = np.array(TR["R"]); c = np.array(TR["c_LPS_mm"])
caps = json.load(open(os.path.join(ROOT, "2_mesh", "run8_07112026", "run6_caps_reference.json")))["angle_separation_30deg"]["largest"][2:]
VEINS = {"RSPV": 0, "LSPV": 1, "RIPV": 2, "LIPV": 3}
def vein_info(k):
    cl = R.T @ np.array(caps[k]["centre"]) + c
    i = np.argmin(np.linalg.norm(P - cl, axis=1)); gend = geo[i]
    sel = (np.linalg.norm(P - P[i], axis=1) < 30) & (geo > gend - 18)
    sub = np.zeros(m0.shape, bool); sub[tuple(pts[sel].T)] = True
    lab, _ = ndi.label(sub, np.ones((3, 3, 3))); vein = lab == lab[tuple(pts[i])]
    vi = idx[vein]; gv = geo[vi]
    cen = np.array([P[vi][(gv >= b) & (gv < b + 1)].mean(0) for b in np.arange(gend - 12, gend - 0.5, 1.0) if ((gv >= b) & (gv < b + 1)).sum() > 5])
    _, _, vt = np.linalg.svd(cen - cen.mean(0)); ax = vt[0] * np.sign(vt[0] @ (cen[-1] - cen[0]))
    distal = vein & (geo[idx] * (idx >= 0) >= gend - 1.5)                    # the last 1.5 mm of the vein
    return dict(end=P[i], gend=gend, axis=ax, distal=distal, c_dist=O + np.argwhere(distal).mean(0) * SP, vein=vein)

m = m0.copy(); stats = {}
bright = (ct >= HU_MIN) & ~m0 & ~ndi.binary_dilation(dev, iterations=1)
for nm in ("RIPV", "LIPV"):
    v = vein_info(VEINS[nm])
    # candidate voxels: bright, outside the LA, within 25 mm of the end, beyond the end plane
    Z = np.argwhere(bright); Pz = O + Z * SP
    keep = (np.linalg.norm(Pz - v["c_dist"], axis=1) < 25) & ((Pz - v["c_dist"]) @ v["axis"] > -0.5)
    cand = np.zeros(m.shape, bool); cand[tuple(Z[keep].T)] = True
    region = cand | v["distal"]
    pr, ir, Gr = neighbours_graph(region)
    src = ir[v["distal"]]; src = src[src >= 0]
    dist = dijkstra(Gr, directed=False, indices=src, min_only=True)
    add = np.zeros(m.shape, bool); ok = np.isfinite(dist) & (dist <= EXT_MM); add[tuple(pr[ok].T)] = True; add &= ~m0
    add = ndi.binary_closing(add | v["distal"], np.ones((3, 3, 3))) & ~m0 & (ct >= HU_MIN - 60)
    m |= add
    stats[nm] = dict(added_mL=round(add.sum() * np.prod(SP) / 1000, 3), axis_LPS=v["axis"].round(3).tolist(), end_LPS=v["end"].round(2).tolist(),
                     reach_along_axis_mm=round(float(((O + np.argwhere(add) * SP - v["c_dist"]) @ v["axis"]).max()) if add.any() else 0.0, 1))
    print(nm, stats[nm])

# device out
devd = ndi.binary_dilation(dev, iterations=1)
stats["device_voxels_inside_LA_before"] = int((m0 & dev).sum()); stats["device_voxels_total"] = int(dev.sum())
m &= ~devd
lab, n = ndi.label(m, np.ones((3, 3, 3))); sizes = np.bincount(lab.ravel()); sizes[0] = 0; m = lab == np.argmax(sizes)
m = ndi.binary_fill_holes(m)
# topology clean-up: a 1-voxel morphological opening removes 1-voxel bridges and spurs, which form small handles/tunnels
# (genus 38 after removing the device, 11 in the original mask; a CFD surface needs genus 0)
def genus(mask):
    v_, f_, _, _ = measure.marching_cubes(np.pad(mask, 1).astype(np.float32), 0.5)
    F_ = f_; E_ = np.unique(np.sort(np.vstack([F_[:, [0, 1]], F_[:, [1, 2]], F_[:, [2, 0]]]), 1), axis=0)
    return int(round((2 - (len(np.unique(F_)) - len(E_) + len(F_))) / 2))
stats["genus_before_opening"] = genus(m)
m = ndi.binary_opening(m, np.ones((3, 3, 3)))
lab, n2 = ndi.label(m, np.ones((3, 3, 3))); sizes = np.bincount(lab.ravel()); sizes[0] = 0; m = ndi.binary_fill_holes(lab == np.argmax(sizes))
stats["genus_after_opening"] = genus(m)
stats["device_voxels_inside_LA_after"] = int((m & dev).sum()); stats["components_removed"] = int(n - 1)
stats["volume_mL"] = dict(before=round(m0.sum() * np.prod(SP) / 1000, 2), after=round(m.sum() * np.prod(SP) / 1000, 2))
print(stats)

# save: same header (Slicer segmentation), segment renamed
h2 = dict(h); h2["Segment0_Name"] = "LA_Case3"; h2["Segment0_NameAutoGenerated"] = "0"
nz = np.argwhere(m); h2["Segment0_Extent"] = " ".join(f"{a} {b}" for a, b in zip(nz.min(0), nz.max(0)))
nrrd.write(OUT, m.astype(h["type"] == "short" and np.int16 or np.uint8), h2)
# STL (LPS mm) for viewing
import pyvista as pv
vs, fs, _, _ = measure.marching_cubes(np.pad(m, 1).astype(np.float32), 0.5, spacing=tuple(SP))
surf = pv.PolyData(vs - SP + O, np.c_[np.full(len(fs), 3), fs].ravel()).clean()
surf.save(OUT.replace(".seg.nrrd", ".stl"))
json.dump(stats, open(os.path.join(HERE, "la_v2_stats.json"), "w"), indent=1)

# QC: planes through each inferior vein axis (old outline cyan, new red, device yellow) and the device region
samp = lambda vol, Gp, o=1: ndi.map_coordinates(vol.astype(np.float32), ((Gp - O) / SP).transpose(2, 0, 1), order=o, mode="nearest")
fig, axs = plt.subplots(3, 4, figsize=(20, 15.5))
for row, nm in enumerate(("RIPV", "LIPV")):
    v = vein_info(VEINS[nm]); ax_ = v["axis"]; e1 = np.cross(ax_, [0, 0, 1.0]); e1 /= np.linalg.norm(e1); e2 = np.cross(ax_, e1)
    s = np.arange(-25, 25.01, 0.25); t = np.arange(-20, 35.01, 0.25)
    for j, phi in enumerate(np.radians([0, 45, 90, 135])):
        dd = np.cos(phi) * e1 + np.sin(phi) * e2; T_, S_ = np.meshgrid(t, s, indexing="ij"); Gp = v["c_dist"] + T_[..., None] * ax_ + S_[..., None] * dd
        a = axs[row, j]; a.imshow(np.clip(samp(ct, Gp), -100, 700).T, cmap="gray", origin="lower", extent=[t[0], t[-1], s[0], s[-1]])
        for vol, col in ((m0, "c"), (m, "r")):
            for cc in measure.find_contours(samp(vol, Gp), 0.5): a.plot(t[0] + cc[:, 0] * 0.25, s[0] + cc[:, 1] * 0.25, col, lw=0.8)
        a.axvline(0, color="y", lw=0.5); a.set_title(f"{nm}: plane through the vein axis, {np.degrees(phi):.0f} deg (mm from the old end; cyan old, red new)", fontsize=8)
kd = int(np.argwhere(dev)[:, 2].mean())
for j, dk in enumerate((-6, -2, 2, 6)):
    k = kd + dk; a = axs[2, j]
    a.imshow(np.clip(ct[:, :, k], -100, 900).T, cmap="gray", origin="lower")
    for vol, col in ((m0, "c"), (m, "r"), (dev, "y")):
        for cc in measure.find_contours(vol[:, :, k].astype(float), 0.5): a.plot(cc[:, 0], cc[:, 1], col, lw=0.8)
    cen = np.argwhere(dev[:, :, kd]).mean(0) if dev[:, :, kd].any() else np.array([256, 256])
    a.set_xlim(cen[0] - 60, cen[0] + 60); a.set_ylim(cen[1] - 60, cen[1] + 60)
    a.set_title(f"device region, axial slice {k}: LA old (cyan), new (red), device (yellow)", fontsize=8)
plt.tight_layout(); plt.savefig(os.path.join(HERE, "qc_la_v2.png"), dpi=70)
print("written", OUT)
