"""Device wire frame (Watchman FLX type) from a gamma-transformed CT, version 3 (03/11/2026). No neural network.

v2 used a white top-hat and one global threshold: where the CT is blurred (one side of the device) the gaps
between struts were filled and the frame looked solid, elsewhere it was open. v3 looks for wires directly and
thresholds relative to the local wire strength:
1. Gamma 0.3: g = clip((CT - blood) / (1500 - blood), 0, 1) ** 0.3 (blood = median CT inside the LA).
2. Ridge (wire) filter: Sato tubeness on g, scales 0.75-1.5 voxels (~0.3-0.7 mm). Lines respond, sheets and
   blobs much less.
3. Allowed region (as v2): axisymmetric outline of the device (angle-averaged g > 0.15 in axial/radius
   coordinates) inside the manual Device.seg.nrrd dilated by 1.5 mm.
4. Local maximum rule: keep a voxel only if its ridge value is >= 50 % of the maximum within 1.5 mm, so every
   region keeps its own struts and drops the background between them, whatever the local brightness.
5. Hysteresis on the ridge value (60th / 85th percentile of the allowed region), hub cores (CT >= 1500) added,
   pieces < 30 voxels removed.
Writes Device_gamma_wire_v3_03112026.seg.nrrd (CT grid, 3D Slicer) and .stl (LPS mm, frame of 2_mesh/HugoJal_Case3.stl).
Usage: python segment_device_gamma_v3.py"""
import os, gzip, struct, json
import numpy as np, nrrd
from scipy import ndimage as ndi
from skimage.filters import sato, apply_hysteresis_threshold
from skimage.measure import marching_cubes

HERE = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"); SEG = os.path.dirname(HERE)
NAME = "Device_gamma_wire_v3_03112026"
GAMMA, HI, SIGMAS, PRIOR_T, ENV_MM, BETA, NB_MM, P_LO, P_HI, MIN_VOX = 0.3, 1500.0, [0.75, 1.0, 1.5], 0.15, 1.5, 0.5, 1.5, 60, 85, 30
# device axis: disc centre (voxel index * spacing, mm) and normal into the LAA, from the disc-rim fit of 22/10/2026
C = np.array([114.181, 156.072, 98.509]); N = np.array([0.57050955, -0.45992626, 0.68043125])

ct, h = nrrd.read(SEG + "/5 DS_Coronaires  0.75  B26f  BestDiast 78 %.nrrd")
la, _ = nrrd.read(SEG + "/Hugo_Jal_left_atrium_segmentation.nrrd")
man, _ = nrrd.read(SEG + "/Device.seg.nrrd"); man = man > 0
SP = np.diag(h["space directions"]).astype(float); ORG = np.asarray(h["space origin"], float)
blood = float(np.median(ct[la > 0]))

def ball(rmm):
    r = np.ceil(rmm / SP).astype(int); zz, yy, xx = np.ogrid[-r[0]:r[0] + 1, -r[1]:r[1] + 1, -r[2]:r[2] + 1]
    return (zz * SP[0]) ** 2 + (yy * SP[1]) ** 2 + (xx * SP[2]) ** 2 <= rmm ** 2

lo = np.array([215, 300, 160]); hi = np.array([315, 400, 250]); s = tuple(slice(a, b) for a, b in zip(lo, hi))
x = ct[s].astype(np.float32); mm = man[s]
g = np.clip((x - blood) / (HI - blood), 0, 1) ** GAMMA
rid = sato(g, sigmas=SIGMAS, black_ridges=False).astype(np.float32)

# allowed region: device outline in (axial, radius) around the axis, inside the dilated manual mask
rel = (np.indices(x.shape).reshape(3, -1).T + lo) * SP - C; ax = rel @ N; rp = rel - np.outer(ax, N)
rad = np.linalg.norm(rp, axis=1).reshape(x.shape); ax = ax.reshape(x.shape)
ab = np.arange(-6, 20.01, 0.5); rb = np.arange(0, 17.01, 0.5)
inb = (ax >= ab[0]) & (ax < ab[-1]) & (rad < rb[-1])
S, _, _ = np.histogram2d(ax[inb], rad[inb], [ab, rb], weights=g[inb]); Nn, _, _ = np.histogram2d(ax[inb], rad[inb], [ab, rb])
outline = ndi.binary_dilation(S / np.maximum(Nn, 1) > PRIOR_T)
prior = outline[np.clip(np.digitize(ax, ab) - 1, 0, len(ab) - 2), np.clip(np.digitize(rad, rb) - 1, 0, len(rb) - 2)] & inb
allowed = prior & ndi.binary_dilation(mm, ball(ENV_MM))

