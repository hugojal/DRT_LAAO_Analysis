"""Check the CT for a device-related thrombus (DRT) on the LA side of the occluder (03/11/2026).

A DRT on contrast CT is a low-density mass (soft tissue, ~50-200 HU) attached to the atrial face of the device and
standing out against the contrast-filled blood (~400 HU here). Steps:
1. Display with a gamma window for thrombus: [-100, 700] HU, gamma 1.5 (dark soft tissue, bright blood).
2. Low-density map: CT 250 > HU > -50 in the LA cavity (LA segmentation closed by 3 mm), 0-10 mm in front of the
   device face, outside the device; connected pieces >= 2 mm3 are measured (volume, density, shape, contact).
3. Blood in contact with the face: density of the LA voxels 0.5-3 mm in front of the face.
4. Profiles from the lower device edge into the LA, to see whether the low-density tissue there is wall.
Writes thrombus_check.png (figure) and thrombus_check.json (numbers). Usage: python thrombus_check.py"""
import os, json
import numpy as np, nrrd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"); ROOT = os.path.dirname(os.path.dirname(HERE)); S = ROOT + "/1_segmentation/"
ct, h = nrrd.read(S + "5 DS_Coronaires  0.75  B26f  BestDiast 78 %.nrrd"); ct = ct.astype(np.float32)
la, _ = nrrd.read(S + "Hugo_Jal_left_atrium_segmentation.nrrd"); la = la > 0
man, _ = nrrd.read(S + "device/manual/Device_manual.seg.nrrd"); man = man > 0
SP = np.diag(h["space directions"]).astype(float)
# device axis: face centre (voxel index * spacing, mm) and normal into the LAA, from the rim fit of 22/10/2026
C = np.array([114.181, 156.072, 98.509]); N = np.array([0.57050955, -0.45992626, 0.68043125])
u = np.cross(N, [0, 0, 1.]); u /= np.linalg.norm(u); v = np.cross(N, u)

def ball(r):
    k = np.ceil(r / SP).astype(int); z, y, w = np.ogrid[-k[0]:k[0] + 1, -k[1]:k[1] + 1, -k[2]:k[2] + 1]
    return (z * SP[0]) ** 2 + (y * SP[1]) ** 2 + (w * SP[2]) ** 2 <= r * r

lo = np.array([190, 270, 120]); hi = np.array([340, 430, 274]); s = tuple(slice(a, b) for a, b in zip(lo, hi))
x = ct[s]; L = la[s]; D = man[s]
rel = (np.indices(x.shape).reshape(3, -1).T + lo) * SP - C; axv = rel @ N
ax = axv.reshape(x.shape); rad = np.linalg.norm(rel - np.outer(axv, N), axis=1).reshape(x.shape)
blood = np.percentile(x[L & (ax > -10) & (ax < 0) & (rad < 17)], [5, 50])

# 2. low-density pieces in front of the face
cav = ndi.binary_closing(L | D, ball(3.0)) | L
zone = (ax > -10) & (ax < 0) & (rad < 17)
hypo = (x < 250) & (x > -50) & cav & zone & ~ndi.binary_dilation(D, ball(0.5))
lab, n = ndi.label(hypo, np.ones((3, 3, 3))); vox = SP.prod(); pieces = []
for k in range(1, n + 1):
    m = lab == k
    if m.sum() * vox < 2: continue
    P = np.argwhere(m) * SP; ev = np.sqrt(np.linalg.eigvalsh(np.cov((P - P.mean(0)).T)))
    c = (np.argwhere(m).mean(0) + lo) * SP - C
    pieces.append(dict(volume_mm3=round(m.sum() * vox, 1), median_CT=float(np.median(x[m])), frac_below_0HU=round(float((x[m] < 0).mean()), 2),
                       axial_mm=round(float(c @ N), 1), angle_deg=round(float(np.degrees(np.arctan2(c @ v, c @ u)))),
                       radius_mm=round(float(np.linalg.norm(c - (c @ N) * N)), 1), size_sd_mm=[round(float(e), 1) for e in ev],
                       touches_device=bool((ndi.binary_dilation(m, ball(1.0)) & D).any())))
pieces.sort(key=lambda p: -p["volume_mm3"])

# 3. blood in contact with the face
front = L & (ax > -3) & (ax < -0.5) & (rad > 4) & (rad < 13)
contact = dict(voxels=int(front.sum()), CT_p1_p5_p50=np.percentile(x[front], [1, 5, 50]).round().tolist(), frac_below_250HU=round(float((x[front] < 250).mean()), 4))

