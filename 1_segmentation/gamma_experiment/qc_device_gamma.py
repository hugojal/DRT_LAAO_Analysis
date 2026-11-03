"""QC images for segment_device_gamma_v3.py, written to qc/: slices parallel to the disc (gamma, ridge filter, masks)
and 3D views of the gamma wire frame next to the manual Device.seg.nrrd. Run right after the segmentation script.
Usage: python qc_device_gamma.py [Device_gamma_wire_v3_03112026] [gamma] [filter label, e.g. "ridge filter"]"""
import os, sys
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy import ndimage as ndi
import pyvista as pv

HERE = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"); SEG = os.path.dirname(HERE)
NAME = sys.argv[1] if len(sys.argv) > 1 else "Device_gamma_wire_v3_03112026"
GLABEL = sys.argv[2] if len(sys.argv) > 2 else "0.3"
FLABEL = sys.argv[3] if len(sys.argv) > 3 else "ridge filter"
SP = np.array([0.4453125, 0.4453125, 0.5]); C = np.array([114.181, 156.072, 98.509]); N = np.array([0.57050955, -0.45992626, 0.68043125])
q = np.load(HERE + "/qc_volumes.npz"); lo = q["lo"]

def plane(vol, off, half=18, res=0.2):
    u = np.cross(N, [0, 0, 1.]); u /= np.linalg.norm(u); v = np.cross(N, u)
    t = np.arange(-half, half, res); U, V = np.meshgrid(t, t, indexing="ij")
    P = C + off * N + U[..., None] * u + V[..., None] * v
    return ndi.map_coordinates(vol.astype(np.float32), (P / SP - lo).transpose(2, 0, 1), order=1).T

offs = [-3, -1, 0, 1, 3, 6, 9, 12]
fig, ax = plt.subplots(3, len(offs), figsize=(2.2 * len(offs), 6.9))
for j, o in enumerate(offs):
    G = plane(q["g"], o)
    ax[0, j].imshow(G, cmap="gray", origin="lower", vmin=0, vmax=1); ax[0, j].set_title(f"gamma {GLABEL}, {o:+d} mm", fontsize=8)
    ax[1, j].imshow(plane(q["th"], o), cmap="gray", origin="lower", vmin=0, vmax=0.6); ax[1, j].set_title(FLABEL, fontsize=8)
    ax[2, j].imshow(G, cmap="gray", origin="lower", vmin=0, vmax=1)
    ax[2, j].contour(plane(q["man"], o) > 0.5, [0.5], colors="c", linewidths=0.6)
    ax[2, j].contour(plane(q["m"], o) > 0.5, [0.5], colors="r", linewidths=0.6); ax[2, j].set_title("red gamma, cyan manual", fontsize=8)
for a in ax.ravel(): a.axis("off")
fig.suptitle("Slices parallel to the device disc (negative = LA side, positive = into the LAA)", fontsize=9)
plt.tight_layout(); plt.savefig(HERE + "/qc/QC_slices_" + NAME + ".png", dpi=110); plt.close()

pv.OFF_SCREEN = True
gam = pv.read(HERE + "/" + NAME + ".stl")
# manual surface from the label map, in the same LPS mm frame
ORG = np.array([-90.77734375, -309.77734375, 795.5])
mvol = pv.ImageData(dimensions=np.array(q["man"].shape), spacing=SP, origin=lo * SP + ORG)
mvol.point_data["m"] = q["man"].astype(np.float32).ravel(order="F")
man = mvol.contour([0.5], scalars="m").smooth(n_iter=50)
foc = C + 6 * N + ORG; side = np.cross(N, [0, 0, 1.]); side /= np.linalg.norm(side); side2 = np.cross(N, side)
views = [("from LA", -N, (0, 0, 1)), ("from LAA", N, (0, 0, 1)), ("side A", side, N), ("side B", side2, N)]
p = pv.Plotter(shape=(2, 4), window_size=(1600, 800))
for i, (mesh, col, title) in enumerate([(gam, "tomato", "Gamma wire frame"), (man, "lightblue", "Manual")]):
    for k, (vn, view, up) in enumerate(views):
        p.subplot(i, k); p.add_mesh(mesh, color=col, smooth_shading=True); p.add_text(f"{title} - {vn}", font_size=9)
        p.camera.focal_point = foc; p.camera.position = foc + 70 * view; p.camera.up = up
p.screenshot(HERE + "/qc/QC_3D_" + NAME + ".png"); p.close()
print("QC images written")
