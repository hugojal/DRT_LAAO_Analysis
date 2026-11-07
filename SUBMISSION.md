# What to submit (deadline 20/11/2026 23:59)

**Everything is run8** (circular PV cylinders, 07/11/2026). Older meshes, runs and figures were moved to `archive/`, which is git-ignored and kept locally only, so they cannot be handed in by mistake. Hand in exactly these files:

| # | Rubric item | File to submit | Notes |
|---|---|---|---|
| 1 | LA segmentation (.nrrd, named after the case) | `1_segmentation/la_v2_06112026/Case3_LA_segmentation_HugoJal_06112026.seg.nrrd` | Corrected: device removed, inferior veins to the first branch, no artefacts (genus 0). Opens in 3D Slicer. `Hugo_Jal_left_atrium_segmentation.nrrd` is only the original input; do not submit it. |
| 2a | Surface mesh (.stl) | `2_mesh/run8_07112026/HugoJal_Case3_run8_07112026.stl` | In the model frame: z = mitral valve axis, origin = annulus centre, mm. `transform_LPS_to_model.json` maps it back to the CT. |
| 2b | Volume mesh (.bdf) | `2_mesh/run8_07112026/HugoJal_Case3_run8_07112026.bdf` | 271 908 tetrahedra, max skewness 0.91, 6 zones at 30°; PV inlets are circular cylinders (9–18 mm). |
| 3 | Simulation files for ParaView | the folder `6_paraview_package/`, as one zip | Contents: last beat of run8, final Fluent case/data, wall metrics, surfaces, flows, **convergence data** (`convergence/`), and the `open_in_paraview.py` script. About 1.2 GB, too large for git and most upload forms: **upload the zip (OneDrive/Drive, "anyone with the link"), test the link in a private window, write the link in the PDF.** Rebuild with `python 4_postprocessing/make_paraview_package.py run8`. |
| 4 | DRT report (PDF, ≤ 2 pages + references) | `5_report/main.pdf` | Run8 results (figures in `5_report/figures_run8/`). Explicit answers: no DRT on the CT (HU argument, Fig. 1), patient at risk (Figs. 2–4). |
| 5 | Device segmentation (.stl, extra point) | `1_segmentation/device/gamma/Device_gamma_wire_v4_06112026.stl` | Wire-frame only (Amulet-type). The alternative is `device/unet/Device_unet_wire.stl`. **Not** `device/manual/` (a solid plug). |

## Checklist before handing in
- [ ] Check segmentation v2 in Slicer (inferior veins, device region).
- [x] `5_report/main.pdf` is the run8 version (07/11/2026, figures from `5_report/figures_run8/`).
- [ ] Report fixes from `docs/agents/reviews/rubric_review_06112026.md`: author names in the bib, Morales → Sci Rep 2026, hub-artefact sentence and CT window, "Amulet-type", ParaView link.
- [ ] ParaView zip uploaded and the link tested.
- [ ] Optional: mock grade with `/rubric-adversary` (in Claude Code).
- [ ] No patient data: never include `data/`, the CT `.nrrd` or the Slicer `.mrml`.

**Convergence evidence:** `4_postprocessing/run8/convergence/` (all 350 steps converged).
- residuals of every iteration;
- iterations and convergence per time step;
- mass balance;
- periodicity of the last two beats;
- `convergence.png`.

**Thrombus assessment on the CT:** `4_postprocessing/device_ct/` (README). **Flow in front of the device:** `4_postprocessing/run8/device_sections/` (README).

Details: `4_postprocessing/run8/README.md`, `2_mesh/run8_07112026/README.md`, `docs/agents/STATUS.md`.
