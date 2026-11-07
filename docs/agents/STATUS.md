# STATUS (update at end of every session)

Last updated: 07/11/2026

**Hand-in list: [SUBMISSION.md](../../SUBMISSION.md)** (run7 only).


## 07/11/2026: run7 done, post-processed, report and package switched to run7; old results archived
- **run7** (`3_simulation/results/run7_4cycles/`, case `case_run7_4cycles_07112026`): 350 steps, ~20 s per step.
  - **Convergence** (`4_postprocessing/run7/convergence/`):
    - all 350 steps met the criteria, median 27 iterations (17–55);
    - mass balance of the last beat 0.46 mL;
    - beats 3 → 4: mitral 0.08 %, PV 3.1 %.
  - **Physiology:**
    - SV 79.7 mL, CO 5.47 L/min;
    - PV split 29/33/10/29 %;
    - LA 157–168 mL;
    - v_max 1.08 m/s.
    - About 6 mL/s leaves through the MV in systole. This comes from the unscaled course curve, not an error.
  - **Wall:** within 5 mm of the device ECAP is highest (median 0.45 vs 0.16–0.30) and TAWSS lowest. The single highest ECAP patches are on the roof and lower wall, far from the device; the report says so.
  - Details: `4_postprocessing/run7/README.md`.
- **Fixes:**
  - `analyze_cycle.py` now picks `la_wall` by name. run7 exports more surfaces, so block 1 was `pv_2`.
  - `make_paraview_package.py` no longer skips existing files. It had left run6 steps in the package; the stale run6 files were moved to `archive/6_paraview_package_run6/`.
- **Report:** `5_report/main.tex` and `main.pdf` now use run7 (`figures_run7/`): methods, numbers and results text. It is 2 pages + references.
- **Package:** `6_paraview_package/` rebuilt for run7 (1.2 GB) with `convergence/`. `open_in_paraview.py` was tested in pvbatch.
- **Archived** to the git-ignored `archive/*_pre_run7/` and removed from git:
  - run5/run6 meshes, BCs, cases and results;
  - run5/run6 post-processing;
  - the old seg `.nrrd`;
  - `5_report/figures`, `figures_run6`.
- **Still to do (user):**
  - check segmentation v2 in Slicer;
  - the rubric-review report fixes (bib author names, Morales → Sci Rep 2026, hub-artefact sentence);
  - zip and upload `6_paraview_package/`, then put the link in the PDF.

## 06/11/2026 (evening): run7 prepared, NOT run. Decisions applied: PV re-cut, unscaled mitral BC, funnel moves with the valve, segmentation fixes
- **Segmentation v2, the one to hand in:** `1_segmentation/la_v2_06112026/Case3_LA_segmentation_HugoJal_06112026.seg.nrrd` (segment `LA_Case3`; README, `fix_la_segmentation.py`, `qc_la_v2.png`).
  - Device removed: 8 820 → 0 device voxels inside the LA.
  - RIPV and LIPV extended to their first division with threshold + mask (≥ 300 HU, ≤ 10 mm along the lumen).
  - 1-voxel opening: genus 38 → 0.
  - 156.0 mL.
  - **The user should check the vein extensions in Slicer.**
- **run7 mesh** `2_mesh/run7_06112026/` (README). Built from segmentation v2. The PVs could only be re-cut from the segmentation: the old Meshmixer cylinders replaced the vein stubs.
  - **PVs:** cut perpendicular to each trunk before its first branch (`find_pv_cuts.py`: RSPV 48, LSPV 40, RIPV 50, LIPV 40 mm geodesic), each with a 10 mm straight oval extension along the trunk.
    - The old caps were 24–55° off their veins; the new ones are 0–2° off.
    - D_eq: RSPV 17.7, LSPV 13.5, LIPV 13.0, RIPV 8.9 mm.
  - **Mitral valve:** as in mv_taper (5.29 cm² oval, cap at z = −6.5 mm).
  - **Device region:** local Taubin smoothing (the device subtraction left folds).
  - **Checks:** 272 293 tetrahedra; 6 zones at 30°; skewness max 0.941 (0 > 0.95); genus 0; 156.1 mL; atrial wall median 0.04 mm from the run6 surface. Images: `check_run6_vs_run7.png`, `check_mitral_on_ct.png`, `qc_pv_cuts.png`.
  - Several build fixes were needed (decimation, cut snapping, even ring spacing, topological local cuts, crease relax after the remesh). They are documented in the README and docstring.
- **Mitral BC, unscaled:** `3_simulation/boundary_conditions_4cycles_run7/` (`make_mitral_bc.py`): course curve × 1 + valve velocity. SV 79.7 mL, CO 5.47 L/min, peak 0.945 m/s. Replaces the scaled `…_mv53` folder.
- **Fluent set-up:** `3_simulation/setup_case_run7.py`.
  - Zones are named by position; `mv_funnel` is split off as the wall with z < 0 (cell register + `sep-face-zone-mark`).
  - The mesh replaces the run6 set-up case's mesh.
  - New dynamic zone: `mv_funnel` rigid with `mov_bc_c`, like `mitral_valve`.
  - Remeshing lengths 0.15 / 4.5 mm.
  - All steps were tested in scratch sessions.
  - **Motion preview over systole:** the cap travels 8.9 mm, the funnel is rigid, the mesh stays valid (skewness ≤ 0.87), and the LA volume grows by 11.6 mL (run6: 8.4).
- **Not done:** the run7 case files were not written. A PyFluent meshing session, started 21:42 and probably the CoW project, held the Student licence. Next:
  - `python 3_simulation/setup_case_run7.py`, then `run_cycle.py … case_run7_setup_06112026.cas.h5 3_simulation/boundary_conditions_4cycles_run7` (about 2 h);
  - then post-process with the run7 paths;
  - then update the report: methods (segmentation v2, PV cuts, 5.3 cm² mitral valve, unscaled BC, funnel motion) and new figures.
- Superseded and kept for history: `2_mesh/mv_taper_06112026/` (the mitral steps only); `setup_case_mv53.py` and `boundary_conditions_4cycles_mv53/` were removed (never used).

## 06/11/2026: device segmentations reorganised — `1_segmentation/device/` (read its README first)
- The device is an **Amulet-type** occluder. There are three segmentations, each `.seg.nrrd` + `.stl` (LPS mm, closed, manifold):
  - `manual/Device_manual.seg.nrrd`: the user's `Device.seg.nrrd`, renamed with `git mv`. It now has an STL (`make_stl.py`). It is the one used in the model.
  - `gamma/`: v4 (below).
  - `unet/Device_unet_wire.*`.
- Gamma v1–v3, built on the Watchman assumption, are archived in `archive/1_segmentation/gamma_v3_03112026/`. The old→new path map is in `logs/reorganisation_06112026.txt`. Nothing is committed yet.
- Paths updated in `4_postprocessing/analyze_cycle.py`, `thrombus_check/thrombus_check.py`, `ct_wire_figure.py` (which now uses gamma **v4**) and the rubric skill. The gamma script, re-run from its new place, gives a byte-identical result.
- **Open:**
  - report Fig. 1 and `4_postprocessing/paraview/device_gamma_wire_mvz_m.stl` (ParaView anatomy view) are still made from gamma v3; re-run `ct_wire_figure.py` and re-make the mvz STL from v4 if v4 is accepted;
  - the report should name the device "Amulet-type" once in the methods.

## 06/11/2026: device gamma segmentation v4 (Amulet-type) — now in `1_segmentation/device/gamma/` (see its README)
- The user confirms the device is an **Amulet-type** occluder, not a Watchman. The CT agrees: two hubs 11.7 mm apart, a ~28 mm disc, a ~22 mm lobe.
- v4 traces the braided sheets (disc, lobe wall, distal end, braid lines inside the lobe) in cylindrical coordinates around the hub axis. The hubs and the dense bar between them are taken by CT value.
  - Result: `Device_gamma_wire_v4_06112026.seg.nrrd` + `.stl` (LPS mm). 1.94 mL, 94 % inside the manual mask, 14 % of voxels at blood level (manual 58 %). Disc and lobe wall are found in 100 % of 5° sectors.
