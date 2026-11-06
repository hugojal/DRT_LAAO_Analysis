# run7 mesh: Case 3 LA (06/11/2026)

Built from the **corrected segmentation**, with **PV inlets re-cut along each vein's trunk** and the **mitral valve narrowed to a 5.3 cm² orifice**. The frame is the same as run6:
- z is the valve axis;
- the origin is the centre of the mitral annulus;
- `transform_LPS_to_model.json` is identical to `../mv_aligned_03112026/`.

All post-processing therefore works unchanged.

- **Surface:** `HugoJal_Case3_run7_06112026.stl`
- **Volume (for Fluent):** `HugoJal_Case3_run7_06112026.bdf`, in mm (scale to mm in Fluent).
- **Zone positions** (model frame, for the Fluent set-up): `caps_model_frame.json`.

## Why
These are the user's decisions of 06/11/2026, after the mock rubric review (`docs/agents/reviews/rubric_review_06112026.md`, plan in `docs/agents/run7_plan_06112026.md`):
1. **Mitral valve 4–6 cm²** (course requirement). run6 had the anatomical annulus cut, 8.6 cm².
2. **Re-cut the PV extensions.** The Meshmixer cylinders of `../HugoJal_Case3.stl` pointed 24–55° away from their veins (`pv_cuts.json`) and were 2–4 times the lumen area. They replaced the vein stubs entirely, so the veins could only be re-cut from the segmentation.
3. **Segmentation fixes** (`1_segmentation/la_v2_06112026/`): device removed, inferior veins extended to their first branch, topology cleaned (genus 0).
   - The user first preferred to leave the mesh as it was.
   - Re-cutting the veins (decision 2) needs the vein anatomy, which only the segmentation has, so the mesh is now built from the corrected segmentation.
   - The atrial body barely moves: median 0.04 mm from the run6 surface, 95th percentile 0.8 mm.
4. The valve region moving with the valve is set in Fluent (`3_simulation/setup_case_run7.py`), not in the mesh.

## Steps (`build_mesh_run7.py`)
0. **Surface from the segmentation.**
   - Marching cubes, then Taubin smoothing: 150 iterations, pass band 0.02, no shrinking. The MeshLab step of the course.
     - 60/0.05 left the paint texture of the segmentation.
     - 300/0.01 pinched thin branches.
   - Then MeshLab quadric decimation and isotropic remeshing to 0.7 mm, cached in `_seg_remeshed_cache_*.stl` (git-ignored).
   - **Around the device** (within 12 mm, fading out by 17 mm): extra local Taubin smoothing. Subtracting the device left folds where the disc rim meets the atrial wall.
1. **PV re-cut** (`find_pv_cuts.py` → `pv_cuts.json`, `qc_pv_cuts.png`).
   - Each vein is followed in the segmentation, shell by shell of geodesic distance from the centre of the atrium.
   - It is cut perpendicular to its trunk axis (fitted through the shell centres), a few mm past the ostium and before the first branch.
   - Only the part of the surface beyond the plane that is connected to that vein is removed.
   - A straight extension of 10 mm is added along the trunk axis, with a flat cap. Its section is the lumen outline smoothed to an oval of the same area, reached over 3 mm, starting with the slope of the vein wall.
   - A circle bulged into a neighbouring structure at the LIPV, so the oval is used.
2. **Mitral valve**, as in `../mv_taper_06112026/`:
   - the atrium kept down to 8 mm above the CT annulus;
   - the valve region rebuilt as a smooth structured surface (ridge removed, neck size kept);
   - a C1 funnel to a convex 5.3 cm² oval;
   - 1.5 mm straight, then a flat cap at z = −6.5 mm.
3. **Cut hygiene.**
   - Before each cut, vertices within 0.15 mm of the cut plane are moved onto it, so the clip makes no near-duplicate points.
   - The extension rings move from the raw seam points to even angles within 1.5 mm.
4. **Rotate into the model frame and remesh in MeshLab** (0.95 mm). Then three repairs:
   - collapse needle edges;
   - relax creases sharper than 25° away from the cap rims (via VTK feature edges);
   - flip cap-rim triangles that cut the 90° corner and relax the interior cap vertices.
5. **Volume mesh in Gmsh:** 0.95 mm at the wall growing to 1.9 mm inside, Netgen + Relocate3D optimisation. Written as `.bdf` (GRID + CTETRA) and `.msh`.

