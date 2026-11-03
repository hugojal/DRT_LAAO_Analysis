"""Locate the mitral annulus on the CT and fit the mitral annular plane (03/11/2026).

In planes that contain the valve axis (every 10 deg), the atrio-ventricular groove appears on each side of the
valve as a notch of wall and fat (CT < 200 HU) pointing towards the axis; the leaflets hang from the notch tips
into the LV as thin dark lines. Thin structures (leaflets, < ~2.5 mm) are removed by a morphological opening,
and on each side the tip of the remaining thick tissue closest to the axis, near the valve, is the annulus
hinge point. The hinge points from all planes are fitted with a plane: its normal is the valve axis (direction
of the flow from LA to LV) and its centroid is the annulus centre. Repeated with the new axis until it is stable.
Writes mitral_annulus.json and mitral_annulus_check.png. Usage: python find_mitral_annulus.py"""
import os, json
import numpy as np, nrrd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy import ndimage as ndi

HERE = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"); ROOT = os.path.dirname(os.path.dirname(HERE))
ct, h = nrrd.read(ROOT + "/1_segmentation/5 DS_Coronaires  0.75  B26f  BestDiast 78 %.nrrd"); ct = ct.astype(np.float32)
SP = np.diag(h["space directions"]).astype(float); ORG = np.asarray(h["space origin"], float)
# LPS mm <-> voxel index (axis-aligned grid)
def to_vox(P): return (P - ORG) / SP
# start: centre and outward normal of the current mitral cap of 2_mesh/HugoJal_Case3.stl
c0 = np.array([27.2, -172.5, 855.0]); n0 = np.array([0.772, -0.564, -0.293]); n0 /= np.linalg.norm(n0)

def frame(n):
    a = np.cross(n, [0, 0, 1.]); a /= np.linalg.norm(a); b = np.cross(n, a); return a, b

def radial_plane(c, n, phi, half=40, res=0.25):
    a, b = frame(n); d = np.cos(phi) * a + np.sin(phi) * b
    t = np.arange(-half, half + 1e-6, res); X, Y = np.meshgrid(t, t, indexing="ij")    # X along axis (LA < 0 < LV), Y in-plane
    P = c + X[..., None] * n + Y[..., None] * d
    img = ndi.map_coordinates(ct, to_vox(P).transpose(2, 0, 1), order=1, mode="nearest")
    return t, img, d

def hinges(c, n, res=0.25, win=(-8, 10), rmin=6, rmax=30):
    pts, prof = [], []
    k = int(round(1.25 / res)); disk = np.hypot(*np.mgrid[-k:k + 1, -k:k + 1]) <= k   # opening radius 1.25 mm
    for phi in np.radians(np.arange(0, 180, 10)):
        t, img, d = radial_plane(c, n, phi, res=res)
        thick = ndi.binary_opening(ndi.gaussian_filter(img, 2) < 200, structure=disk)  # wall/fat, leaflets removed
        X, Y = np.meshgrid(t, t, indexing="ij")
        for sgn in (+1, -1):                                                       # each side of the axis
            cand = thick & (X > win[0]) & (X < win[1]) & (sgn * Y > rmin) & (sgn * Y < rmax)
            if not cand.any(): continue
            r = np.where(cand, sgn * Y, np.inf); i, j = np.unravel_index(np.argmin(r), r.shape)
            pts.append(c + X[i, j] * n + Y[i, j] * d); prof.append((np.degrees(phi), sgn, X[i, j], sgn * Y[i, j]))
    return np.array(pts), prof

c, n = c0.copy(), n0.copy()
for it in range(5):
    pts, prof = hinges(c, n)
    cen = pts.mean(0); _, _, vt = np.linalg.svd(pts - cen); nn = vt[2] * np.sign(vt[2] @ n0)
    res_mm = (pts - cen) @ nn
    keep = np.abs(res_mm) < 2.5 * res_mm.std() + 1e-9                            # drop outliers, refit
    cen = pts[keep].mean(0); _, _, vt = np.linalg.svd(pts[keep] - cen); nn = vt[2] * np.sign(vt[2] @ n0)
    print(f"pass {it + 1}: centre {cen.round(2)}, normal {nn.round(4)}, change of axis {np.degrees(np.arccos(np.clip(nn @ n, -1, 1))):.1f} deg, "
          f"shift {np.linalg.norm(cen - c):.1f} mm, kept {keep.sum()}/{len(pts)}")
    c, n = cen, nn
P2 = (pts[keep] - c) - np.outer((pts[keep] - c) @ n, n); rad = np.linalg.norm(P2, axis=1)
a, b = frame(n); ang = np.arctan2(P2 @ b, P2 @ a)
out = dict(centre_LPS_mm=c.round(3).tolist(), normal_LA_to_LV=n.round(5).tolist(),
           annulus_radius_mm=dict(mean=round(float(rad.mean()), 2), min=round(float(rad.min()), 2), max=round(float(rad.max()), 2)),
           saddle_height_mm=round(float(np.ptp((pts[keep] - c) @ n)), 2), n_points=int(keep.sum()),
           old_cap=dict(centre=c0.tolist(), normal=n0.round(4).tolist(), angle_to_new_axis_deg=round(float(np.degrees(np.arccos(n0 @ n))), 1),
                        offset_along_axis_mm=round(float((c0 - c) @ n), 2), offset_in_plane_mm=round(float(np.linalg.norm((c0 - c) - ((c0 - c) @ n) * n)), 2)),
           hinge_points=pts[keep].round(2).tolist())
json.dump(out, open(HERE + "/mitral_annulus.json", "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "hinge_points"}, indent=1))

# check figure: radial planes through the new axis, hinge points (yellow), new annulus plane (red), old cap plane (cyan)
fig, axs = plt.subplots(2, 3, figsize=(15, 10))
for k, phi in enumerate(np.radians([0, 30, 60, 90, 120, 150])):
    t, img, d = radial_plane(c, n, phi); ax_ = axs.ravel()[k]
    ax_.imshow(np.clip((img + 160) / 1000, 0, 1).T, cmap="gray", origin="lower", extent=[t[0], t[-1], t[0], t[-1]])
    ax_.axvline(0, color="r", lw=1, label="new annulus plane")
    # old cap plane in this view: points p with (p - c0).n0 = 0 -> x*(n.n0) + y*(d.n0) = (c0 - c).n0
    yy = np.array([-30, 30]); xx = ((c0 - c) @ n0 - yy * (d @ n0)) / (n @ n0)
    ax_.plot(xx, yy, color="c", lw=1, ls="--", label="old mitral cap")
    sel = np.abs(np.degrees(phi) - np.array([p[0] for p in prof])) < 1
    for (ph_, sgn, x_, r_), s_ in zip(prof, sel):
        if s_: ax_.plot(x_, sgn * r_, "o", ms=6, mfc="none", mec="y", mew=1.5)
    ax_.set_xlim(-30, 30); ax_.set_ylim(-30, 30); ax_.set_title(f"plane through the valve axis, {np.degrees(phi):.0f} deg (left = LA, right = LV)", fontsize=8)
    if k == 0: ax_.legend(fontsize=7, loc="lower left")
plt.suptitle("Mitral annulus from the CT: yellow = hinge points (narrowest point of the LA-LV funnel), red = fitted annulus plane", fontsize=10)
plt.tight_layout(); plt.savefig(HERE + "/mitral_annulus_check.png", dpi=90)
