# 01 · Project overview

Source: `docs/Lab1_Segmentation.pdf`, `docs/L2 MOS26.pdf`, `docs/L3+L4 MOS26.pdf` (Joel Romero, Paula Casademunt — UPF, *Modelling of Organs and Systems*).

## Clinical problem
Atrial fibrillation (AF) → disorganised atrial contraction → blood stagnation, ~90 % of clots form in the **left atrial appendage (LAA)** → anticoagulants, or mechanical **LAA occlusion (LAAO)** devices. The labs assess whether a given occluder leaves flow conditions favourable for **device-related thrombus (DRT)**. Hypothesis context: LAA morphology, stagnation, wall shear stress (WSS).

## Workflow and deliverables
| Lab | Stage | Tools | Deliverable |
|---|---|---|---|
| L1 | Geometry / segmentation | FreeCAD (warm-up), 3D Slicer | Left atrium segmentation `.nrrd`; device segmentation `.stl` |
| L2 | Meshing | MeshLab, Meshmixer, Gmsh | Processed LA surface mesh `.stl`; volumetric mesh `.bdf` |
| L3+L4 | Solver & physics | **Ansys Fluent 2026 R1 (Student)** | Case-specific simulation (ZIP of result files) |
| L5 | Post-processing | (ParaView/EnSight-compatible output) | Written PDF report on presence and risk of DRT |

## Grading and report requirements (professor's email, Paula, received 16/10/2026)
- Lab deliverable = **20 % of the final MOS grade**. Due **likely second half of November 2026** (date not yet confirmed; not requested yet).
- Short written report with a **clear YES/NO answer**: is the patient at risk of **device-related thrombus (DRT)** in the region close to the device? Needs a well-developed justification; may use any lab material (CT image → simulation results) and supporting images.
- Also submit **all materials generated**: LA and device segmentations, surface mesh, volumetric mesh, simulation results (see Lab1 slide 12).
- Implication for agents: results must be post-processed with DRT in mind — flow stagnation/low velocity, wall shear stress and residence-time-type indicators **near the device/LAA** — and every figure should be reproducible from saved files. There is time to iterate (mesh, parameters), so prefer correctness over speed.

## Case
Patient case **Case_003** (CT, 4 patients available in the course; LAA not visible because an occluder is already in place → device modelled separately).
Anatomy: left atrium (LA), 4 pulmonary veins (PV, ~10–25 mm diameter), mitral valve (MV, ~28–42 mm), LAA.

## File map (project root = `DRT_LAAO_Case3/`; reorganised 01/11/2026, old → new paths in `logs/reorganisation_01112026.txt`)
| Path | Content |
|---|---|
| `data/Case_003/` | Raw DICOM CT (sensitive — do not share, git-ignored) |
| `1_segmentation/` | Slicer scene `2026-10-15-Scene.mrml`, CT volume `.nrrd` (git-ignored), LA segmentation (`Hugo_Jal_left_atrium_segmentation.nrrd` original input; **`la_v2_06112026/`** corrected, the one to hand in), `device/` = the **Amulet-type** occluder, three segmentations, each `.seg.nrrd` + `.stl` (see `1_segmentation/device/README.md`): `manual/Device_manual.seg.nrrd` (edited by hand by the user 23/10, the one used in the model), `gamma/` (wireframe from gamma 0.3 + sheet tracing, v4 06/11/2026) and `unet/` (U-Net wireframe as saved from Slicer 31/10) |
| `2_mesh/` | `run7_06112026/`: from the corrected segmentation, PV extensions along the vein trunks, **5.3 cm² mitral orifice**, 272,293 tets (**run7, in the report**), README. Older meshes (run5, run6, mv_taper) are in `archive/2_mesh_pre_run7/` |
| `3_simulation/boundary_conditions/*.prof` | `pressure_inlet.prof` (`function_pressure_c`, Pa vs s, ~810–830 Pa), `velocity_outlet.prof` (`velocity_bc_c`, u in m/s, ≈ −0.0116 at t=0; sign already inverted for use as a velocity *inlet* at the MV), `motion.prof` (`mov_bc_c`, z displacement in m vs s, 0.01 s sampling) |
| `3_simulation/boundary_conditions_4cycles/` | the same extended to 4 heartbeats (used for run5) |
| `3_simulation/boundary_conditions_4cycles_run7/` | run7: course curve unscaled (529 mm² orifice, CO 5.47 L/min) + valve velocity (run6's scaled BC is archived) |
| `3_simulation/cases/` | `mesh_run7_06112026.cas.h5`, `case_run7_setup_06112026.cas.h5`, `case_run7_4cycles_07112026.cas/dat.h5` (**run7, in the report**); `case_dm_v3_16102026.cas.h5` base set-up — git-ignored |
| `3_simulation/results/run7_4cycles/` | EnSight Gold per step + `all_steps.encas` + `flows.csv` + `transcript.trn` (all residuals) + `solver_settings.json` — git-ignored |
| `3_simulation/run_cycle.py`, `setup_case_run7.py` | PyFluent driver (writes the transcript for the convergence check) and run7 case set-up (mesh replace keeps all settings; `mv_funnel` moves with the valve) |
| `4_postprocessing/` | `analyze_cycle.py`, `report_quant.py`, `pv_figures.py` (ParaView), `check_convergence.py`, `paraview/` inputs, `run7/` numbers, figures and `convergence/` |
| `5_report/` | LaTeX report (`main.tex`, `references.bib`, `figures_run7/`, `main.pdf`) |
| `tools/fluent_mcp/` | Python MCP server for Fluent (see 03); venv in `../mcp/.venv` |
| `archive/` | superseded files (old runs, old meshes, segmentation attempts, old report versions) — git-ignored, do not use |

## Open-science / confidentiality
Student coursework; still treat patient imaging as personal data (RGPD): keep DICOMs local, pseudonymised names only in anything shared.
