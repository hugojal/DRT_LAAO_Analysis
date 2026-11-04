# ParaView package: Case 3 left-atrium simulation (run6, 04/11/2026)

These are all the files needed to visualise the case-specific simulation in ParaView (tested with ParaView 6.2).

**Open:** in ParaView go to *View > Python Shell > Run Script* and choose `open_in_paraview.py`, or run `paraview --script=open_in_paraview.py` from this folder. The script loads every item below into the Pipeline Browser. Press Play to run the heartbeat.

Without the script, open these files directly:
- `simulation/run6_last_beat.encas`, the flow;
- `surfaces/*.vtp` / `*.stl`, the wall metrics and models.

| folder / file | content |
|---|---|
| `simulation/run6_last_beat.encas` (+ `step_263`–`step_350.*`) | Last (analysed) heartbeat of the 4-beat run, t = 2.63–3.50 s, every 0.01 s. Arrays: velocity (vector and magnitude), static/total pressure, vorticity, Q-criterion (1/s², labelled "Normalized" by the EnSight export), λ₂, wall shear stress (x, y, z, magnitude), strain rate. Blocks: `fluid-1`, `la_wall`, `pv_1`–`pv_4`, `mitral_valve`. The mesh moves and is remeshed every step (dynamic mesh). |
| `surfaces/wall_metrics_last_beat.vtp` | TAWSS (Pa), OSI, ECAP (1/Pa), RRT and wall vorticity over the last beat, plus the previous beat (`_prevcycle`) and `dist_to_device_mm`. |
| `surfaces/la_surface.stl` | LA model used in the simulation. |
| `surfaces/device_wire_frame.stl` | Device wire frame segmented from the gamma-transformed CT. |
| `surfaces/device_unet.stl` | Device segmented with a pretrained promptable 3D U-Net (nnInteractive), intersected with the CT wire contrast. |
| `surfaces/device_manual_mask.stl` | Manual device segmentation, used for the distance to the device. |
| `fluent/case_mvz_run6_4cycles_04112026.cas.h5` / `.dat.h5` (+ `.sf`) | Final Fluent case and data at t = 3.50 s. They can also be opened in ParaView with the Fluent CFF reader. |
| `flows.csv` | Mass flow through each PV and the MV, and LA volume, every time step of the 4 beats. In Fluent's sign convention, mitral outflow is negative. |
| `mitral_bc_scaling.json` | Mitral boundary condition: scale factor 0.5616, giving a cardiac output of 5.0 L/min (73 mL per beat). |
| `transform_LPS_to_model.json` | Rotation and translation from the CT (LPS, mm) to this frame. |

**Frame and units**
- Units are SI (m, s, Pa).
- The origin is the centre of the mitral annulus.
- **z is the mitral valve axis**, pointing from the valve into the atrium.
- The valve moves rigidly along −z, by up to 9.7 mm towards the ventricle in systole: this is the longitudinal motion.

**Simulation in short**
- Ansys Fluent 2026 R1; transient, laminar, Newtonian blood (ρ = 1060 kg/m³, μ = 3.5 mPa·s).
- 308,000 tetrahedra.
- Inlets: PV pressure curve from the course.
- Mitral valve: velocity curve from the course, scaled to a normal cardiac output, with the valve motion added.
- dt = 0.01 s; 4 heartbeats of 0.875 s, of which the last is analysed.

**Physiological check (last beat)**
- Stroke volume 72.9 mL; cardiac output 5.0 L/min.
- PV inflow split 20 / 28 / 20 / 31 %.
- Maximum velocity 0.57 m/s at the E-wave peak.
- LA volume 172.7–181.2 mL.
- More detail: `4_postprocessing/run6/README.md` in the project repository.

**Data in the repository.** The EnSight and Fluent files (1.2 GB) are not in the git repository; only this README and the script are. To rebuild the folder from the project, run `python 4_postprocessing/make_paraview_package.py`.
