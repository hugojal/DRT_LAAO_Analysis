# run9 (mesh 15/11/2026, simulation 15-16/11/2026): the run in the report and in the ParaView package

Replaces run8 (kept in `4_postprocessing/run8/`, not used any more). Same set-up and boundary conditions; only the mesh changed:
`2_mesh/run9_15112026/` (spur next to the RIPV removed, atrium smoothed, PV inlets with a smooth change of diameter ending in circular cylinders, 274 425 tetrahedra). Case `3_simulation/cases/case_run9_4cycles_15112026.cas/dat.h5`, results `3_simulation/results/run9_4cycles/`, set-up script `3_simulation/setup_case_run9.py`, logs `logs/run9_run_15112026.log`, `logs/setup_run9_15112026.log` (the computer slept for ~7.5 h at step 204; the run resumed by itself).

## Convergence (`convergence/`)
- Every step of the last beat met the criteria. One step of beat 2 (131) reached the 200-iteration cap (continuity 0.0066). Steps 346-350 are flagged "False" only because the transcript lacks their "solution is converged" line (file ended); their residuals are below the criteria.
- Mass balance in beat 4: 0.44 mL. Periodicity beats 3 -> 4: mitral outflow 0.08 %, PV inflow 3.2 %; ECAP median within 5 mm of the device 0.51 -> 0.57 (11 %).
- Physiology (beat 4): SV 79.7 mL; PV split LIPV/RSPV/RIPV/LSPV 27/38/6/28 %; v_max 1.11 m/s at 3.06 s; LA volume 157.4-168.7 mL.

## Results that changed against run8 (the report text was revised)
| | run8 | run9 |
|---|---|---|
| wall < 5 mm from the device: TAWSS / OSI / ECAP medians | 0.50 / 0.22 / 0.46 | 0.48 / 0.25 / 0.57 |
| rest of the wall (>= 10 mm) | 0.72 / 0.19 / 0.27 | 0.71 / 0.17 / 0.24 |
| ECAP ratio near / rest | 1.7 | 2.4 |
| share of ECAP > 2 area within 20 mm of the device (wall area 21 %) | 37 % | 73 % |
| mean speed < 5 mm of the device / whole LA (m/s) | 0.081 / 0.122 | 0.083 / 0.122 |
| Q > 0 share, < 5 mm / whole LA | 18 / 33 % | 19 / 33 % |
| retention after one beat (release 2.63 s), independent review, 600 volume-weighted seeds: 0-5 mm of the device / body core / near-wall far | 63 / 40 / 67 % | 67 / 41 / 67 % |
| retention, ParaView, 400 uniform seeds (`pathlines/retention_check_seeds.py`, `retention_check_body.py`): 5 mm layer / 8 mm sphere / body sphere (2.63 s) | 58 / 27 / - % | 56 / 74 / 57 % |
| PV pathlines reaching within 12 mm of the device centre | 6 % | 10 % |

Reading: the speed and vortex findings are unchanged; the OSI near the device is now higher than elsewhere, and ECAP near the device is higher. Retention in front of the device is only slightly above the body blood (and equal to near-wall blood far from the device), and depends on how the blood is counted. The report states 55-65 % vs 40-55 %. The old claim that the blood in front of the device moves least with the valve closed (12 mm vs 15-20 mm) does not hold in run9 (median path length in the first 0.3 s: 28 mm in front of the device, 22 mm body) and was removed.

## Files
`results.npz`, `report_numbers.json`, `figures/` (ParaView and matplotlib), `device_sections/`, `pathlines/`, `near_device_timecourse.csv`, `independent_review_15112026/` (the six scripts of the run8 review re-run on run9; JSON outputs, no new written review). Commands as in `../run8/README.md` with run9 (set `PV_RUN=run9` for `pv_pathlines.py` and `make_pathline_panels.py`; `make_report_figures.py run9 ../5_report/figures_run9`).
