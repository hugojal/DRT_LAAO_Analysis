# run8 mesh: Case 3 LA with circular PV cylinders (07/11/2026)

**This is the mesh to hand in and the one simulated in run8.** It is identical to `../run7_06112026/`, with one change.

**The change:** the pulmonary-vein extensions end in **circular cylinders**, as the course guide asks.
- run7 smoothed each vein's lumen into an oval of the same area. That was closer to the anatomy, but not what the guide asks for.
- In run8 each extension keeps the lumen's area and blends over 5 mm (run7: 3 mm) from the cut outline into a circle. It then runs straight for the rest of the 10 mm and ends in a flat cap.

| vein (Fluent zone) | area at the cut | cylinder diameter |
|---|---|---|
| RSPV (`pv_2`) | 247 mm² | 17.7 mm |
| LSPV (`pv_4`) | 144 mm² | 13.5 mm |
| LIPV (`pv_1`) | 133 mm² | 13.0 mm |
| RIPV (`pv_3`) | 63 mm² | 9.0 mm |

- **Diameter limit:** all diameters are below the 22.5 mm maximum mentioned by the user (course guide).
- **Cap direction:** every cap is perpendicular to its vein trunk, 0–2° off the trunk axis.

**Unchanged from run7:**
- the corrected segmentation;
- the vein cut positions (`pv_cuts.json`);
- the mitral valve: 5.29 cm² cap at z = −6.5 mm;
- the model frame: z = mitral valve axis, origin = annulus centre, with the same `transform_LPS_to_model.json`.

All post-processing therefore works unchanged.

**Files:**
- Surface: `HugoJal_Case3_run8_07112026.stl`
- Volume (Fluent): `HugoJal_Case3_run8_07112026.bdf`, in mm (scale to mm in Fluent).
- Zone positions: `caps_model_frame.json`.
- Build log: `build_run8.log`.

## Build
```
set PYMESHLAB_PYTHON=C:\Python314\python.exe   (a Python with pymeshlab)
python build_mesh_run8.py
python check_mesh_run8.py
python render_pv_cylinders.py
```
`build_mesh_run8.py` is the run7 build script (archived) with two changes:
- the end shape is a circle of the lumen area;
- the blend length `PV_T` is 5 mm.

The steps are listed below.

## Why the run7/run8 mesh differs from the earlier ones (run7 decisions, 06/11/2026)
These are the user's decisions of 06/11/2026, after the mock rubric review (`docs/agents/reviews/rubric_review_06112026.md`, plan in `docs/agents/run7_plan_06112026.md`):
1. **Mitral valve 4–6 cm²** (course requirement). run6 had the anatomical annulus cut, 8.6 cm².
2. **Re-cut the PV extensions.** The Meshmixer cylinders of `../HugoJal_Case3.stl` pointed 24–55° away from their veins (`pv_cuts.json`) and were 2–4 times the lumen area. They replaced the vein stubs entirely, so the veins could only be re-cut from the segmentation.
3. **Segmentation fixes** (`1_segmentation/la_v2_06112026/`): device removed, inferior veins extended to their first branch, topology cleaned (genus 0).
   - The user first preferred to leave the mesh as it was.
   - Re-cutting the veins (decision 2) needs the vein anatomy, which only the segmentation has, so the mesh is now built from the corrected segmentation.
   - The atrial body barely moves: median 0.04 mm from the run6 surface, 95th percentile 0.8 mm.
4. The valve region moving with the valve is set in Fluent (`3_simulation/setup_case_run8.py`), not in the mesh.

## Steps (`build_mesh_run8.py`; identical to run7 except step 1)
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
   - A straight extension of 10 mm is added along the trunk axis, with a flat cap. **run8:** its section blends over 5 mm from the lumen outline (starting with the slope of the vein wall) into a **circle of the same area**, then stays circular. (run7 used a same-area oval reached over 3 mm.)
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

## Checks (`check_mesh_run8.json`, `check_pv_cylinders_run7_vs_run8.png`)
| item | run8 | run7 |
|---|---|---|
| zones after the 30° separation | 6 (wall, MV cap, 4 PV caps), caps flat | 6 |
| PV caps | circular; 247 / 143 / 132 / 63 mm² | ovals, same areas |
| mitral cap | 529.0 mm² (5.29 cm²) | same |
| surface | closed, 0 non-manifold edges, genus 0, 42 980 triangles | 43 034 |
| volume mesh | 271 908 tetrahedra, 0 negative volumes, 156.0 mL | 272 293, 156.1 mL |
| skewness | max 0.907, mean 0.24, 2 cells > 0.9, 0 > 0.95 | max 0.941 |
| minSICN | min 0.36 | 0.31 |

**Self-intersection:** in the run7 build, a circle at the LIPV ran into a neighbouring structure. In run8 the 5 mm blend avoids this. Gmsh meshed the volume without errors, and the surface and volume mesh enclose the same 156.0 mL.

run7 itself (mesh, results, figures) is archived in the git-ignored `archive/` (local only).
