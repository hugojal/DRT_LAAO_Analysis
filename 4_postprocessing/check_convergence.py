"""Convergence and periodicity of a run (07/11/2026). Reads <results>/transcript.trn (Fluent transcript: residuals of
every iteration), <results>/solver_settings.json (residual criteria) and <results>/flows.csv. Writes <out>/:
  residuals_per_iteration.csv   time step, iteration, continuity, x/y/z-velocity residuals
  convergence_per_step.csv      time step, flow time, iterations, converged (criteria met before the 200-iteration cap), final residuals
  convergence_summary.json      criteria, steps converged, iterations per step, mass balance and beat-to-beat periodicity
  convergence.png               residual history, iterations per step, LA volume and flows, beat 3 vs beat 4
usage: python check_convergence.py <results_dir> <out_dir> [steps_per_beat=87.5] [dt=0.01]"""
import os, re, sys, json, csv
import numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
RES, OUT = sys.argv[1], sys.argv[2]; SPB = float(sys.argv[3]) if len(sys.argv) > 3 else 87.5; DT = float(sys.argv[4]) if len(sys.argv) > 4 else 0.01
os.makedirs(OUT, exist_ok=True)
row = re.compile(r"^\s*(\d+)\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)\s+\d+:\d+:\d+\s+\d+")
done = re.compile(r"Flow time = ([0-9.eE+-]+)s, time step = (\d+)"); conv = re.compile(r"!\s+\d+ solution is converged")
iters, steps, cur, conv_flag = [], [], [], False
for line in open(os.path.join(RES, "transcript.trn"), errors="ignore"):
    m = row.match(line)
    if m: cur.append([int(m.group(1))] + [float(m.group(i)) for i in range(2, 6)]); continue
    if conv.search(line): conv_flag = True; continue
    m = done.search(line)
    if m:
        k = int(m.group(2)); arr = np.array(cur) if cur else np.zeros((0, 5))
        for r in arr: iters.append([k] + list(r))
        steps.append(dict(step=k, flow_time=round(float(m.group(1)), 4), iterations=len(arr), converged=conv_flag,
                          continuity=arr[-1, 1] if len(arr) else np.nan, x_vel=arr[-1, 2] if len(arr) else np.nan,
                          y_vel=arr[-1, 3] if len(arr) else np.nan, z_vel=arr[-1, 4] if len(arr) else np.nan))
        cur, conv_flag = [], False
with open(os.path.join(OUT, "residuals_per_iteration.csv"), "w", newline="") as f:
    w = csv.writer(f); w.writerow(["time_step", "iteration", "continuity", "x_velocity", "y_velocity", "z_velocity"]); w.writerows(iters)
