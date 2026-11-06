"""Device wire frame (Amulet-type occluder) from a gamma-transformed CT, version 4 (06/11/2026). No neural network.

The device is an Amulet-type occluder: two hubs 11.7 mm apart on one axis, a braided disc (~28 mm) on the LA side and
a braided lobe (~22 mm, wall ~8 mm long) in the LAA. On this CT the braid is a thin bright sheet, not separate struts.
v3 used a tube (Sato) filter, built for a Watchman strut cage: it broke the sheets into speckles.
v4 traces the sheets in cylindrical coordinates around the device axis (line through the two hubs):
1. Gamma 0.3: g = clip((CT - blood) / (1500 - blood), 0, 1) ** 0.3 (blood = median CT inside the LA).
2. Resample g on a (theta, axial, radius) grid: 2.5 deg x 0.25 mm x 0.25 mm. In each half-plane through the axis
   every sheet of the device is a curve (disc at axial ~ 0, lobe wall at radius ~ 10-11 mm, distal end, and the
   inner braid lines of the lobe).
3. Ridge detection in each half-plane: 2D Hessian at 0.5 mm, ridge strength = -(most negative eigenvalue),
   smoothed over +-1 theta step.
4. Sheet width: keep bins >= 50 % of the strongest ridge within +-0.5 mm (about the half-maximum width).
   Hysteresis at 25 % / 45 % of the 99th percentile of the ridge strength, pieces < 50 bins removed.
5. Back to the CT grid by looking up each voxel's (theta, axial, radius) bin.
6. Axis (radius < 3 mm, where cylindrical coordinates break down): the hubs and the dense bar between them,
   by CT value (>= 900 HU). The bar is seen identically in every long-axis plane, so it is metal, not streak.
Allowed region: manual device/manual/Device_manual.seg.nrrd dilated by 1.5 mm (removes structures around the device and streak tails).
Writes Device_gamma_wire_v4_06112026.seg.nrrd (CT grid, 3D Slicer) and .stl (LPS mm, frame of 2_mesh/HugoJal_Case3.stl).
Usage: python segment_device_gamma.py"""
import os, gzip, struct, json
import numpy as np, nrrd
from scipy import ndimage as ndi
from skimage.feature import hessian_matrix, hessian_matrix_eigvals
from skimage.filters import apply_hysteresis_threshold
from skimage.measure import marching_cubes

HERE = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"); SEG = os.path.dirname(os.path.dirname(HERE))   # 1_segmentation/
MANUAL = SEG + "/device/manual/Device_manual.seg.nrrd"
NAME = "Device_gamma_wire_v4_06112026"
GAMMA, HI, DTH, DAR, SIG_MM, T_LO, T_HI, LOCMAX, HALF_T, ENV_MM, R_AXIS, AXIS_HU, MIN_VOX = 0.3, 1500.0, 2.5, 0.25, 0.5, 0.25, 0.45, 0.5, 0.5, 1.5, 3.0, 900.0, 30

ct, h = nrrd.read(SEG + "/5 DS_Coronaires  0.75  B26f  BestDiast 78 %.nrrd")
la, _ = nrrd.read(SEG + "/Hugo_Jal_left_atrium_segmentation.nrrd")
man, _ = nrrd.read(MANUAL); man = man > 0
SP = np.diag(h["space directions"]).astype(float); ORG = np.asarray(h["space origin"], float)
blood = float(np.median(ct[la > 0]))

def ball(rmm):
    r = np.ceil(rmm / SP).astype(int); zz, yy, xx = np.ogrid[-r[0]:r[0] + 1, -r[1]:r[1] + 1, -r[2]:r[2] + 1]
    return (zz * SP[0]) ** 2 + (yy * SP[1]) ** 2 + (xx * SP[2]) ** 2 <= rmm ** 2

lo = np.array([215, 300, 160]); hi = np.array([315, 400, 250]); s = tuple(slice(a, b) for a, b in zip(lo, hi))
x = ct[s].astype(np.float32); mm = man[s]
g = np.clip((x - blood) / (HI - blood), 0, 1) ** GAMMA
env = ndi.binary_dilation(mm, ball(ENV_MM))

