# LA mesh with a 5.3 cm² mitral outlet (06/11/2026)

> **Superseded by `../run7_06112026/`.** That mesh uses the same mitral steps, plus the corrected segmentation and re-cut PV inlets. The scaled BC and set-up script mentioned below (`…_mv53`) were removed. run7 uses `boundary_conditions_4cycles_run7/` (unscaled) and `setup_case_run7.py`.

These are new files. Nothing in `../mv_aligned_03112026/` (the run6 mesh) or in the original mesh is changed. The frame is the same as run6:
- z is the valve axis;
- the origin is the centre of the mitral annulus;
- `transform_LPS_to_model.json` is identical.

All post-processing therefore works unchanged.

- **Surface:** `HugoJal_Case3_mv53_06112026.stl`
- **Volume (for Fluent):** `HugoJal_Case3_mv53_06112026.bdf`, in mm (scale to mm in Fluent).

## Why
The mitral cap of the run6 mesh is the anatomical annulus cut, **8.6 cm²**. This was measured on the mesh (861 mm²) and on the Fluent run6 output (8.61 cm²). The course asks for a mitral valve cross-section of **4–6 cm²**, which is the orifice of the open leaflets in diastole.

## What the build does (`build_mesh_mv53.py`)
The LA surface more than 8 mm above the annulus, the PV caps, the crease fixes, the remeshing and the Gmsh settings are the same as in run6. Only the region around the valve is rebuilt, as a structured surface in polar coordinates around the valve axis. Every section there is star-shaped (checked).

1. **8 mm above the annulus → annulus.**
   - Each 0.5 mm layer is the original segmented section.
   - It is blended into the same section low-pass filtered in angle (10 harmonics). The blend starts at 0 at 8 mm (exactly the segmentation, no kink) and reaches 1 at 5 mm.
   - This removes a ~1 mm ridge and groove of the segmentation next to the annulus (≤ 1.06 mm change). The **size of the neck is kept**: 8.62 cm² at the annulus, equal to the CT cut.
2. **Annulus → 5 mm below.**
   - A cubic Hermite curve per angle starts with the value **and slope** of the LA wall at the annulus (mean 47°), so the wall keeps converging the way it does: no step.
   - It ends parallel to the axis on a **convex oval of 5.3 cm²**: the annulus outline with only 2 harmonics. The annulus is kidney-shaped. With the oval outlet its notch fades out along the funnel and does not run down it as a groove.
3. **Straight end.** 1.5 mm straight and a flat cap at z = −6.5 mm, instead of −10 mm.
   - The cap meets the wall at 90°, so Fluent separates it by angle.
   - The end is a straight cylinder, so the moving cap keeps its area.
4. **Repairs after the MeshLab remesh:**
   - edges shorter than 0.14 mm (needles) are collapsed;
   - MV-rim triangles that cut the 90° corner are flipped (they would become an extra Fluent zone);
   - the interior cap vertices are relaxed within the cap plane.

**Earlier tries** (user feedback) are kept for reference:
- `first_try_step/`: a cosine taper below the annulus that started parallel to the axis. This made a **step** (collar) at the annulus.
- `second_try_erase/`: the LA was erased from 6 mm above the annulus and a funnel lofted from there. There was no step, but it **narrowed the neck** (−1.3 cm² at the annulus) and the kidney notch ran down the funnel as **grooves**.
- Comparison images:
  - `check_step_before_after.png`: 3D close-ups and two sections, each against run6 in grey; made by `render_before_after.py`.
  - `check_sections.png`: horizontal sections, run6 vs now; made by `plot_sections.py`.

## Checks (`check_mesh_mv53.py` → `check_mesh_mv53.json`, `check_*.png`)
| item | result (run6 mesh in brackets) |
|---|---|
| mitral cap | **529.0 mm² = 5.29 cm²**; flat, normal −z, centre (−0.4, −0.1, −6.5) mm (861 mm², z = −10 mm) |
| cross-section along the axis (cm²) | z = −6.5: 5.29; −5: 5.31; −4: 5.46; −3: 5.89; −2: 6.59; −1: 7.52; 0 (annulus): 8.62; 2: 11.16; 4: 13.71; 6: 16.46; 8: 19.22 (run6 from z = 2 up: 11.11, 13.70, 16.46, 19.23) |
| smoothness near the valve | no step and no grooves (images); largest edge angle about 25°; untouched LA body: 43° |
| separation by angle (30°) | 6 zones: wall, MV cap, 4 PV caps (PV caps unchanged) |
| surface | closed, 0 non-manifold edges, 47 318 triangles, same as the .stl |
| volume mesh | **297 606 tetrahedra**, 0 negative volumes, volume 167.8 mL (172.6) |
| quality | skewness max 0.93, mean 0.24; 3 cells > 0.9, 0 > 0.95 (Ansys "acceptable" < 0.94). minSICN min 0.32 |
| shape away from the valve | unchanged: > 8.5 mm on the LA side, mean 0.00 mm, max 0.38 mm from the original |

## For the Fluent run (run7, not run yet)
- **Mesh and case:** `3_simulation/setup_case_mv53.py`, a copy of `setup_case_mvz.py` with the new .bdf, the cap at (−0.4, −0.1, −6.5) mm and new output names.
  - It imports the mesh, separates and names the zones.
  - It then replaces the mesh in the set-up case, so all settings are kept.
  - Output: `cases/case_mv53_setup_06112026.cas.h5`.
- **Mitral BC:** `3_simulation/boundary_conditions_4cycles_mv53/`.
  - The course velocity curve is scaled to the same cardiac output as run6 (5.0 L/min, 72.9 mL/beat). The factor is now **0.9145**; it was 0.5616 on the 8.6 cm² cap.
  - The peak velocity at the orifice becomes **0.86 m/s**, a normal E-wave (run6: 0.53 m/s).
- **Run:**
  ```
  python 3_simulation/run_cycle.py 350 3_simulation/results/run7_mv53_4cycles 3_simulation/cases/case_mv53_run7_4cycles_DDMMYYYY.cas.h5 3_simulation/cases/case_mv53_setup_06112026.cas.h5 3_simulation/boundary_conditions_4cycles_mv53
  ```
  This takes about 2 h. The Fluent Student licence allows only one session, so check first that no other session is running.

## Reproduce (from the project folder)
```
set PYMESHLAB_PYTHON=<python with pymeshlab>
python 2_mesh/mv_taper_06112026/build_mesh_mv53.py
python 2_mesh/mv_taper_06112026/check_mesh_mv53.py
python 2_mesh/mv_taper_06112026/render_before_after.py
python 2_mesh/mv_taper_06112026/plot_sections.py
```
