# Device-related thrombus after LAA occlusion — Case 3

Course project for *Modelling of Organs and Systems* (Universitat Pompeu Fabra, 2026).
From a contrast CT of a patient with a left atrial appendage occluder, we segment the left atrium and the device, build a mesh, simulate the blood flow in Ansys Fluent with a moving mitral valve, and use the flow and wall shear stress to judge whether the patient has, or is at risk of, a device-related thrombus (DRT).

**Answer (see [5_report/main.pdf](5_report/main.pdf)):** no thrombus is visible in the CT, but the patient **is at risk** of developing one: the device sits in the region with the slowest blood and the lowest, most oscillating wall shear stress of the atrium.

## Pipeline and folders

| Step | Folder | Tools | Main files |
|---|---|---|---|
| 1. Segmentation | `1_segmentation/` | 3D Slicer, Python | `Hugo_Jal_left_atrium_segmentation.nrrd`, `Device.seg.nrrd` (manual, used in the model), scene screenshot (the Slicer `.mrml` scene stays local: it holds DICOM metadata); device wire-frame experiments in `gamma_experiment/` (gamma transform + wire filter) and `unet_experiment/` (promptable U-Net) |
| 2. Mesh | `2_mesh/` | MeshLab, Meshmixer, Gmsh | `HugoJal_Case3.stl` (surface), `HugoJal_Case3_gmsh.bdf` (volume, ~390k tetrahedra) |
| 3. Simulation | `3_simulation/` | Ansys Fluent 2026 R1 Student, PyFluent | boundary-condition profiles, `run_cycle.py`; cases and results are not in the repo (too large) |
| 4. Post-processing | `4_postprocessing/` | Python (PyVista, NumPy), ParaView 6.2 | `analyze_cycle.py`, `report_quant.py`, `pv_figures.py`, `paraview/run5_wall_metrics.vtp` |
| 5. Report | `5_report/` | LaTeX | `main.tex`, `references.bib`, `figures/`, `main.pdf` |

Other folders: `docs/agents/` (working notes and the Fluent recipe), `tools/fluent_mcp/` (MCP server to drive Fluent from Claude Code), `logs/`.

## Simulation in short
- Transient, laminar, Newtonian blood (ρ = 1060 kg/m³, μ = 3.5 mPa·s).
- Pulmonary veins: pressure curve; mitral valve: velocity curve and valve motion (dynamic mesh with smoothing and remeshing).
- Time step 0.01 s, taken from the boundary-condition files; 4 heartbeats (350 steps), the last one analysed.
- Wall metrics: TAWSS, OSI and ECAP = OSI/TAWSS; flow: streamlines, velocity on a plane, Q-criterion.

## Reproducing
Python environment: PyFluent 0.43, PyVista, SciPy, pynrrd, matplotlib (here in `../mcp/.venv`); ParaView 6.2 for the figures.
```
python 3_simulation/run_cycle.py 350 3_simulation/results/rerun 3_simulation/cases/case_dm_rerun_YYYYMMDD.cas.h5 3_simulation/cases/case_dm_v3_16102026.cas.h5 3_simulation/boundary_conditions_4cycles
python 4_postprocessing/analyze_cycle.py 3_simulation/results/run5_4cycles 4_postprocessing/run5 175 88 2
python 4_postprocessing/report_quant.py
pvbatch --force-offscreen-rendering 4_postprocessing/pv_figures.py all
cd 5_report && latexmk -pdf main.tex
```
The first line re-runs the simulation into new files (the published run is `run5_4cycles`, analysed by the following lines); it needs the Fluent case (`3_simulation/cases/`), which is not in the repository.

## Data
The CT images and the DICOM files are patient data and are **not** included (`data/` and the CT volume are git-ignored). Only the segmentations, meshes and derived results are shared.