# device axis = line through the two hub centres (index * spacing, mm); origin at the disc hub plane of the rim fit
hub = x > 2500; lab, n = ndi.label(hub); sz = ndi.sum(hub, lab, range(1, n + 1)); top = 1 + np.argsort(-sz)[:2]
hubs = np.array([(np.array(ndi.center_of_mass(hub, lab, t)) + lo) * SP for t in top])
C0 = np.array([114.181, 156.072, 98.509]); N0 = np.array([0.57050955, -0.45992626, 0.68043125])
N = hubs[1] - hubs[0]; N /= np.linalg.norm(N); N = N if N @ N0 > 0 else -N
C = hubs[0] + ((C0 - hubs[0]) @ N) * N                        # point on the hub line at the disc plane of the rim fit
u = np.cross(N, [0, 0, 1.]); u /= np.linalg.norm(u); w = np.cross(N, u)

# cylindrical resampling
TH = np.deg2rad(np.arange(0, 360, DTH)); A = np.arange(-5, 16 + 1e-6, DAR); R = np.arange(0, 16 + 1e-6, DAR)
T3, A3, R3 = np.meshgrid(TH, A, R, indexing="ij")
P = C + A3[..., None] * N + R3[..., None] * (np.cos(T3)[..., None] * u + np.sin(T3)[..., None] * w)
cidx = (P / SP - lo).transpose(3, 0, 1, 2)
G = ndi.map_coordinates(g, cidx, order=1, mode="constant")
E = ndi.map_coordinates(env.astype(np.float32), cidx, order=1, mode="constant") > 0.5

# ridges in each half-plane (axial, radius)
sig = SIG_MM / DAR; RS = np.zeros_like(G)
for k in range(len(TH)):
    l1, l2 = hessian_matrix_eigvals(hessian_matrix(G[k], sigma=sig, order="rc", use_gaussian_derivatives=True))  # l1 >= l2
    RS[k] = np.maximum(-l2, 0) * sig ** 2 * (np.abs(l2) > np.abs(l1))
RS = ndi.gaussian_filter1d(RS, 1.0, axis=0, mode="wrap")
# sheet width: keep bins with at least LOCMAX of the strongest ridge within HALF_T across it (about the FWHM)
lm = ndi.maximum_filter(RS, size=(1, 2 * int(round(HALF_T / DAR)) + 1, 2 * int(round(HALF_T / DAR)) + 1))
allowed = E & (R3 >= R_AXIS) & (A3 > -4) & (A3 < 14)
ah = sorted(float((p - C) @ N) for p in hubs)                  # axial position of the disc hub and the lobe hub
ref = np.percentile(RS[allowed & (RS > 0)], 99)
curv = apply_hysteresis_threshold(np.where(allowed & (RS >= LOCMAX * lm), RS, 0), T_LO * ref, T_HI * ref)
labc, nc = ndi.label(curv, np.ones((3, 3, 3))); szc = ndi.sum(curv, labc, range(1, nc + 1))
curv = np.isin(labc, 1 + np.flatnonzero(szc >= 50))
thick = curv
rel = (np.indices(x.shape).reshape(3, -1).T + lo) * SP - C; ax_ = rel @ N; rp = rel - np.outer(ax_, N)
rad = np.linalg.norm(rp, axis=1); th = np.mod(np.arctan2(rp @ w, rp @ u), 2 * np.pi)
it = np.round(th / np.deg2rad(DTH)).astype(int) % len(TH); iaa = np.round((ax_ - A[0]) / DAR).astype(int); irr = np.round(rad / DAR).astype(int)
ok = (iaa >= 0) & (iaa < len(A)) & (irr < len(R))
sheet = np.zeros(x.size, bool); sheet[ok] = thick[it[ok], iaa[ok], irr[ok]]
sheet = sheet.reshape(x.shape) & env
ax_ = ax_.reshape(x.shape); rad = rad.reshape(x.shape)

# axis (cylindrical coordinates break down there): hubs and the dense bar that joins them, by CT value
core = (rad < R_AXIS + 1.5) & (ax_ > ah[0] - 2.5) & (ax_ < ah[1] + 2.5) & (x >= AXIS_HU) & env
m = (sheet & (rad >= R_AXIS)) | core
labm, nm = ndi.label(m, np.ones((3, 3, 3))); szm = ndi.sum(m, labm, range(1, nm + 1))
m = np.isin(labm, 1 + np.flatnonzero(szm >= MIN_VOX))
mask = np.zeros(ct.shape, np.uint8); mask[s] = m

