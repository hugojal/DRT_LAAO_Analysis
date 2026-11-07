"""Is there a thrombus on the device? CT attenuation (HU) on the atrial face of the occluder, 07/11/2026.
On contrast CT a device-related thrombus is a hypoattenuating thickening (HAT): a layer on the atrial face of the device
that does not take up contrast and is darker than the contrast-filled blood (Agudelo et al. 2021: enhancement defect on
the atrial surface, > 3 mm = high grade / definite DRT). Thrombus vs blood is judged relative to the blood
(Li et al. 2022: appendage/aorta HU ratio 0.33 separates thrombus from slow blood).
Measured here, on the CT grid (no segmentation of the blood is used near the device, because thresholding would
have excluded a dark layer):
  - LA blood pool: LA segmentation (v2) voxels more than 15 mm from the device;
  - rays from the blood to the device (the main test): rays parallel to the device axis, 0.5 mm apart, that start in
    the LA blood and reach the device mask within 4 mm of leaving it (so rays through the atrial wall or fat are not
    used). For each ray: mean HU over the last 3 mm before the device, the thickness of the dark (< 0.33 x blood)
    segment directly on the device, and its minimum HU (clot is soft tissue, > 0 HU; values < 0 HU are metal artefact);
  - a simple layer (voxels 0-3 mm in front of the device within the disc radius - 3 mm), kept for comparison: it also
    catches fat/lung outside the thin atrial wall where the disc is tilted, so it overstates the dark fraction;
  - profile along the device axis: mean HU over a disc of 5 mm radius, every 0.5 mm, from the atrium through the
    device into the appendage;
  - appendage behind the device (sealed if < 100 HU, Agudelo et al. 2021).
Writes 4_postprocessing/device_ct/{device_ct_hu.json, hu_profile, hu_layer_histogram, hu_rays_map (.png/.pdf)}.
The CT stays local (patient data, git-ignored); only these numbers and plots are written.
usage: python device_ct_hu.py"""
import os, json
import numpy as np, nrrd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy import ndimage as nd
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); S = os.path.join(ROOT, "1_segmentation")
OUT = os.path.join(ROOT, "4_postprocessing", "device_ct")                    # independent of the simulation run; os.makedirs(OUT, exist_ok=True)
ct, h = nrrd.read(os.path.join(S, "5 DS_Coronaires  0.75  B26f  BestDiast 78 %.nrrd")); ct = ct.astype(np.float32)
la, _ = nrrd.read(os.path.join(S, "la_v2_06112026", "Case3_LA_segmentation_HugoJal_06112026.seg.nrrd")); la = la > 0
dv, _ = nrrd.read(os.path.join(S, "device", "manual", "Device_manual.seg.nrrd")); dv = (dv[-3:] if dv.ndim == 4 else dv) > 0
SP = np.diag(h["space directions"]).astype(float)
C = np.array([114.181, 156.072, 98.509]); N = np.array([0.57050955, -0.45992626, 0.68043125]); N /= np.linalg.norm(N)   # device disc centre/normal (index*spacing mm), N into the appendage, as in ct_wire_figure.py

# box around the device to keep it light
lo = np.maximum(((C - 40) / SP).astype(int), 0); hi = np.minimum(((C + 40) / SP).astype(int), np.array(ct.shape))
sl = tuple(slice(a, b) for a, b in zip(lo, hi))
X = np.stack(np.meshgrid(*[np.arange(a, b) * s for a, b, s in zip(lo, hi, SP)], indexing="ij"), -1)
D = X - C; s_ax = D @ N; rho = np.linalg.norm(D - s_ax[..., None] * N, axis=-1)
ctb, dvb, lab = ct[sl], dv[sl], la[sl]
d_dev = nd.distance_transform_edt(~dvb, sampling=SP)                      # mm to the device mask
near_axis = dvb & (rho < 5); s_face = float(s_ax[near_axis].min())          # proximal (atrial) face of the device on the axis
R_disc = float(np.percentile(rho[dvb & (s_ax < s_face + 3)], 98))           # disc radius (proximal part)
layer = (~dvb) & (d_dev <= 3.0) & (s_ax < s_face + 1.0) & (rho < R_disc - 3.0)
blood_all = la & (nd.distance_transform_edt(~dv, sampling=SP) > 15)
blood = ct[blood_all]
B = float(np.median(blood))
L = ctb[layer]
behind = (~dvb) & (s_ax > float(s_ax[dvb & (rho < 5)].max()) + 1) & (s_ax < float(s_ax[dvb & (rho < 5)].max()) + 10) & (rho < 6)
prof_s = np.arange(-20, 30.01, 0.5); prof = []
for s0 in prof_s:
    m = (np.abs(s_ax - (s_face + s0)) < 0.35) & (rho < 5)
    prof.append(float(np.mean(ctb[m])) if m.any() else np.nan)
