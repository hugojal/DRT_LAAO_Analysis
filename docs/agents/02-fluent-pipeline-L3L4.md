# 02 · Fluent pipeline (L3+L4) — "Left atrium occlusion and thrombus formation"

Source: `docs/L3+L4 MOS26.pdf` (34 steps). Slide caveat: this is an **example** pipeline; values must be re-derived for this mesh. Fluent GUI path in *italics*; PyFluent settings path in `code` for `fluent_get`/`fluent_set`.

## A. Mesh and general setup
1. *File > Import > NASTRAN > Bulkdata File* → `2_mesh/HugoJal_Case3_gmsh.bdf`.
2. Display the mesh.
3. *Mesh Check* and *Mesh Quality* (`fluent_mesh_check`): no negative volumes, check orthogonal quality/skewness.
4. **Scale the mesh to mm** (mesh was built in mm).
5. *General > Time > Transient* (`setup.general.solver.time`).
6. *Models > Viscous*: SST k-ω → change to **Laminar** (`setup.models.viscous.model`).

## B. Zones
7. Separate boundary faces of PVs and MV by angle, **~20–40°**: *Domain > Zones > Separate > Faces*.
8. *Domain > Zones > Combine > Merge* to merge fragments per vein/valve.
9. Identify each zone in Display; **rename** (e.g. `pv_1…pv_4`, `mitral_valve`, `wall`).

## C. Material and boundary conditions
10. Blood: **ρ = 1060 kg/m³, μ = 0.0035 kg/(m·s)** (Newtonian).
11. *Cell Zone Conditions*: solid → **fluid**, material = blood.
12. Load transient profiles via TUI: `/file/read-transient-table 3_simulation/boundary_conditions/<file>.prof` (`fluent_read_profile`).
13. Zone types:
    - Pulmonary veins → **Pressure inlet** (`pressure_inlet.prof`, `function_pressure_c`).
    - Mitral valve → slide says "velocity outlet", but implement as **velocity inlet with the sign inverted in the `.prof`** (`velocity_outlet.prof` already contains the inverted values).
    - Dynamic mesh motion on the MV (see D).

## D. Dynamic mesh  ← **user reports this is DONE**
14. Enable dynamic mesh; check smoothing and remeshing.
15. Smoothing: **Spring/Laplace**.
16. Remeshing: **Local cell**.
17. *Minimum length scale* = the minimum from **Mesh Scale Info** (never 0 / very small → negative cells).
18. *Maximum length scale* = a little **above** the Mesh Scale Info maximum.
19. Max cell skewness **0.9**; remeshing interval **5–10**.
20. Dynamic mesh zones:
    - Interior (volume) and exterior (LA wall) → **Deforming** (with the meshing options above).
    - **MV** → **Rigid body**, motion from `motion.prof` (`mov_bc_c`, z displacement) — this is where motion is imposed, no deformation.
    - **PVs** (all) → **Stationary**.
26. *Preview motion* to confirm everything is set up properly.

## E. Initialization and solver
27. Initialize with **all zones**. Re-initialize every time a run is stopped and parameters change.
29. *Solution > Methods*: Scheme **Coupled**; Gradient **Green-Gauss Node Based**; **2nd-order** (implicit transient).
30. *Residual monitors*: continuity **0.005**.

## F. Outputs and run
31. *Calculation Activities* → new **EnSight Case Gold (ASCII)** export; save: velocity magnitude, velocity x/y/z, all pressures, vorticity, Q-criterion, Lambda2, **wall shear stress** (wall properties are the focus), strain rate.
32. *Run Calculation*: **85 time steps** (case specific: one cardiac cycle of this data).
33. **Time step size 0.01 s** (matches the 0.01 s sampling of the `.prof` files).
34. **Max 200 iterations / time step**, then *Calculate*.

## Agent checks before pressing Calculate
- Profiles end at/after t = 0.85 s (85 × 0.01) — verify last row of each `.prof`.
- MV motion profile and velocity profile refer to the same zone and are consistent in sign (MV moves, flow enters the LA through PVs and leaves through MV in diastole/systole logic — confirm with the user).
- Dynamic-mesh preview runs through the whole motion without negative-volume errors.
- Case saved under a new name before the run (`fluent_save_case`).
- Estimate cost: 85 steps × up to 200 iterations on ~100k–500k cells → minutes to hours; run in the background (`fluent_run_start`) and poll.

## Results to hand over (L5 input)
EnSight Case Gold exports + saved `.cas.h5/.dat.h5`, zipped. Metrics of interest for DRT risk: low-velocity/stagnation volume near the LAA and device, WSS (TAWSS, OSI), vortex structures (Q-criterion, Lambda2), strain rate.
