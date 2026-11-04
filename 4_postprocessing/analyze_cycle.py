"""Cycle analysis of a run (EnSight Gold per step): TAWSS, OSI, ECAP (= OSI/TAWSS), RRT on the wall; vorticity and stagnation in the fluid.
usage: python analyze_cycle.py <results_dir> <outdir> <first_step_cycleA> <n_steps_per_cycle> <n_cycles>
Cycle A, B ... are consecutive blocks of n steps; the LAST block is the 'analysis cycle', the one before it is used for the periodicity check.
Wall quantities are mapped from each step's (remeshed) la_wall surface onto the wall mesh of the first step of the analysis cycle by
inverse-distance interpolation of the 3 nearest nodes (the wall is remeshed every step, so node-by-node averaging is impossible)."""
import os, sys, time, numpy as np, vtk, pyvista as pv, nrrd
from scipy.spatial import cKDTree
RES, OUT = sys.argv[1], sys.argv[2]
FIRST, NC, NCYC = int(sys.argv[3]), int(sys.argv[4]), int(sys.argv[5])
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/"); DT = 0.01   # ROOT = project folder (DRT_LAAO_Case3)
THR = [0.01, 0.025, 0.05]; ROIS = [10.0, 20.0]
d, h = nrrd.read(ROOT + "/1_segmentation/Device.seg.nrrd")
dev = np.array(h["space origin"], float) + np.argwhere(d > 0)[:, -3:] @ np.array(h["space directions"], float)   # mm, same LPS frame as the mesh
if os.environ.get("MODEL_TRANSFORM"):                        # rotated mesh (2_mesh/mv_aligned_03112026): device LPS -> model frame
    import json; TR = json.load(open(os.environ["MODEL_TRANSFORM"])); dev = (dev - np.array(TR["c_LPS_mm"])) @ np.array(TR["R"]).T
dev_tree = cKDTree(dev[::4])
def load(k):
    r = vtk.vtkEnSightGoldBinaryReader(); r.SetCaseFileName(f"{RES}/step_{k:03d}.encas"); r.Update()
    o = r.GetOutput(); return pv.wrap(o.GetBlock(0)), pv.wrap(o.GetBlock(1))
steps = list(range(FIRST, FIRST + NC * NCYC))
ref_k = steps[-NC]                                           # first step of the analysis cycle
_, wref = load(ref_k); ref = np.asarray(wref.points); tri = wref.cells_dict[5]
W = np.zeros((len(steps), len(ref), 3), np.float32); WV = np.zeros((len(steps), len(ref)), np.float32)
ts = {k: [] for k in ("t", "vol", "vort_mean", "vort_p95", "vort_max", "umean")}
for nm in ["vort_mean_roi%d" % r for r in ROIS] + ["umean_roi%d" % r for r in ROIS] + ["stag_%g_all" % t for t in THR] + ["stag_%g_roi%d" % (t, r) for t in THR for r in ROIS]: ts[nm] = []
nn_d = []; t0 = time.time()
for i, k in enumerate(steps):
    fl, wl = load(k); pts = np.asarray(fl.points); tets = fl.cells_dict[10]; P = pts[tets]
    vol = np.abs(np.einsum("ij,ij->i", P[:,1]-P[:,0], np.cross(P[:,2]-P[:,0], P[:,3]-P[:,0]))) / 6.0
    u = np.asarray(fl["Velocity_Magnitude"])[tets].mean(1); om = np.asarray(fl["Vorticity_Magnitude"])[tets].mean(1)
    dist = dev_tree.query(P.mean(1) * 1000)[0]; V = vol.sum()
    ts["t"].append(k * DT); ts["vol"].append(V); ts["vort_mean"].append((om * vol).sum() / V); ts["umean"].append((u * vol).sum() / V)
    o = np.argsort(om); cw = np.cumsum(vol[o]); ts["vort_p95"].append(om[o][np.searchsorted(cw, 0.95 * V)]); ts["vort_max"].append(om.max())
    for t in THR: ts["stag_%g_all" % t].append(vol[u < t].sum() / V)
    for r in ROIS:
        m = dist < r; vr = vol[m].sum()
        ts["vort_mean_roi%d" % r].append((om[m] * vol[m]).sum() / vr); ts["umean_roi%d" % r].append((u[m] * vol[m]).sum() / vr)
        for t in THR: ts["stag_%g_roi%d" % (t, r)].append(vol[m & (u < t)].sum() / vr)
    dd, ii = cKDTree(np.asarray(wl.points)).query(ref, k=3); wgt = 1 / np.maximum(dd, 1e-9); wgt /= wgt.sum(1, keepdims=True); nn_d.append(dd[:, 0])
    for c, nmn in enumerate(("X_Wall_Shear_Stress", "Y_Wall_Shear_Stress", "Z_Wall_Shear_Stress")):
        W[i, :, c] = (np.asarray(wl[nmn])[ii] * wgt).sum(1)
    WV[i] = (np.asarray(wl["Vorticity_Magnitude"])[ii] * wgt).sum(1)
    if (i + 1) % 25 == 0: print(f"{i+1}/{len(steps)} {time.time()-t0:.0f}s", flush=True)
nn_d = np.array(nn_d) * 1000
res = {k: np.array(v) for k, v in ts.items()}
def metrics(sl):
    w = W[sl]; mag = np.linalg.norm(w, axis=2); tawss = mag.mean(0); vec = np.linalg.norm(w.mean(0), axis=1)
    osi = 0.5 * (1 - vec / np.maximum(tawss, 1e-12)); ecap = osi / np.maximum(tawss, 1e-12)
    return tawss, osi, ecap, 1 / np.maximum((1 - 2 * osi) * tawss, 1e-9), WV[sl].mean(0)
for j in range(NCYC):
    sl = slice(j * NC, (j + 1) * NC); tw, osi, ec, rrt, wv = metrics(sl)
    res.update({f"c{j}_tawss": tw, f"c{j}_osi": osi, f"c{j}_ecap": ec, f"c{j}_rrt": rrt, f"c{j}_wallvort": wv})
res.update(mag_steps=np.linalg.norm(W, axis=2).astype(np.float32), wallvort_steps=WV, ref_pts=ref, tri=tri, dev=dev, nn_d=nn_d, nc=NC, ncyc=NCYC, first=FIRST, ref_step=ref_k)
np.savez_compressed(OUT + "/results.npz", **res)
print("mapping offset to nearest wall node (mm): mean %.2f p95 %.2f max %.2f" % (nn_d.mean(), np.percentile(nn_d, 95), nn_d.max()))
print("DONE", time.time() - t0)
