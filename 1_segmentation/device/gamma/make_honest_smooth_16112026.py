"""Smooth, honest version of the edited gamma device segmentation (16/11/2026). No model, no closing, no hole filling: the CT-based mask
(Device_gamma_wire_v4_06112026.seg.nrrd = gamma tracing + the user's manual edits of 09/11/2026) is only smoothed.
1. Specks < 40 voxels removed (the main piece, with disc, hubs and lobe attached as in the CT, is kept whole).
2. Gaussian smoothing of the binary mask (sigma 0.5 mm); iso-level chosen so the volume equals the mask volume (thin sheets do not shrink).
3. Resampling to 0.25 mm, marching cubes, Taubin smoothing (volume-preserving). Vertices in LPS mm.
4. Base (disc) and dome (lobe) = the same smooth surface cut at the waist plane (a = 1.85 mm along the hub axis) and capped: two closed bodies that touch only at the cut.
Writes Device_gamma_wire_v4_edited_smooth_{both,base,dome}_16112026.stl and make_honest_smooth_16112026.json."""
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
l, k = ndi.label(m, np.ones((3, 3, 3))); sizes = ndi.sum(m, l, range(1, k + 1)); keep = np.isin(l, 1 + np.flatnonzero(sizes >= 40)); V0 = keep.sum() * SP.prod() / 1000
s = ndi.gaussian_filter(keep.astype(np.float32), 0.5 / SP)
step = 0.25; gz = [np.arange(0, shp[i] - 1, step / SP[i]) for i in range(3)]; fine = ndi.map_coordinates(s, np.array(np.meshgrid(*gz, indexing="ij")), order=1)
lv = float(np.quantile(fine, 1 - V0 * 1000 / (fine.size * step ** 3)))          # iso-level that keeps the mask volume
v, fc, _, _ = marching_cubes(fine, lv, spacing=(step,) * 3); v = v + lo * SP + ORG
pm = pv.PolyData(v, np.hstack([np.full((len(fc), 1), 3), fc]).ravel()).smooth_taubin(n_iter=40, pass_band=0.08).compute_normals(consistent_normals=True, auto_orient_normals=True)
cs = pm.connectivity("all"); rid = cs.cell_data["RegionId"]; big = np.bincount(rid).argmax(); pieces = int(rid.max()) + 1
out = dict(mask_mL=round(V0, 3), iso_level=round(lv, 3), pieces=pieces, triangles=pm.n_cells, mesh_mL=round(abs(pm.volume) / 1000, 3))
pm.save(f"{HERE}/Device_gamma_wire_v4_edited_smooth_both_16112026.stl")
WAIST = 1.85; cen = C + ORG + WAIST * N
for name, sign in (("base", -1), ("dome", 1)):
    part = pm.clip_closed_surface(normal=sign * N, origin=cen).clean(); part = part.connectivity("all"); r = part.cell_data["RegionId"]
    part = part.extract_cells(np.where(r == np.bincount(r).argmax())[0]).extract_surface(algorithm="dataset_surface").compute_normals(consistent_normals=True, auto_orient_normals=True)
    ed = part.extract_feature_edges(boundary_edges=True, non_manifold_edges=True, feature_edges=False, manifold_edges=False)
    out[name] = dict(triangles=part.n_cells, mL=round(abs(part.volume) / 1000, 3), open_edges=int(ed.n_cells)); part.save(f"{HERE}/Device_gamma_wire_v4_edited_smooth_{name}_16112026.stl")
json.dump(out, open(HERE + "/make_honest_smooth_16112026.json", "w"), indent=1); print(json.dumps(out))
