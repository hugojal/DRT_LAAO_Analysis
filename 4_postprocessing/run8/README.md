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

To fill the report figure folder (`5_report/figures_run8/`, report version of 07/11/2026 evening):
```
python near_device_timecourse.py run8                      (speed, slow blood, vorticity and Q shares per step -> run8/near_device_timecourse.csv)
PV_RUN=run8 PV_RESULTS=run8_4cycles PV_OUT=$R/4_postprocessing/run8/figures PV_Q=500 PV_Q_LATE=250 PV_TRANSFORM=2_mesh/run8_07112026/transform_LPS_to_model.json pvbatch --force-offscreen-rendering pv_figures.py unet|manual|flow|vortex|wall
python ct_wire_figure.py run8/figures                      (ct_unet_enface.png)
copy into 5_report/figures_run8: run8/figures/{ct_unet_enface, pv_unet_device, pv_manual_device, pv_streamlines_peak, pv_streamlines_late,
     pv_qcriterion_peak, pv_qcriterion_late, pv_wall_ecap_dev}.png, run8/figures/fig_bands.pdf,
     run8/device_sections/views/streamlines_side_{systole_t290, filling_t306, late_t340}.png
python thrombus_check/thrombus_report_figure.py ../5_report/figures_run8   (fig_thr_ct.pdf, fig_thr_profile.pdf)
python make_report_figures.py run8 ../5_report/figures_run8               (fig_timecourse.pdf; trims the PNGs)
```

## Time course near the device (`near_device_timecourse.csv`, report Fig. 3)
Beat averages, volume-weighted:

| zone | mean speed | slow blood (|v| < 5 cm/s) | vorticity | rotation-dominated (Q > 0) |
|---|---|---|---|---|
| whole LA | 0.122 m/s | 22 % | 44 1/s | 33 % |
| within 5 mm of the device | 0.083 m/s | 38 % (up to 66 % with the valve closed) | 55 1/s | 19 % |
| within 10 mm | 0.109 m/s | 26 % | 49 1/s | 24 % |

Vorticity is higher next to the device because next to a wall it mostly measures shear. The Q-criterion separates swirl from shear and shows fewer vortices there.

> **14/11/2026:** the scripts and outputs of the sections *Extra flow figures* and *Long-axis plane* (`extra/`, `device_planes/`, `pv_extract_extra.py`, `pv_slow_blood.py`, `pv_washout_views.py`, `plot_extra_figures.py`, `render_device_planes.py`) were not used in the report and moved to `archive/cleanup_14112026/` (git-ignored).

## Extra flow figures (`extra/`, 09/11/2026; candidates, not yet in the report)
- **Washout test** (`pv_extract_extra.py washout`, `pv_washout_views.py`, `plot_extra_figures.py`):
  - Particles were released at the start of beat 3 (t = 1.75 s) in two spheres of r = 8 mm and traced for two beats. One sphere sits 6 mm in front of the device (1056 particles inside the blood); the other sits in the middle of the atrial body (1500 particles).
  - Particles that leave through the mitral valve stop being counted. Losses during systole, when the valve is closed, are small (about 2–4 %); they are particles that cross the wall numerically.
  - **Still in the LA after one beat:** 61 % of the blood released in front of the device, against 28 % of the atrial-body blood.
  - **After two beats:** 44 % against 12 %.
  - Outputs: `fig_washout.pdf` (curve) and `washout_{release,1beat,2beats}.png` (3D: red = released in front of the device, grey = released in the atrial body).
- **Beat-averaged speed** on the plane through the mitral axis and the device centre (`pv_extract_extra.py mean`) → `fig_mean_speed.pdf`.
  - The blood next to the device is slower, but only in a thin rim, and the vortex centres in the atrial body are also slow. It is weaker evidence than the washout test.
- **Slowest 10 % of the blood** (`pv_slow_blood.py`, `slow_blood.json`):
  - Within 15 mm of the device, 24 % of the blood belongs to the slowest 10 % of the atrium.
  - In 3D, this slow blood is a thin layer along the whole wall, so the 3D view was not kept (archived).

