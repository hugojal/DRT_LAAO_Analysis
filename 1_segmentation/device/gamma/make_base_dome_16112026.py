"""Clean, smooth base + dome of the Amulet-type device from the edited gamma segmentation (16/11/2026).
Guided by the device geometry (disc/skirt with a rounded rim on the LA side, cylindrical lobe ('dome') with a rounded closed end in the LAA).
Input is only read: Device_gamma_wire_v4_06112026.seg.nrrd (gamma tracing + the user's manual edits of 09/11/2026) and the CT (hub positions).
1. Device axis = line through the two hubs (CT >= 2500 HU), axial coordinate a (mm), radius r.
2. The mask is split at the waist (a = 1.85 mm) into base (disc, a < 1.65) and dome (lobe, a >= 2.05): two bodies with a 0.4 mm gap, never joined.
3. Dome: closing (gaps in the braid sheets), hole fill, opening (spurs, streak tails), largest piece only. Base: the disc is a flat saucer that the hub streaks leave patchy in the CT, so it is rebuilt from the CT mask: rim radius per direction and plate thickness per radius.
4. Gaussian smoothing of the binary field, resampling to 0.25 mm, marching cubes, Taubin smoothing. Vertices in LPS mm (frame of 2_mesh/HugoJal_Case3.stl).
Writes Device_gamma_wire_v4_edited_clean_{base,dome,both}_16112026.stl and make_base_dome_16112026.json. Usage: python make_base_dome_16112026.py"""
import os, json, struct
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
ii = np.indices(m.shape).reshape(3, -1).T; P = (ii + lo) * SP - C; A = (P @ N).reshape(m.shape)
def ball(rmm, sp=SP):
    r = np.ceil(rmm / sp).astype(int); z, y, x = np.ogrid[-r[0]:r[0] + 1, -r[1]:r[1] + 1, -r[2]:r[2] + 1]; return (z * sp[0]) ** 2 + (y * sp[1]) ** 2 + (x * sp[2]) ** 2 <= rmm ** 2
PAD = 10; WAIST, GAP = 1.85, 0.4
# --- base (disc): a flat saucer built from the CT mask: rim radius R(theta) from the outer edge of the mask in 15 deg sectors (3 harmonics),
# plate thickness profile a_lo(r), a_hi(r) from the 5th/95th percentile of the mask in 1 mm radial bins (hub thicker at r < 3 mm)
Rv = np.sqrt(np.maximum((P ** 2).sum(1) - (P @ N) ** 2, 0)).reshape(m.shape); u = np.cross(N, [0, 0, 1.]); u /= np.linalg.norm(u); w = np.cross(N, u)
TH = np.mod(np.arctan2(P @ w, P @ u), 2 * np.pi).reshape(m.shape)
braw = m & (A < WAIST - GAP / 2); sec = np.floor(np.degrees(TH) / 15).astype(int)
R95 = np.array([np.percentile(Rv[braw & (sec == k) & (Rv > 9)], 95) for k in range(24)]); tc = np.radians(np.arange(24) * 15 + 7.5)
Bm = np.column_stack([np.ones(24)] + [f(j * tc) for j in (1, 2, 3) for f in (np.cos, np.sin)]); coef = np.linalg.lstsq(Bm, R95, rcond=None)[0]
Rth = coef[0] + sum(coef[1 + 2 * (j - 1)] * np.cos(j * TH) + coef[2 + 2 * (j - 1)] * np.sin(j * TH) for j in (1, 2, 3))
rb = np.arange(0, 16); alo, ahi = [], []
for r0 in rb:
    k = braw & (Rv >= r0) & (Rv < r0 + 1)
    if k.sum() > 30: alo.append(np.percentile(A[k], 5)); ahi.append(np.percentile(A[k], 95))
    else: alo.append(np.nan); ahi.append(np.nan)
