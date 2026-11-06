"""Cut point and trunk axis of each pulmonary vein for the run7 mesh (06/11/2026). Writes pv_cuts.json and qc_pv_cuts.png.

The PV cylinders of the earlier meshes (Meshmixer, HugoJal_Case3.stl) point 30-60 deg away from their veins and are
2-4x the lumen area (rubric review C2-1). Here each vein is followed in the corrected LA segmentation
(1_segmentation/la_v2_06112026/), shell by shell of geodesic distance from the centre of the atrium (1 mm shells):
the piece connected to the vein is tracked from the old cap outwards (to the first split) and inwards (to where the
vein joins the atrial body). Each vein is then cut a few mm past the ostium, on its trunk, before its first branch
(CUT_GEO below, chosen from the printed table), perpendicular to the trunk axis = line fitted through the shell
centres within AX_HALF mm of the cut.
Table of run 06/11/2026 (geodesic mm: lumen area mm2):
  RSPV joins the body at ~42; trunk 44: 291 -> 54: 116 (ostial funnel narrowing into the vein); mask ends ~58.
  LSPV joins at ~35; trunk 36: 253 -> 46: 82; mask ends ~50.
  RIPV joins at ~37; trunk 46-66: 60-76 (straight, constant); first split at 68.
  LIPV joins at ~35; trunk 36: 220 -> 44: 138; side branch at ~45; trunk 46-62: 65-77; split at 63.
Cuts chosen: RSPV 48, LSPV 40, RIPV 50 (trunk), LIPV 40 (at 38 the plane still crosses the ostium, at 42 the side
branch already bulges the section; checked on sections of the surface).
Fluent zone names follow run6 (pv_1 = LIPV, pv_2 = RSPV, pv_3 = RIPV, pv_4 = LSPV).
Usage (from the project folder): python 2_mesh/run7_06112026/find_pv_cuts.py"""
import os, json
import numpy as np, nrrd, pyvista as pv
from scipy import ndimage as ndi
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import dijkstra
from skimage import measure

HERE = os.path.dirname(os.path.abspath(__file__)); MESH = os.path.dirname(HERE); ROOT = os.path.dirname(MESH)
CUT_GEO = dict(RSPV=48.0, LSPV=40.0, RIPV=50.0, LIPV=40.0)   # LIPV: at 38 the plane is still at the ostium, at 42 the side branch (~45) bulges the section
AX_HALF = 4.0
FLUENT = dict(LIPV="pv_1", RSPV="pv_2", RIPV="pv_3", LSPV="pv_4")
OLD_CAP = dict(RSPV=0, LSPV=1, RIPV=2, LIPV=3)                              # order of the PV caps in check_mesh_mvz.json

m, h = nrrd.read(os.path.join(ROOT, "1_segmentation", "la_v2_06112026", "Case3_LA_segmentation_HugoJal_06112026.seg.nrrd")); m = m > 0
SP = np.diag(np.asarray(h["space directions"], float)); O = np.asarray(h["space origin"], float)
pts = np.argwhere(m); idx = -np.ones(m.shape, np.int64); idx[tuple(pts.T)] = np.arange(len(pts))
rows, cols, w = [], [], []
for dx in (-1, 0, 1):
    for dy in (-1, 0, 1):
        for dz in (-1, 0, 1):
            if (dx, dy, dz) <= (0, 0, 0): continue
            q = pts + [dx, dy, dz]; ok = np.all((q >= 0) & (q < m.shape), 1); q2 = q[ok]; inm = m[tuple(q2.T)]
            rows.append(idx[tuple(pts[ok][inm].T)]); cols.append(idx[tuple(q2[inm].T)]); w.append(np.full(inm.sum(), np.linalg.norm(np.array([dx, dy, dz]) * SP)))
G = coo_matrix((np.concatenate(w), (np.concatenate(rows), np.concatenate(cols))), shape=(len(pts), len(pts))).tocsr()
seed = np.unravel_index(np.argmax(ndi.distance_transform_edt(m, sampling=SP)), m.shape)
geo = dijkstra(G, directed=False, indices=idx[seed]); P = O + pts * SP
GV = np.full(m.shape, np.inf, np.float32); GV[tuple(pts.T)] = geo

