# run7: results (07/11/2026)

**This is the run in the report and in the ParaView package.**

The set-up:
- **Mesh:** `2_mesh/run7_06112026/` (272 293 tetrahedra). It is built from segmentation v2, with the PV extensions along the vein trunks and a 5.3 cm² mitral orifice.
- **Mitral BC:** the course curve, unscaled, plus the valve velocity (`3_simulation/boundary_conditions_4cycles_run7/`).
- **Funnel:** `mv_funnel` moves rigidly with the valve.
- **Time:** dt 0.01 s; 350 steps = 4 beats of 0.875 s. Beat 4 (steps 263–350) is analysed.
- **Files:** case `3_simulation/cases/case_run7_4cycles_07112026.cas/dat.h5`; results `3_simulation/results/run7_4cycles/`. Both are git-ignored.

## Convergence (`convergence/`, from `check_convergence.py`)
- **Every time step converged:** all 350 steps met the residual criteria (continuity 5e-3, velocities 1e-3).
  - Iterations per step: median 27, range 17–55. No step hit the 200-iteration cap.
- **Mass balance:** PV inflow − mitral outflow − ΔV = 0.46 mL over beat 4.
- **Periodicity between beats 3 and 4:** mitral outflow differs by 0.08 %, PV inflow by 3.1 %, near-device ECAP by 0.4 %.
  - In `convergence.png`, the two beats look slightly shifted in time. That is only an effect of plotting: a beat is 87.5 steps, so beat 4 starts half a step later.
- **Files:**
  - `residuals_per_iteration.csv` (all iterations);
  - `convergence_per_step.csv`;
  - `convergence_summary.json`;
  - `convergence.png`.
  - Raw Fluent transcript: `3_simulation/results/run7_4cycles/transcript.trn`. Solver settings: `solver_settings.json` in the same folder.

## Physiology (beat 4)
- **Stroke volume and output:** 79.7 mL; cardiac output 5.47 L/min.
- **PV inflow split** (pv_1 LIPV / pv_2 RSPV / pv_3 RIPV / pv_4 LSPV): 29 / 33 / 10 / 29 %. The RIPV is small (D_eq 8.9 mm).
- **LA volume:** 156.9–168.3 mL.
- **Maximum velocity:** 1.08 m/s at t = 3.06 s (E wave), in the mitral orifice.
- **Small outflow in systole:** about 6 mL/s leaves through the MV in systole. This comes from the course curve itself, which is about −0.011 m/s in that phase, applied unscaled on 5.3 cm². It is not a set-up error.

## Wall metrics (`report_numbers.json`, `figures/`)
Median ECAP by distance from the device:

| distance (mm) | median ECAP (1/Pa) |
|---|---|
| 0–5 | 0.45 |
| 5–10 | 0.17 |
| 10–20 | 0.16 |
| 20–40 | 0.24 |
| > 40 | 0.30 |

- **Device region (0–5 mm):** lowest TAWSS (median 0.54 Pa) and highest OSI (0.21). 13 % of its area has ECAP > 1.
- **Other patches:** the single highest ECAP values are in separate patches on the roof and lower wall, far from the device. This differs from run6, and the report says so.

## Commands
Run from the project folder; `R` = absolute project path. PyFluent sets Fluent's working directory to `logs/fluent`, so pass absolute paths.

```
python 3_simulation/run_cycle.py 350 $R/3_simulation/results/run7_4cycles $R/3_simulation/cases/case_run7_4cycles_07112026.cas.h5 $R/3_simulation/cases/case_run7_setup_06112026.cas.h5 $R/3_simulation/boundary_conditions_4cycles_run7
python 4_postprocessing/check_convergence.py 3_simulation/results/run7_4cycles 4_postprocessing/run7/convergence
MODEL_TRANSFORM=$R/2_mesh/run7_06112026/transform_LPS_to_model.json python 4_postprocessing/analyze_cycle.py $R/3_simulation/results/run7_4cycles $R/4_postprocessing/run7 175 88 2
cd 4_postprocessing; python make_paraview_inputs.py; python make_wall_vtp.py run7; python report_quant.py run7 $R/4_postprocessing/run7/figures
PV_RUN=run7 PV_RESULTS=run7_4cycles PV_OUT=$R/4_postprocessing/run7/figures PV_Q=500,250,700 PV_TRANSFORM=2_mesh/run7_06112026/transform_LPS_to_model.json pvbatch --force-offscreen-rendering 4_postprocessing/pv_figures.py flow|vortex|wall|unet|anatomy
python 4_postprocessing/ct_wire_figure.py 5_report/figures_run7
python 4_postprocessing/make_paraview_package.py
```

## Fixed on 07/11/2026
- **`analyze_cycle.py`:** it now picks the wall block by name (`la_wall`). run7 exports more surfaces, so block 1 was `pv_2`.
- **`make_paraview_package.py`:** it no longer skips files that already exist, which had left run6 steps in the package.
