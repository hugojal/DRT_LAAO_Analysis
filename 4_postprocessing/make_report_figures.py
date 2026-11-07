"""Report-sized figures (fonts match the 10 pt text, legends outside the data), 07/11/2026.
Default output: fig_timecourse.pdf (+ trims the ParaView PNGs copied into the folder). REPORT_EXTRA=1 also writes the earlier
panels below (CT rays/profile, section plots). The thrombus panels are made by thrombus_check/thrombus_report_figure.py.
  fig_ct_axis.pdf      plain CT on a plane through the device axis: blood reaches the device face; dark spots beside the hub
  fig_ct_rays.pdf      mean HU in the 3 mm of blood in front of the device, seen from the atrium
  fig_ct_profile.pdf   HU along the device axis vs the blood level and the thrombus-like level
  fig_sections.pdf     slow blood and two-way flow on sections in front of the device over the heartbeat (run)
Inputs: 4_postprocessing/device_ct/device_ct_arrays.npz (device_ct_hu.py) and 4_postprocessing/<run>/device_sections/*.csv
(device_sections.py). usage: python make_report_figures.py <run> <out_dir>"""
import os, sys, csv
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = sys.argv[1] if len(sys.argv) > 1 else "run8"; OUT = sys.argv[2] if len(sys.argv) > 2 else os.path.join(ROOT, "5_report", f"figures_{RUN}")
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"text.usetex": True, "font.family": "serif", "font.size": 8, "axes.linewidth": 0.6, "axes.spines.top": False,
                     "axes.spines.right": False, "xtick.major.width": 0.6, "ytick.major.width": 0.6, "legend.fontsize": 7.5})
save = lambda fig, n: (fig.savefig(os.path.join(OUT, n), bbox_inches="tight", pad_inches=0.02), plt.close(fig), print("saved", n))

EXTRA = os.environ.get("REPORT_EXTRA") == "1"      # earlier report panels (HU rays, section plots); off since 07/11/2026 evening
if EXTRA:
    Z = np.load(os.path.join(ROOT, "4_postprocessing", "device_ct", "device_ct_arrays.npz")); B = float(Z["blood"]); TH = 0.33 * B
    # (a) plain CT through the device axis
    pa = Z["plane_mm"]; ext = [pa[0], pa[-1], pa[0], pa[-1]]
    fig, ax = plt.subplots(figsize=(1.6, 1.6))
    ax.imshow(Z["ct_plane"], cmap="gray", vmin=-150, vmax=650, extent=ext)
    ax.axvline(0, color="tab:orange", lw=0.6, ls="--"); ax.axvline(-3, color="tab:orange", lw=0.6, ls="--")
    ax.text(-17, 16, "LA blood", color="w", fontsize=7.5, va="top"); ax.text(4, 16, "device", color="w", fontsize=7.5, va="top")
    ax.annotate("", xy=(-0.8, -3.2), xytext=(-9, -12), arrowprops=dict(arrowstyle="->", color="tab:cyan", lw=0.8))
    ax.text(-19, -13, "dark spots\nbeside the hub", color="tab:cyan", fontsize=7, va="top")
    ax.plot([8, 18], [-18, -18], color="w", lw=1.5); ax.text(13, -16.5, "10 mm", color="w", fontsize=7, ha="center")
    ax.set_xticks([]); ax.set_yticks([]); [sp.set_visible(False) for sp in ax.spines.values()]
    save(fig, "fig_ct_axis.pdf")

    # (b) HU just in front of the device, seen from the atrium
    g = Z["grid_mm"]; R = Z["ray_mean"]
    fig, ax = plt.subplots(figsize=(2.0, 1.6))
    im = ax.imshow(R, cmap="gray", vmin=0, vmax=600, origin="lower", extent=[g[0], g[-1], g[0], g[-1]])
    ax.contour(g, g, np.nan_to_num(R, nan=1e4) < TH, [0.5], colors="tab:cyan", linewidths=0.7)
    ax.set_xlim(-15, 15); ax.set_ylim(-9, 15); ax.set_xlabel("mm"); ax.set_ylabel("mm", labelpad=1)
    cb = fig.colorbar(im, ax=ax, fraction=0.05, pad=0.03); cb.set_label("HU, 3 mm in front", labelpad=2); cb.outline.set_linewidth(0.5)
    save(fig, "fig_ct_rays.pdf")

    # (c) profile along the device axis
    fig, ax = plt.subplots(figsize=(2.55, 1.35))
    s, p = Z["prof_s"], Z["prof"]
    ax.axvspan(-3, 0, color="tab:orange", alpha=0.18, lw=0)
    ax.plot(s, p, color="k", lw=1.0, label="CT on the device axis")
    ax.axhline(B, color="tab:red", ls="--", lw=0.8, label=f"LA blood ({B:.0f} HU)")
    ax.axhline(TH, color="tab:blue", ls=":", lw=1.0, label=r"thrombus-like ($0.33\times$ blood)")
    ax.set_xlim(-15, 25); ax.set_ylim(0, 1400); ax.set_xlabel(r"distance from the device face (mm)"); ax.set_ylabel("HU", labelpad=1)
    ax.text(-14, 1300, r"$\leftarrow$ atrium", fontsize=7, va="top"); ax.text(24, 1300, r"device, appendage $\rightarrow$", fontsize=7, va="top", ha="right")
    ax.legend(loc="upper center", bbox_to_anchor=(0.45, -0.32), ncol=2, frameon=False, handlelength=1.6, columnspacing=1.0)
    save(fig, "fig_ct_profile.pdf")

    # (d) sections in front of the device over the heartbeat
    D = os.path.join(ROOT, "4_postprocessing", RUN, "device_sections")
    if os.path.exists(os.path.join(D, "sections.csv")):
        rows = list(csv.DictReader(open(os.path.join(D, "sections.csv")))); T0, TE = 2.625, 3.06
        def ser(d, k):
            Rr = [r for r in rows if int(r["d_mm"]) == d]; return np.array([float(r["t"]) - T0 for r in Rr]), np.array([float(r[k]) for r in Rr])
        cols = {2: "#3b0f70", 8: "#21918c", 16: "#c8b100"}
        fig, axs = plt.subplots(2, 1, figsize=(3.3, 2.1), sharex=True, gridspec_kw=dict(hspace=0.32))
        for d, c in cols.items():
            t, y = ser(d, "frac_stag"); axs[0].plot(t, 100 * y, color=c, lw=1.0, label=f"{d} mm")
            t, a = ser(d, "frac_towards"); _, b = ser(d, "frac_away"); axs[1].plot(t, 100 * np.minimum(a, b), color=c, lw=1.0)
        axs[0].set_ylabel(r"\%", labelpad=2); axs[0].set_ylim(0, 100)
        axs[1].set_ylabel(r"\%", labelpad=2); axs[1].set_ylim(0, 60)
        axs[0].set_title(r"(a) slow blood on the section", loc="left", fontsize=7.5, pad=2)
        axs[1].set_title(r"(b) two-way flow (recirculation)", loc="left", fontsize=7.5, pad=2)
        axs[1].set_xlabel("time in the heartbeat (s)"); axs[1].set_xlim(0, 0.875)
        for a_ in axs: a_.axvline(TE - T0, color="0.5", ls=":", lw=0.8); a_.axvline(2.90 - T0, color="0.5", ls="--", lw=0.6)
        axs[0].legend(title="distance from the device", loc="lower center", bbox_to_anchor=(0.5, 1.12), ncol=3, frameon=False, title_fontsize=7.5, handlelength=1.6)
        save(fig, "fig_sections.pdf")