## Long-axis plane in front of the device (`device_planes/`, 09/11/2026; candidates)
- **Script:** `render_device_planes.py`.
- **Plane:** contains the device axis and the mitral axis. The device is on the right, drawn as its cut by the same plane (filled orange; gamma + manual segmentation).
- **Locator:** `longaxis_locator.png` shows the transparent atrium, the device in orange, and the part of the plane shown in blue.
- **Kept for the report (user, 09/11/2026):** both rows, speed and vorticity.
- **Content:** speed or vorticity magnitude, with arrows showing the in-plane flow direction, at 2.90 / 3.06 / 3.40 s.
- **What the images show:**
  - **Valve closed and late diastole:** in front of the device the blood is slow and turns on itself.
  - **E-wave peak:** the jet from the veins passes on the left of this region.
  - **Vorticity:** high only in the thin shear layer along the wall and at the edge of the jet. Inside the region in front of the device it stays low, so no vortex sweeps it.
- **Dropped:** cross-sections perpendicular to the device axis (archived). They cut through the whole atrial body.
- **Disliked:** the washout and beat-averaged speed figures (`extra/`) were rejected by the user on 09/11/2026.
- **In the report (09/11/2026, revised):** Fig. 2 is back to one row of streamlines. A separate column figure (`fig:plane`) shows the locator and the late-diastole vorticity only (ParaView colour bar below the image). The speed row and the other two phases are not used. The 2x3 layout, the matplotlib colour bars and `make_fig2_panels.py` are in `archive/fig2_unused_09112026/`.
- **Vorticity near the device** (`run8/extra/vorticity_near_device.npy`, columns t, 0-5 mm slab, 0-10 mm slab, whole LA, LA p95, slab speed): the volume mean in the 0-5 mm slab is above the LA mean (diastole 76 vs 56 1/s). This comes from the shear layer on the wall (vorticity magnitude includes shear). The Q-criterion shows fewer vortices there (18 vs 33 %). Literature (Albors et al. 2024, PLoS Comput Biol, PMID 39325818) links DRT to low velocity and recirculation around the device, not to high vorticity.

## Pathlines (10/11/2026)
- `4_postprocessing/pv_pathlines.py` -> `run8/pathlines/`. Particles are released once at the start of a beat and followed for one beat (ParticleTracer, one position per 0.01 s step); the lines are built from each ParticleId. Colour = time after release. ParaView's ParticlePath filter drew straight artefacts from the vein inlets (archived in `archive/pathlines_particlepath_10112026/`).
- Seeds: sphere r 8 mm, 5 mm in front of the device (as the device streamlines); the same sphere at the centroid of the atrial body; points just inside the four vein inlets.
- **Still in the LA after one beat** (`pathlines_summary.txt`):
  - last beat (release 2.63 s): in front of the device 25 %, atrial body 42 %, vein blood 99 %.
  - beat 3 (release 1.75 s): in front of the device 61 %, atrial body 32 % (same as the washout test of 09/11/2026).
- The whole-atrium flow repeats from beat to beat (mean LA speed 0.083 / 0.086 / 0.083 m/s in beats 2-4, `extra/mean_speed_per_step_beats2to4.npy`), but the fate of the blood in front of the device does not: in the last beat most of it leaves with the E wave. A one-beat washout of this region is therefore not a reliable measure; it depends on the beat.
- **In the report (10/11/2026):** Fig. 3 = pathlines of the last beat only (device, atrial body, PV inlets; `make_pathline_panels.py` -> `path_*.png`, one shared colour bar). It replaces the locator + vorticity figure (archived). Beat 3 is not shown: the analysed beat is the 4th. The text now contrasts streamlines (direction of the flow at one instant) with pathlines (where the blood goes during the beat); "least renewed" was replaced by "rarely reached by fresh blood" (7 % of the vein pathlines reach the device region in the last beat).
- **Retention reconciled (10/11/2026, `pathlines/retention_check_seeds.py`):** with 400 evenly spread seeds, still in the LA after one beat: 5 mm layer in front of the device face (radius 16 mm) 62 % (release 1.76 s) / 58 % (2.63 s); 8 mm sphere 5 mm in front 64 % / 27 %. Seeds on mesh nodes give higher values (nodes crowd near the wall). The earlier 25 % came from the sphere, whose outer part the E wave sweeps out in the last beat; the blood at the device itself stays ~60 % in both beats, against ~40 % of the body blood (independent review agrees). Report text revised: retention 60 vs 40 %, no OSI rise, "possible rather than clear" risk, flat-device limitation.
