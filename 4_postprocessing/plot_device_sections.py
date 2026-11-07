"""Separate plots of the device cross-sections and recirculation check (run7, last beat), 07/11/2026.
Reads 4_postprocessing/run7/device_sections/{sections.csv, near_device_volume.csv} (written by device_sections.py) and writes
one figure per quantity (PNG + PDF) to 4_postprocessing/run7/device_sections/plots/. Legends sit outside the axes.
usage: python plot_device_sections.py"""
import os, csv
import numpy as np, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "4_postprocessing", "run7", "device_sections"); OUT = os.path.join(D, "plots"); os.makedirs(OUT, exist_ok=True)
T0, T_E = 2.625, 3.06                                   # start of the analysed beat; peak of rapid filling (E wave)
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False})
rows = list(csv.DictReader(open(os.path.join(D, "sections.csv")))); vol = list(csv.DictReader(open(os.path.join(D, "near_device_volume.csv"))))
DS = sorted({int(r["d_mm"]) for r in rows}); cols = plt.cm.viridis(np.linspace(0, 0.9, len(DS)))
def series(d, key):
    R = [r for r in rows if int(r["d_mm"]) == d]
    return np.array([float(r["t"]) - T0 for r in R]), np.array([float(r[key]) for r in R])

def fig_lines(key, ylabel, name, transform=lambda y: y, ylim=None):
    fig, ax = plt.subplots(figsize=(6.4, 3.2))
    for d, c in zip(DS, cols):
        t, y = series(d, key) if isinstance(key, str) else key(d)
        ax.plot(t, transform(y), color=c, lw=1.6, label=f"{d} mm")
    finish(ax, ylabel, ylim); ax.legend(title="distance from\ndevice disc", loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False)
    save(fig, name)

def finish(ax, ylabel, ylim=None):
    ax.axvline(T_E - T0, color="0.5", ls=":", lw=1)
    ax.set_xlabel("time in heartbeat (s)   (dotted line: peak of rapid filling)"); ax.set_ylabel(ylabel); ax.set_xlim(0, 0.875)
    if ylim: ax.set_ylim(*ylim)

def save(fig, name):
    fig.tight_layout()
    for ext in ("png", "pdf"): fig.savefig(os.path.join(OUT, f"{name}.{ext}"), dpi=200, bbox_inches="tight")
    plt.close(fig); print("saved", name)

fig_lines("vmean", "mean speed on section (m/s)", "sections_mean_speed")
fig_lines("frac_stag", "area fraction with |v| < 0.05 m/s", "sections_stagnant_fraction", ylim=(0, 1))
def recirc(d):
    t, a = series(d, "frac_towards"); _, b = series(d, "frac_away"); return t, np.minimum(a, b)
fig_lines(recirc, "smaller of the two area fractions\n(towards / away from device)", "sections_recirculation_index", ylim=(0, 0.6))
# towards vs away, one figure per distance pair is too much: show 2 mm and 12 mm
fig, ax = plt.subplots(figsize=(7.8, 3.2))
for d, c in ((2, cols[0]), (12, cols[3])):
    t, a = series(d, "frac_towards"); _, b = series(d, "frac_away")
    ax.plot(t, a, color=c, lw=1.6, label=f"{d} mm: towards device"); ax.plot(t, b, color=c, lw=1.6, ls="--", label=f"{d} mm: back into atrium")
finish(ax, "area fraction of section", (0, 1)); ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False)
save(fig, "sections_towards_away")
fig, ax = plt.subplots(figsize=(6.4, 3.2))
t = np.array([float(v["t"]) - T0 for v in vol])
ax.plot(t, [float(v["frac_stag"]) for v in vol], color="tab:blue", lw=1.6, label="stagnant\n(|v| < 0.05 m/s)")
ax.plot(t, [float(v["frac_vortex"]) for v in vol], color="tab:orange", lw=1.6, label="vortex-dominated\n(Q > 0)")
finish(ax, "fraction of blood volume\nwithin 10 mm of the device", (0, 1)); ax.legend(loc="upper left", bbox_to_anchor=(1.01, 1.0), frameon=False)
save(fig, "near_device_volume")
fig, ax = plt.subplots(figsize=(4.8, 3.0))
A = [np.median(series(d, "area_mm2")[1]) / 100 for d in DS]
ax.plot(DS, A, "o-", color="k"); ax.set_xlabel("distance from device disc (mm)"); ax.set_ylabel("section area within 20 mm\nof the device axis (cm²)")
save(fig, "sections_area")
