# LA mesh with the mitral cut on the annulus and z along the valve axis (03–04/11/2026)

New files. The original `../HugoJal_Case3.stl` and `../HugoJal_Case3_gmsh.bdf` are not changed.

- **Surface**: `HugoJal_Case3_mvz_03112026.stl`
- **Volume (for Fluent)**: `HugoJal_Case3_mvz_03112026.bdf`
- **Units**: mm, so scale to mm in Fluent as before.

## Why z has to follow the valve axis
In the Fluent case, the mitral valve moves as a **rigid body**. Its motion profile, `3_simulation/*/motion.prof` (`mov_bc_c`), contains only a **z** displacement, which reaches −8.9 mm at t = 0.35 s.

In the old mesh the mitral cap was **73° away from z**. In run5 the valve therefore slid about 8.5 mm within its own plane and moved only about 2.6 mm along its axis.

Physiologically, the mitral annulus moves along the valve (LV long) axis. A real-time 3D echo study measured a peak annulus motion of 8.7 ± 3.0 mm in healthy people (Veronesi et al., *J Am Soc Echocardiogr* 2008;21:347–54, doi:10.1016/j.echo.2007.06.017). The z axis must therefore be the axis of the valve.

**Sign.** The profile is negative during systole (0–0.35 s), before the mitral inflow peak at 0.42 s. In systole the annulus moves towards the LV apex. So **−z = from the LA into the LV**: diastolic flow goes through the valve towards −z, and the annulus moves towards the LV in systole and back in early diastole. If +z = LA→LV is wanted instead, the model only has to be rotated 180° about x.

Course practice (slides L2) is followed: flat caps on the PV and MV extensions, cylinder edges at about 90°, smooth transitions, so the caps can be separated by angle in Fluent (slides L3–L4, 20–40°). Added extensions are also used in published LAAO CFD so that the flow is normal to the inlets/outlets (Aguado et al., *Front Physiol* 2019;10:237, doi:10.3389/fphys.2019.00237). No published convention for the z axis was found. The requirement comes from the z-only motion profile.

## Steps
1. **`find_mitral_annulus.py` — mitral annulus on the CT.**
   - In planes through the valve axis (every 10°), the atrio-ventricular groove forms a notch of wall/fat on each side, and the leaflets hang from its tip.
   - Thin leaflets are removed and the notch tips (hinge points) are found.
   - A plane is fitted through 34 points and the process repeated until stable.
   - Result: centre (22.1, −168.4, 857.1) mm LPS, axis (0.666, −0.720, −0.194) LA→LV, mean radius 18.5 mm, saddle height 9 mm.
   - The old cap was 12° tilted from this plane and on average 6.7 mm inside the LV (`mitral_annulus_check.png`).
2. **`build_mesh_mvz.py` — build the new mesh.**
   - Cut the original surface on the annulus plane.
   - Extrude the cut outline 10 mm along the axis and close it with a flat cap at 90°.
   - Smooth only a ±4 mm band at the junction.
   - Relax 13 isolated creases of the original surface (dihedral > 45°, Meshmixer artefacts) locally.
   - Rotate: annulus centre → origin, axis → −z (`transform_LPS_to_model.json` holds the matrix and its inverse).
   - Remesh isotropically with MeshLab (`remesh_surface.py`, pymeshlab, ~0.95 mm, cap rings kept sharp, nodes re-projected on the surface).
   - Tetrahedra in Gmsh on that surface, with sizes 0.95 mm at the wall growing to 1.9 mm inside, and Netgen + Relocate3D optimisation.
3. **`check_mesh_mvz.py` — checks.** Results in `check_mesh_mvz.json`, `compare_old_mesh.json` and the `check_*.png` images.

## Requirements
| requirement | result |
|---|---|
| PV and MV cut, separable by angle | A 30° separation of the surface (as Fluent's *Separate > Faces*) gives exactly **6 zones**: wall, MV cap and 4 PV caps. The MV cap is flat, 33.1 mm equivalent diameter, normal exactly −z. |
| MV cut consistent with the CT | Cut on the annulus plane fitted on the CT, perpendicular to the valve axis (`check_mitral_on_ct.png`). The outline is the LA surface at that plane: on average 2.3 mm inside the hinge points (max 7.9 mm, where the LA segmentation stops short of the groove). |
| No non-manifold edges / negative volumes | Surface closed, 0 boundary edges, 0 non-manifold edges. 0 tetrahedra with negative volume. |
| Not oversmoothed | More than 6 mm from the valve the new surface lies on the original one: mean distance 0.00 mm, max 0.38 mm (only the 13 crease fixes). |
| < 500k elements, good quality | **307,927 tetrahedra**. Skewness max 0.885 (mean 0.24), none above 0.9. Gmsh minSICN ≥ 0.43. Old mesh: 393,557 tetrahedra, skewness max 1.00, 253 above 0.9. |
| .stl and .bdf | `HugoJal_Case3_mvz_03112026.stl` (49,032 triangles, the same triangles as the boundary of the volume mesh) and `.bdf` (GRID + CTETRA, like the old one). |

## What changes in Fluent
- **Mesh and case.** Import the new .bdf, scale to mm, *Separate > Faces* by angle (30°) and rename the zones (MV cap = the face at z = −10 mm). Then set up the case again as before. run5 results belong to the old mesh.
- **Flow rate.** The MV cap is now 862 mm² instead of about 420 mm². The MV boundary condition is a **velocity**, so the same profile gives about twice the flow through the valve. Check the mitral flow rate per beat (old run ≈ 46 mL/beat) and decide whether the velocity profile must be scaled.
- **Coordinates.** Results come out in the model frame. To compare with the CT, device or old results, map back with `transform_LPS_to_model.json` (x_LPS = Rᵀ x + c).

## Reproduce
From the project folder, with a Python that has pyvista, gmsh, pynrrd and scipy, plus one with pymeshlab:
```
python 2_mesh/mv_aligned_03112026/find_mitral_annulus.py
set PYMESHLAB_PYTHON=<python with pymeshlab>
python 2_mesh/mv_aligned_03112026/build_mesh_mvz.py
python 2_mesh/mv_aligned_03112026/check_mesh_mvz.py
```