- Checked and rejected: removing the lobe's inner diagonals and the bar between the hubs as metal streaks. Long-axis CT planes show both at every angle (`qc/explore_long_axis_planes_v4.png`).
- Limits: the disc is patchy where the hub streaks darken the CT; a few spikes remain near the distal hub.
- Not yet used in the report or figures, and not checked by the user in Slicer. The gamma README now says Amulet; the 03/11 "Watchman" notes below are wrong.

## 06/11/2026: mitral outlet narrowed to 5.3 cm² (SUPERSEDED by the run7 entry above; the mitral steps live on in the run7 mesh)
- **Measured.** The run6 mitral cap is **8.61 cm²** (mesh 861 mm²; Fluent output 8.61 cm²). The course asks for 4–6 cm².
- **New mesh** `2_mesh/mv_taper_06112026/` (see its README):
  - **Third version (current).** Above 8 mm over the annulus, the LA is exactly as segmented. From 8 mm down to the annulus, it is rebuilt as a structured polar surface:
    - each section is the original one, blended into its angular low-pass (10 harmonics);
    - this removes a ~1 mm ridge/groove of the segmentation, while the neck area is unchanged (8.62 cm² at the annulus, equal to the CT cut; same as run6 from 2 mm up).
  - **Funnel.** Below the annulus, a C1 Hermite funnel starts with the wall's own slope (47°) and ends on a **convex oval of 5.29 cm²** 5 mm below the annulus. Then come 1.5 mm straight and a flat cap at z = −6.5 mm (was −10 mm).
  - **Earlier tries (user feedback).** Both are kept, and `check_step_before_after.png` and `check_sections.png` compare them.
    - `first_try_step/`: a step at the annulus.
    - `second_try_erase/`: the neck was narrowed by 1.3 cm², and the kidney notch of the annulus ran down the funnel as grooves.
  - **Automatic repairs** after the MeshLab remesh: needle-edge collapse, flip of MV-rim corner-cutting triangles, and in-plane relaxation of the cap.
  - Same frame and transform as run6; 297 606 tetrahedra; 6 zones at 30°; skewness max 0.93 (0 > 0.95).
- **Prepared:**
  - `3_simulation/setup_case_mv53.py` (cap centre (−0.4, −0.1, −6.5) mm);
  - `3_simulation/boundary_conditions_4cycles_mv53/` (cap 529.0 mm²; factor 0.9145, which keeps CO 5.0 L/min and gives a peak orifice velocity of 0.86 m/s).
- **Plan for run7:** [docs/agents/run7_plan_06112026.md](run7_plan_06112026.md), built from the rubric review and the new mesh. Four decisions are needed before running:
  - re-cut the misaligned PV extensions;
  - scaled or unscaled mitral BC;
  - move the funnel with the cap;
  - fold the segmentation fixes into the mesh or not.
- **Next.** Run7 is only on the user's go:
  - run `setup_case_mv53.py`, then `run_cycle.py` (command in the mesh README; about 2 h);
  - then re-run the post-processing with `PV_RUN=run7` and update the report;
  - the report still describes run6 (10 mm extension, scaled to 0.56).

## 06/11/2026 — adversarial rubric-review skill
- Deadline confirmed: **20/11/2026 23:59**. The full rubric (incl. criterion 5, device segmentation, +1) is now in `.claude/skills/rubric-adversary/references/rubric.md`.
- New skill `/rubric-adversary` (`.claude/skills/rubric-adversary/`): deterministic checks (`scripts/deliverable_checks.py`, read-only) → one strict "examiner" subagent per criterion → a defence pass that tries to refute each finding → dated scorecard in `docs/agents/reviews/`. Arguments: a criterion number, or `quick` (no subagents).
- First run of the checks (no full review yet) already shows things to look at:
  - `Hugo_Jal_left_atrium_segmentation.nrrd` has no case id in its name; `HugoJal_Case3_stl.seg.nrrd` has, but it differs (188.6 vs 155.7 mL, 18 components).
  - ~17 % of `Device.seg.nrrd` voxels fall inside the LA mask; `Device.seg.nrrd` has 15 islands < 50 voxels; no STL of the manual device in `1_segmentation/`.
  - Old LA STLs give 18 regions at 30° (only the mvz mesh gives exactly 6).
- **Full review done:** [reviews/rubric_review_06112026.md](reviews/rubric_review_06112026.md).
  - Mock score about 8.0/10 likely (7.3 if graded harshly), plus about 0.7 for the device.
  - Blocking:
    - share the 1.2 GB ParaView package by a tested link;
    - do NOT hand in the manual `Device.seg.nrrd` as the device (it is a solid plug); hand in the gamma or U-Net STL;
    - hand in case-named copies.
  - Fix plan: about 2.5 h, no Fluent needed.
  - Nothing in the deliverables was changed.
- **Correction (device type):** the CT shows an **Amulet-type** device. Evidence: two hubs 11.7 mm apart, a ~28 mm disc, a waist and a ~22–24 mm lobe. The "Watchman FLX" in the 03/11 entry below and in `1_segmentation/gamma_experiment/README.md` is wrong, unless the user has a clinical record saying otherwise.
- **Correction (veins):** R sup and L sup reach their first division. L inf stops about 5 mm short of its main split, R inf about 7–8 mm short. The 31/10 entry ("≈ first branch for all four") was too optimistic.

## 04/11/2026 (afternoon) — report switched to run6, device removed from result figures, ParaView package
- **Report** (`5_report/main.tex`, figures in `5_report/figures_run6/`): now uses run6; still 2 pages + references.
  - The previous run5 version is kept in `archive/5_report_run5_01112026/` (and in git).
  - Two new verified references: Kawel-Boehm 2020 (PMID 33308262) for the flow scaling; Morales 2025 (arXiv:2505.09746) for Q = 500.
- **Figures.** User feedback: the device must appear only in Fig. 1.
  - Fig. 1 = (a) gamma CT en-face on the device disc with the wire segmentation; (b) CT along the device axis with the LA and wire outlines (blood reaches the face); (c) transparent LA model + wire device. Made by `4_postprocessing/ct_wire_figure.py` and `pv_figures.py anatomy` (with `PV_TRANSFORM`).
  - `pv_figures.py`: the device is off by default (`PV_DEVICE=1` to show it). `PV_VMAX_PEAK=0.6` for run6. The run6 slice is the long-axis plane through the mitral axis and the device.
  - **Bug fixed:** the 2nd ECAP view was double-log-scaled (shared lookup table). Old Fig. 2d (run5) had wrong colours.
- **ParaView package** `6_paraview_package/` (course criterion 3), built by `4_postprocessing/make_paraview_package.py`:
  - last heartbeat EnSight + `.encas`, final Fluent case/data, wall metrics `.vtp`, LA/device STLs, `flows.csv`;
  - `open_in_paraview.py` (tested in pvbatch), `README.md`;
  - the data (1.2 GB) is git-ignored; README + script are tracked.
- **U-Net in the report** (user: the professor gives extra credit for it). Fig. 1 is now 5 panels:
  - (a) U-Net device (`unet_experiment/Device_unet_wire.seg.nrrd`) on the disc plane, plain CT 0–1500 HU; (b) its 3D model, display-smoothed in ParaView only;
  - (c) gamma CT + wire; (d) CT along the axis + LA + wire; (e) LA + wire 3D;
  - a methods paragraph, plus the reference Isensee 2025, nnInteractive (arXiv:2503.08373, verified);
  - U-Net vs others: 2.50 mL, 97 % inside the manual mask, Dice 0.65 vs manual and 0.57 vs gamma.
  - The U-Net model is also in the ParaView package (`surfaces/device_unet.stl`).
- Still 2 pages + references. Not committed yet.

## 04/11/2026 — run6 on the new mesh (DONE; see `4_postprocessing/run6/README.md`)
- **Run.** Finished 12:36, 350/350, with no errors.
  - Final case: `cases/case_mvz_run6_4cycles_04112026.cas.h5`.
  - Analysed: `4_postprocessing/run6/` (results.npz, report_numbers.json, figures/).
  - Comparison: `4_postprocessing/compare_run5_run6.json`.
- **Physiology (beat 4).**
  - SV 72.9 mL, CO 5.0 L/min (run5: 46 mL, 3.2 L/min); mitral backflow 0.4 mL.
  - PV split 20/28/20/31 %.
  - Max |u| at E-peak 0.57 m/s (run5: 1.72 m/s jet from the narrow mitral zone).
  - Per-beat SV and PV volumes are periodic in beats 3–4.