# .seg.nrrd: reuse the Slicer segmentation header of the manual device, with new name/extent/colour
with open(MANUAL, "rb") as f: raw = f.read()
lines = raw[:raw.find(b"\n\n")].decode("latin1").splitlines()
idx = np.argwhere(mask); e = np.c_[idx.min(0), idx.max(0)].ravel()
rep = {"Segment0_Extent": " ".join(map(str, e)), "Segment0_Name": NAME, "Segment0_ID": NAME, "Segment0_Color": "1.0 0.55 0.1"}
lines = [l.split(":=")[0] + ":=" + rep[l.split(":=")[0]] if ":=" in l and l.split(":=")[0] in rep else l for l in lines]
with open(HERE + "/" + NAME + ".seg.nrrd", "wb") as f:
    f.write(("\n".join(lines) + "\n\n").encode("latin1")); f.write(gzip.compress(np.ascontiguousarray(mask.T).tobytes(), 6))

# STL: marching cubes on the lightly smoothed mask, voxel -> LPS mm
a = np.maximum(idx.min(0) - 3, 0); crop = mask[tuple(slice(p, q + 4) for p, q in zip(a, idx.max(0)))].astype(np.float32)
v, fc, _, _ = marching_cubes(ndi.gaussian_filter(crop, 0.5), 0.5); v = (v + a) * SP + ORG
tri = v[fc]; nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-12
rec = np.zeros(len(fc), dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])); rec["n"] = nrm; rec["v"] = tri
with open(HERE + "/" + NAME + ".stl", "wb") as f:
    f.write(NAME.encode().ljust(80, b" ")); f.write(struct.pack("<I", len(fc))); f.write(rec.tobytes())

# metrics
mb = mask > 0; vox = SP.prod() / 1000
ang = np.degrees(th.reshape(x.shape))
cov = {}
for nm_, reg in [("disc", (np.abs(ax_) < 1.5) & (rad > 3) & (rad < 14)), ("lobe_wall", (ax_ > 3) & (ax_ < 9.5) & (rad > 8.5) & (rad < 12.5))]:
    cov[nm_] = round(len(np.unique(np.floor(ang[m & reg] / 5))) / 72, 3)   # fraction of 5-degree sectors that contain the sheet
stats = {"blood_median_CT": blood, "hub_distance_mm": round(float(np.linalg.norm(hubs[1] - hubs[0])), 2),
         "voxels": int(mb.sum()), "mL": round(mb.sum() * vox, 2), "manual_mL": round(man.sum() * vox, 2),
         "dice_vs_manual": round(2 * (mb & man).sum() / (mb.sum() + man.sum()), 3),
         "fraction_inside_manual": round((mb & man).sum() / mb.sum(), 3),
         "fraction_blood_level_CT_le_454": round(float((ct[mb] <= 454).mean()), 3),
         "angular_coverage_5deg": cov, "median_CT": float(np.median(ct[mb])), "STL_triangles": len(fc),
         "params": dict(gamma=GAMMA, hi=HI, dtheta_deg=DTH, dar_mm=DAR, hessian_sigma_mm=SIG_MM, hysteresis_fraction_of_p99=[T_LO, T_HI], local_max_ratio=LOCMAX,
                        sheet_half_thickness_mm=HALF_T, envelope_mm=ENV_MM, axis_radius_mm=R_AXIS, axis_core_CT=AXIS_HU, min_vox=MIN_VOX)}
json.dump(stats, open(HERE + "/" + NAME + "_stats.json", "w"), indent=1); print(json.dumps(stats, indent=1))
np.savez_compressed(HERE + "/qc_volumes.npz", g=g, th=sheet.astype(np.float32) * 0.5, m=m, man=mm, lo=lo)
np.savez_compressed(HERE + "/qc_cyl_v4.npz", G=G.astype(np.float16), RS=RS.astype(np.float16), curv=curv, A=A, R=R, TH=TH)
