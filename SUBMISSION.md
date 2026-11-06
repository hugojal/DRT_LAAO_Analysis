# What to submit (deadline 20/11/2026 23:59)

One file (or folder) per rubric item. **Hand in only the files in this table.** The rest of the repository is working material.

The mesh, the simulation and the report must all come from the **same run**:
- **today (06/11/2026)** that is **run6**;
- **after run7 is run and the report is updated**, switch to the run7 column.

| # | Rubric item | Submit now (run6) | Submit after run7 | Notes |
|---|---|---|---|---|
| 1 | LA segmentation (.nrrd, named after the case) | `1_segmentation/la_v2_06112026/Case3_LA_segmentation_HugoJal_06112026.seg.nrrd` | same | Corrected: device removed, inferior veins to the first branch, no artefacts. **Check it in Slicer first.** Do not submit `Hugo_Jal_left_atrium_segmentation.nrrd` (original) or `HugoJal_Case3_stl.seg.nrrd`. |
| 2a | Surface mesh (.stl) | `2_mesh/mv_aligned_03112026/HugoJal_Case3_mvz_03112026.stl` | `2_mesh/run7_06112026/HugoJal_Case3_run7_06112026.stl` | Both are in the model frame (z = valve axis). Do not submit `2_mesh/HugoJal_Case3*.stl` or `mv_taper_06112026/`. |
| 2b | Volume mesh (.bdf) | `2_mesh/mv_aligned_03112026/HugoJal_Case3_mvz_03112026.bdf` | `2_mesh/run7_06112026/HugoJal_Case3_run7_06112026.bdf` | Must be the pair of 2a. |
| 3 | Simulation files for ParaView | the folder `6_paraview_package/` (zip, ~1.2 GB) | rebuild it for run7 (the script must be pointed at run7 first) | Too large for git and for most upload forms: **upload the zip to OneDrive/Drive, share "anyone with the link", test the link in a private window, and write the link in the PDF.** Rebuild with `python 4_postprocessing/make_paraview_package.py`. |
| 4 | DRT report (PDF, ≤ 2 pages + references) | `5_report/main.pdf` | `5_report/main.pdf` after updating it to run7 | Explicit answer: no DRT on CT, patient at risk. |
| 5 | Device segmentation (.stl, extra point) | `1_segmentation/device/gamma/Device_gamma_wire_v4_06112026.stl` | same | Wire-frame only (Amulet-type). Alternative: `device/unet/Device_unet_wire.stl`. **Not** `device/manual/` (a solid plug). Consider a copy named `Case3_device_HugoJal.stl`. |

## Checklist before handing in
- [ ] Decide **run6 or run7** and use one column for 2a, 2b, 3 and 4.
- [ ] Check segmentation v2 in Slicer (inferior veins, device region).
- [ ] Report: the fixes in `docs/agents/reviews/rubric_review_06112026.md` (author names in the bib, Morales → Sci Rep 2026, hub-artefact sentence and CT window, "Amulet-type", ParaView link).
- [ ] ParaView zip uploaded and the link tested.
- [ ] Optional: mock grade with `/rubric-adversary` (in Claude Code) on the final set.
- [ ] No patient data: never include `data/`, the CT `.nrrd` or the Slicer `.mrml`.

Status and details: `docs/agents/STATUS.md`. What run7 changes: `2_mesh/run7_06112026/README.md`.