## Checks (`check_mesh_run7.py` → `check_mesh_run7.json`, `check_mesh_views.png`, `check_mitral_on_ct.png`; `render_compare_run6.py` → `check_run6_vs_run7.png`)
| item | result (run6 mesh in brackets) |
|---|---|
| separation by angle (30°) | **6 zones**: wall, MV cap, 4 PV caps |
| mitral cap | **529.0 mm² = 5.29 cm²**; flat, normal −z, centre (−0.3, −0.2, −6.5) mm (861 mm², z = −10 mm) |
| mitral cross-section (cm²) | z = −6.5: 5.29; −4: 5.48; −2: 6.55; 0 (annulus): 8.57; 2: 11.2; 4: 13.7; 8: 18.1 |
| PV caps (D_eq, cap normal vs vein trunk) | RSPV 246 mm² (17.7 mm, 0°); LSPV 143 mm² (13.5 mm, 1°); LIPV 133 mm² (13.0 mm, 0°); RIPV 63 mm² (8.9 mm, 2°). Course: 10–25 mm; the RIPV is small in the segmentation. (run6: 220–312 mm², 24–55° off the trunk) |
| surface | closed, 0 non-manifold edges, genus 0, 43 034 triangles, same as the .stl |
| volume mesh | **272 293 tetrahedra**, 0 negative volumes, 156.1 mL (run6 167.4 mL incl. the larger cylinders) |
| quality | skewness max 0.941, mean 0.24, 4 cells > 0.9, **0 > 0.95** (run6: 0.885). minSICN min 0.31 |
| vs segmentation | atrial wall (> 8.5 mm above the annulus, > 12 mm from the PV cuts): median 0.06 mm, 95th percentile 0.18 mm, max 0.95 mm |
| vs run6 surface | same region: median 0.04 mm, 95th percentile 0.82 mm, max 5.9 mm (around the device, where the corrected segmentation follows the device face) |

## Fluent set-up and run (run7, not run yet)
- **Set-up:** `3_simulation/setup_case_run7.py`.
  - It imports the mesh and names the zones by position (pv_1 = LIPV, pv_2 = RSPV, pv_3 = RIPV, pv_4 = LSPV, as in run6).
  - It splits the wall below the annulus plane (z < 0) into `mv_funnel`.
  - It replaces the mesh in the run6 set-up case, so all settings are kept, and adds a **rigid-body dynamic zone for `mv_funnel` with the mitral motion**.
  - Remeshing lengths: 0.15 / 4.5 mm. The edges are 0.14–4.07 mm.
- **Mitral BC:** `3_simulation/boundary_conditions_4cycles_run7/`.
  - The course curve **unscaled** (SV 79.7 mL, CO 5.47 L/min, peak 0.945 m/s at the orifice), plus the valve velocity.
- **Tested on 06/11/2026** in scratch Fluent sessions (no project case written):
  - every step of the set-up script works;
  - the angle separation gives 6 zones; `mv_funnel` is 711.7 mm²;
  - the rigid dynamic zone gets the mitral motion `mov_bc_c`.
- **Mesh-motion preview over systole** (35 steps of 0.01 s, t = 0 → 0.35 s):
  - The cap travels the full 8.9 mm (z −6.5 → −15.4 mm), and the funnel moves rigidly with it.
  - Minimum cell volume stays positive; maximum skewness ≤ 0.87.
  - **LA volume +11.6 mL.** With only the cap moving this would be 5.2 mL; run6 had 8.4 mL. It is more than annulus area × travel (7.6 mL) because the LA floor flares above the annulus, so the stretched band is wider than the annulus.
- **The case files** (`cases/mesh_run7_06112026.cas.h5`, `case_run7_setup_06112026.cas.h5`) were **not written yet**. Another Fluent session (a PyFluent meshing session, probably the Circle-of-Willis project) held the Student licence. Run the set-up when Fluent is free.
- **Run:**
  ```
  python 3_simulation/setup_case_run7.py
  python 3_simulation/run_cycle.py 350 3_simulation/results/run7_4cycles 3_simulation/cases/case_run7_4cycles_DDMMYYYY.cas.h5 3_simulation/cases/case_run7_setup_06112026.cas.h5 3_simulation/boundary_conditions_4cycles_run7
  ```

## Reproduce (from the project folder)
```
python 1_segmentation/la_v2_06112026/fix_la_segmentation.py
python 2_mesh/run7_06112026/find_pv_cuts.py
set PYMESHLAB_PYTHON=<python with pymeshlab>
python 2_mesh/run7_06112026/build_mesh_run7.py
python 2_mesh/run7_06112026/check_mesh_run7.py
python 2_mesh/run7_06112026/render_compare_run6.py
```
