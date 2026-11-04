# run6 — new mesh (mitral cut on the CT annulus, z = valve axis), flow-scaled mitral BC, 4 cycles (04/11/2026)

**Inputs**
- Mesh: `2_mesh/mv_aligned_03112026/HugoJal_Case3_mvz_03112026.bdf`. It has 307,927 tetrahedra and a mitral cap of 861 mm².
- Results are in the model frame (m). Use `transform_LPS_to_model.json` to map them back to the CT (LPS).
- Case: `3_simulation/cases/case_mvz_setup_04112026.cas.h5`, made by `3_simulation/setup_case_mvz.py`. It is the run5 set-up with the mesh replaced, so all settings are the same. Remeshing lengths are 0.3 / 4.5 mm.
- Boundary conditions: `3_simulation/boundary_conditions_4cycles_mvz/`.
  - PV pressure and MV motion are the same as run5.
  - MV velocity = course profile × 0.5616 + annulus velocity dz/dt. See `scale_mitral_velocity.py` and `scaling.json`.
- Run: `3_simulation/run_cycle.py`, 350 steps × 0.01 s (4 beats of 0.875 s), log `logs/run6.out`. It took 10:43 → 12:36 with no errors.
- Final case: `3_simulation/cases/case_mvz_run6_4cycles_04112026.cas.h5`. EnSight per step: `3_simulation/results/run6_mvz_4cycles/`.

**Why the mitral BC was scaled.** The course profile applied unchanged on the 861 mm² annulus gives:
- 130 mL/beat;
- 8.9 L/min;
- this is above the CMR normal range: SV 103 ± 21 mL (men) and 83 ± 16 mL (women); CO 5.6 and 4.5 L/min (Kawel-Boehm et al. 2020, J Cardiovasc Magn Reson 22:87, doi:10.1186/s12968-020-00683-3).

The flow is what must be physiological. By continuity, the same flow crosses the wide annulus at a lower velocity than at the leaflet tips. Multiplying the profile by one constant keeps its shape and timing and gives CO 5.0 L/min.

**Post-processing**
```
MODEL_TRANSFORM=<abs>/2_mesh/mv_aligned_03112026/transform_LPS_to_model.json python analyze_cycle.py <abs>/3_simulation/results/run6_mvz_4cycles <abs>/4_postprocessing/run6 175 88 2
python make_wall_vtp.py run6
python report_quant.py run6 <abs>/4_postprocessing/run6/figures
PV_RUN=run6 PV_RESULTS=run6_mvz_4cycles PV_OUT=<abs>/4_postprocessing/run6/figures PV_Q=500,250,700 \
  PV_TRANSFORM=2_mesh/mv_aligned_03112026/transform_LPS_to_model.json pvbatch pv_figures.py flow|vortex|wall
python compare_runs.py          # -> 4_postprocessing/compare_run5_run6.json
```
- Wall metrics use the last 2 beats (steps 175–350). The last beat is the analysis beat; the one before it is the periodicity check.
- Mean mapping offset is 0.03 mm (p95 0.28 mm).

**Physiology check (beat 4; run5 in brackets)**

| quantity | run6 | run5 | reference |
|---|---|---|---|
| mitral stroke volume | 72.9 mL | 46.4 mL | 83–103 mL (52–145) |
| cardiac output | 5.0 L/min | 3.2 L/min | 4.5–5.6 L/min (2.7–7.8) |
| peak mitral flow | 455 mL/s | 296 mL/s | — |
| mitral backflow | 0.4 mL | 0.0 mL | closed valve in systole |
| PV split (pv_1–4) | 20 / 28 / 20 / 31 % | 20 / 29 / 18 / 34 % | — |
| LA volume (min–max) | 172.7–181.2 mL | 167.3–168.5 mL | — |
| max \|u\| at E-peak (t = 3.06 s) | 0.57 m/s | 1.72 m/s | — |
| mean \|u\| at E-peak | 0.21 m/s | 0.15 m/s | — |

- **Periodicity.** The per-beat integrals are periodic:
  - mitral SV is 72.8 and 72.9 mL in beats 3 and 4;
  - each PV's inflow changes by 1.5 mL or less between beats 3 and 4;
  - the ECAP change near the device between beats 3 and 4 is 14 % (run5: 22 %).
- **Instantaneous flows.** The PV flows vary more from beat to beat. The input profile itself is not sample-periodic (87.5 steps per beat), so a point-by-point comparison is not meaningful.
- **Velocities.** Velocities stay below 0.6 m/s. run5's 1.7 m/s came from the 307 mm² mitral zone, a jet that is too narrow for the LA body.
- **LA volume.** The LA volume now changes by 8.5 mL per beat because the annulus moves along its axis. In run5 the valve slid sideways and the volume changed by 1.3 mL.

**Wall metrics by distance from the device (median; run5 in brackets)**

| band (mm) | TAWSS (Pa) | OSI | ECAP (1/Pa) | area ECAP > 2 |
|---|---|---|---|---|
| 0–5 | 0.21 (0.09) | 0.22 (0.39) | 1.02 (3.50) | 19 % (89 %) |
| 5–10 | 0.40 (0.20) | 0.15 (0.24) | 0.35 (1.39) | 1 % (30 %) |
| 10–20 | 0.57 (0.30) | 0.15 (0.16) | 0.26 (0.48) | 0 % (7 %) |
| 20–40 | 0.55 (0.32) | 0.15 (0.13) | 0.26 (0.40) | 0 % (4 %) |
| > 40 | 0.42 (0.24) | 0.17 (0.17) | 0.40 (0.71) | 2 % (15 %) |

**Main result**
- The qualitative conclusion of run5 holds: the 0–5 mm ring around the device is still the region with the lowest shear, the highest OSI and the highest ECAP. 48 % of the ECAP > 2 area lies within 20 mm of the device, which is only 20 % of the wall (run5: 42 %).
- The absolute values are lower because the flow is 57 % higher. Device-region ECAP is therefore sensitive to the inflow, so it should be reported as a relative pattern, not as an absolute threshold.

**Q-criterion**
- Isovalue 500 s⁻², with 250 and 700 s⁻² for sensitivity. Source: Morales et al. 2025, LA 4D flow MRI, arXiv:2505.09746; their results were consistent for Q > 100.
- At E-peak the 99th percentile of Q is 2.4 × 10⁴ s⁻², so the vortex cores survive these isovalues. The vein-jet rings are coherent at 500.

**Figures** (`figures/`, same views as run5):
- `pv_slice_*`, `pv_streamlines_*`;
- `pv_qcriterion_peak*.png`;
- `pv_wall_{tawss,osi,ecap}_{front,dev}.png`;
- `fig_bands.pdf`, `fig_time.pdf`.

**Limitations**
- The course pressure and motion profiles are unchanged.
- The rigid annulus moves only along z.
- The flow scaling uses population CMR means, not patient data.