# figure
def samp(vol, P): return ndi.map_coordinates(np.asarray(vol, np.float32), (P / SP).transpose(2, 0, 1), order=1, mode="nearest")
def gw(c): return np.clip((c + 100) / 800, 0, 1) ** 1.5
ph = np.radians(pieces[0]["angle_deg"]) if pieces else 0.0
fig = plt.figure(figsize=(16, 9.6)); gs = fig.add_gridspec(2, 4)
def panel(a, P, ext, ttl, lines=None):
    c = samp(ct, P); a.imshow(gw(c).T, cmap="gray", origin="lower", extent=ext, vmin=0, vmax=1)
    X = np.linspace(ext[0], ext[1], c.shape[0]); Y = np.linspace(ext[2], ext[3], c.shape[1])
    a.contour(X, Y, samp(la, P).T, [0.5], colors="lime", linewidths=0.7); a.contour(X, Y, samp(man, P).T, [0.5], colors="c", linewidths=0.7)
    for (p0, p1, col) in (lines or []): a.plot([p0[0], p1[0]], [p0[1], p1[1]], color=col, lw=1.2)
    a.set_title(ttl, fontsize=9); a.set_xticks([]); a.set_yticks([])
t = np.arange(-30, 30, 0.2); A, B = np.meshgrid(t, t, indexing="ij")
profiles = {}
for j, dphi in enumerate([0, 90]):
    d = np.cos(ph + np.radians(dphi)) * u + np.sin(ph + np.radians(dphi)) * v
    P = C + 5 * N + A[..., None] * N + B[..., None] * d
    lines = []
    if j == 0:   # profiles from the face into the LA at 3 heights on the lower half of the device
        for hgt, col in [(-4, "orange"), (-8, "yellow"), (-11, "magenta")]:
            q = C + hgt * d; ts = np.arange(0, 15, 0.2); line = q[None] - ts[:, None] * N
            profiles[(hgt, col)] = (ts, samp(ct, line[None])[0]); lines.append(((0, hgt), (-15, hgt), col))
    panel(fig.add_subplot(gs[0, j]), P, [-25, 35, -30, 30], f"long axis {'through the low-density region' if j == 0 else '90 deg to it'}\nleft = LA, right = LAA", lines)
t2 = np.arange(-20, 20, 0.2); A2, B2 = np.meshgrid(t2, t2, indexing="ij")
for j, o in enumerate([-1.5, -3.5]):
    panel(fig.add_subplot(gs[0, 2 + j]), C + o * N + A2[..., None] * u + B2[..., None] * v, [-20, 20, -20, 20], f"parallel to the device face, {o} mm on the LA side")
a = fig.add_subplot(gs[1, :2])
for (hgt, col), (ts, prof) in profiles.items(): a.plot(ts, prof, color=col, label=f"{abs(hgt)} mm below the hub")
a.axhspan(blood[0], 520, color="0.85", label="LA blood (5th pct to above median)"); a.axhspan(50, 200, color="#f6d7d7", label="thrombus / soft tissue range")
a.set_xlabel("distance from the device face into the LA (mm)"); a.set_ylabel("CT (HU)"); a.set_ylim(-200, 1200); a.legend(fontsize=8); a.set_title("Density from the lower device edge into the LA", fontsize=9)
a = fig.add_subplot(gs[1, 2:]); a.axis("off")
txt = [f"LA blood next to the device: median {blood[1]:.0f} HU (5th percentile {blood[0]:.0f})",
       f"Blood touching the face (0.5-3 mm, r 4-13 mm): 5th percentile {contact['CT_p1_p5_p50'][1]:.0f} HU, {100 * contact['frac_below_250HU']:.1f} % below 250 HU",
       "Low-density pieces (<250 HU) in front of the face:"]
for p in pieces[:3]:
    txt.append(f"  {p['volume_mm3']} mm3, median {p['median_CT']:.0f} HU, {p['axial_mm']} mm in front, angle {p['angle_deg']} deg, "
               f"size SD {p['size_sd_mm']} mm, touches device: {p['touches_device']}")
a.text(0, 1, "\n".join(txt), va="top", fontsize=9, family="monospace", wrap=True)
fig.suptitle("Thrombus check on the LA side of the device. Window [-100, 700] HU with gamma 1.5; green = LA segmentation, cyan = device", fontsize=10)
plt.tight_layout(); plt.savefig(HERE + "/thrombus_check.png", dpi=110)
json.dump(dict(blood_CT_p5_p50=blood.round().tolist(), blood_at_face=contact, low_density_pieces=pieces,
               profiles={f"{abs(k[0])}mm_below_hub": dict(dist_mm=v_[0][::5].round(1).tolist(), CT=v_[1][::5].round().tolist()) for k, v_ in profiles.items()}),
          open(HERE + "/thrombus_check.json", "w"), indent=1)
print(json.dumps(dict(blood=blood.tolist(), contact=contact, pieces=pieces[:3]), indent=1))
