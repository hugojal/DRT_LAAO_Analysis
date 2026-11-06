# DRT_LAAO_Case3 — Modelling of Organs and Systems (UPF) · Left atrium CFD

Goal: replicate a modelling workflow for **device-related thrombus risk after left atrial appendage occlusion (LAAO)**:
Segmentation (L1) → Meshing (L2) → Solver/physics in Ansys Fluent (L3+L4) → Post-processing (L5) → PDF report.
The user is a student (third year); Fluent is driven mainly by hand in the GUI and this agent continues from where they stop.
This folder is meant to become a GitHub repository (see `README.md`, `.gitignore`).

## Read first (in this order)
1. [docs/agents/STATUS.md](docs/agents/STATUS.md) — what is done / what is next. **Update it at the end of every work session.**
2. [docs/agents/01-project-overview.md](docs/agents/01-project-overview.md) — labs, deliverables, data and file map.
3. [docs/agents/02-fluent-pipeline-L3L4.md](docs/agents/02-fluent-pipeline-L3L4.md) — the 34-step Fluent recipe from the course slides.
4. [docs/agents/03-mcp-ansys.md](docs/agents/03-mcp-ansys.md) — how to connect to Fluent through the `ansys-fluent` MCP.
5. [docs/agents/04-geometry-meshing-L1L2.md](docs/agents/04-geometry-meshing-L1L2.md) — only if mesh/geometry problems appear.
6. [docs/agents/05-paraview.md](docs/agents/05-paraview.md) — post-processing: results are visualised in **ParaView**.
7. [docs/agents/06-submission-criteria.md](docs/agents/06-submission-criteria.md) — **how the work is graded** (segmentation, meshes, simulation, ≤ 2-page PDF + 1 page of references). Deadline 20/11/2026 23:59. For a mock grade against this rubric use the skill `/rubric-adversary` (`.claude/skills/rubric-adversary/`; reviews saved in `docs/agents/reviews/`).

## Folder map
`data/Case_003/` raw CT (never touch, git-ignored) · `1_segmentation/` Slicer scene, CT `.nrrd`, LA segmentation (original + **`la_v2_06112026/` = corrected one to hand in**), `device/` (Amulet-type occluder: `manual/`, `gamma/`, `unet/`, each `.seg.nrrd` + `.stl`; read `device/README.md`) · `2_mesh/` segmented surface `HugoJal_Case3.stl`, `mv_aligned_03112026/` (mesh of run6, mitral cap 8.6 cm²), `run7_06112026/` (**next mesh**: from the corrected segmentation, PV extensions along the vein trunks, 5.3 cm² mitral orifice), `mv_taper_06112026/` (superseded mitral-only step), old `HugoJal_Case3_gmsh.bdf` (run5) · `3_simulation/` boundary-condition profiles (`boundary_conditions_4cycles_mvz/` run6, `boundary_conditions_4cycles_run7/` run7, unscaled), `setup_case_mvz.py` / `setup_case_run7.py`, `cases/` (**current run `case_mvz_run6_4cycles_04112026`**), `results/run6_mvz_4cycles/` EnSight Gold per step, `run_cycle.py` · `4_postprocessing/` analysis scripts, `paraview/` inputs, `run6/` numbers and figures · `6_paraview_package/` files to hand in for ParaView (data git-ignored, rebuilt by `4_postprocessing/make_paraview_package.py`) · `5_report/` LaTeX report + `main.pdf` (the deliverable) · `docs/` slides (git-ignored) and agent notes · `tools/fluent_mcp/` Fluent MCP server (venv: `../mcp/.venv`, shared) · `logs/` Fluent transcripts and logs · `archive/` superseded files (git-ignored, do not use).
Outside this folder (in `MOs/`): `Project/` is a **separate project (Circle of Willis) — don't touch**; `tutorial/` straight-pipe Fluent exercise; `mcp/.venv` shared Python environment (also used by the CoW project — don't move it).

## Rules
- Source material is `docs/*.pdf` (course slides). Slide values are **an example for the in-class case**; parameters for this case must be justified from the mesh (`Mesh Scale Info`), not copied blindly.
- Never overwrite user files in `1_segmentation/`, `2_mesh/`, `3_simulation/` or `data/` (CT data, segmentations, meshes, `.cas.h5`). Save new states as new, dated files (e.g. `3_simulation/cases/case_dm_YYYYMMDD.cas.h5`).
- Before any action that is hard to undo in Fluent (re-initialize, run calculation, change zone types, exit), tell the user and confirm. Never `exit` the user's Fluent GUI. The Student licence allows one Fluent session: check no other session (e.g. the CoW project) is running Fluent first.
- Fluent Student licence limits: ~1 M cells, 4 cores. Current mesh is far below that.
- Units: SI in Fluent (mesh is imported in mm → **scale to mm**), time in s, pressure in Pa. Dates DD/MM/YYYY in written output.
- No patient identifiers: the DICOMs and the CT volume must not be uploaded (they are git-ignored) or described beyond anonymous metadata.
- Report style (user feedback 01/11/2026): third-year level, qualitative descriptions that let the figures speak, few numbers, few references (4), no AI-use declaration. Segmentation method = manual thresholding + masking + manual paint/erase (LA); device = manual segmentation. Do not claim region growing.
- Respond in the user's language (the user writes English; documentation here is English).