prof = np.array(prof)
res = dict(
    la_blood_HU=dict(median=B, p25=float(np.percentile(blood, 25)), p75=float(np.percentile(blood, 75)), n_voxels=int(blood.size)),
    atrial_face_layer_0_3mm_HU=dict(median=float(np.median(L)), p5=float(np.percentile(L, 5)), p25=float(np.percentile(L, 25)), p75=float(np.percentile(L, 75)),
                                    n_voxels=int(L.size), ratio_median_to_blood=float(np.median(L) / B),
                                    fraction_below_0p33_blood=float((L < 0.33 * B).mean()), fraction_below_150HU=float((L < 150).mean())),
    appendage_behind_device_HU=dict(median=float(np.median(ctb[behind])), n_voxels=int(behind.sum()), sealed_if_below=100),
    device=dict(disc_radius_mm=R_disc, proximal_face_offset_mm=s_face),
    references=dict(HAT="Agudelo et al. 2021 EuroIntervention 17:e944 (enhancement defect on atrial face; >3 mm high grade; LAA <100 HU = sealed)",
                    ratio="Li et al. 2022 Front Cardiovasc Med 9:809688 (LAA/AA HU ratio 0.33: thrombus vs stasis)"))
# rays from the LA blood to the device face
from scipy.ndimage import map_coordinates
e1 = np.cross(N, [0, 0, 1.0]); e1 /= np.linalg.norm(e1); e2 = np.cross(N, e1)
gg = np.arange(-16, 16.01, 0.5); GA, GB = np.meshgrid(gg, gg); ss = np.arange(-20, 6.01, 0.25)
Pr = C + ss[None, None, :, None] * N + GA[..., None, None] * e1 + GB[..., None, None] * e2; ix = (Pr / SP).reshape(-1, 3).T
Hr = map_coordinates(ct, ix, order=1, mode="nearest").reshape(Pr.shape[:3])
Dr = map_coordinates(dv.astype(np.float32), ix, order=0).reshape(Pr.shape[:3]); Lr = map_coordinates(la.astype(np.float32), ix, order=0).reshape(Pr.shape[:3])
TH = 0.33 * B; ray_mean = np.full(GA.shape, np.nan); dark_th, dark_min, dark_rho = [], [], []
for i in range(GA.shape[0]):
    for j in range(GA.shape[1]):
        hit = np.where(Dr[i, j] > 0)[0]
        if not len(hit): continue
        k = hit[0]; inb = np.where(Lr[i, j, :k] > 0)[0]
        if not len(inb) or (k - inb[-1]) * 0.25 > 4 or ss[k] > 3: continue
        seg = Hr[i, j, max(k - 12, 0):k]; ray_mean[i, j] = seg.mean()
        if seg.mean() < TH:
            d = 0
            for x in Hr[i, j, :k][::-1]:
                if x < TH: d += 1
                else: break
            dark_th.append(d * 0.25); dark_min.append(float(seg.min())); dark_rho.append(float(np.hypot(GA[i, j], GB[i, j])))
rv = ray_mean[~np.isnan(ray_mean)]; dark_th = np.array(dark_th)
hub = float(Hr[np.hypot(GA, GB) < 2].max())
res["rays_blood_to_device"] = dict(n_rays=int(rv.size), mean_HU_last_3mm=dict(median=float(np.median(rv)), p25=float(np.percentile(rv, 25)), p75=float(np.percentile(rv, 75))),
    ratio_median_to_blood=float(np.median(rv) / B), fraction_dark_rays=float((rv < TH).mean()),
    dark_rays=dict(n=int(len(dark_th)), thickness_mm_median=float(np.median(dark_th)), thickness_mm_p90=float(np.percentile(dark_th, 90)), thickness_mm_max=float(dark_th.max()),
                   min_HU_median=float(np.median(dark_min)), fraction_reaching_below_0HU=float(np.mean(np.array(dark_min) < 0)), distance_from_axis_mm_median=float(np.median(dark_rho))),
    hub_max_HU=hub)
