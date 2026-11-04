"""Quantitative analysis for the report (analysis cycle of a run): distance bands, low-shear exposure, time course. Writes figures + a VTP for ParaView + a numbers file.
usage: python report_quant.py [run] [figure_dir]   (default: run5, 5_report/figures; e.g. run6 4_postprocessing/run6/figures)"""
import os, sys, numpy as np, json, matplotlib, pyvista as pv
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
plt.rcParams.update({"text.usetex": True, "font.family": "serif", "font.size": 8.5, "axes.linewidth": 0.6})
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/"); RUN = sys.argv[1] if len(sys.argv) > 1 else "run5"; FIG = (sys.argv[2] if len(sys.argv) > 2 else ROOT + "/5_report/figures").rstrip("/") + "/"   # ROOT = project folder (DRT_LAAO_Case3)
Z = np.load(ROOT + f"/4_postprocessing/{RUN}/results.npz"); nc = int(Z["nc"]); A, Bc = 0, 1
ref, tri = Z["ref_pts"], Z["tri"]
dist = cKDTree(Z["dev"] / 1000.0).query(ref)[0] * 1000                     # mm from each wall node to the device segmentation
P = ref[tri]; ta = 0.5 * np.linalg.norm(np.cross(P[:, 1] - P[:, 0], P[:, 2] - P[:, 0]), axis=1)
area = np.zeros(len(ref)); [np.add.at(area, tri[:, k], ta / 3) for k in range(3)]
mag = Z["mag_steps"][Bc * nc:(Bc + 1) * nc]                                 # |tau| per step, analysis cycle  (nc x nodes)
tw, osi, ec, rrt, wv = (Z[f"c{Bc}_{q}"] for q in ("tawss", "osi", "ecap", "rrt", "wallvort"))
LOW = 0.1                                                                     # Pa: 'low shear' level for the exposure time
lowfrac = (mag < LOW).mean(0)
bands = [(0, 5), (5, 10), (10, 20), (20, 40), (40, 1e9)]; lab = ["0--5", "5--10", "10--20", "20--40", "$>$40"]
def wq(x, w, q): o = np.argsort(x); cw = np.cumsum(w[o]) / w.sum(); return x[o][np.searchsorted(cw, q)]
out = {"bands": []}
for (a, b), L in zip(bands, lab):
    m = (dist >= a) & (dist < b); w = area[m]
    row = dict(band=L, area_cm2=float(w.sum() * 1e4), tawss_med=float(wq(tw[m], w, .5)), tawss_iqr=[float(wq(tw[m], w, .25)), float(wq(tw[m], w, .75))],
               osi_med=float(wq(osi[m], w, .5)), ecap_med=float(wq(ec[m], w, .5)), ecap_iqr=[float(wq(ec[m], w, .25)), float(wq(ec[m], w, .75))], rrt_med=float(wq(rrt[m], w, .5)),
               frac_ecap_gt1=float((w * (ec[m] > 1)).sum() / w.sum()), frac_ecap_gt2=float((w * (ec[m] > 2)).sum() / w.sum()), frac_tawss_lt02=float((w * (tw[m] < 0.2)).sum() / w.sum()),
               lowshear_time=float((w * lowfrac[m]).sum() / w.sum()), wallvort=float((w * wv[m]).sum() / w.sum()))
    out["bands"].append(row)
near, rest = dist < 10, dist >= 20
tt = (np.arange(nc) + 1) * 0.01
ts_near = (mag[:, near] * area[near]).sum(1) / area[near].sum(); ts_rest = (mag[:, rest] * area[rest]).sum(1) / area[rest].sum()
out["time"] = dict(peak_near=float(ts_near.max()), peak_rest=float(ts_rest.max()), t_peak=float(tt[ts_rest.argmax()]),
                   frac_time_near_below_low=float((ts_near < LOW).mean()), frac_time_rest_below_low=float((ts_rest < LOW).mean()))
