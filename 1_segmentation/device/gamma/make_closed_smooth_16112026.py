"""Closed, hole-free, smooth device from the edited gamma segmentation (16/11/2026). Data-driven, attached as in the CT.
Input only read: Device_gamma_wire_v4_06112026.seg.nrrd (gamma tracing + the user's manual edits of 09/11/2026).
1. Axis through the two hubs; a = axial position, r = radius, theta = angle.
2. Dome (a >= 1.85 mm): closing (2.5 mm), hole fill, opening (1 mm, removes spurs and sharp bumps).
3. Base (a < 1.85 mm): the disc is a plate with holes where the hub streaks darken the CT. Its (theta, r) footprint is closed (5 mm) and filled; where the footprint
   was empty the plate takes the thickness the CT mask has at that radius (median a_lo/a_hi over theta). Where the CT shows the disc, the mask is kept.
4. Whole device = base U dome U original mask (so base and dome stay attached exactly where the CT attaches them), largest piece.
5. Gaussian 0.9 mm, iso-level that keeps the volume, 0.25 mm grid, marching cubes, Taubin 60 passes.
6. Base and dome = this one surface cut at the waist plane and capped (closed bodies touching at the cut).
Writes Device_gamma_wire_v4_edited_closed_{both,base,dome}_16112026.stl and make_closed_smooth_16112026.json."""
import os, json
import numpy as np, nrrd, pyvista as pv
from scipy import ndimage as ndi
from skimage.measure import marching_cubes
HERE = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"); SEG = os.path.dirname(os.path.dirname(HERE)) + "/"
ct, h = nrrd.read(SEG + "5 DS_Coronaires  0.75  B26f  BestDiast 78 %.nrrd"); seg, _ = nrrd.read(HERE + "/Device_gamma_wire_v4_06112026.seg.nrrd")
SP = np.diag(h["space directions"]).astype(float); ORG = np.asarray(h["space origin"], float)
lo = np.array([215, 300, 160]); shp = np.array([100, 100, 90]); sl = tuple(slice(a, b) for a, b in zip(lo, lo + shp)); m = seg[sl] > 0
hub = ct[sl] > 2500; lab, n = ndi.label(hub); sz = ndi.sum(hub, lab, range(1, n + 1)); top = 1 + np.argsort(-sz)[:2]
hubs = np.array([(np.array(ndi.center_of_mass(hub, lab, t)) + lo) * SP for t in top])
N0 = np.array([0.57050955, -0.45992626, 0.68043125]); C0 = np.array([114.181, 156.072, 98.509])
N = hubs[1] - hubs[0]; N /= np.linalg.norm(N); N = N if N @ N0 > 0 else -N; C = hubs[0] + ((C0 - hubs[0]) @ N) * N
ii = np.indices(m.shape).reshape(3, -1).T; P = (ii + lo) * SP - C; A = (P @ N).reshape(m.shape); Rp = P - np.outer(P @ N, N); Rv = np.linalg.norm(Rp, axis=1).reshape(m.shape)
u = np.cross(N, [0, 0, 1.]); u /= np.linalg.norm(u); w = np.cross(N, u); TH = np.mod(np.arctan2(Rp @ w, Rp @ u), 2 * np.pi).reshape(m.shape)
def ball(rmm, sp=SP):
    r = np.ceil(rmm / sp).astype(int); z, y, x = np.ogrid[-r[0]:r[0] + 1, -r[1]:r[1] + 1, -r[2]:r[2] + 1]; return (z * sp[0]) ** 2 + (y * sp[1]) ** 2 + (x * sp[2]) ** 2 <= rmm ** 2
def largest(f):
    l, k = ndi.label(f); return l == (1 + np.argmax(ndi.sum(f, l, range(1, k + 1))))