fig, ax = plt.subplots(figsize=(4.6, 3.9))
im = ax.imshow(ray_mean, cmap="gray", vmin=0, vmax=600, origin="lower", extent=[gg[0], gg[-1], gg[0], gg[-1]])
ax.contour(gg, gg, np.nan_to_num(ray_mean, nan=1e4) < TH, [0.5], colors="tab:cyan", linewidths=1.0)
ax.plot(0, 0, "+", color="tab:orange", ms=10, mew=2)
ax.set_xlabel("mm"); ax.set_ylabel("mm"); ax.set_aspect("equal")
cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.04); cb.set_label("mean HU in the 3 mm of blood\njust in front of the device")
fig.tight_layout()
for e in ("png", "pdf"): fig.savefig(os.path.join(OUT, f"hu_rays_map.{e}"), dpi=200, bbox_inches="tight")
plt.close(fig)
json.dump(res, open(os.path.join(OUT, "device_ct_hu.json"), "w"), indent=1)
# plain CT on the plane through the device axis that also cuts the dark spots beside the hub (spanned by N and e1)
pa = np.arange(-20, 20.001, 0.1); PA, PB = np.meshgrid(pa, pa[::-1])                 # PA along N (atrium -> appendage), PB along e1
Pp = C + (s_face + PA)[..., None] * N + PB[..., None] * e1
ct_plane = map_coordinates(ct, (Pp / SP).reshape(-1, 3).T, order=1, mode="nearest").reshape(PA.shape)
dv_plane = map_coordinates(dv.astype(np.float32), (Pp / SP).reshape(-1, 3).T, order=0).reshape(PA.shape)
np.savez(os.path.join(OUT, "device_ct_arrays.npz"), ray_mean=ray_mean, grid_mm=gg, prof_s=prof_s, prof=prof, blood=B, layer=L, ct_plane=ct_plane, dv_plane=dv_plane, plane_mm=pa)   # for make_report_figures.py
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
# profile along the device axis
fig, ax = plt.subplots(figsize=(6.6, 3.2))
ax.axvspan(-3, 0, color="tab:orange", alpha=0.15, lw=0)
ax.plot(prof_s, prof, color="k", lw=1.6, label="CT along the device axis\n(mean over 5 mm radius)")
ax.axhline(B, color="tab:red", ls="--", lw=1.2, label=f"LA blood (median {B:.0f} HU)")
ax.axhline(0.33 * B, color="tab:blue", ls=":", lw=1.4, label="thrombus-like level\n(0.33 x blood)")
ax.axvline(0, color="0.4", lw=0.8)
ax.set_xlabel("distance from the atrial face of the device (mm)\n← atrium      device / appendage →"); ax.set_ylabel("CT attenuation (HU)")
ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False, fontsize=9)
ax.set_ylim(0, max(np.nanmax(prof), B) * 1.1); ax.set_xlim(prof_s[0], prof_s[-1])
fig.tight_layout()
for e in ("png", "pdf"): fig.savefig(os.path.join(OUT, f"hu_profile.{e}"), dpi=200, bbox_inches="tight")
plt.close(fig)
# histogram: layer vs blood
fig, ax = plt.subplots(figsize=(6.0, 3.0))
bins = np.arange(-100, 1200, 20)
ax.hist(blood, bins=bins, density=True, color="tab:red", alpha=0.5, label="LA blood (> 15 mm from device)")
ax.hist(L, bins=bins, density=True, color="tab:orange", alpha=0.7, label="0–3 mm layer on the\natrial face of the device")
ax.axvline(0.33 * B, color="tab:blue", ls=":", lw=1.4, label="thrombus-like level (0.33 x blood)")
ax.set_xlabel("CT attenuation (HU)"); ax.set_ylabel("share of voxels (density)"); ax.set_yticks([])
ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False, fontsize=9)
fig.tight_layout()
for e in ("png", "pdf"): fig.savefig(os.path.join(OUT, f"hu_layer_histogram.{e}"), dpi=200, bbox_inches="tight")
plt.close(fig)
print(json.dumps(res, indent=1))