- **Wall.** The 0–5 mm device ring is still the worst band, but the values are milder:
  - ECAP median 1.02 (run5 3.50); TAWSS 0.21 Pa (0.09); 19 % of the ring has ECAP > 2 (89 %).
  - 48 % of the ECAP > 2 area lies within 20 mm of the device (20 % of the wall).
  - Conclusion holds qualitatively; magnitude depends on the inflow.
- Report switched to run6 the same afternoon (see above).

- **Case.** `3_simulation/cases/case_mvz_setup_04112026.cas.h5`, built by `3_simulation/setup_case_mvz.py`:
  - imports the new .bdf, scales to mm, separates by angle at 30° → exactly 6 zones;
  - names the caps by position (same names as the old caps);
  - `/mesh/replace` into the old set-up case, so all settings are kept;
  - remeshing lengths 0.3 / 4.5 mm.
- **Mitral BC** (`3_simulation/boundary_conditions_4cycles_mvz/`, see `scale_mitral_velocity.py` and `scaling.json`):
  - The course velocity × 0.5616, so that CO = 5.0 L/min (SV 72.9 mL, HR 68.6). Reference: Kawel-Boehm 2020, CMR normal values. Unscaled on the 861 mm² annulus it would be 130 mL/beat and 8.9 L/min.
  - **Plus the annulus velocity dz/dt**, so the flux through the moving cap = the scaled profile. Without it, the receding cap pulled ~8 mL into the LA in systole through the "closed" valve; found in the 5-step smoke test.
  - Pressure and motion profiles unchanged.
- **Run.**
  - Command: `run_cycle.py 350 3_simulation/results/run6_mvz_4cycles 3_simulation/cases/case_mvz_run6_4cycles_04112026.cas.h5 <setup case> <BC mvz>`
  - Log: `logs/run6.out`. Started 10:43, ~28 s/step.
  - Check: the MV cap moves exactly along −z.
- **Post-processing prepared.**
  - `analyze_cycle.py` (env `MODEL_TRANSFORM`); `report_quant.py [run] [fig_dir]`; `make_wall_vtp.py <run>`; `compare_runs.py`.
  - `pv_figures.py` env: `PV_RUN`, `PV_RESULTS`, `PV_OUT`, `PV_Q`, `PV_TRANSFORM`.
  - `paraview/device_frame_mvz_m.stl` = device in the model frame.
- **Q-criterion.** Main isovalue now 500 1/s² (Morales et al. 2025, arXiv:2505.09746, LA 4D flow; results consistent for Q > 100), plus 250/700 for sensitivity. The old 4000 kept only fragments. run5 re-rendered in `4_postprocessing/run5/figures_q/`; the report figure is untouched.

## 04/11/2026 — New mesh: mitral cut on the CT annulus, z along the valve axis (`2_mesh/mv_aligned_03112026/`, see its README)
- **Why.** The MV is a rigid body moved by `motion.prof`, which holds a z displacement only (down to **−8.9 mm** at 0.35 s). The old MV cap was 73° off z, so in run5 the valve slid ~8.5 mm in its own plane. This is a limitation of run5 and should be mentioned.
- **Annulus.** Fitted on the CT from the AV-groove notch tips in radial planes:
  - centre (22.1, −168.4, 857.1) LPS, axis (0.666, −0.720, −0.194) LA→LV, radius ~18.5 mm;
  - the old cap was 12° tilted and ~6.7 mm inside the LV.
- **New surface/volume.**
  - Cut at the annulus plane; 10 mm extrusion of the outline; flat cap; junction smoothed ±4 mm; 13 isolated creases relaxed.
  - Rotated so that the annulus centre is the origin and **−z = LA→LV** (sign chosen so the negative systolic displacement moves the annulus towards the LV; flip 180° about x if the user wants +z).
  - MeshLab isotropic remesh (pymeshlab, installed only in a scratch venv; `PYMESHLAB_PYTHON`), then Gmsh tetrahedra on that surface.
- **Results.**
  - 307,927 tetrahedra, skewness max 0.885 (old: 393,557, max 1.00, 253 > 0.9); no negative volumes.
  - 49,032 surface triangles, closed and manifold.
  - 30° angle separation gives exactly wall + MV cap (−z, 33 mm) + 4 PV caps.
  - Away from the valve the surface is unchanged (max 0.38 mm).
- **Open.**
  - The MV cap area doubled (862 vs ~420 mm²). The MV BC is a velocity, so the flow per beat roughly doubles: check, and decide whether to scale `velocity_outlet.prof`.
  - The Fluent case must be rebuilt on the new mesh (not done).
  - Results are in the model frame: map back with `transform_LPS_to_model.json`.
  - The cut outline is ~2.3 mm inside the CT hinge points (segmentation).
  - Committed and pushed 04/11/2026.

## 03/11/2026 — GitHub repo + device re-segmented with a gamma transform + thrombus check
- **Thrombus check** (`4_postprocessing/thrombus_check/`, see its README). Method: CT shown with a thrombus window ([-100, 700] HU, gamma 1.5); low-density search in front of the device face; density profiles.
  - **Result: no DRT visible.** Blood reaches the face directly: 5th percentile 321 HU, 0.1 % < 250 HU in the first 3 mm. The only low-density pieces are the metal streak beside the hub (thin band along one line, 252 mm³) and a 51 mm³ partial-volume sliver at the rim/wall.
  - Limitation: metal streaks hide the first 1–2 mm around the hub.
  - The report already says no thrombus is visible, so no figure was added (the user wanted one only if a thrombus was found). Committed and pushed 03/11/2026 (b7a76db).
- Repo: github.com/hugojal/DRT_LAAO_Analysis (`main`, first commit 01/11/2026). The user is the **only author**: no Co-Authored-By or Claude lines in commits or PRs. The Slicer `.mrml` scenes are git-ignored because they contain DICOM metadata (birth date, study IDs).
- **Layout of `1_segmentation/`** (set by the user): device segmentations kept are only:
  - the manual `Device.seg.nrrd` (used in the model);
  - `unet_experiment/Device_unet_wire.seg.nrrd` + `.stl`: the version the user saved from Slicer on 31/10, which differs from the automatic output by 5 425 voxels;
  - `gamma_experiment/` = v3 below.

  gamma v1/v2 and the exploration images are in `archive/1_segmentation/gamma_v1_v2_03112026/`. Committed and pushed 03/11/2026.
- v1, in `device_gamma_03112026/` (since moved; see above): wire frame from gamma 0.6 → top-hat 2.5 mm → hysteresis 0.16/0.30 inside the device cylinder. No neural network. 2.34 mL vs 5.02 mL for the manual mask; 92 % lies inside the manual mask; Dice 0.58. The disc, waist and hollow lobe are visible. Hub streak bars remain to be erased.
- **v3 (current)**, after user feedback that v2 was solid in one part and open in another. Pipeline: gamma 0.3 → Sato ridge filter (0.75–1.5 vox) → v2 allowed region → keep voxels ≥ 50 % of the local ridge max within 1.5 mm → hysteresis at the 60/85 percentiles. Result: an even strut lattice on face and wall (fill 12–27 % / 8–29 % per 45° sector, vs 25–81 % / 17–63 % in v2), complete rim ring, 1.26 mL, 97 % inside the manual mask. Outputs: `Device_gamma_wire_v3_03112026.seg.nrrd`/`.stl`; iteration images `iter*.png`.
- v2, after user feedback: the device is a **Watchman** (FLX type, ~27 mm). Settings: gamma 0.3; an axisymmetric shape prior from the angle-averaged (axial, radius) map; envelope = manual mask dilated 1.5 mm; hysteresis 0.30/0.50. The antennae are gone and the base rim is found in 100 % of 5° sectors. 2.60 mL; 96 % inside the manual mask; Dice 0.65. Outputs: `Device_gamma_wire_v2_03112026.seg.nrrd`/`.stl`.
- **Not used yet** in the mesh, figures or report (these still use the manual `Device.seg.nrrd`). Note: older notes (and the archived U-Net README) call the device an Amulet; the user says it is a Watchman.