TR = json.load(open(os.path.join(MESH, "mv_aligned_03112026", "transform_LPS_to_model.json"))); R = np.array(TR["R"]); c = np.array(TR["c_LPS_mm"])
caps = json.load(open(os.path.join(MESH, "mv_aligned_03112026", "check_mesh_mvz.json")))["angle_separation_30deg"]["largest"][2:]
ST = np.ones((3, 3, 3), bool); out = {}
for nm, k in OLD_CAP.items():
    cl = R.T @ np.array(caps[k]["centre"]) + c; n_old = R.T @ np.array(caps[k]["normal"])
    i = np.argmin(np.linalg.norm(P - cl, axis=1)); gs = np.floor(geo[i])
    lo = np.maximum(pts[i] - (60 / SP).astype(int), 0); hi = np.minimum(pts[i] + (60 / SP).astype(int), np.array(m.shape) - 1)
    sub = GV[lo[0]:hi[0] + 1, lo[1]:hi[1] + 1, lo[2]:hi[2] + 1]; s0 = tuple(pts[i] - lo)
    def shell(g0):
        lab, _ = ndi.label((sub >= g0) & (sub < g0 + 1.0), ST); return lab
    lab = shell(gs); track = {gs: lab == lab[s0]}
    for direction in (-1, 1):
        g0, cur = gs, track[gs]
        while 10 < g0 < 120:
            g0 += direction; lab = shell(g0); ids = np.unique(lab[ndi.binary_dilation(cur, ST) & (lab > 0)])
            if len(ids) == 0: break
            sizes = [(lab == j).sum() for j in ids]; cur = lab == ids[int(np.argmax(sizes))]; track[g0] = cur
    cen = {g0: O + (np.argwhere(v).mean(0) + lo) * SP for g0, v in track.items()}
    area = {g0: v.sum() * np.prod(SP) for g0, v in track.items()}
    gc = CUT_GEO[nm]; near = [g0 for g0 in cen if abs(g0 - gc) <= AX_HALF]
    C = np.array([cen[g0] for g0 in sorted(near)])
    _, _, vt = np.linalg.svd(C - C.mean(0)); ax = vt[0] * np.sign(vt[0] @ (C[-1] - C[0]))
    p = C.mean(0) + ((cen[gc] - C.mean(0)) @ ax) * ax                       # the cut point: on the fitted axis, at the cut shell
    out[nm] = dict(fluent_name=FLUENT[nm], cut_geodesic_mm=gc, cut_point_LPS=p.round(3).tolist(), axis_LPS=ax.round(4).tolist(),
                   lumen_area_at_cut_mm2=round(float(area[gc]), 1), D_eq_mm=round(float(2 * np.sqrt(area[gc] / np.pi)), 1),
                   angle_old_cap_normal_vs_axis_deg=round(float(np.degrees(np.arccos(abs(ax @ n_old)))), 1),
                   old_cap_centre_LPS=cl.round(2).tolist())
    print(nm, out[nm])
json.dump(out, open(os.path.join(HERE, "pv_cuts.json"), "w"), indent=1)

# QC: segmentation surface, cut discs and trunk axes (green), old cap normals (red), one view per vein
pv.OFF_SCREEN = True
vs, fs, _, _ = measure.marching_cubes(np.pad(m, 1).astype(np.float32), 0.5, spacing=tuple(SP))
surf = pv.PolyData(vs - SP + O, np.c_[np.full(len(fs), 3), fs].ravel()).smooth_taubin(n_iter=40, pass_band=0.05)
pl = pv.Plotter(shape=(1, 4), window_size=(2000, 560), border=False)
for j, (nm, d) in enumerate(out.items()):
    p = np.array(d["cut_point_LPS"]); a = np.array(d["axis_LPS"]); pl.subplot(0, j)
    box = [p[0] - 30, p[0] + 30, p[1] - 30, p[1] + 30, p[2] - 30, p[2] + 30]
    pl.add_mesh(surf.clip_box(box, invert=False), color="steelblue", opacity=0.55, smooth_shading=True)
    pl.add_mesh(pv.Disc(center=p, inner=0, outer=d["D_eq_mm"] / 2, normal=a, c_res=40), color="yellow")
    pl.add_mesh(pv.Arrow(p, a, scale=15), color="green")
    pl.add_mesh(pv.Arrow(np.array(d["old_cap_centre_LPS"]), R.T @ np.array(caps[OLD_CAP[nm]]["normal"]), scale=12), color="red")
    side = np.cross(a, [0, 0, 1.0]); side /= np.linalg.norm(side)
    pl.camera_position = [p + 110 * side, p, (0, 0, 1)]
    pl.add_text(f"{nm}: cut (yellow), trunk axis (green), old cap normal (red, {d['angle_old_cap_normal_vs_axis_deg']:.0f} deg off)", font_size=8)
pl.screenshot(os.path.join(HERE, "qc_pv_cuts.png"))
