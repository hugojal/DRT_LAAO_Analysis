# ParaView package: Case 3 left-atrium simulation (run7, 07/11/2026)

These are all the files needed to visualise the case-specific simulation in ParaView (tested with ParaView 6.2).

**Open:** in ParaView go to *View > Python Shell > Run Script* and choose `open_in_paraview.py`, or run `paraview --script=open_in_paraview.py` from this folder. The script loads every item below into the Pipeline Browser. Press Play to run the heartbeat.

Without the script, open these files directly:
- `simulation/run7_last_beat.encas`, the flow;
- `surfaces/*.vtp` / `*.stl`, the wall metrics and models.

| folder / file | content |
|---|---|
| `simulation/run7_last_beat.encas` (+ `step_263`–`step_350.*`) | Last (analysed) heartbeat of the 4-beat run, t = 2.63–3.50 s, every 0.01 s. Arrays: velocity (vector and magnitude), static/total pressure, vorticity, Q-criterion (1/s², labelled "Normalized" by the EnSight export), λ₂, wall shear stress (x, y, z, magnitude), strain rate. Blocks: `fluid-1`, `la_wall`, `mv_funnel` (short tube below the annulus that moves with the valve), `pv_1`–`pv_4`, `mitral_valve`. The mesh moves and is remeshed every step (dynamic mesh). |
| `surfaces/wall_metrics_last_beat.vtp` | TAWSS (Pa), OSI, ECAP (1/Pa), RRT and wall vorticity over the last beat, plus the previous beat (`_prevcycle`) and `dist_to_device_mm`. |
| `surfaces/la_surface.stl` | LA model used in the simulation. |
| `surfaces/device_wire_frame.stl` | Device wire frame segmented from the gamma-transformed CT. |
| `surfaces/device_unet.stl` | Device segmented with a pretrained promptable 3D U-Net (nnInteractive), intersected with the CT wire contrast. |
| `surfaces/device_manual_mask.stl` | Manual device segmentation, used for the distance to the device. |
| `fluent/case_run7_4cycles_07112026.cas.h5` / `.dat.h5` (+ `.sf`) | Final Fluent case and data at t = 3.50 s. They can also be opened in ParaView with the Fluent CFF reader. |
| `flows.csv` | Mass flow through each PV and the MV, and LA volume, every time step of the 4 beats. In Fluent's sign convention, mitral outflow is negative. |
| `mitral_bc.json` | Mitral boundary condition: course velocity curve, **unscaled**, on the 5.3 cm² orifice (79.7 mL per beat, 5.47 L/min), plus the valve velocity. |
| `convergence/` | Convergence evidence: residuals of every iteration, iterations and convergence per time step, mass balance and beat-to-beat periodicity (`convergence_summary.json`, `convergence.png`). |
| `open_device_sections.py`, `device_sections/` | Region in front of the device: cross-sections at 2–16 mm from the device disc, recirculation and stagnant blood. Run the script like `open_in_paraview.py`; numbers, plots, images and an interpretation are in `device_sections/` (README). |
| `transform_LPS_to_model.json` | Rotation and translation from the CT (LPS, mm) to this frame. |

**Frame and units**
- Units are SI (m, s, Pa).
- The origin is the centre of the mitral annulus.
- **z is the mitral valve axis**, pointing from the valve into the atrium.
- The valve moves rigidly along −z, by up to 8.9 mm towards the ventricle in systole: this is the longitudinal motion.

**Simulation in short**
- Ansys Fluent 2026 R1; transient, laminar, Newtonian blood (ρ = 1060 kg/m³, μ = 3.5 mPa·s).
- 272,293 tetrahedra, from the corrected segmentation; PV extensions along the vein trunks; mitral orifice 5.3 cm².
- Inlets: PV pressure curve from the course.
- Mitral valve: velocity curve from the course (unscaled), with the valve motion added.
- dt = 0.01 s; 4 heartbeats of 0.875 s, of which the last is analysed.

**Physiological check (last beat)**
- Stroke volume 79.7 mL; cardiac output 5.47 L/min.
- PV inflow split (pv_1 LIPV / pv_2 RSPV / pv_3 RIPV / pv_4 LSPV) 29 / 33 / 10 / 29 %.
- Maximum velocity 1.08 m/s at the E-wave peak, near the mitral orifice.
- LA volume 156.9–168.3 mL.
- Convergence: all 350 time steps met the residual criteria (median 27 iterations); last two beats differ by 0.1 % in mitral outflow.
- More detail: `4_postprocessing/run7/README.md` in the project repository.

**Data in the repository.** The EnSight and Fluent files (1.2 GB) are not in the git repository; only this README and the script are. To rebuild the folder from the project, run `python 4_postprocessing/make_paraview_package.py`.