# (e) time course near the device vs the whole atrium (near_device_timecourse.py): mean speed and share of slow blood
TC = os.path.join(ROOT, "4_postprocessing", RUN, "near_device_timecourse.csv")
if os.path.exists(TC):
    r_ = list(csv.DictReader(open(TC))); A_ = {k: np.array([float(x[k]) for x in r_]) for k in r_[0]}; t_ = A_["t_in_beat"]
    fig, axs = plt.subplots(2, 1, figsize=(3.3, 2.0), sharex=True, gridspec_kw=dict(hspace=0.32))
    for lab, c, nm in (("all", "k", "whole atrium"), ("10mm", "tab:orange", "within 10 mm"), ("5mm", "tab:red", "within 5 mm of the device")):
        axs[0].plot(t_, 100 * A_["vmean_" + lab], color=c, lw=1.0, label=nm); axs[1].plot(t_, 100 * A_["stag0.05_" + lab], color=c, lw=1.0)
    axs[0].set_ylabel("cm/s", labelpad=2); axs[1].set_ylabel(r"\%", labelpad=2); axs[1].set_ylim(0, 70)
    axs[0].set_title(r"(a) mean blood speed", loc="left", fontsize=7.5, pad=2); axs[1].set_title(r"(b) slow blood, $|v|<5$ cm/s", loc="left", fontsize=7.5, pad=2)
    axs[1].set_xlabel("time in the heartbeat (s)"); axs[1].set_xlim(0, 0.875)
    for a_ in axs:
        for tt, ls in ((2.90, "--"), (3.06, ":"), (3.40, "-.")): a_.axvline(tt - 2.625, color="0.55", ls=ls, lw=0.6)
    axs[0].legend(loc="lower center", bbox_to_anchor=(0.5, 1.1), ncol=3, frameon=False, handlelength=1.4, columnspacing=0.8, fontsize=7)
    save(fig, "fig_timecourse.pdf")

# ParaView images copied into the report folder: trim the white margins (keeps the colour bar)
from PIL import Image, ImageChops
for f in sorted(os.listdir(OUT)):
    if f.endswith(".png") and (f.startswith(("streamlines_", "longaxis_", "section_", "pv_wall_", "pv_anatomy", "pv_streamlines_", "pv_qcriterion_", "pv_unet_", "pv_manual_"))):
        im = Image.open(os.path.join(OUT, f)).convert("RGB"); bb = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).getbbox()
        if bb and bb != (0, 0) + im.size:
            pad = 6; im.crop((max(bb[0] - pad, 0), max(bb[1] - pad, 0), min(bb[2] + pad, im.width), min(bb[3] + pad, im.height))).save(os.path.join(OUT, f)); print("trimmed", f)