## 01/11/2026 — Report v5 + folder reorganisation (read this first)
- **Folder:** everything for this project now lives in `MOs/DRT_LAAO_Case3/` (future GitHub repo: `README.md`, `.gitignore`). Old → new path map: `logs/reorganisation_01112026.txt`. **The log below this entry uses the OLD paths** (`L1/` → `1_segmentation/`, `L2/` → `2_mesh/`, `L3/mesh/HugoJal_Case3_gmsh.bdf` → `2_mesh/`, `L3/BC*` → `3_simulation/boundary_conditions*`, `L3/cases|results` → `3_simulation/…` (only the v3 set-up and run5 kept; the rest in `archive/`), `postproc/` → `4_postprocessing/` (kept scripts only), `report/latex/` → `5_report/`, `Case_003/` → `data/Case_003/`, `mcp/*.py` → `tools/fluent_mcp/`). Superseded material (run2/run4, old meshes, U-Net and v2 segmentation attempts, quick-look figures, reportlab/docx reports, unused ParaView figures) is in `archive/` (git-ignored), nothing deleted. `MOs/mcp/.venv` stays outside (shared with the CoW project, which was running Fluent from it during this session). Root `fluent-*.trn` files belong to the CoW project and were left in `MOs/`.
- Scripts now use paths relative to the project folder (`ROOT` = parent of the script's folder). Fixed a latent bug in `pv_figures.py` (anatomy mode: `la` was hidden in a comment); the anatomy mode was re-run from the new location. Unused overview/device-hull renders removed from it.
- **Report v5** (`5_report/main.pdf`, 2 pages + 1 page references), per user feedback: third-year level, qualitative descriptions driven by the figures, no CT voxel size or HU values, no Table 1 (Fig. 4 boxplots kept), RRT dropped, 4 references (Dukkipati2018, Korsholm2019, Zhong2024, Vogl2024; Iriart2023 and Mutlu2023 removed). Methods corrected: LA = **manual thresholding, then manual paint/erase with the threshold range as mask** (NOT region growing); device = **manual segmentation**. Date 01/11/2026.
- Open: the user should check the methods wording against what they did in Slicer/MeshLab/Meshmixer; Fig. 3 colour-bar titles are partly hidden behind the model in the device views.

## Done (per user / files on disk)
- [x] L1 — LA segmentation, device segmentation (`L1/`)
- [x] L2 — surface STL and volumetric BDF (`L2/HugoJal_Case3_gmsh.bdf`, copied to `L3/`)
- [x] Project setup: agent docs, `ansys-fluent` MCP (venv), `.mcp.json`
- [x] **Case verified by the agent (read-only, no-GUI PyFluent launch, 16/10/2026)** on `L3/cases/fluent_before_dynamicmesh.cas.h5` (this file was *overwritten* by the user's save at 15:58 and now contains the dynamic-mesh setup despite its name; `case_dm_16102026.cas.h5` was never created):
  - OK: transient; laminar; blood ρ=1060, μ=0.0035 on `fluid-1`; 4 pressure inlets with profile `function_pressure_c`; MV (`default_exterior-1.82`) velocity inlet with profile `velocity_bc_c`; wall `default_exterior-1`.
  - OK: dynamic mesh enabled; smoothing spring; zones: PVs `…1.83–1.86` stationary, MV `…1.82` rigid-body with `mov_bc_c`, `default_interior-1` and `default_exterior-1` deforming (remeshing + spring).

## Fixes applied by agent (16/10/2026, no-GUI session) → `L3/cases/case_dm_fixed_16102026.cas.h5` (new file; originals untouched; calculation NOT run)
- Remeshing `length_min = 2.0e-4 m`, `length_max = 3.5e-3 m` — **estimated** from mesh-check stats (min/max face area 1.1e-8 / 4.0e-6 m², cell volume 1.7e-12 / 2.1e-9 m³), not from the GUI Mesh Scale Info button: compare with it and adjust.
- Pressure–velocity coupling **Coupled**, gradient **Green-Gauss Node Based**, transient **2nd order**, continuity criterion **0.005**.
- Mesh facts: 393,557 tets, extents ≈ 94 mm (mm scaling OK), 1 velocity-inlet + 4 pressure-inlet zones.
- Still open: remeshing interval (5–10, not set — TUI path not found), unified-remeshing checkbox left as is (it is not the same as the remeshing *method*, so item 2 below may be a non-issue), zone renaming, initialization, EnSight export, `.prof` coverage to 0.85 s.

## Latest case: `L3/cases/case_dm_v3_16102026.cas.h5` (agent, 16/10/2026, 16:24) — USE THIS ONE
- The user's GUI save `case_dm_fixed_16102026.cas.h5` had the mesh **scaled twice (1000× too small)**; agent applied `/mesh/scale 1000 1000 1000` → extents back to x −0.0594…0.0359 m, y −0.1809…−0.1060 m, z 0.8322…0.9169 m. Never click *Scale* in the GUI again on this case.
- Zones renamed: `mitral_valve` (82), `pv_1…pv_4` (83–86), `la_wall` (zone 1); dynamic-zone and BC assignments follow the new names (verified).
- Remeshing interval: **no TUI/settings path exists in 26.1** (`remeshing_parameters` has only cell/face skew, length min/max, retain size distribution, prism/sizing controls, unified_remeshing). Treat step 19's interval as not applicable unless the GUI shows one.
- Do not use the third-party `knewnothing-git/ansys-mcp-server` repo (unvetted code); the local `mcp/` server covers the same need.
- Use no-GUI PyFluent sessions only when the user's Fluent GUI is closed (Student licence: concurrent sessions fail to start).

## Motion preview (agent, 16/10/2026, on `case_dm_v3_16102026.cas.h5`, 2 cores, no GUI)
- Ran 47 of 85 preview steps (dt 0.01) in ~9.5 min (~12 s/step for mesh motion alone) before the agent's own timeout killed it; no negative volumes (min volume 4e-13…1.8e-12 m³), no errors.
- **Maximum cell skewness is ≈0.9994–0.9997 from step 1 on and does not improve** (face skew 0.999) → the initial Gmsh mesh already has near-degenerate cells and remeshing (threshold 0.9) is not removing them. Check `/mesh/quality` on the original mesh; consider re-meshing in Gmsh/Netgen before the full run.
- Not saved: initialized/preview state (no `case_dm_v4…`). EnSight Case Gold automatic export NOT set up: settings API `automatic_exports` offers only ascii/cgns/visualize(DVS)/mapdl/nastran/tecplot; legacy TUI `/file/transient-export/ensight-gold-transient` exists but its prompt order is unknown — set it in the GUI (Calculation Activities) or find the prompt sequence.
- Cost warning: full run = 85 steps × ≤200 iterations on 393k cells with remeshing; expect hours on 2–4 cores.

## Mesh quality audit (agent, 16/10/2026; `L3/mesh/HugoJal_Case3_gmsh.bdf`, 393,557 tets, 78,988 nodes, no inverted cells)
- Independent numpy calculation from the BDF (script was in session scratchpad, not kept): **equivolume skewness** (the quantity Fluent prints as "Maximum Cell Skew") min 0.001, mean 0.245, max 0.99999; cells > 0.8: 1,409 · > 0.9: 253 · > 0.95: 99 · > 0.99: 30 · > 0.999: 14 (0.06 % of cells at most). Histogram 0–0.25: 240,146 · 0.25–0.5: 123,334 · 0.5–0.75: 27,176 · 0.75–0.9: 2,648 · 0.9–0.95: 154 · 0.95–0.99: 69 · >0.99: 30. Equiangle skew max only 0.969 (17 cells > 0.9) → the bad cells are flat **slivers** (angles ≈2° and 176°).
- Fluent `/mesh/quality` (same result for BDF import in single/double precision and for the checkpoint): **min orthogonal quality 7.0e-6** at (−8.488e-3, −0.1790, 0.8624) m = one sliver (vol 4e-3 mm³), warning "<0.01". The agent's own orthogonal-quality estimate (min 0.046) did NOT reproduce this — do not quote it; the full OQ distribution still has to be read from Fluent.
- Hence the preview's max skew 0.9997 from step 1 is **inherited from the original mesh**, not created by the motion, and it is independent of remeshing length scales (tested: remeshing off and lengths 1e-4/5e-3 give the same). Remeshing (threshold 0.9) does not remove these cells.
- Recommended fix (in order): (1) try Fluent's mesh repair/improve-quality tools on the ~100 cells > 0.95 (TUI path under `/mesh/repair-improve/`, unverified); (2) otherwise re-run Gmsh 3D with Netgen optimisation (+ Mesh.Optimize, 3D smoothing) and re-check; keep < 500k cells; (3) before a full run, test a short run (5–10 steps) with Coupled solver.

## Fluent mesh-improve attempt (agent, 16/10/2026) — did NOT fix the worst cell
- `/mesh/repair-improve/improve-quality` on `case_dm_v3` processed ~400 cells (worst 0.1 %, OQ < 0.139) but **min orthogonal quality stayed 7.008e-6** at (−8.488e-3, −0.1790, 0.8624) m and max aspect ratio stayed 127.5; max cell volume 2.09e-9 → 1.82e-9 m³. Saved as `L3/cases/case_dm_v5_improved_16102026.cas.h5` (marginal change; not recommended over v3 unless you want it).
- Repeating it 3× with `allow-repair-at-boundaries yes` made it **worse**: max aspect ratio 127 → 162 → 188 → 204, worst cell unchanged (that attempt was discarded, file deleted). `repair` found no poor elements. Don't repeat.
- Conclusion: regenerate the volumetric mesh in Gmsh (Netgen optimisation, 3D smoothing; inspect Tools > Statistics / quality plots for SICN/gamma) and re-check with Fluent `/mesh/quality` (target min OQ > 0.01–0.05, ideally > 0.1; fewer than ~10 cells with equivolume skew > 0.95). Alternative: accept the 99 cells > 0.95 and do a short 5–10 step test with Coupled to see whether it converges.

## Gmsh regeneration (user, 16/10/2026 20:12) → `L3/mesh/HugoJal_Case3_gmsh_v2.bdf` (copy of the file Gmsh wrote over `L2/HugoJal_Case3_gmsh.bdf`; `L3/mesh/HugoJal_Case3_gmsh.bdf` is still the original)
- 78,648 nodes, 391,600 tets. Gmsh SICN avg 0.874 (min 0.0103), Gamma avg 0.853 (min 1.7e-4).
- Agent equivolume skew: **103 cells > 0.95 (original: 99)**, 38 > 0.98, 9 > 0.999, max 1.0 → **no improvement**.
- **All 103 slivers have 3 of 4 nodes on the boundary** (flat tets lying on the wall), scattered in 84 clusters of ≤4 cells across the whole wall (median vol 0.05 mm³ vs 0.44 mm³) → cause is the surface triangulation/curvature at the wall, not one local defect. Fix must act on the surface mesh (Meshmixer remesh at regularity 100 %, similar element size, then Gmsh with another 3D algorithm: Frontal-Delaunay or HXT) or be accepted.
- Fluent setup was NOT rebuilt on v2 (no gain); keep using `L3/cases/case_dm_v3_16102026.cas.h5`.

## 5-step test run (agent, 16/10/2026 20:16–20:18, no-GUI, 4 cores) on `case_dm_v3`, Coupled, dt 0.01, ≤200 it/step
- **Did not diverge.** 5/5 time steps finished in 88 s; each step reported "solution is converged" (~33, 33, 38, 46, 55 iterations; final continuity ≈ 1e-3–2e-3, velocities ≈ 7e-4–9e-4). (Correction 16/10/2026: the iteration numbers above were the cumulative counter, not per-step; real per-step counts are ~5–13.)
- No negative-volume or remeshing errors in the solver transcript, but the solver does not print cell skew; the 103/99 sliver cells (>0.95 skew) did not break the preview or the 5 steps.
- **Reversed flow at the 4 pressure inlets** (PVs): 10–25 % of face area early in each step, up to ≈ 70 % mid-iteration, ≈ 11 % at the end of step 5. Not a crash, but consider the backflow direction/pressure profile (gauge vs absolute) and whether the profile values (≈ 810–830 Pa) are meant as gauge total pressure.
- Not saved: no data/case written from this test. Full 85-step run and EnSight export still pending (EnSight Case Gold has no settings-API object in 26.1; automatic export has only DVS "visualize").

## Full 85-step run (agent, 16/10/2026 20:21–20:38, 17 min, 4 cores) → `L3/cases/case_dm_v3_run85_16102026.cas.h5` + `.dat.h5` (final state t = 0.85 s only; plus two `-sf-*.sf` files)
- Finished 85/85 steps, flow time 0.85 s, **85 "converged" messages, 0 divergence / negative-volume / error lines**. 564 iterations total, mean 6.6 per step (step 1: 20, max thereafter 13, falling to ~3 at the end). Final continuity ≤ 0.005 on every step except step 1 (7.8e-3); velocities ~1e-4–4e-3.
- **Reversed flow at the PV pressure inlets is large and intermittent**: peak 95 % of inlet area at step 1, 0 % around steps 41–51, back up to 82–93 % at steps 61–85. Treat the physics as suspect (inlet pressure profile gauge/absolute reference, backflow direction, flow reversing at the end of the cycle) before drawing DRT conclusions.
- **No time history was saved** (EnSight export skipped; settings API has no EnSight Case Gold, TUI `/file/transient-export/ensight-gold-transient` prompt order unknown). Only the final step is in the `.dat.h5`; the whole-cycle results (WSS, velocity, Q-criterion…) require re-running with an export enabled — the run is only ~17 min.

## Backflow investigation (agent, 16/10/2026; read-only, nothing run)
- BCs as set: PVs `pv_1…pv_4` pressure inlet, **gauge total pressure** from `function_pressure_c` (673–1126 Pa, operating pressure 101325 Pa), direction *Normal to Boundary*, `prevent_reverse_flow = false`, absolute frame. MV velocity inlet, *Magnitude, Normal to Boundary*, `velocity_bc_c` always **negative** (−0.0104 … −0.945 m/s) = outflow through the MV, as intended by the slides. Profiles span t = 0–1.75 s; run used 0–0.85 s. MV rigid-body z-displacement −8.9 mm max (t ≈ 0.35 s).
- The reversed flow tracks the MV outflow: 0 % at t ≈ 0.4–0.5 s (MV outflow 0.5–0.85 m/s, PVs forced forward) and 80–95 % at t ≥ 0.6 s (MV outflow only 0.01–0.04 m/s). The cavity is almost closed then, so net PV inflow ≈ 0 (blood is incompressible) while all four PVs impose the same pressure → each PV face has part of its area in, part out. This is a **consequence of the BC set, not a solver fault**; do not set `prevent_reverse_flow` (it would distort the physics).
- Likely start-up shock: flow initialised at 0 Pa gauge while PVs impose ≈ 809 Pa at t = 0 (step 1: 20 iterations, continuity 7.8e-3, 95 % reversed).
- Recommended changes before re-run: (1) initial gauge pressure ≈ 809.4 Pa (= profile at t = 0); (2) add per-step surface report definitions (mass flow of pv_1…pv_4 and mitral_valve, area-weighted pressure) written to a report file, to verify ΣQ_PV ≈ Q_MV + dV/dt and quantify the backflow; (3) save results every step or every 2nd step: per-step `file.export.ensight_gold(file_name, quantities)` (settings API; `quantities` names to be checked) because no automatic EnSight Gold export exists; budget ~2–3 GB for every step. (4) physics caveat for the report: with identical pressure at all PVs the PV flow split is symmetric by BC, not by anatomy.

## Re-run with exports (agent, 16/10/2026 20:48–21:21, 33 min, 4 cores) — CURRENT RESULTS
- Setup: `case_dm_v3_16102026.cas.h5`, init pressure 809.42 Pa gauge, dt 0.01 s × 85 (t = 0.85 s), ≤ 200 it/step, one step at a time. Script (not kept in repo) wrote EnSight Gold (binary, node-based, fluid-1) every step.
- Outputs: **`L3/results/run2/step_001…step_085.encas`** (+ `.geo/.scl1-15/.vel`; 1.6 GB; moving mesh → geometry per step; fields: pressure, absolute-pressure, total-pressure, velocity magnitude & x/y/z, vorticity-mag, q-criterion (normalized), lambda2, wall shear (mag, x, y, z), strain rate), `L3/results/run2/flows.csv` (mass flow at pv_1…pv_4, mitral_valve, LA volume per step), final `L3/cases/case_dm_v3_run2_16102026.cas.h5/.dat.h5`. Earlier `L3/cases/case_dm_v3_run85_*` run (init 0 Pa, no exports) superseded.
- **Mass conservation verified**: Σ(PV) + MV vs ρ·dV/dt of the deforming LA: correlation 0.98, residual 0.3 % of peak MV flow (0.31 kg/s at t ≈ 0.4 s). LA volume 167.3–168.6 mL·1e-3 ... i.e. 1.6734–1.6863e-4 m³ (±0.4 %).
- Flow pattern: PVs supply 5e-3 kg/s while MV ≈ closed (t < 0.3 s), MV outflow peaks 0.30 kg/s at t ≈ 0.41 s, then closes again; from step 57 on pv_3 has **net outflow** (−1 to −2.7e-3 kg/s) while pv_2 carries ~10e-3 → asymmetric PV split despite identical imposed pressure (geometry-driven).
- Still missing for the report: EnSight/ParaView post-processing (stagnation/low-velocity volume near LAA and device, TAWSS/OSI from wall shear series, Q-criterion), judgement on the **device** (the device segmentation `L1/Device.seg.nrrd` is NOT part of this CFD domain — the LA mesh has no occluder; check whether the lab expects a device-in-LA mesh), YES/NO DRT conclusion.

## Post-processing (agent, 16/10/2026) — `postproc/compute.py` → `postproc/results.npz`; `postproc/figures.py` → `figures/01…06_*.png` (uses `mcp/.venv` with pyvista, matplotlib, scipy, pynrrd; run with VTK `vtkEnSightGoldBinaryReader`, forward-slash paths)
- ROI = fluid / wall within 10 mm (20 mm) of the device segmentation (`L1/Device.seg.nrrd`; same LPS frame as the mesh; device centroid ≈ (26, −157, 897) mm; device lies at the LA edge, the mesh has no LAA/device). ROI volume 7.9 mL (10 mm), 27 mL (20 mm) of 167 mL.
- Stagnation (volume fraction below threshold, time-average over 0.85 s; whole LA / ROI 10 mm / ROI 20 mm): <1 cm/s 41/47/41 %; <2.5 cm/s 56/71/59 %; <5 cm/s 70/87/75 %. ROI reaches 100 % for t < 0.28 s (MV nearly closed, PV inflow only ≈ 5 g/s) and ≈ 34 % (<5 cm/s) at the E-wave peak t ≈ 0.41 s, then climbs again; mean |u| in ROI10 averages 2.0 cm/s, min 0.10 cm/s at t = 0.16 s.
- Wall (nearest-neighbour map of WSS onto the step-1 wall; mean/max mapping distance 3.1/6.3 mm → TAWSS/OSI are approximate, esp. near the moving MV): TAWSS whole-wall mean 0.32 Pa (median 0.23, p95 0.75); near device (10 mm) 0.12 Pa vs 0.34 Pa elsewhere; OSI 0.28 vs 0.19; RRT median 21.9 vs 7.1 1/Pa.
- Caveats for the report: the BC data give strong flow only at 0.3–0.55 s; the LA volume changes ≈ 0.7 % (only MV rigid motion deforms it); the PV pressure is identical at all 4 PVs; remeshing grew the mesh from 393k to ≈ 500k tets at step 1; the mesh has no device. No DRT conclusion drawn yet.

## Reorganisation (agent, 19/10/2026)
- 44 Fluent transcripts/log moved from the project root and `L3/` to `logs/fluent/` (nothing deleted); new no-GUI sessions now start in `logs/fluent/` so the root stays clean. `L3/` now has `mesh/`, `cases/`, `BC/`, `results/run2/`; all path references in docs and `postproc/` updated (older STATUS entries use the new paths).
- ParaView: `L3/results/run2/all_steps.encas` (85-step transient, verified readable with the VTK EnSight reader), `postproc/paraview/*.vtp`; see `05-paraview.md`. ParaView itself is not installed on this machine.

## Number of time steps — professor: infer it from the boundary conditions (20/10/2026)
- `pressure_inlet.prof` and `velocity_outlet.prof` are **periodic with T ≈ 0.88 s** (the 1.75 s / 176-sample files hold two cycles; pressure repeats at lag 0.88 s with 0.4 % mismatch). Sampling is dt = 0.01 s → **≈ 88 steps per cycle, 175 steps for the two cycles in the files**. The earlier 85-step run (0.85 s) was slightly **less than one cycle** and a first cycle includes start-up transients; analysis should use a later cycle (e.g. run 2 cycles, post-process the 2nd).
- `motion.prof` (MV z-displacement) is **not periodic** (ends at −1.0 mm instead of 0; first/second half differ by ≈ 25 %) — decide with the professor how the second cycle's wall motion should be treated.
- Unverified: the last number in each `.prof` header (`… 2 176 0`) may be Fluent's "periodic" flag (0 = not periodic); check the Fluent docs for `read-transient-table` before relying on it to repeat the cycle beyond t = 1.75 s.

## Tutorial pipe (agent, 20/10/2026) — `tutorial/README.md`
- Straight pipe D 4 mm × L 100 mm, 44,874 tets, blood. Stage 1 steady converged in 168 iterations: inlet pressure 79.9 Pa, mean WSS 0.77 Pa (Poiseuille 70 Pa / 0.70 Pa; excess = entrance region). Stage 2 (dynamic mesh: rigid-body inlet from profile, deforming wall/interior, spring + local-cell remeshing) and stage 3 (pulsatile inlet from profile, 0.1405 m/s at t = 0.12 s as expected) each ran 12 steps OK; continuity criterion 0.005 needed.
- Finding: rigid-body motion profile column `z` = **displacement [m]**. Professor: derive step count from BCs → one period of profiles (T = 0.8 s pipe / ≈ 0.88 s atrium) at dt = 0.01 s.
- The user asked for a basic assignment (flow inlet → outlet); no brief received yet — this pipe stands in for it.

## 4-cycle run (agent, started 20/10/2026 14:0x) — `postproc/run_cycle.py 350 …`
- Professor: at least two cycles. The BC files hold 2 cycles (1.75 s); extended to **4 cycles / 3.5 s / 350 steps** in new files `L3/BC_4cycles/*.prof` (originals untouched). Rules: pressure and velocity = the 1.75 s block repeated (end value equals start value, joint is seamless); motion = original data for t ≤ 1.75 s, then block-2 = −1.013 mm offset + the detrended block (original minus its linear drift), i.e. continuous at t = 1.75 s and **periodic with no accumulating drift** afterwards (shape differs from block 1 by at most 1.0 mm). State this rule in the report; ask the professor if it is acceptable.
- Output: `L3/results/run4_4cycles/` (EnSight per step, `flows.csv`, `all_steps.encas`), final case `L3/cases/case_dm_v3_run4_4cycles_20102026.cas.h5`, partial case every 25 steps (`…_partial.cas.h5`). Log: `logs/run4.out`. Expected ≈ 2.5 h; aborted earlier attempt (175 steps) discarded.
- Analysis plan: use the last full cycle(s) (e.g. t = 2.625–3.5 s) for TAWSS/OSI/stagnation; compare cycles 3 and 4 to show periodicity.

## BUG FOUND 20/10/2026 — iteration cap was silently 20, not 200
- PyFluent `dual_time_iterate(..., iter_count=N)` **ignores** `iter_count` (warning only in stderr: "Unknown keyword 'iter_count'"); the correct argument is **`max_iter_per_step`**. All agent runs (run85, run2, run4 and the pipe tests) therefore used Fluent's default of **20 iterations per time step**. Fixed in `postproc/run_cycle.py` and `tutorial/pipe/stage2_dynamic.py`.
- Impact in run4 (4 cycles): 224 of 350 steps stopped at the cap, 154 "converged"; end-of-step continuity residual up to 0.0234 (step 170) vs criterion 0.005. Earlier runs: run2 had 85/85 "converged" messages (so unaffected in practice), run85 85/85 too; the 5-step test and first steps of every run (step 1: 20 its, 7.8e-3) hit the cap.
- Action: rerun run4 with `max_iter_per_step=200` before using it for conclusions (expected 1.5–2× longer). Until then treat `run4_4cycles` as under-converged.

## run5_4cycles (agent, started 20/10/2026 17:23, detached) — rerun of run4 with the real cap `max_iter_per_step=200`
- Output `L3/results/run5_4cycles/`, final case `L3/cases/case_dm_v3_run5_4cycles_20102026.cas.h5` (+ `_partial` every 25 steps), logs `logs/run5.out/.err`. run4 left untouched (under-converged, iteration cap 20). Use run5 for conclusions once finished.

## run5 analysis (agent, 20/10/2026) — **current results; supersedes run2 numbers and the report draft's numbers**
- run5_4cycles finished 19:48 (2.4 h): 351 "converged" messages, 11–34 iterations/step (mean 20.7, cap 200 never reached), worst continuity 0.005. Analysis cycle = steps 263–350 (t 2.63–3.50 s), previous cycle = steps 175–262 (`postproc/analyze_cycle.py … 175 88 2` → `postproc/run5/results.npz`; `postproc/figures_cycle.py` → `figures/run5/*.png` and `postproc/paraview/run5_wall_metrics.vtp`).
- Definitions: TAWSS = mean |τ|; OSI = 0.5(1 − |mean τ|/mean|τ|); **ECAP = OSI/TAWSS [1/Pa]**; RRT = 1/((1−2·OSI)·TAWSS); vorticity = |ω| from Fluent. Wall quantities mapped onto the wall mesh of step 263 by 3-node inverse-distance interpolation (mean offset 0.05 mm, p95 0.25 mm, max 5.3 mm near the moving MV).
- Wall, analysis cycle (whole / within 10 mm of device / within 20 mm / rest): TAWSS mean 0.366 / 0.147 / 0.245 / 0.395 Pa; OSI mean 0.189 / 0.323 / 0.246 / 0.175; ECAP median 0.62 / 2.39 / 1.08 / 0.57 1/Pa; RRT median 6.1 / 28.8 / 9.3 / 5.7; time-avg wall vorticity 101.7 / 39.4 / 66.0 / 110.2 1/s.
- Fluid, analysis cycle: mean vorticity 18.2 1/s whole LA vs 12.6 within 10 mm of the device (peak 35.9 / 25.7 at t ≈ 0.43 s in the cycle); p95 54 1/s, local spikes up to ~1.9e4 1/s; mean |u| 5.7 vs 3.2 cm/s; volume with |u| < 5 cm/s: 57 % whole, 81 % within 10 mm, 61 % within 20 mm (< 1 cm/s: 8 / 22 / 10 %).
- Periodicity (previous vs analysis cycle): spatial correlation of TAWSS 0.90, OSI 0.87, ECAP 0.92; cycle means differ by +2 % (TAWSS), +6 % (OSI), +10 % (ECAP); mean-vorticity time series rms difference 6 %, |u| 9.5 %, LA volume 0.2 % → approximately periodic, not fully converged to a limit cycle (the motion profile was extended with an assumed rule, see 4-cycle entry).
- Not done: no clinical thresholds applied; the device itself is still not in the mesh; report draft (`report/DRT_report_DRAFT.docx`) still quotes run2 numbers.

## Device re-segmentation (agent, 22/10/2026) — `postproc/device_seg/*.py`
- Device = Amulet-type occluder (lobe + disc, two radiopaque hubs > 2000 HU). LA blood 401 ± 32 HU; frame wires 550–1500 HU → threshold 550 HU on Gaussian σ = 0.5 vox, components connected to lobe/disc rim, clipped to a cylinder around the disc axis (removes hub streak artefacts). Disc rim planar (0.5 mm rms), diameter ≈ 26 mm; disc faces the LA.
- User feedback: wanted the **frame itself**, not a wrapped hull, and the 550 HU threshold missed many wires. Redone: residual = CT − 3D median (9 vox) → Gaussian σ 0.5 → hysteresis threshold (low 60, high 220 HU) ∪ (smoothed CT > 600 HU, keeps hubs/rim); small holes ≤ 20 vox filled; largest component only; clipped to a cylinder (disc radius + 2 mm, −5…+18 mm along axis) to drop hub streaks outside the device (`postproc/device_seg/final.py`, `clip.py`, `save2.py`).
- `L1/Device.seg.nrrd` now = **frame** (segment "Device_frame", 3.2 mL, 32,066 vox). Hull version kept as `L1/Device_hull_22102026.seg.nrrd`; user's original as `L1/Device_original_15102026.seg.nrrd`. QC: `L1/Device_frame_QC_*_22102026.png`. Known limits: wires bloom to ~1 mm (CT resolution); radial streaks inside the device near the two hubs are still included.
- Not done: device not yet subtracted from the LA / not in the mesh.

## Device segmentation with pretrained U-Net (agent, 31/10/2026) — `L1/device_unet_attempt/` (see its README)
- User edited `L1/Device.seg.nrrd` by hand on 23/10 (50,652 vox) — read only, not changed. Professor: wireframe only, extra structures cost marks; export STL. Device = Abbott Amulet (lobe + disc, two hubs).
- nnInteractive v1.0 (DKFZ nnU-Net-based promptable 3D model, HF `MIC-DKFZ/nnInteractive`, CC BY-NC-SA) on CPU, prompts generated automatically from the CT. Pure model fills blood between wires (46 % of voxels without local contrast); **recommended `Device_unet_wire`** = model ROI ∩ wire contrast, 2.86 mL, 1 % non-wire voxels. Each variant exported as `.seg.nrrd` + `.stl` (LPS mm, same frame as `L2/HugoJal_Case3.stl`). Not yet checked by the user in Slicer.

## Audit against the submission criteria (agent, 31/10/2026) — see `06-submission-criteria.md`, figures in `figures/audit/`
- Concurrent activity found: another session is using the single Fluent Student licence for the Circle of Willis project (`tools/fluent-setup/setup_steady_cow.py`) and another is installing nnInteractive into `L1/device_unet_attempt/.venv` for the device. **Do not start Fluent while those run; do not touch `L1/device_unet_attempt/`.**
- Segmentation (`L1/Hugo_Jal_left_atrium_segmentation.nrrd`, 512×512×274, 0.445×0.445×0.5 mm, 156 mL, bbox 96×71×75 mm): contour follows the LA wall closely on coronal and axial slices (`ct_overlay.png`), smooth, LAA/device excluded. **Gap: the pulmonary veins are only short stubs; the CT shows them continuing to their branches (`ct_mip_veins.png`)** → criterion "veins up to the first branch" not met. Filename lacks the case name pattern asked for (`…_nrrd` ok; confirm naming).
- Surface mesh (`L2/HugoJal_Case3.stl`, 49,260 tris, 167.4 mL): watertight, 0 non-manifold edges, 0 open edges; 4 PV cylinders and a flat MV cut present. The PV cylinders were added on short stubs.
- Volume mesh (`L3/mesh/HugoJal_Case3_gmsh.bdf`): 393,557 tets (< 500k OK) but ~100 sliver cells (equivolume skew > 0.95), min orthogonal quality 7e-6 in Fluent → "good quality" doubtful.
- Simulation: transient 4 cycles with MV motion; case-specific; flows per prescribed profiles. Missing: streamlines/pathlines figures, convergence study.
- Report: draft is .docx ≈ 4 pages without references → needs ≤ 2-page PDF with verified references and CT-based images.

## Vein / mitral re-assessment (agent, 31/10/2026) — `postproc/seg_v2/*.py`, figures `figures/audit/`
- Correction of the earlier audit: the **vein stubs are longer than they looked**. Opening at 11 mm radius isolates 4 PV stubs, each ≈ 52 mm from the LA centre (≈ 10–15 mm beyond the LA wall), tip radius 3.6–4.0 mm (`stubs.py`). A 5th stub next to the device = LAA remnant (not a vein). Geodesic growth at 170 HU (`geo.py`): LV-posterior and RV-posterior veins branch **5–6 mm beyond** the stub tip (so only ≈ 8–9 mm to add, 0.5 mL total); the other two veins narrow below 2 mm at the tip → **the old segmentation already reaches ≈ the first branch for all four veins**. Remaining vein defect: thin veins slightly narrower than the bright lumen (LA boundary voxels have median 316 HU, i.e. the contour sits ~0.3–0.5 mm inside the true edge).
- The user's PV cylinders in the STL are ≈ 17–20 mm in diameter (caps r 8.4–10 mm, areas 221–313 mm²) with outward normals as set by hand.
- Mitral valve: radial long-axis CT views (`mv_radial_views.png`) show the cut is placed at the LA–LV narrowing, perpendicular to the valve axis, following the leaflet plane → anatomically consistent. The MV opening is ≈ 22 × 12–15 mm (≈ 205–250 mm²), smaller than the slides' 28–42 mm and than a typical open-valve orifice; this is why the prescribed MV flow gives peak 1.6 m/s. Option: enlarge the cut by moving it 3–5 mm toward the LV.
- Not done: no new segmentation/mesh written; no Fluent use (licence busy with the CoW session).

## FINAL REPORT (agent, 31/10/2026) — `report/DRT_report_Case003.pdf` (2 pages + 1 page of references)
- User decision: **keep the original geometry/meshes as they were** (the v2 segmentation/surface experiments were archived in `postproc/seg_v2/archive/`; L1/L2/L3 untouched). Simulation = run5_4cycles (analysis cycle t 2.63–3.50 s).
- Verdict on run5 quality: converged (11–34 it/step, continuity ≤ 0.005), mass balance 0.6 % of peak MV flow, cycles 3–4 agree (TAWSS map r = 0.90), 46 mL/beat through MV. **Not physiological**: MV peak velocity 1.7 m/s and local pressure drop ≈ 3 kPa (small MV opening ≈ 22×13 mm with prescribed velocity); LA volume change only 0.75 %; PV flow splits 20/29/18/34 % with net outflow in some PV for ≈ 2/3 of the cycle; absolute TAWSS (0.37 Pa) below published DRT cohorts (Vogl 2024: 1.76 ± 1.24 Pa). Hence only regional contrasts are interpreted. No mesh/time-step convergence study; ≈ 100 sliver cells.
- CT finding (device hull `L1/Device_hull_22102026.seg.nrrd`, axis from the appendage-ostium stub): lumen shell 0.5–3 mm outside the device on the LA side = 383–385 HU (LA blood 404 ± 32), 0.2 % of voxels < 250 HU → **no hypoattenuating thickening / no DRT visible**; dark material beside the device lies outside the lumen (82 ± 73 HU, wall/fat). Scripts: analysis was run inline (see report text); figures by `postproc/report_figs.py`, PDF by `postproc/make_report_pdf.py`.
- References (all verified in PubMed): Dukkipati 2018 (PMID 29752398), Korsholm 2019 (31514523), Iriart 2023 (37668517), Zhong 2024 (37291248), Vogl 2024 (39493311), Mutlu 2023 (36724610). Di Achille 2014 (original ECAP definition) is NOT in PubMed → not cited. Report includes an AI-use declaration line (user may edit).
- Older `report/DRT_report_DRAFT*.docx` are superseded.

## Report v3 — LaTeX, ParaView figures (agent, 31/10/2026) — `report/latex/` (main.tex, references.bib, figures/) → `report/latex/main.pdf`
- User feedback on the reportlab PDF: style looked auto-generated; wanted the CoW-draft LaTeX format (`Project/report/CoW_Group_First_Draft/main.tex`), the device segmentation shown, CT indications in a normal radiological style (arrows, scale bars, orientation letters), **the question framed as RISK of DRT (answer: yes, at risk), not presence**, much more analysis (isolines, ECAP, TAWSS), and **ParaView visualisations**.
- ParaView 6.2.0 is installed (`C:/Program Files/ParaView 6.2.0/bin/pvbatch.exe --force-offscreen-rendering`). Script `postproc/paraview_scripts/pv_figures.py [anatomy|flow|vortex|wall|all]` → `report/latex/figures/pv_*.png` (streamlines from the PV caps at t = 3.06/3.40 s, slice through LA centre–device–MV with velocity isolines, Q = 4000 s^-2 isosurface, wall TAWSS/OSI/ECAP with isolines + 10/20 mm distance-to-device isolines). PV 6 notes: presets are 'Viridis', 'Inferno', 'Plasma', 'Turbo'; colour-bar formats use `{}` style; `ColorBy(x, None)` fails → set `x.ColorArrayName = ["POINTS", ""]`; log LUT needs `MapControlPointsToLogSpace()`.
- New inputs for ParaView: `postproc/paraview/device_frame_m.stl` (segmentation), `device_wires_750_m.stl` (CT ≥ 750 HU isosurface within the hull), `device_hull_m.stl`, `la_surface_m.stl`, `run5_wall_metrics.vtp` (+ `LowShearTimeFraction`, `dist_to_device_mm`).
- Quantification `postproc/report_quant.py` → `postproc/run5/report_numbers.json`, `figures/fig_bands.pdf`, `fig_time.pdf`. Distance bands (0–5/5–10/10–20/20–40/>40 mm): TAWSS median 0.09/0.20/0.30/0.32/0.24 Pa; OSI 0.39/0.24/0.16/0.13/0.17; ECAP 3.50/1.38/0.48/0.40/0.71 1/Pa; ECAP>2 on 89/30/7/4/15 % of the band area; low-shear (|τ|<0.1 Pa) time 66/50/39/32/44 %. Mean |τ| within 10 mm < 0.1 Pa for 57 % of the beat vs 13 % beyond 20 mm; peaks 0.57 vs 1.36 Pa. Wall within 20 mm = 20 % of wall area, holds 42 % of ECAP>2 area. At the mitral peak, fluid within 5 mm of the device: median |u| 2 cm/s (p95 8), 10–20 mm: 13 cm/s. Near-device ECAP changed +22 % between beats 3 and 4. `postproc/analyze_cycle.py` now also saves `mag_steps` (per-step |τ| on the reference wall).
- CT figure `postproc/report_ct_figure.py` (matplotlib with usetex). Report length: 3 pages + references (over the 2-page guideline — flagged to the user).

## Report v4 (agent, 31/10/2026) — `report/latex/main.pdf`: 2 pages + 1 page of references
- User decisions: answer BOTH questions (no DRT visible on CT; patient AT RISK); max 2 pages + references (professors' email); **no AI-use declaration**; limitations kept short (device not in domain, generic BCs; no list of internal simulation issues); device shown everywhere as the user's segmentation (`device_frame_m.stl`, orange) — the CT-isosurface device was rejected ("not what I see in the image"); Fig. 1 rebuilt in ParaView (`pv_figures.py ct`: CT plane + LA/device segmentations, oblique CT with outlines, 3D view); matplotlib CT panels with arrows were rejected as "AI-looking".
- User did not recognise the WSS transfer step from class; the report explains it in one plain sentence (remeshing → map each step's WSS onto one fixed wall copy before averaging).
- Layout tricks: Fig. 1 sits in the `	wocolumn[...]` title block (braced); figure* for Figs 2–3 are defined before §2 so they land on page 2; `stfloats` is not installed in MiKTeX (don't use).

## Problems found (fix before running) — items 1 and 3 are now fixed in the new case
1. **Remeshing length scales are 0.0 / 0.0** (`length_min`, `length_max`) → negative cells risk. Set from Mesh Scale Info (step 17–18).
2. Remeshing method is **unified** (`unified_remeshing: true`), slides say **local cell** → check/uncheck "unified" accordingly. Interval (5–10) not checked.
3. **Solver methods not yet set (steps 27–30)**: currently SIMPLE, gradient least-squares cell based, transient **1st order**; slides: **Coupled**, Green-Gauss Node Based, **2nd order** transient. Continuity residual is 0.001 (slide: 0.005).
4. Zones still carry default names (`default_exterior-1.8x`) — rename (step 9).
5. Not yet checked: mesh scale (mm), velocity-profile unit/sign, `.prof` coverage up to 0.85 s, initialization, EnSight export.

## Next
1. User: fix items 1–3 in the GUI (or ask the agent to do it in its own session), save under a new name.
2. Agent: initialize all zones, preview motion, set EnSight Case Gold export, then run 85 steps, dt 0.01, 200 it/step (after confirmation).
3. L5: post-processing and PDF report.

## Deadline
Report + all materials: likely second half of November 2026 (20 % of grade; YES/NO DRT risk with justification). See 01-project-overview.md.

## Notes
- Attaching to the GUI session (`/server/start-server`) did not work; agent-owned session works: set `AWP_ROOT261` (done in `.mcp.json`), `fluent_launch(case_file=…)`. A no-GUI launch while the user's GUI Fluent is open worked with the Student licence.