alo, ahi = np.array(alo), np.array(ahi); ok = ~np.isnan(alo); rc = rb[ok] + 0.5
alo_s = np.polyval(np.polyfit(rc, alo[ok], 7), rc); ahi_s = np.minimum(np.polyval(np.polyfit(rc, ahi[ok], 7), rc), WAIST - GAP / 2 - 0.05)
Rn = Rv * (Rth.mean() / Rth)                                              # radius normalised to the mean rim radius
fl = np.interp(Rn, rc, alo_s); fh = np.interp(Rn, rc, ahi_s)
rim = np.clip((Rth - Rv) / 1.2, 0, 1)                                      # rounded rim: thickness goes to 0 over the last 1.2 mm
mid = 0.5 * (fl + fh); half = 0.5 * (fh - fl) * np.sqrt(np.clip(1 - (1 - rim) ** 2, 0, 1))
disc = (Rv < Rth) & (np.abs(A - mid) <= half)
out_disc = dict(rim_radius_mm=[round(float(Rth.min()), 2), round(float(Rth.max()), 2)], plate_a_range_mm=[round(float(alo_s.min()), 2), round(float(ahi_s.max()), 2)],
                fraction_of_mask_within_0p6mm_of_model=round(float((ndi.binary_dilation(disc, ball(0.6)) & braw).sum() / braw.sum()), 3))
PARTS = {"base": (disc, 0.0, A < WAIST - GAP / 2), "dome": (m & (A >= WAIST), 2.5, A >= WAIST + GAP / 2)}
def clip_largest(f):
    l, k = ndi.label(f); return l == (1 + np.argmax(ndi.sum(f, l, range(1, k + 1))))
out, meshes = {}, {}
for name, (part, rc, dom) in PARTS.items():
    if rc > 0:
        f = ndi.binary_closing(np.pad(part, PAD), ball(rc))[PAD:-PAD, PAD:-PAD, PAD:-PAD]; f = ndi.binary_fill_holes(f); f = ndi.binary_opening(f, ball(1.0))
    else: f = part
    f = clip_largest(f & dom)
    s = ndi.gaussian_filter(f.astype(np.float32), (0.7 if name == "base" else 1.1) / SP)   # sigma in mm
    step = 0.25; gz = [np.arange(0, shp[k] - 1, step / SP[k]) for k in range(3)]   # 0.25 mm grid
    idx = np.meshgrid(*gz, indexing="ij"); fine = ndi.map_coordinates(s, np.array(idx), order=1)
    v, fc, _, _ = marching_cubes(fine, 0.5, spacing=(step,) * 3); v = v + ((np.array([g[0] for g in gz]) * SP)[None] * 0)  # grid origin = voxel 0 of ROI
    v = v + (lo * SP + ORG)
    pm = pv.PolyData(v, np.hstack([np.full((len(fc), 1), 3), fc]).ravel()).smooth_taubin(n_iter=50, pass_band=0.08).compute_normals(consistent_normals=True, auto_orient_normals=True)
    meshes[name] = pm; fv = f.sum() * SP.prod() / 1000
    ed = pm.extract_feature_edges(boundary_edges=True, non_manifold_edges=True, feature_edges=False, manifold_edges=False)
    out[name] = dict(voxel_volume_mL=round(float(fv), 3), mesh_volume_mL=round(abs(pm.volume) / 1000, 3), triangles=pm.n_cells, open_edges=int(ed.n_cells),
                     axial_range_mm=[round(float(A[f].min()), 2), round(float(A[f].max()), 2)])
    pm.save(f"{HERE}/Device_gamma_wire_v4_edited_clean_{name}_16112026.stl")
both = meshes["base"].merge(meshes["dome"]); both.save(f"{HERE}/Device_gamma_wire_v4_edited_clean_both_16112026.stl")
d = meshes["base"].compute_implicit_distance(meshes["dome"]); out["min_distance_base_to_dome_mm"] = round(float(np.abs(d["implicit_distance"]).min()), 3)
out["dome_points_inside_base"] = int((meshes["dome"].compute_implicit_distance(meshes["base"])["implicit_distance"] < 0).sum())
out["axis_N"] = N.round(5).tolist(); out["base_model"] = out_disc
json.dump(out, open(HERE + "/make_base_dome_16112026.json", "w"), indent=1); print(json.dumps(out, indent=1))
