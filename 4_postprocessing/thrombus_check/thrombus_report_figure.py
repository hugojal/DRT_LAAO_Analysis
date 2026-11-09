"""Report panels of the thrombus check (07/11/2026), same method as thrombus_check.py (03/11/2026):
  fig_thr_views.pdf    (report, since 09/11/2026) CT side view along the device axis and front view parallel to the device face,
                       candidate regions in red, and a grey scale marking contrast blood and soft tissue (clot, approx. 40-150 HU).
  (until 07/11/2026:) fig_thr_ct.pdf  CT on the long-axis plane through the largest low-density region in front of the device, thrombus
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
man, _ = nrrd.read(os.path.join(S, "device", "gamma", "Device_gamma_wire_v4_06112026.seg.nrrd")); man = man > 0   # device: gamma + manual edits (09/11/2026)
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
# report figure (09/11/2026): CT only, the regions that could be clot outlined in red, plus a grey scale that shows how
# contrast blood and soft tissue (a clot) look in this window. Two planes: along the device axis through the largest
# candidate, and parallel to the device face at the depth of that candidate.
dep = float(cb @ N)                                                     # mm in front of the face centre (negative = LA side)
P1 = C + 3 * N + A[..., None] * N + B[..., None] * d                    # side view: x along the axis (LA on the left)
P2 = C + dep * N + A[..., None] * np.cross(N, d) + B[..., None] * d     # front view, seen from the LA
fig = plt.figure(figsize=(3.9, 1.75)); gs = fig.add_gridspec(1, 3, width_ratios=[1, 1, 0.09], wspace=0.22)
for k, (Pk, ttl) in enumerate(((P1, "side view"), (P2, "front view"))):
    a = fig.add_subplot(gs[0, k]); xs = t + 3 if k == 0 else t
    a.imshow(gw(samp(ct, Pk)).T, cmap="gray", origin="lower", extent=[xs[0], xs[-1], t[0], t[-1]], vmin=0, vmax=1)
    a.contour(xs, t, samp(full, Pk, 0).T, [0.5], colors="red", linewidths=0.9)
    if k == 0:
        a.text(-14.5, 16, "LA", color="w", fontsize=7.5, va="top"); a.text(4, 16, "device", color="w", fontsize=7.5, va="top"); a.set_xlim(-16, 21)
    else:
        a.set_xlim(-18, 18)
    a.plot([4, 14] if k == 1 else [9, 19], [-16, -16], color="w", lw=1.5); a.text(9 if k == 1 else 14, -14.7, "10 mm", color="w", fontsize=6.5, ha="center")
    a.set_ylim(-18, 18); a.set_xticks([]); a.set_yticks([]); [sp.set_visible(False) for sp in a.spines.values()]
    a.set_title(ttl, fontsize=7.5, pad=2)
# grey scale with what each grey means (same window and gamma as the images)
cb_ax = fig.add_subplot(gs[0, 2]); hu = np.linspace(-100, 700, 200)
cb_ax.imshow(gw(hu)[:, None], cmap="gray", origin="lower", extent=[0, 1, -100, 700], aspect="auto", vmin=0, vmax=1)
cb_ax.set_xticks([]); cb_ax.yaxis.tick_right(); cb_ax.set_yticks([0, 200, 400, 600]); cb_ax.tick_params(labelsize=6.5, length=2, pad=1)
for (lo_, hi_, lab_) in ((blood[0], 520, "blood"), (40, 150, "clot")):
    cb_ax.annotate("", xy=(-0.7, lo_), xytext=(-0.7, hi_), xycoords=("axes fraction", "data"), arrowprops=dict(arrowstyle="-", color="k", lw=0.8))
    cb_ax.text(-1.25, 0.5 * (lo_ + hi_), lab_, rotation=90, fontsize=6.5, ha="center", va="center", transform=cb_ax.get_yaxis_transform())
cb_ax.set_title("HU", fontsize=6.5, pad=2)
fig.savefig(os.path.join(OUT, "fig_thr_views.pdf"), bbox_inches="tight", pad_inches=0.01); plt.close(fig)
print("candidates:", len(keep), "largest", round((lab == big).sum() * SP.prod(), 1), "mm3; blood p5/p50", blood.round())
