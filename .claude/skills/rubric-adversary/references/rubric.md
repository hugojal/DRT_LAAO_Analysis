# Rubric, attack checklists and severity guide

Contents: [Rubric as sent](#rubric-as-sent) · [1 Segmentation](#1-segmentation-310) · [2 Meshes](#2-left-atrial-meshes-210) · [3 Simulation](#3-simulation-210) · [4 DRT report](#4-device-related-thrombus-310) · [5 Device](#5-device-segmentation-1-extra) · [Severity guide](#severity-guide)

## Rubric as sent
Deadline: **20/11/2026 23:59**. Total 10 + 1 extra.

1. **Segmentation (3/10)**
   - The pulmonary veins must be well segmented, at least up to the first branch, as well as the mitral valve.
   - The surface should be smooth, free of obvious artefacts, and closely follow the contour of the entire left atrium (excluding the device and any thrombi).
   - Save the segmentation as a .nrrd file, named after the case you have segmented.
2. **Left atrial meshes (2/10)**
   - The pulmonary veins and mitral valve should be cut as explained in class. They should be easily separable in Ansys using the angle method.
   - The position and orientation of the mitral valve cut should be as consistent as possible with the anatomy displayed in the CT scans.
   - The surface mesh should not present non-manifold edges or negative volumes.
   - The surface mesh should not be oversmoothed: you must preserve the atrium's anatomical features.
   - The volumetric mesh must have fewer than 500k elements, while maintaining good quality.
   - Save the surface mesh as .stl and the volumetric mesh as a .bdf file.
3. **Simulation (2/10)**
   - You must run a case-specific simulation and share with us all files needed for visualization in ParaView.
   - The simulation should show physiological flow values and trajectories, include the mitral valve's longitudinal movement, and be informative for thrombus risk evaluation in that specific case.
4. **Presence of device-related thrombus (3/10)**
   - You must answer whether there is a device-related thrombus and justify your answer.
   - A simple yes/no will automatically receive 0 points. Include a short text explanation, screenshots, and visualizations from your simulation and image data that support your conclusion, as well as proper academic references. Reports not expected over 2 pages (without references).
   - Submit this part as a PDF.
5. **Device segmentation [1 extra point]**
   - You do not need to process the device mesh in Meshmixer, but the segmentation must be accurate.
   - Only the device wireframe should be included in the segmentation. Any extra structures will lower your grade.
   - Check the type of device you have (in the slides or online) to confirm that your segmentation matches its expected appearance.
   - Export the device as an .stl file.

Course slides with the in-class method ("as explained in class") are in `docs/*.pdf` (`Lab1_Segmentation.pdf`, `L2 MOS26.pdf`, `L3+L4 MOS26.pdf`); extract text with `pdftotext` and look at the pages that matter. Slide values are an example for the in-class case, not targets — but deviating from the *method* without saying why is attackable.

Useful project files: `docs/agents/STATUS.md`, `docs/agents/01…06-*.md`, `2_mesh/mv_aligned_03112026/` (README, `check_mesh_mvz.json`, `mitral_annulus.json`, PNGs), `4_postprocessing/run6/` (README, `report_numbers.json`), `4_postprocessing/compare_run5_run6.json`, `4_postprocessing/thrombus_check/`, `3_simulation/boundary_conditions_4cycles_mvz/scaling.json`, `5_report/main.tex`, `references.bib`, `main.pdf`, `6_paraview_package/README.md`. The project's own checks are claims to verify, not evidence.

Python: `../mcp/.venv/Scripts/python.exe` has numpy, scipy, scikit-image, pyvista/vtk, pynrrd, pypdf, PyMuPDF. ParaView: `C:/Program Files/ParaView 6.2.0/bin/pvbatch.exe --force-offscreen-rendering`. Renders and scripts go to the scratchpad.

---

## 1. Segmentation (3/10)
Submission candidates: `1_segmentation/Hugo_Jal_left_atrium_segmentation.nrrd`, `1_segmentation/HugoJal_Case3_stl.seg.nrrd`. CT: `1_segmentation/5 DS_Coronaires … .nrrd` (local, git-ignored; never copy it into the project tree or upload it).

Attack:
- **File name / which file.** Does the file meant for grading carry the case name ("Case3"/"Case_003")? If two LA `.nrrd` exist, which one will be graded, and do they agree? Different volumes or extra labels in one of them are worth noting.
- **Pulmonary veins to the first branch.** For each of the 4 PVs, follow the vessel in the CT from the ostium outward and find the first branching point; measure whether the mask reaches it (render oblique/MIP slices with the mask outline to the scratchpad and look at them with Read). Stubs that stop before the branch = direct rubric violation. Note the LAA remnant is not a vein.
- **Mitral valve included.** Does the mask reach the mitral annulus / leaflet plane, or stop short (an LA mask ending above the annulus means the MV cut in the mesh is guessed)? `2_mesh/mv_aligned_03112026/README.md` admits the LA surface sits ~2.3 mm (max 7.9 mm) inside the CT hinge points — check this and price it.
- **Follows the contour.** Sample the CT intensity on the mask boundary vs inside the blood pool: a boundary systematically inside the bright lumen = under-segmentation; leaks into LV, aorta, pulmonary artery, LAA body or fat = over-segmentation. Look at several axial/coronal/sagittal slices with the outline.
- **Excludes device and thrombus.** Use `la_device_overlap` in `checks.json`: device voxels inside the LA mask mean the device is (partly) included. Distinguish true inclusion from a one-voxel contact at the boundary (dilate/erode by 1 voxel and recompute before claiming it).
- **Smooth, no artefacts.** Islands (`connected_components` > 1), holes, staircase steps, spikes, flat "cut" faces from manual erase, bridges between veins. Marching-cubes the mask and look at it.

## 2. Left atrial meshes (2/10)
Submission candidates: `2_mesh/mv_aligned_03112026/HugoJal_Case3_mvz_03112026.stl/.bdf` (current, used by run6) and the older `2_mesh/HugoJal_Case3.stl`, `HugoJal_Case3_meshlab.stl`, `HugoJal_Case3_gmsh.bdf`.

Attack:
- **Angle-method separability.** `angle_separation_30deg.regions` must equal 1 wall + 1 MV + number of PVs (= 6). More regions (spurious creases) or fewer (a cap merging with the wall) fail "easily separable". Also check at 20° and 40° (the slides' range) — a mesh that only separates at exactly 30° is fragile. Caps should be planar (`planarity` ≈ 1) with ~90° edges.
- **Cut "as explained in class".** Compare with the L2 slides: flat cuts perpendicular to the vessel axis, cylindrical extensions, smooth transitions. Extension lengths and diameters vs the anatomy.
- **MV position/orientation vs CT.** Use `mitral_annulus.json`, `check_mitral_on_ct.png`, `transform_LPS_to_model.json`: overlay the cut plane on CT long-axis views through the annulus. Is it on the annulus (not inside the LV, not up in the LA)? Is its normal along the LA→LV axis? Is the cap diameter plausible for a mitral annulus?
- **Non-manifold / negative volumes.** From `checks.json` (`non_manifold_edges`, `open_edges`, `negative_volume_tets`). Also self-intersections if cheap to test.
- **Not oversmoothed.** Compare the STL with the segmentation surface (marching cubes of the LA mask, same frame — map the mvz mesh back with `transform_LPS_to_model.json`): signed distance stats, loss of ridges (e.g. the LAA ostium/ridge, vein ostia), volume change. Both under-processing (staircase, creases) and over-smoothing are attackable.
- **< 500k and good quality.** `tetrahedra`, `equivolume_skewness` (Fluent's "maximum cell skewness"; > 0.95 is commonly treated as poor, > 0.98 as unacceptable). Also aspect ratio if computed. Element size at the PV caps vs PV diameter (enough cells across?).
- **File formats and ambiguity.** .stl and .bdf present? Several candidates in `2_mesh/` → which one is graded, and does the STL match the BDF's boundary?

## 3. Simulation (2/10)
Current run: run6 (mvz mesh, 4 beats, flow-scaled mitral BC). See `4_postprocessing/run6/README.md`, `report_numbers.json`, `3_simulation/boundary_conditions_4cycles_mvz/scaling.json`, `logs/run6.out` (local).

Attack:
- **Case-specific.** Geometry is the patient's; but are the BCs generic course profiles? Is the scaling justified by something case-specific or by a population value? A grader may say "generic BCs on a patient geometry" — price it, and note what the report says about it.
- **ParaView files complete.** Open `6_paraview_package/README.md`; check that every file it lists exists locally (`checks.json` → `inventory.paraview_package`), that `open_in_paraview.py` runs (`pvbatch` it, output to the scratchpad), that time steps load, that the device and LA surfaces are in the same frame as the results. 1.2 GB: how will it be shared (upload limit)? Data that is git-ignored and only on this laptop is a submission risk.
- **Physiological values.** Compare with literature ranges *that you verify* (PubMed/web): mitral E-wave peak velocity, PV peak velocities, stroke volume / cardiac output, LA volume (this LA ~170 mL is large — consistent with an AF patient?), Reynolds number, pressure range. Check mass balance and beat-to-beat periodicity in `report_numbers.json` / `compare_run5_run6.json`.
- **Trajectories.** Streamlines/pathlines present in the report and reproducible from the package? Do they show the expected PV jets meeting and turning toward the MV?
- **MV longitudinal movement.** Is the motion applied along the valve axis (z) and does the cap actually move (−8.9 mm peak per `motion.prof`)? Check `3_simulation/setup_case_mvz.py` and the per-step geometry in the EnSight files if needed. Is the LA volume change meaningful or does only the cap move?
- **Informative for thrombus risk.** Device-adjacent metrics (ECAP, TAWSS, OSI, low-velocity volume, residence time). Weaknesses to probe: the device is not in the fluid domain (domain ends at the occluded LAA ostium?), no mesh or time-step convergence study, near-device conclusions sensitive to inflow scaling (run5 vs run6 differ a lot), thresholds (ECAP > 2?) sourced or not.

## 4. Device-related thrombus (3/10)
File: `5_report/main.pdf` (from `main.tex`, `references.bib`).

Attack:
- **Hard fails first.** Body ≤ 2 pages (`checks.json` → `pdf.body_pages_before_references`; also check margins/font size were not shrunk to cheat the limit — a grader notices). Is there an explicit answer (yes / no DRT) *and* a justification? A conclusion that only says "at risk" without answering presence is attackable, and vice versa.
- **Evidence from both sources.** Screenshots from the image data (CT around the device, with window/level suitable for thrombus) *and* from the simulation. Does the CT figure actually show the device face and the blood next to it? Would a hypoattenuating thickening be visible at this window? Are metal artefacts discussed?
- **Logic.** Does the text's conclusion follow from the figures? Over-claims ("no thrombus" when artefacts hide 1–2 mm at the hub; "high risk" from a model without the device in the domain)? Is "presence" (CT) clearly separated from "risk" (CFD)?
- **Consistency.** Numbers in the text vs `4_postprocessing/run6/report_numbers.json`; figure captions vs figure content; device type named consistently (STATUS notes disagree between Amulet and Watchman — check what the report says and what the CT shows); methods text vs what was done (LA = manual thresholding + masking + manual paint/erase, not region growing).
- **References.** "Proper academic references": every entry in `references.bib` must exist with the stated authors/year/journal/DOI — verify each one (PubMed lookup tools, DOI resolver, arXiv). Flag preprints (arXiv) as weaker, any reference not cited in the text, any claim needing a source that has none (e.g. ECAP threshold, Q-criterion value, flow scaling).
- **Figures.** Legible at print size, colour bars with units, scale bars/orientation on CT, panels referenced in text.

## 5. Device segmentation (+1 extra)
Candidates (all in `1_segmentation/device/`, see its README): `manual/Device_manual.*`, `gamma/Device_gamma_wire_v4_06112026.*`, `unet/Device_unet_wire.*`, each `.seg.nrrd` + `.stl`; older STLs in `6_paraview_package/surfaces/`.

Attack:
- **Device type.** Identify it from the CT morphology (single lobe without a separate disc → Watchman/Watchman FLX family; lobe + disc with two hubs → Amulet-type) and from the slides (grep `docs/*.pdf` text for "Case 3", device names). The user and the CT agree on an **Amulet-type** device (two hubs 11.7 mm apart, ~28 mm disc, ~22 mm lobe); notes before 06/11/2026 that say Watchman are wrong. Check that the segmentation shape matches an Amulet wireframe (disc + waist + lobe).
- **Wireframe only.** Fraction of the mask that is blood between wires, streak artefacts, hubs blooming, wall tissue (sample CT HU inside the mask; compare the volume with a plausible wire-frame volume). Stray islands (`connected_components`, `components_under_50_voxels`).
- **Accuracy.** Missing struts, broken rim, holes in the frame; overlay on CT slices.
- **Which one is submitted, and is there an .stl of that one** (each of the three has an `.stl` since 06/11/2026; check). Units of the STL (mm vs m).

---

## Severity guide
Use it to price findings; adjust with judgement and say why.

| Severity | Meaning | Typical cost |
|---|---|---|
| Hard fail | The rubric states a condition that zeroes or caps the item (bare yes/no; missing PDF; >500k cells; required file missing) | the item, or most of it |
| Major | A rubric bullet clearly not met (veins stop before the first branch; MV cap not separable; no ParaView files; report > 2 pages; unverifiable reference) | 25–50 % of the criterion |
| Minor | Bullet met with visible defects (a few islands; slight under-segmentation; one figure unreadable; ambiguous file naming) | 5–15 % of the criterion |
| Note | Not penalised by the rubric wording, but a grader may comment | 0 |

Per-criterion weights for pricing: 1 → 3 pts, 2 → 2 pts, 3 → 2 pts, 4 → 3 pts, 5 → 1 pt.
