"""Run the left-atrium transient in a no-GUI Fluent session (Fluent GUI must be closed: Student licence = 1 session).
usage: python run_cycle.py <n_steps> <out_dir> <out_case.cas.h5> [case_in] [profile_dir]
profile_dir (optional): folder with pressure_inlet.prof, velocity_outlet.prof, motion.prof that REPLACE the profiles stored in the case (e.g. 3_simulation/boundary_conditions_4cycles)
Per step: dual_time_iterate(1 step, <=200 iterations), EnSight Gold export (binary, node-based), mass-flow reports -> flows.csv.
Convergence: Fluent transcript (residuals of every iteration) -> <out_dir>/transcript.trn, residual criteria and methods -> solver_settings.json.
case+data are also written every 25 steps so a crash keeps the last state. Writes <out_dir>/all_steps.encas at the end."""
import ansys.fluent.core as pf, time, sys, os, csv
NSTEPS = int(sys.argv[1]); OUTDIR = sys.argv[2]; SAVE = sys.argv[3]
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/")   # project folder (DRT_LAAO_Case3)
CASE_IN = sys.argv[4] if len(sys.argv) > 4 else ROOT + "/3_simulation/cases/case_dm_v3_16102026.cas.h5"
PROFDIR = sys.argv[5] if len(sys.argv) > 5 else None
DT = 0.01
os.makedirs(OUTDIR, exist_ok=True)
Q = ["pressure", "absolute-pressure", "total-pressure", "velocity-magnitude", "x-velocity", "y-velocity", "z-velocity", "vorticity-mag",
     "q-criterion", "lambda2-criterion", "wall-shear", "x-wall-shear", "y-wall-shear", "z-wall-shear", "strain-rate-mag"]
NAMES = ["Static_Pressure", "Absolute_Pressure", "Total_Pressure", "Velocity_Magnitude", "X_Velocity", "Y_Velocity", "Z_Velocity", "Vorticity_Magnitude",
         "Q_Criterion_Normalized", "Lambda_2_Criterion", "Wall_Shear_Stress", "X_Wall_Shear_Stress", "Y_Wall_Shear_Stress", "Z_Wall_Shear_Stress", "Strain_Rate"]
log = lambda m: print(time.strftime("%H:%M:%S"), m, flush=True)
s = pf.launch_fluent(mode="solver", dimension=3, precision="single", processor_count=4, ui_mode="no_gui", cwd=ROOT + "/logs/fluent", start_transcript=False)
S = s.settings
try: s.transcript.start(file_name=os.path.join(OUTDIR, "transcript.trn"))   # every iteration's residuals -> convergence report
except Exception as e: log(f"transcript not started: {e}")
S.file.read_case(file_name=CASE_IN)
if PROFDIR:
    for pf_name in ("pressure_inlet", "velocity_outlet", "motion"):
        s.scheme.eval('(ti-menu-load-string "/file/read-transient-table \\"%s/%s.prof\\"")' % (PROFDIR, pf_name))
rc = S.solution.run_calculation
try:
    import json as _j
    _j.dump(dict(residuals=S.solution.monitor.residual.get_state(), methods=S.solution.methods.get_state() if hasattr(S.solution, "methods") else None),
            open(os.path.join(OUTDIR, "solver_settings.json"), "w"), indent=1, default=str)
except Exception as e: log(f"settings not saved: {e}")
rc.transient_controls.time_step_size = DT
S.solution.initialization.defaults["pressure"] = 809.4245264      # = pressure_inlet.prof at t = 0 (gauge)
S.solution.initialization.standard_initialize()
rd = S.solution.report_definitions
zones = {"pv_1": ["pv_1"], "pv_2": ["pv_2"], "pv_3": ["pv_3"], "pv_4": ["pv_4"], "mv": ["mitral_valve"]}
names = []
for k, z in zones.items():
    n = "mf_" + k
    rd.flux.create(n); rd.flux[n].report_type = "flux-massflow"; rd.flux[n].boundaries = z; names.append(n)
rd.volume.create("vol_la"); rd.volume["vol_la"].report_type = "volume-zonevol"; rd.volume["vol_la"].cell_zones = ["fluid-1"]; names.append("vol_la")
f = open(os.path.join(OUTDIR, "flows.csv"), "w", newline=""); w = csv.writer(f); w.writerow(["step", "time_s"] + names)
def vals():
    out = {}
    for d in (lambda r: r if isinstance(r, list) else [r])(rd.compute(report_defs=names)): out.update(d if isinstance(d, dict) else {})
    return out
k = 0
try:
    for k in range(1, NSTEPS + 1):
        rc.dual_time_iterate(time_step_count=1, max_iter_per_step=200)
        S.file.export.ensight_gold(file_name=os.path.join(OUTDIR, "step_%03d" % k), quantities=Q, cellzones=["fluid-1"], cell_centered=False, binary_format=True)
        v = vals()
        w.writerow([k, round(DT * k, 4)] + [str(v.get(n)) for n in names]); f.flush()
        if k % 10 == 0 or k == NSTEPS: log(f"step {k}/{NSTEPS} t={DT*k:.2f} s done; {v}")
        if k % 25 == 0 and k < NSTEPS: S.file.write_case_data(file_name=SAVE.replace(".cas.h5", "_partial.cas.h5"))
    S.file.write_case_data(file_name=SAVE)
    with open(os.path.join(OUTDIR, "all_steps.encas"), "w") as c:
        L = ["FORMAT", "type:  ensight gold", "GEOMETRY", "model: 1 step_***.geo", "VARIABLE"]
        L += [f"scalar per node: 1 {n} step_***.scl{i+1}" for i, n in enumerate(NAMES)]
        L += ["vector per node: 1 Velocity step_***.vel", "TIME", "time set: 1", f"number of steps: {NSTEPS}", "filename start number: 1", "filename increment: 1", "time values:"]
        L += [f"{DT*i:.2f}" for i in range(1, NSTEPS + 1)]
        c.write("\n".join(L) + "\n")
    log(f"FINISHED {NSTEPS}/{NSTEPS} saved")
except Exception as e:
    log(f"FAILED at step ~{k}: {type(e).__name__}: {str(e)[:400]}")
    try: S.file.write_case_data(file_name=SAVE.replace(".cas.h5", "_failed.cas.h5"))
    except Exception: pass
f.close()
try: s.exit()
except Exception: pass
