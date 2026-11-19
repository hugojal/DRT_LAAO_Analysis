# What to submit (deadline 20/11/2026 23:59)

**Everything is in `submission/`** (git-ignored), rebuilt on 16/11/2026 by `python 4_postprocessing/make_submission.py` (copies only; run it again after any change; `--no-zip` skips the 1.1 GB zip). It is all run9 (smoothed atrium, spur removed, smooth PV inlets ending in circular cylinders; mesh 15/11/2026, simulation 15-16/11/2026). Older meshes, runs and figures are in `archive/` (git-ignored, local only).

| # | Rubric item | File in `submission/` | Source in the project | Checked 14/11/2026 |
|---|---|---|---|---|
| 1 | LA segmentation (.nrrd, named after the case) | `Case3_LA_segmentation_HugoJal.seg.nrrd` | `1_segmentation/la_v3_17112026/Case3_LA_segmentation_HugoJal_17112026.seg.nrrd` (v2 + RSPV trunk to its division, 17/11/2026; the mesh is still built from v2) | 512x512x274, 157.7 mL, 1 component, genus 0, anonymous header (17/11/2026) |
| 2a | Surface mesh (.stl) | `HugoJal_Case3_LA_surface_mesh.stl` | `2_mesh/run9_15112026/HugoJal_Case3_run9_15112026.stl` | 44 166 triangles, 0 open edges, manifold; model frame (z = mitral axis, mm) |
| 2b | Volume mesh (.bdf) | `HugoJal_Case3_LA_volume_mesh.bdf` | `2_mesh/run9_15112026/HugoJal_Case3_run9_15112026.bdf` | 274 425 tetrahedra (< 500k); skewness max 0.88; 6 zones at 30° |
| 3 | Simulation files for ParaView | `HugoJal_Case3_ParaView.zip` (simple: EnSight files + .pvsm state) | `6_paraview_basic_18112026/` | state tested in pvbatch (88 time steps); no patient data; the full package `6_paraview_package/` is kept locally |
| 4 | DRT report (PDF, <= 2 pages + references) | `HugoJal_Case3_report.pdf` | `5_report/main.pdf` | 2 pages + 1 page of 5 references |
| 5a | Device segmentation (.stl, extra point), used in the analysis, Fig. 1b | `HugoJal_Case3_device_segmentation_manual.stl` | `1_segmentation/device/gamma/Device_gamma_wire_v4_edited_closed_both_16112026.stl` | Amulet-type device (edited gamma segmentation, closed and smoothed 16/11/2026; disc and lobe attached), CT frame (mm); not `device/manual/` (solid plug) |
| 5b | Device segmentation with the U-Net (nnInteractive), Fig. 1a | `HugoJal_Case3_device_segmentation_unet.stl` | `1_segmentation/device/unet/Device_unet_wire.stl` | same frame; 56 426 triangles |

## Simulation to send separately (17/11/2026)
Submission instructions: the simulation is **not** in the Aula Global zip; send it separately to Joel (group 102) or the professor (group 101). Use **`submission/JalHugo_simulation.zip`** (591 MB, made by hand on 17/11/2026). It holds only the data needed to view the simulation in ParaView:
- `simulation/` = the Fluent EnSight Gold export of the last beat, 88 steps;
- `fluent/` = the case and data at t = 3.50 s, plus the `.sf` files;
- a short `README.txt`.

Both files were checked in pvbatch 6.2 (88 steps; 294,305 cells). The older `HugoJal_Case3_ParaView.zip` (scripts, wall metrics, pathlines, device sections, convergence files) is kept, but it is not the one to send. `make_submission.py` does not build the new zip yet.

## Still to do by the author
- [ ] Upload `HugoJal_Case3_ParaView.zip` (OneDrive/Drive, "anyone with the link"), test the link in a private window, and write the link in the upload form or the report (not yet in the PDF; it needs a line, and the report is full at 2 pages).
- [ ] Check segmentation v3 in Slicer (RSPV trunk added 17/11/2026, inferior veins, device region).
- [ ] Read Sections 3.1-5 of the report once more (the diagnosis is the author's), then rebuild: `cd 5_report && latexmk -pdf main.tex`, and run `make_submission.py` again.
- [ ] No patient data: never include `data/`, the CT `.nrrd` or the Slicer `.mrml` (the script refuses to zip them).

## Evidence behind the report
- Convergence: `4_postprocessing/run9/convergence/` (last beat all converged; step 131, in beat 2, reached the 200-iteration cap; steps 346-350 lack the transcript's convergence line but their residuals are below the criteria).
- Thrombus assessment on the CT: `4_postprocessing/device_ct/`, `4_postprocessing/thrombus_check/`.
- Flow in front of the device: `4_postprocessing/run9/device_sections/`; pathlines: `4_postprocessing/run9/pathlines/`.
- Independent check of the thrombogenicity of each variable, computed from the data only: `4_postprocessing/run9/independent_review_15112026/` (JSON outputs; the written review `run8/independent_review_10112026/REVIEW.md` describes run8).

Details: `4_postprocessing/run9/README.md`, `2_mesh/run9_15112026/README.md`, `docs/agents/STATUS.md`.
