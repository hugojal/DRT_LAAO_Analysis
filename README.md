# Device-related thrombus after LAA occlusion — Case 3

Course project for *Modelling of Organs and Systems* (Universitat Pompeu Fabra, 2026).
From a contrast CT of a patient with a left atrial appendage occluder, we segment the left atrium and the device, build a mesh, simulate the blood flow in Ansys Fluent with a moving mitral valve, and use the flow and wall shear stress to judge whether the patient has, or is at risk of, a device-related thrombus (DRT).

**Answer (see [5_report/main.pdf](5_report/main.pdf)):** no thrombus is visible in the CT, but the patient **is at risk** of developing one: the device sits in the region with the slowest blood and the lowest, most oscillating wall shear stress of the atrium.

## Pipeline and folders

**What to hand in:** see [SUBMISSION.md](SUBMISSION.md) (one file per rubric item).


| Step | Folder | Tools | Main files |
|---|---|---|---|
| 1. Segmentation | `1_segmentation/` | 3D Slicer, Python | `Hugo_Jal_left_atrium_segmentation.nrrd`, scene screenshot (the Slicer `.mrml` scene stays local: it holds DICOM metadata); `device/`: the **Amulet-type** occluder, segmented three ways, each as `.seg.nrrd` + `.stl`: `manual/` (used in the model), `gamma/` (gamma transform + sheet tracing) and `unet/` (promptable U-Net). See `1_segmentation/device/README.md` |
| 2. Mesh | `2_mesh/` | MeshLab, Meshmixer, Gmsh | `run7_06112026/`: **the mesh in the report (run7)**, built from the corrected segmentation `1_segmentation/la_v2_06112026/`, PV extensions along the vein trunks, **5.3 cm² mitral orifice** (course range 4–6 cm²), 272k tetrahedra. README in the folder. Older meshes are in the git-ignored `archive/`. |
| 3. Simulation | `3_simulation/` | Ansys Fluent 2026 R1 Student, PyFluent | boundary-condition profiles (`boundary_conditions_4cycles_run7/`, course curve unscaled; `boundary_conditions*/` = course inputs), `setup_case_*.py`, `run_cycle.py`; cases and results are not in the repo (too large) |
| 4. Post-processing | `4_postprocessing/` | Python (PyVista, NumPy), ParaView 6.2 | `analyze_cycle.py`, `report_quant.py`, `pv_figures.py`, `check_convergence.py`, `run7/` (numbers, figures, convergence, README) |
| 5. Report | `5_report/` | LaTeX | `main.tex`, `references.bib`, `figures_run7/`, `main.pdf` |

Other folders: `docs/agents/` (working notes and the Fluent recipe), `tools/fluent_mcp/` (MCP server to drive Fluent from Claude Code), `logs/`.

## Simulation in short
- Transient, laminar, Newtonian blood (ρ = 1060 kg/m³, μ = 3.5 mPa·s).
- Pulmonary veins: pressure curve; mitral valve (5.3 cm²): the course velocity curve, unscaled (cardiac output 5.47 L/min), and the valve's longitudinal motion along its axis (dynamic mesh with smoothing and remeshing).
- Time step 0.01 s, taken from the boundary-condition files; 4 heartbeats (350 steps), the last one analysed.
- Wall metrics: TAWSS, OSI and ECAP = OSI/TAWSS; flow: streamlines, velocity on a plane, Q-criterion.

## Reproducing
Python environment: PyFluent 0.43, PyVista, SciPy, pynrrd, matplotlib (here in `../mcp/.venv`); ParaView 6.2 for the figures.
```
python 3_simulation/setup_case_run7.py AB
python 3_simulation/run_cycle.py 350 <abs>/3_simulation/results/run7_4cycles <abs>/3_simulation/cases/case_run7_4cycles_07112026.cas.h5 <abs>/3_simulation/cases/case_run7_setup_06112026.cas.h5 <abs>/3_simulation/boundary_conditions_4cycles_run7
```
The published run is `run7_4cycles` (07/11/2026; all 350 steps converged). Use absolute paths: Fluent runs in `logs/fluent`. The Fluent cases (`3_simulation/cases/`) and results are not in the repository. The post-processing commands are in [4_postprocessing/run7/README.md](4_postprocessing/run7/README.md); the report is built with `cd 5_report && latexmk -pdf main.tex`. The mesh is described in [2_mesh/run7_06112026/README.md](2_mesh/run7_06112026/README.md); the LA segmentation to hand in is [1_segmentation/la_v2_06112026/](1_segmentation/la_v2_06112026/README.md).

## Data
The CT images and the DICOM files are patient data and are **not** included (`data/` and the CT volume are git-ignored). Only the segmentations, meshes and derived results are shared.