locmax = ndi.maximum_filter(np.where(allowed, rid, 0), footprint=ball(NB_MM))
keep = allowed & (rid >= BETA * locmax)
t_lo, t_hi = np.percentile(rid[allowed], [P_LO, P_HI])
m = apply_hysteresis_threshold(np.where(keep, rid, 0), t_lo, t_hi) | (allowed & (x >= HI))
lab, n = ndi.label(m, np.ones((3, 3, 3))); sz = ndi.sum(m, lab, range(1, n + 1))
m = np.isin(lab, 1 + np.flatnonzero(sz >= MIN_VOX))
mask = np.zeros(ct.shape, np.uint8); mask[s] = m

# .seg.nrrd: reuse the Slicer segmentation header of the manual device, with new name/extent/colour
with open(SEG + "/Device.seg.nrrd", "rb") as f: raw = f.read()
lines = raw[:raw.find(b"\n\n")].decode("latin1").splitlines()
idx = np.argwhere(mask); e = np.c_[idx.min(0), idx.max(0)].ravel()
rep = {"Segment0_Extent": " ".join(map(str, e)), "Segment0_Name": NAME, "Segment0_ID": NAME, "Segment0_Color": "0.2 0.6 1.0"}
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

# metrics: overlap with the manual mask, rim completeness, and how evenly the frame is filled around the device
mb = mask > 0; vox = SP.prod() / 1000
u = np.cross(N, [0, 0, 1.]); u /= np.linalg.norm(u); w = np.cross(N, u)
ang = np.degrees(np.arctan2(rp @ w, rp @ u)).reshape(x.shape)
rim = (np.abs(ax) < 1.5) & (rad > 12.5) & (rad < 15.5)
fill = {}
for nm, reg in [("face", (np.abs(ax) < 1.5) & (rad < 12.5)), ("wall", (ax > 1.5) & (ax < 10.5) & (rad > 9) & (rad < 13))]:
    f = [m[sec].sum() / max(sec.sum(), 1) for sec in (reg & allowed & (ang >= -180 + 45 * k) & (ang < -135 + 45 * k) for k in range(8))]
    fill[nm] = [round(float(v_), 2) for v_ in f]
stats = {"blood_median_CT": blood, "voxels": int(mb.sum()), "mL": round(mb.sum() * vox, 2),
         "manual_voxels": int(man.sum()), "manual_mL": round(man.sum() * vox, 2),
         "dice_vs_manual": round(2 * (mb & man).sum() / (mb.sum() + man.sum()), 3),
         "fraction_inside_manual": round((mb & man).sum() / mb.sum(), 3), "fraction_of_manual_covered": round((mb & man).sum() / man.sum(), 3),
         "rim_angular_coverage_5deg": round(len(np.unique(np.floor(ang[m & rim] / 5))) / 72, 3),
         "fill_per_45deg_sector": fill, "median_CT": float(np.median(ct[mb])), "STL_triangles": len(fc),
         "params": dict(gamma=GAMMA, hi=HI, sato_sigmas_vox=SIGMAS, prior_t=PRIOR_T, envelope_mm=ENV_MM, local_max_ratio=BETA,
                        local_max_mm=NB_MM, hysteresis_percentiles=[P_LO, P_HI], min_vox=MIN_VOX)}
json.dump(stats, open(HERE + "/" + NAME + "_stats.json", "w"), indent=1); print(json.dumps(stats, indent=1))
np.savez_compressed(HERE + "/qc_volumes.npz", g=g, th=np.clip(rid / t_hi, 0, 2) * 0.3, m=m, man=mm, lo=lo)
