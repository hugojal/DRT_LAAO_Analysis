# 05 · Post-processing in ParaView

The course expects the Ansys results to be visualised in **ParaView**. The Python quick-look figures are archived in `archive/figures_quicklook/`. Verified 19/10/2026: ParaView is **not** installed on the user's machine as far as the agent could see (no `pvpython` in PATH / Program Files) — install it from paraview.org first.

## Files to open
| File | What | Notes |
|---|---|---|
| `archive/3_simulation/results/run2/all_steps.encas` | **Transient EnSight Gold, 85 steps, t = 0.01…0.85 s** | Open with *File > Open*, reader "EnSight Gold Case Reader" (or "EnSight Files"). Parts: `fluid-1` (tets), `la_wall`, `mitral_valve`, `pv_1…pv_4` (triangles). Mesh is remeshed → points/cells change every step. Units: **m**. |
| `archive/3_simulation/results/run2/step_NNN.encas` | the same, one snapshot per file | use only if the combined file gives trouble |
| `archive/4_postprocessing/paraview/la_wall_metrics.vtp` | step-1 wall mesh with point arrays `TAWSS_Pa`, `OSI`, `RRT_1_per_Pa` | computed in Python (see caveat) |
| `archive/4_postprocessing/paraview/device_points_m.vtp` | device segmentation voxel centres, in m (same frame as the mesh) | show as points to mark the device |
| `archive/3_simulation/results/run2/flows.csv` | mass flow at pv_1…pv_4, mitral_valve, volume per step | open as table → *Line Chart View* |

Fields per node: `Static_Pressure`, `Absolute_Pressure`, `Total_Pressure`, `Velocity` (vector), `Velocity_Magnitude`, `X/Y/Z_Velocity`, `Vorticity_Magnitude`, `Q_Criterion_Normalized`, `Lambda_2_Criterion`, `Wall_Shear_Stress` (+ X/Y/Z), `Strain_Rate`. Wall shear is non-zero only on `la_wall`.

## Current run (run5, 4 cycles, 350 steps)
Open `3_simulation/results/run5_4cycles/all_steps.encas` (t = 0.01…3.50 s). Analysis cycle = t 2.63–3.50 s. Wall maps for that cycle: `4_postprocessing/paraview/run5_wall_metrics.vtp` with arrays `TAWSS_Pa`, `OSI`, `ECAP_1_per_Pa`, `RRT_1_per_Pa`, `WallVorticity_1_per_s` (+ `_prevcycle` versions) and `dist_to_device_mm` (use *Threshold* on it for the region near the device). ECAP = OSI/TAWSS.

## Recipes (ParaView GUI)
- **Time animation:** the VCR toolbar steps through the 85 times.
- **Velocity / streamlines:** select `fluid-1`, *Slice* (Z or Y normal) coloured by `Velocity_Magnitude`; *Stream Tracer* with seed type "Point Cloud" near a PV, vectors = `Velocity`; *Glyph* for arrows. Try t = 0.41 s (mitral peak, max |u| ≈ 1.6 m/s) and t = 0.85 s.
- **Vortices:** *Contour* on `Q_Criterion_Normalized` (positive isovalue, e.g. 0.1–0.3 — adjust by eye).
- **Wall shear at one time:** select `la_wall`, colour by `Wall_Shear_Stress`.
- **Stagnant volume per step:** *Threshold* `fluid-1` on `Velocity_Magnitude` below 0.05 (lower threshold = 0) → *Integrate Variables* (Divide cell data by volume off; read `Volume`) → *Plot Data Over Time* gives the stagnant volume in m³; divide by the total (1.67e-4 m³).
- **Near the device:** open `device_points_m.vtp`, *Delaunay 3D* is not needed; use *Clip* of `fluid-1` with a *Sphere* centred at the device centroid ≈ (0.026, −0.157, 0.897) m, radius 0.010–0.020 m, then the threshold/integrate above.
- **TAWSS / OSI / RRT:** open `la_wall_metrics.vtp`, colour by the array, set colour range (TAWSS 0–1 Pa, OSI 0–0.5, RRT 0–20 1/Pa as in the quick-look figures).

## Caveat — do not use *Temporal Statistics* on the wall
The mesh is remeshed in every step (wall nodes 24k and changing), so ParaView's *Temporal Statistics* / *Temporal Interpolator* cannot average WSS node-by-node. `la_wall_metrics.vtp` was computed in Python by mapping each step's WSS onto the step-1 wall by nearest neighbour (mean offset ≈ 3 mm, max ≈ 6 mm near the moving mitral valve) → treat TAWSS/OSI as approximate and say so in the report. To get a fixed-mesh time series, the simulation would need remeshing off (deforming mesh only) or a smaller motion.

## Reproduce the numbers/figures (Python, `../mcp/.venv`)
See the README: `4_postprocessing/analyze_cycle.py` → `report_quant.py` → `pv_figures.py` (pvbatch). The older run2 scripts are in `archive/4_postprocessing/`.