PAD, WAIST = 10, 1.85
# dome
dm = m & (A >= WAIST); dome = ndi.binary_closing(np.pad(dm, PAD), ball(2.5))[PAD:-PAD, PAD:-PAD, PAD:-PAD]; dome = ndi.binary_fill_holes(dome); dome = ndi.binary_opening(dome, ball(1.0)) & (A >= WAIST)
# base: footprint in (theta, r), closed and filled; empty cells get the median plate thickness at that r
bm = m & (A < WAIST); DT, DR = 2.0, 0.25; nt, nr = int(360 / DT), int(16 / DR)
it = np.minimum((np.degrees(TH) / DT).astype(int), nt - 1); ir = np.minimum((Rv / DR).astype(int), nr - 1)
foot = np.zeros((nt, nr), bool); foot[it[bm], ir[bm]] = True
fp = np.pad(foot, ((40, 40), (0, 0)), mode="wrap"); k = np.ones((int(5 / (Rv.mean() * np.radians(DT)) ) if False else 5, int(5 / DR)), bool)   # about 5 mm in r, 10 deg in theta
fp = ndi.binary_closing(fp, np.ones((11, int(4 / DR)), bool)); fp = ndi.binary_fill_holes(np.pad(fp, ((0, 0), (1, 1)), constant_values=False))[:, 1:-1][40:-40]
rc = (np.arange(nr) + 0.5) * DR; alo = np.full(nr, np.nan); ahi = np.full(nr, np.nan)
for j in range(nr):
    s = bm & (ir == j)
    if s.sum() > 30: alo[j] = np.percentile(A[s], 5); ahi[j] = np.percentile(A[s], 95)
okj = ~np.isnan(alo); alo = np.polyval(np.polyfit(rc[okj], alo[okj], 7), rc); ahi = np.minimum(np.polyval(np.polyfit(rc[okj], ahi[okj], 7), rc), WAIST - 0.3)
add = (A < WAIST) & foot[0:0].any() if False else (A < WAIST) & fp[it, ir] & (A >= alo[ir]) & (A <= ahi[ir]) & (Rv > 3.0)
base = (bm | add); base = ndi.binary_closing(np.pad(base, PAD), ball(1.0))[PAD:-PAD, PAD:-PAD, PAD:-PAD] & (A < WAIST)
W = largest(base | dome | m); V0 = W.sum() * SP.prod() / 1000
s = ndi.gaussian_filter(W.astype(np.float32), 0.9 / SP); step = 0.25; gz = [np.arange(0, shp[i] - 1, step / SP[i]) for i in range(3)]
fine = ndi.map_coordinates(s, np.array(np.meshgrid(*gz, indexing="ij")), order=1); lv = float(np.quantile(fine, 1 - V0 * 1000 / (fine.size * step ** 3)))
v, fc, _, _ = marching_cubes(fine, lv, spacing=(step,) * 3); v = v + lo * SP + ORG
pm = pv.PolyData(v, np.hstack([np.full((len(fc), 1), 3), fc]).ravel()).smooth_taubin(n_iter=60, pass_band=0.07).compute_normals(consistent_normals=True, auto_orient_normals=True)
def edges(x): return int(x.extract_feature_edges(boundary_edges=True, non_manifold_edges=True, feature_edges=False, manifold_edges=False).n_cells)
out = dict(mask_mL=round(float((m).sum() * SP.prod() / 1000), 3), closed_mask_mL=round(V0, 3), mesh_mL=round(abs(pm.volume) / 1000, 3), triangles=pm.n_cells, open_edges=edges(pm),
           pieces=int(pm.connectivity("all").cell_data["RegionId"].max()) + 1, footprint_cells_added=int((fp & ~foot).sum()))
pm.save(f"{HERE}/Device_gamma_wire_v4_edited_closed_both_16112026.stl"); cen = C + ORG + WAIST * N
for name, sg in (("base", -1), ("dome", 1)):
    part = pm.clip_closed_surface(normal=sg * N, origin=cen).clean().connectivity("all"); r = part.cell_data["RegionId"]
    part = part.extract_cells(np.where(r == np.bincount(r).argmax())[0]).extract_surface(algorithm="dataset_surface").compute_normals(consistent_normals=True, auto_orient_normals=True)
    out[name] = dict(triangles=part.n_cells, mL=round(abs(part.volume) / 1000, 3), open_edges=edges(part)); part.save(f"{HERE}/Device_gamma_wire_v4_edited_closed_{name}_16112026.stl")
json.dump(out, open(HERE + "/make_closed_smooth_16112026.json", "w"), indent=1); print(json.dumps(out))
