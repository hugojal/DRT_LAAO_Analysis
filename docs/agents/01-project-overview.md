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
| `1_segmentation/` | Slicer scene `2026-10-15-Scene.mrml`, CT volume `.nrrd` (git-ignored), LA segmentation (`Hugo_Jal_left_atrium_segmentation.nrrd`, `HugoJal_Case3_stl.seg.nrrd`), device segmentation (`Device.seg.nrrd`, edited by hand by the user 23/10) |
| `2_mesh/` | `HugoJal_Case3.stl` (final surface), `…_meshlab.stl`, `.mix`/`.geo` project files, `HugoJal_Case3_gmsh.bdf` (**the volume mesh used in Fluent**, 393,557 tets) |
| `3_simulation/boundary_conditions/*.prof` | `pressure_inlet.prof` (`function_pressure_c`, Pa vs s, ~810–830 Pa), `velocity_outlet.prof` (`velocity_bc_c`, u in m/s, ≈ −0.0116 at t=0; sign already inverted for use as a velocity *inlet* at the MV), `motion.prof` (`mov_bc_c`, z displacement in m vs s, 0.01 s sampling) |
| `3_simulation/boundary_conditions_4cycles/` | the same extended to 4 heartbeats (used for run5) |
| `3_simulation/cases/` | `case_dm_v3_16102026.cas.h5` (set-up) and `case_dm_v3_run5_4cycles_20102026.cas/dat.h5` (final run) — git-ignored |
| `3_simulation/results/run5_4cycles/` | EnSight Gold per step + `all_steps.encas` + `flows.csv` — git-ignored |
| `3_simulation/run_cycle.py` | PyFluent driver used for run5 |
| `4_postprocessing/` | `analyze_cycle.py`, `report_quant.py`, `pv_figures.py` (ParaView), `paraview/` inputs, `run5/` numbers |
| `5_report/` | LaTeX report (`main.tex`, `references.bib`, `figures/`, `main.pdf`) |
| `tools/fluent_mcp/` | Python MCP server for Fluent (see 03); venv in `../mcp/.venv` |
| `archive/` | superseded files (old runs, old meshes, segmentation attempts, old report versions) — git-ignored, do not use |

## Open-science / confidentiality
Student coursework; still treat patient imaging as personal data (RGPD): keep DICOMs local, pseudonymised names only in anything shared.
