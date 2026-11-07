# run8: results (07/11/2026)

**This is the run in the report and in the ParaView package.**

The set-up is identical to run7 (archived), except for the mesh.
- **Mesh:** `2_mesh/run8_07112026/` has **circular PV cylinders** of 17.7 / 13.5 / 13.0 / 9.0 mm. It has 271 908 tetrahedra and a 5.3 cm² mitral orifice.
- **Mitral BC:** the course curve, unscaled, plus the valve velocity (`3_simulation/boundary_conditions_4cycles_run7/`, the same curves as run7).
- **Funnel:** `mv_funnel` moves rigidly with the valve.
- **Time:** dt 0.01 s; 350 steps = 4 beats of 0.875 s. Beat 4 (steps 263–350) is analysed.
- **Files:** case `3_simulation/cases/case_run8_4cycles_07112026.cas/dat.h5`; results `3_simulation/results/run8_4cycles/`. Both are git-ignored.
- **Set-up script:** `3_simulation/setup_case_run8.py`. Log: `logs/run8.out`.

## Convergence (`convergence/`, from `check_convergence.py`)
- **Every time step converged:** all 350 steps met the residual criteria (continuity 5e-3, velocities 1e-3).
  - Iterations per step: median 28, range 18–50. No step hit the 200-iteration cap.
- **Mass balance:** PV inflow − mitral outflow − ΔV = 0.45 mL over beat 4.
- **Periodicity, beats 3 → 4:**
  - Mitral outflow differs by 0.08 %, PV inflow by 3.1 %.
  - Wall metrics (area-weighted medians): TAWSS changes ≤ 4 %, ECAP 7 % near the device and 12 % elsewhere, OSI 10–18 %.
  - The device region has 1.8× the ECAP of the rest of the wall in beat 3 and 1.7× in beat 4, so the conclusion is the same for both beats.
  - `report_numbers.json` holds `periodicity_ecap_rel_change_near` = 0.27. That compares area-weighted *means*, which a few high values pull, so it overstates the change.
- **Plot:** the beat-3 and beat-4 curves in `convergence.png` look offset by half a step. A beat is 87.5 steps, so beat 4 starts half a step later.

## Physiology (beat 4)
- **Stroke volume and output:** 79.7 mL; cardiac output 5.47 L/min.
- **PV inflow split** (pv_1 LIPV / pv_2 RSPV / pv_3 RIPV / pv_4 LSPV): 27 / 37 / 9 / 27 %. The RIPV is the smallest vein (9 mm).
- **LA volume:** 156.8–168.2 mL.
- **Maximum velocity:** 1.07 m/s at t = 3.06 s (E wave), in the mitral orifice.
- **Small outflow in systole:** about 6 mL/s leaves through the MV in systole. This comes from the course curve, which is about −0.011 m/s in that phase, applied unscaled. It is not a set-up error.

## Wall metrics (`report_numbers.json`, `figures/`)
| distance from the device (mm) | TAWSS median (Pa) | OSI median | ECAP median (1/Pa) | area with ECAP > 1 |
|---|---|---|---|---|
| 0–5 | 0.49 | 0.22 | 0.46 | 16 % |
| 5–10 | 0.76 | 0.10 | 0.15 | 2 % |
| 10–20 | 0.88 | 0.13 | 0.15 | 0 % |
| 20–40 | 0.80 | 0.18 | 0.24 | 1 % |
| > 40 | 0.56 | 0.21 | 0.37 | 11 % |

- **Within 5 mm of the device** compared with the rest of the wall (≥ 10 mm):
  - TAWSS is 0.50 vs 0.72 Pa, about 30 % lower;
  - OSI is 0.22 vs 0.19;
  - ECAP is 0.46 vs 0.27, about 1.7×.
- **Share of high ECAP:** the wall within 10 mm of the device is 10 % of the atrium but holds 38 % of the area with ECAP > 2.
- **Highest single values:** these are in small patches on the roof and the lower wall, about 60 mm away.

## Flow in front of the device (`device_sections/`; see its README)
- **2 mm in front of the device:** 70 % of the section is slower than 0.05 m/s on average over the beat. It never drops below about 50 %, not even at the filling peak.
  - The blood there is still, not recirculating: two-way flow occurs during only 9 % of the beat.
- **5–16 mm:** at least 20 % of the section flows each way during 91–100 % of the beat, so the blood recirculates. This is clearest just after the filling peak.
- **8 and 16 mm:** the slow share falls to about 10 % or less at the filling peak.
- **Within 10 mm of the device** (8.3 mL of blood): on average 26 % is stagnant and 24 % is inside vortex cores (Q > 0).

## Commands (from the project folder; R = absolute path)
```
python 3_simulation/setup_case_run8.py AB
python 3_simulation/run_cycle.py 350 $R/3_simulation/results/run8_4cycles $R/3_simulation/cases/case_run8_4cycles_07112026.cas.h5 $R/3_simulation/cases/case_run8_setup_07112026.cas.h5 $R/3_simulation/boundary_conditions_4cycles_run7
python 4_postprocessing/check_convergence.py 3_simulation/results/run8_4cycles 4_postprocessing/run8/convergence
MODEL_TRANSFORM=$R/2_mesh/run8_07112026/transform_LPS_to_model.json python 4_postprocessing/analyze_cycle.py $R/3_simulation/results/run8_4cycles $R/4_postprocessing/run8 175 88 2
cd 4_postprocessing; python make_paraview_inputs.py run8; python make_wall_vtp.py run8; python report_quant.py run8 $R/4_postprocessing/run8/figures
python device_sections.py run8; python plot_device_sections.py run8
python make_paraview_package.py run8
PV_RUN=run8 pvbatch --force-offscreen-rendering render_device_views.py
PV_RUN=run8 PV_RESULTS=run8_4cycles PV_OUT=$R/4_postprocessing/run8/figures PV_WALL_SHIFT=0.008 PV_TRANSFORM=2_mesh/run8_07112026/transform_LPS_to_model.json pvbatch --force-offscreen-rendering pv_figures.py wall|anatomy
python device_ct_hu.py            (CT, run-independent -> 4_postprocessing/device_ct/)
python make_report_figures.py run8 ../5_report/figures_run8   (also trims the PNGs copied there)
```

To fill the report figure folder:
- copy from `device_sections/views/`: `streamlines_side_filling_t306`, `streamlines_side_systole_t290`, `longaxis_slice_systole_t290`, `section_8mm_systole_t290`;
- copy from `figures/`: `pv_anatomy_wire`, `pv_wall_ecap_dev`, `fig_bands.pdf`;
- run `make_report_figures.py` last.