# whole-wall share of high-ECAP area that lies near the device
hi = ec > 2; out["share_of_ecap_gt2_area_within_20mm"] = float(area[hi & (dist < 20)].sum() / area[hi].sum())
out["wall_area_within_20mm_share"] = float(area[dist < 20].sum() / area.sum())
# periodicity per band
out["periodicity_ecap_rel_change_near"] = float(Z[f"c{Bc}_ecap"][near].mean() / Z[f"c{A}_ecap"][near].mean() - 1)
json.dump(out, open(ROOT + f"/4_postprocessing/{RUN}/report_numbers.json", "w"), indent=1); print(json.dumps(out, indent=1))
# VTP with the extra arrays (for ParaView)
VTP = ROOT + f"/4_postprocessing/paraview/{RUN}_wall_metrics.vtp"; surf = pv.read(VTP); surf.point_data["LowShearTimeFraction"] = lowfrac; surf.point_data["dist_to_device_mm"] = dist; surf.save(VTP)
# ---- Figure: metrics by distance band (box plots, area-weighted quartiles drawn as boxes)
fig, axs = plt.subplots(1, 3, figsize=(3.45, 1.5))
for ax, (arr, yl, logy) in zip(axs, ((tw, "TAWSS (Pa)", True), (osi, "OSI", False), (ec, r"ECAP (Pa$^{-1}$)", True))):
    for i, (a, b) in enumerate(bands):
        m = (dist >= a) & (dist < b); w = area[m]; q1, q2, q3 = (wq(arr[m], w, q) for q in (.25, .5, .75)); p5, p95 = wq(arr[m], w, .05), wq(arr[m], w, .95)
        col = "#b2182b" if b <= 10 else ("#ef8a62" if b <= 20 else "#4d4d4d")
        ax.add_patch(plt.Rectangle((i - .32, q1), .64, q3 - q1, fc=col, ec="k", lw=.4, alpha=.8)); ax.plot([i - .32, i + .32], [q2, q2], "k", lw=.9); ax.plot([i, i], [p5, q1], "k", lw=.4); ax.plot([i, i], [q3, p95], "k", lw=.4)
    ax.set_xticks(range(5)); ax.set_xticklabels(lab, rotation=55, fontsize=6.5); ax.set_xlim(-.6, 4.6); ax.set_ylabel(yl, fontsize=7.5, labelpad=1); ax.tick_params(labelsize=6.5, length=2)
    if logy: ax.set_yscale("log")
    ax.grid(alpha=.25, lw=.4)
axs[1].set_xlabel("distance from the device (mm)", fontsize=7.5)
fig.tight_layout(pad=0.25, w_pad=0.6); fig.savefig(FIG + "fig_bands.pdf"); plt.close(fig)
# ---- Figure: time course in the last heartbeat
fig, axs = plt.subplots(1, 2, figsize=(3.45, 1.5))
ax = axs[0]; ax.plot(tt, ts_rest, "k", lw=1, label=r"$>$20 mm"); ax.plot(tt, ts_near, color="#b2182b", lw=1.1, label=r"$<$10 mm"); ax.axhline(LOW, color="gray", lw=.6, ls="--")
ax.set_yscale("log"); ax.set_xlabel("time in heartbeat (s)", fontsize=7.5); ax.set_ylabel(r"mean $|\tau_w|$ (Pa)", fontsize=7.5); ax.legend(fontsize=6.5, frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, handlelength=1.2, columnspacing=0.8); ax.tick_params(labelsize=6.5, length=2); ax.grid(alpha=.25, lw=.4)
sl = slice(Bc * nc, (Bc + 1) * nc); ax = axs[1]
ax.plot(tt, 100 * Z["stag_0.05_all"][sl], "k", lw=1, label="whole LA"); ax.plot(tt, 100 * Z["stag_0.05_roi10"][sl], color="#b2182b", lw=1.1, label=r"$<$10 mm")
ax.set_xlabel("time in heartbeat (s)", fontsize=7.5); ax.set_ylabel(r"blood $|u|<5$ cm/s (\%)", fontsize=7.5); ax.legend(fontsize=6.5, frameon=False, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=2, handlelength=1.2, columnspacing=0.8); ax.tick_params(labelsize=6.5, length=2); ax.grid(alpha=.25, lw=.4)
fig.tight_layout(pad=0.25, w_pad=0.8); fig.savefig(FIG + "fig_time.pdf"); plt.close(fig); print("figures ok")