with open(os.path.join(OUT, "convergence_per_step.csv"), "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(steps[0].keys())); w.writeheader(); w.writerows(steps)
crit = None
try:
    st = json.load(open(os.path.join(RES, "solver_settings.json")))["residuals"]
    crit = {k: v.get("absolute_criteria") for k, v in st.get("equations", {}).items()}
except Exception: pass
# flows: mass balance and periodicity
import ast
_rows = list(csv.DictReader(open(os.path.join(RES, "flows.csv"))))
_val = lambda x: float(ast.literal_eval(x)[0]) if x.strip().startswith("[") else float(x)
F = {k: np.array([_val(r[k]) for r in _rows]) for k in _rows[0]}                      # values are stored as "[value, 'unit']"
t = F["time_s"]; mv = F["mf_mv"]; pvs = F["mf_pv_1"] + F["mf_pv_2"] + F["mf_pv_3"] + F["mf_pv_4"]
vol = F["vol_la"]; rho = 1060.0
def beat(b):
    s = (t > (b - 1) * SPB * DT + 1e-9) & (t <= b * SPB * DT + 1e-9); return s
summ = dict(criteria=crit, n_steps=len(steps), steps_converged=int(sum(s["converged"] for s in steps)),
            iterations_per_step=dict(median=float(np.median([s["iterations"] for s in steps])), max=int(max(s["iterations"] for s in steps)),
                                     min=int(min(s["iterations"] for s in steps))),
            steps_hitting_200_iterations=int(sum(s["iterations"] >= 200 for s in steps)),
            final_residuals_max_over_steps=dict(continuity=float(np.nanmax([s["continuity"] for s in steps])),
                                                velocity=float(np.nanmax([max(s["x_vel"], s["y_vel"], s["z_vel"]) for s in steps]))))
nb = int(round(t[-1] / (SPB * DT)))
beats = []
for b in range(1, nb + 1):
    s = beat(b)
    if s.sum() < 5: continue
    sv = -np.sum(mv[s]) * DT / rho * 1e6; pin = np.sum(pvs[s]) * DT / rho * 1e6
    beats.append(dict(beat=b, mitral_outflow_mL=round(float(sv), 2), pv_inflow_mL=round(float(pin), 2),
                      LA_volume_change_mL=round(float((vol[s][-1] - vol[s][0]) * 1e6), 2), LA_volume_min_max_mL=[round(float(vol[s].min() * 1e6), 1), round(float(vol[s].max() * 1e6), 1)]))
summ["beats"] = beats
if len(beats) >= 2:
    a, b = beats[-2], beats[-1]
    summ["periodicity_last_two_beats_percent"] = dict(mitral_outflow=round(100 * abs(b["mitral_outflow_mL"] - a["mitral_outflow_mL"]) / abs(a["mitral_outflow_mL"]), 2),
                                                      pv_inflow=round(100 * abs(b["pv_inflow_mL"] - a["pv_inflow_mL"]) / abs(a["pv_inflow_mL"]), 2))
    summ["mass_balance_last_beat_mL"] = round(b["pv_inflow_mL"] - b["mitral_outflow_mL"] - b["LA_volume_change_mL"], 2)
json.dump(summ, open(os.path.join(OUT, "convergence_summary.json"), "w"), indent=1, default=float)
# figure
I = np.array(iters); S = np.array([[s["step"], s["iterations"]] for s in steps])
fig, ax = plt.subplots(2, 2, figsize=(13, 8))
gi = np.arange(len(I))
for j, lab in enumerate(["continuity", "x-velocity", "y-velocity", "z-velocity"]): ax[0, 0].semilogy(gi, I[:, 2 + j], lw=0.4, label=lab)
if crit:
    for v_ in set(x for x in crit.values() if x): ax[0, 0].axhline(v_, color="k", ls="--", lw=0.8)
ax[0, 0].set_xlabel("iteration (all time steps)"); ax[0, 0].set_ylabel("scaled residual"); ax[0, 0].legend(fontsize=8); ax[0, 0].set_title("Residuals (dashed: convergence criteria)")
ax[0, 1].bar(S[:, 0], S[:, 1], width=1.0, color=["tab:green" if s["converged"] else "tab:red" for s in steps])
ax[0, 1].set_xlabel("time step"); ax[0, 1].set_ylabel("iterations to converge"); ax[0, 1].set_title(f"{summ['steps_converged']}/{len(steps)} steps converged (red: hit the cap)")
ax[1, 0].plot(t, vol * 1e6, "k"); ax[1, 0].set_xlabel("t (s)"); ax[1, 0].set_ylabel("LA volume (mL)")
a2 = ax[1, 0].twinx(); a2.plot(t, -mv / rho * 1e6, "tab:red", lw=0.8, label="mitral outflow"); a2.plot(t, pvs / rho * 1e6, "tab:blue", lw=0.8, label="PV inflow")
a2.set_ylabel("flow (mL/s)"); a2.legend(fontsize=8, loc="upper right"); ax[1, 0].set_title("LA volume and flows, 4 beats")
for b, col in ((nb - 1, "tab:gray"), (nb, "tab:red")):
    s = beat(b); ax[1, 1].plot(t[s] - (b - 1) * SPB * DT, -mv[s] / rho * 1e6, color=col, label=f"beat {b}")
ax[1, 1].set_xlabel("time in beat (s)"); ax[1, 1].set_ylabel("mitral outflow (mL/s)"); ax[1, 1].legend(); ax[1, 1].set_title("Periodicity: last two beats")
plt.tight_layout(); plt.savefig(os.path.join(OUT, "convergence.png"), dpi=110)
print(json.dumps({k: v for k, v in summ.items() if k != "beats"}, indent=1, default=float))
