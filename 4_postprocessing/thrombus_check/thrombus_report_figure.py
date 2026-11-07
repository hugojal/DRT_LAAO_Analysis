"""Report panels of the thrombus check (07/11/2026), same method as thrombus_check.py (03/11/2026):
  fig_thr_ct.pdf       CT on the long-axis plane through the largest low-density region in front of the device, thrombus
                       window [-100, 700] HU with gamma 1.5 (soft tissue dark, contrast blood bright). Only the regions that could
                       be thrombus are outlined (red: < 250 HU, inside the LA cavity, 0-10 mm in front of the device face, >= 2 mm3);
                       coloured lines = density profiles of the second panel (dashed: through the largest dark region).
  fig_thr_profile.pdf  CT density along those lines, from the device face into the LA, against the LA blood range and the
                       soft-tissue (thrombus) range.
usage: python thrombus_report_figure.py <out_dir>"""
import os, sys
import numpy as np, nrrd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy import ndimage as ndi
HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(os.path.dirname(HERE)); S = os.path.join(ROOT, "1_segmentation")
OUT = sys.argv[1] if len(sys.argv) > 1 else HERE; os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"text.usetex": True, "font.family": "serif", "font.size": 8, "axes.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "legend.fontsize": 7.5})
ct, h = nrrd.read(os.path.join(S, "5 DS_Coronaires  0.75  B26f  BestDiast 78 %.nrrd")); ct = ct.astype(np.float32)
la, _ = nrrd.read(os.path.join(S, "Hugo_Jal_left_atrium_segmentation.nrrd")); la = la > 0
man, _ = nrrd.read(os.path.join(S, "device", "manual", "Device_manual.seg.nrrd")); man = man > 0
SP = np.diag(h["space directions"]).astype(float)
C = np.array([114.181, 156.072, 98.509]); N = np.array([0.57050955, -0.45992626, 0.68043125])   # device face centre and axis (rim fit 22/10/2026)
u = np.cross(N, [0, 0, 1.]); u /= np.linalg.norm(u); v = np.cross(N, u)
def ball(r):
    k = np.ceil(r / SP).astype(int); z, y, w = np.ogrid[-k[0]:k[0] + 1, -k[1]:k[1] + 1, -k[2]:k[2] + 1]
    return (z * SP[0]) ** 2 + (y * SP[1]) ** 2 + (w * SP[2]) ** 2 <= r * r
lo = np.array([190, 270, 120]); hi = np.array([340, 430, 274]); s = tuple(slice(a, b) for a, b in zip(lo, hi))
x = ct[s]; L = la[s]; D = man[s]
rel = (np.indices(x.shape).reshape(3, -1).T + lo) * SP - C; axv = rel @ N
ax = axv.reshape(x.shape); rad = np.linalg.norm(rel - np.outer(axv, N), axis=1).reshape(x.shape)
blood = np.percentile(x[L & (ax > -10) & (ax < 0) & (rad < 17)], [5, 50])
cav = ndi.binary_closing(L | D, ball(3.0)) | L
hypo = (x < 250) & (x > -50) & cav & (ax > -10) & (ax < 0) & (rad < 17) & ~ndi.binary_dilation(D, ball(0.5))
lab, n = ndi.label(hypo, np.ones((3, 3, 3)))
keep = [k for k in range(1, n + 1) if (lab == k).sum() * SP.prod() >= 2]
cand = np.isin(lab, keep)
big = max(keep, key=lambda k: (lab == k).sum()); cb = (np.argwhere(lab == big).mean(0) + lo) * SP - C
ph = np.arctan2(cb @ v, cb @ u)                         # long-axis plane through the largest candidate region
d = np.cos(ph) * u + np.sin(ph) * v
full = np.zeros(ct.shape, np.float32); full[s] = cand
def samp(vol, P, o=1): return ndi.map_coordinates(np.asarray(vol, np.float32), (P / SP).transpose(2, 0, 1), order=o, mode="nearest")
gw = lambda c: np.clip((c + 100) / 800, 0, 1) ** 1.5
t = np.arange(-18, 18, 0.1); A, B = np.meshgrid(t, t, indexing="ij")
P = C + 3 * N + A[..., None] * N + B[..., None] * d                     # plane centred 3 mm behind the face
ext = [t[0] + 3, t[-1] + 3, t[0], t[-1]]                                 # x: distance along the axis from the face (LA < 0)
fig, a = plt.subplots(figsize=(1.75, 1.75))
a.imshow(gw(samp(ct, P)).T, cmap="gray", origin="lower", extent=ext, vmin=0, vmax=1)
a.contour(t + 3, t, samp(full, P, 0).T, [0.5], colors="red", linewidths=0.8)
cols = {-4: "orange", -8: "yellow", -11: "magenta"}; prof = {}
m2 = samp(full, P, 0) > 0.5; hc = float(B[m2].mean()); cols[hc] = "darkred"   # one more line through the centre of the dark region in this plane
for hgt, col in cols.items():
    q = C + hgt * d; ts = np.arange(0, 15, 0.2); prof[hgt] = (ts, samp(ct, (q[None] - ts[:, None] * N)[None])[0])
    a.plot([0, -15], [hgt, hgt], color=col, lw=0.9, ls="--" if col == "darkred" else "-")
a.text(-14.5, 15.5, "LA", color="w", fontsize=7.5, va="top"); a.text(4, 15.5, "device", color="w", fontsize=7.5, va="top")
a.plot([10, 20], [-16.5, -16.5], color="w", lw=1.5); a.text(15, -15.2, "10 mm", color="w", fontsize=6.5, ha="center")
a.set_xlim(-16, 21); a.set_ylim(-18, 18); a.set_xticks([]); a.set_yticks([]); [sp.set_visible(False) for sp in a.spines.values()]
fig.savefig(os.path.join(OUT, "fig_thr_ct.pdf"), bbox_inches="tight", pad_inches=0.01); plt.close(fig)
fig, a = plt.subplots(figsize=(2.3, 1.55))
a.axhspan(blood[0], 520, color="0.85", lw=0, label="LA blood"); a.axhspan(50, 200, color="#f4c9c9", lw=0, label="soft tissue (thrombus)")
for hgt, col in cols.items(): a.plot(*prof[hgt], color=col if col != "yellow" else "#d4b000", lw=1.0, ls="--" if col == "darkred" else "-")
print("profile through the dark region: min", prof[hc][1].min().round(), "HU at", prof[hc][0][prof[hc][1].argmin()], "mm; height", round(hc, 1), "mm")
a.set_xlabel("distance from the device face (mm)"); a.set_ylabel("CT (HU)", labelpad=1); a.set_ylim(min(-100, float(min(p_[1].min() for p_ in prof.values())) - 50), 900); a.set_xlim(0, 15)
a.legend(loc="upper center", bbox_to_anchor=(0.5, -0.32), ncol=2, frameon=False, handlelength=1.4, columnspacing=1.0)
fig.savefig(os.path.join(OUT, "fig_thr_profile.pdf"), bbox_inches="tight", pad_inches=0.01); plt.close(fig)
print("candidates:", len(keep), "largest", round((lab == big).sum() * SP.prod(), 1), "mm3; blood p5/p50", blood.round())
