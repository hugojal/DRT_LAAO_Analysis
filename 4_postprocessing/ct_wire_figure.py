"""CT screenshots of the gamma wire-frame device segmentation (1_segmentation/gamma_experiment, v3) for the report, 04/11/2026.
(a) en-face slice through the device disc (proximal face): gamma-transformed CT (as used for the segmentation) with the
    wire segmentation outlined in orange -> rim ring and struts.
(a') the same disc plane with the U-Net (nnInteractive) device segmentation in magenta, plain CT window 0-1500 HU.
(b) slice along the device axis: CT in a standard contrast window with the LA (blue) and wire device (orange) outlines ->
    contrast-filled blood reaches the atrial face of the device (no hypoattenuating layer = no thrombus).
Device axis = disc centre and normal of segment_device_gamma_v3.py (index*spacing mm, same grid as the CT).
usage: python ct_wire_figure.py <out_dir>"""
import os, sys
import numpy as np, nrrd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.ndimage import map_coordinates

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); SEG = os.path.join(ROOT, "1_segmentation")
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "5_report", "figures_run6"); os.makedirs(OUT, exist_ok=True)
C = np.array([114.181, 156.072, 98.509]); N = np.array([0.57050955, -0.45992626, 0.68043125]); N /= np.linalg.norm(N)
GAMMA, HI = 0.3, 1500.0
ct, h = nrrd.read(os.path.join(SEG, "5 DS_Coronaires  0.75  B26f  BestDiast 78 %.nrrd"))
la, _ = nrrd.read(os.path.join(SEG, "Hugo_Jal_left_atrium_segmentation.nrrd"))
wire, _ = nrrd.read(os.path.join(SEG, "gamma_experiment", "Device_gamma_wire_v3_03112026.seg.nrrd"))
unet, _ = nrrd.read(os.path.join(SEG, "unet_experiment", "Device_unet_wire.seg.nrrd"))          # nnInteractive (promptable 3D U-Net), 31/10/2026
SP = np.diag(h["space directions"]).astype(float)
blood = float(np.median(ct[la > 0]))

def plane(origin, e1, e2, half, res=0.1):
    s = np.arange(-half, half + res / 2, res); A, B = np.meshgrid(s, s[::-1])         # rows top->bottom = +e2 -> -e2
    P = origin + A[..., None] * e1 + B[..., None] * e2; idx = (P / SP).reshape(-1, 3).T
    sample = lambda vol, o: map_coordinates(vol.astype(np.float32), idx, order=o, mode="nearest").reshape(A.shape)
    return sample, half

def scalebar(ax, half, n_px, mm=10):
    px = n_px / (2 * half); x0, y0 = 0.06 * n_px, 0.93 * n_px
    ax.plot([x0, x0 + mm * px], [y0, y0], color="white", lw=3); ax.text(x0 + mm * px / 2, y0 - 0.025 * n_px, f"{mm} mm", color="white", ha="center", va="bottom", fontsize=13)

def overlay(ax, w, col=(1.0, 0.62, 0.1), edge="#ff9f1a"):                           # segmentation: filled, semi-transparent (orange = gamma wire)
    rgba = np.zeros(w.shape + (4,)); rgba[..., :3] = col; rgba[..., 3] = 0.55 * (w > 0.5); ax.imshow(rgba)
    ax.contour(w, [0.5], colors=[edge], linewidths=0.8)

def save(fig, name): fig.savefig(os.path.join(OUT, name), dpi=150, bbox_inches="tight", pad_inches=0); plt.close(fig); print("saved", name)

# (a) en-face through the disc
u = np.cross(N, [0, 0, 1.0]); u /= np.linalg.norm(u); v = np.cross(N, u)
sample, half = plane(C, u, v, 17.0)
g = np.clip((sample(ct, 1) - blood) / (HI - blood), 0, 1) ** GAMMA; w = sample(wire, 1)
fig, ax = plt.subplots(figsize=(4.5, 4.5)); ax.imshow(g, cmap="gray", vmin=0, vmax=1)
overlay(ax, w); scalebar(ax, half, g.shape[0]); ax.axis("off"); save(fig, "ct_wire_enface.png")
# (a') same plane, U-Net segmentation (magenta) on the plain CT in a wide window (the U-Net used no gamma transform)
img = sample(ct, 1); wu = sample(unet, 1)
fig, ax = plt.subplots(figsize=(4.5, 4.5)); ax.imshow(img, cmap="gray", vmin=0, vmax=1500)
overlay(ax, wu, (0.85, 0.25, 0.85), "#e040e0"); scalebar(ax, half, img.shape[0]); ax.axis("off"); save(fig, "ct_unet_enface.png")

# (b) along the device axis, standard window; LA side on the left (-N), appendage on the right (+N)
for tag, e2 in (("axis", u),):                                                   # plane through the axis that cuts the cage struts
    sample, half = plane(C, N, e2, 21.0)
    img = sample(ct, 1); w = sample(wire, 1); l = sample((la > 0).astype(np.float32), 1)
    fig, ax = plt.subplots(figsize=(4.5, 4.5)); ax.imshow(img, cmap="gray", vmin=-150, vmax=650)
    ax.contour(l, [0.5], colors=["#4da3ff"], linewidths=1.8); overlay(ax, w)
    scalebar(ax, half, img.shape[0]); ax.axis("off"); save(fig, f"ct_wire_{tag}.png")
