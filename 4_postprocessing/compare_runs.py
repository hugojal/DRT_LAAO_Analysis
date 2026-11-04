"""Physiology check and comparison of two runs (default run5 = old mesh, run6 = mitral cut on the annulus, z = valve axis).
Per heartbeat from flows.csv: mitral stroke volume, cardiac output, peak mitral flow, pulmonary-vein inflow and split, LA
volume change; in the fluid at the E-wave peak and late diastole: max and mean velocity; on the wall: the distance-band
numbers of report_quant.py. Writes 4_postprocessing/compare_<a>_<b>.json.
usage: python compare_runs.py [runA results_dirA runB results_dirB]"""
import os, sys, csv, json
import numpy as np, vtk, pyvista as pv
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/")
A, RA, B, RB = (sys.argv[1:5] if len(sys.argv) > 4 else ["run5", "run5_4cycles", "run6", "run6_mvz_4cycles"])
RHO, DT, T_BEAT, NB = 1060.0, 0.01, 0.875, 4
T_PEAK, T_LATE = 3.06, 3.40

def flows(rdir):
    rows = list(csv.DictReader(open(f"{ROOT}/3_simulation/results/{rdir}/flows.csv")))
    num = lambda s: float(s.strip("[]").split(",")[0])
    t = np.array([float(r["time_s"]) for r in rows]); out = {"t": t}
    for k in rows[0]:
        if k not in ("step", "time_s"): out[k] = np.array([num(r[k]) for r in rows])
    return out

def beat_stats(F):
    res = []
    for b in range(NB):
        m = (F["t"] > b * T_BEAT + 1e-9) & (F["t"] <= (b + 1) * T_BEAT + 1e-9)
        q_mv = -F["mf_mv"][m] / RHO                                   # m3/s, + = out of the LA through the valve
        q_pv = np.array([F[f"mf_pv_{i}"][m] / RHO for i in range(1, 5)])
        sv = float(np.sum(q_mv) * DT * 1e6); pv_in = q_pv.sum(1) * DT * 1e6
        res.append(dict(beat=b + 1, mitral_SV_mL=round(sv, 1), cardiac_output_L_min=round(sv * 60 / T_BEAT / 1000, 2),
                        peak_mitral_flow_mL_s=round(float(q_mv.max()) * 1e6), mitral_backflow_mL=round(float(-np.sum(np.minimum(q_mv, 0)) * DT * 1e6), 1),
                        pv_net_inflow_mL=[round(float(x), 1) for x in pv_in], pv_split_pct=[round(float(100 * x / max(pv_in.sum(), 1e-9)), 1) for x in pv_in],
                        pv_reverse_flow_time_pct=[round(float(100 * (q < 0).mean()), 1) for q in q_pv],
                        LA_volume_mL=dict(min=round(float(F["vol_la"][m].min() * 1e6), 2), max=round(float(F["vol_la"][m].max() * 1e6), 2))))
    return res

def fluid_velocity(rdir, t):
    k = int(round(t / DT)); r = vtk.vtkEnSightGoldBinaryReader(); r.SetCaseFileName(f"{ROOT}/3_simulation/results/{rdir}/step_{k:03d}.encas"); r.Update()
    fl = pv.wrap(r.GetOutput().GetBlock(0)); u = np.asarray(fl["Velocity_Magnitude"]); q = np.asarray(fl["Q_Criterion_Normalized"])
    vol = fl.compute_cell_sizes(length=False, area=False)["Volume"]; uc = fl.point_data_to_cell_data()["Velocity_Magnitude"]
    return dict(t=t, max_m_s=round(float(u.max()), 3), p99_m_s=round(float(np.percentile(u, 99)), 3), mean_m_s=round(float((uc * vol).sum() / vol.sum()), 4),
                q_p99_1_s2=round(float(np.percentile(q, 99)), 1), q_max_1_s2=round(float(q.max()), 1))

out = {}
for run, rdir in ((A, RA), (B, RB)):
    F = flows(rdir); out[run] = dict(beats=beat_stats(F), fluid=[fluid_velocity(rdir, T_PEAK), fluid_velocity(rdir, T_LATE)])
    p = f"{ROOT}/4_postprocessing/{run}/report_numbers.json"
    if os.path.exists(p): out[run]["wall_bands"] = json.load(open(p))["bands"]
out["reference_ranges"] = dict(source="Kawel-Boehm et al. 2020, J Cardiovasc Magn Reson 22:87 (CMR, adults)",
                               LV_SV_mL=dict(men="103 +- 21 (61-145)", women="83 +- 16 (52-114)"),
                               CO_L_min=dict(men="5.6 +- 1.1 (3.4-7.8)", women="4.5 +- 0.9 (2.7-6.3)"))
json.dump(out, open(f"{ROOT}/4_postprocessing/compare_{A}_{B}.json", "w"), indent=1)
for run in (A, B):
    b4 = out[run]["beats"][-1]; f = out[run]["fluid"][0]
    print(f"{run}: last beat SV {b4['mitral_SV_mL']} mL, CO {b4['cardiac_output_L_min']} L/min, peak MV flow {b4['peak_mitral_flow_mL_s']} mL/s, "
          f"MV backflow {b4['mitral_backflow_mL']} mL, PV split {b4['pv_split_pct']} %, LA vol {b4['LA_volume_mL']}; E-peak max |u| {f['max_m_s']} m/s, mean {f['mean_m_s']} m/s")
