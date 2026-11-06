# Rubric review — 06/11/2026

This is a mock grade written by AI agents from the rubric text, made with the `/rubric-adversary` skill. Five strict "examiner" agents (one per criterion) produced 36 findings, and a defence agent then tried to refute each one. The scores below use the defence-checked costs. The professors may weigh things differently, and the decisions on what to change are the student's. Deadline: **20/11/2026 23:59**.

Working files (scripts, renders, numbers) are in the session scratchpad and are not kept in the repo. Every number below was recomputed from the project files.

## Submission set reviewed

| Rubric item | File assumed | Problem |
|---|---|---|
| 1. LA segmentation (.nrrd) | `1_segmentation/Hugo_Jal_left_atrium_segmentation.nrrd` | No case id in the name. `HugoJal_Case3_stl.seg.nrrd` is a different mask built from the STL; do not submit it. |
| 2. Surface .stl / volume .bdf | `2_mesh/mv_aligned_03112026/HugoJal_Case3_mvz_03112026.stl` / `.bdf` | The old `2_mesh/HugoJal_Case3*.stl/.bdf` are worse (18 zones at 30°, skewness 1.0); leave them out. |
| 3. ParaView files | `6_paraview_package/` (1.2 GB) | Exists only on this laptop and is git-ignored. |
| 4. DRT report (PDF) | `5_report/main.pdf` | — |
| 5. Device (.stl) | not designated (manual / gamma / U-Net) | The choice changes this criterion's score by about 0.5. |

## Scorecard

| Criterion | Max | Likely | Harsh | Main reason |
|---|---|---|---|---|
| 1. Segmentation | 3 | 2.3 | 2.0 | Two of the four veins stop 5–8 mm before their first branch. The LA mask covers the device's atrial face. The file name has no case id. |
| 2. LA meshes | 2 | 1.6 | 1.4 | Two PV cylinders are not aligned with their veins. The mesh is in a rotated frame, so it cannot be overlaid on the CT. |
| 3. Simulation | 2 | 1.8 | 1.75 | Sound work; only wording and small issues. **About 1.0 if the ParaView data does not reach the graders.** |
| 4. DRT report | 3 | 2.35 | 2.15 | The CT figure shows a dark area at the hub that the report does not explain. 12 author first names in the references are wrong. |
| **Total, criteria 1–4** | **10** | **≈ 8.0** | **≈ 7.3** | |
| 5. Device (extra) | +1 | +0.7 | +0.6 | Assumes the gamma or U-Net STL is submitted and the device type is named. **+0.1–0.2 if the manual `Device.seg.nrrd` is submitted.** |

How the scores were computed: each criterion starts at full marks. The defence's corrected cost of every confirmed or weakened finding is then subtracted: the middle of the range gives "Likely", the upper end gives "Harsh". Duplicates are counted once. Refuted findings cost nothing.

## Blocking issues (fix before submitting)

1. **The ParaView data has to reach the graders** (C3-4).
   - `6_paraview_package/` is complete. It loads in pvbatch, all 88 steps and every file the README lists are there.
   - But it is 1.2 GB, git-ignored, and cannot be rebuilt from a clone, because the source results (4.3 GB) are git-ignored too.
   - Zip it, share a download link (e.g. OneDrive, "anyone with the link"), and put the link in the PDF and the README. Test the download in a private window.
   - If the link fails, criterion 3 drops by up to 1 point.
2. **Do not hand in the manual `Device.seg.nrrd` as the device segmentation** (C5-2).
   - It is a solid plug, not a wireframe: 58 % of its voxels are at blood level (≤ 454 HU), and it fills 85 % of the gap between disc and lobe.
   - Hand in the gamma wire-frame STL (most wire-only: 6.7 % blood-level voxels) or the U-Net STL. Give it a case-named file name.
3. **Make the hand-in list explicit and case-named** (C1-3, C2-2, C5-4).
   - LA segmentation: a renamed copy of `Hugo_Jal_left_atrium_segmentation.nrrd`, e.g. `Case3_LA_segmentation_HugoJal.nrrd`, with the segment renamed from "Segment_1" to "LA".
   - Mesh: the mvz `.stl` and `.bdf` only.
   - Device: one STL.
   - Make copies with new names; do not rename the originals.

## Findings by criterion

### 1. Segmentation (3)
- [WEAKENED] **C1-1: veins and the first branch** — cost 0.3–0.45. Rubric: "at least up to the first branch".
  - Right superior and left superior PVs reach their first division (within 0–3 mm).
  - Left inferior stops about 5 mm short of its main split; right inferior about 7–8 mm short (thin side branches leave at 3–5 mm).
  - Two claims were both too strong: the examiner's "all four, 3–13 mm short" and STATUS 31/10's "≈ first branch for all four".
  - `main.tex:79` says "The four pulmonary veins (PVs) were kept up to their first branch". That is true for two of the four.
  - Evidence: the CT, followed outward from each vein's mask edge along the bright lumen (geodesic, > 280 HU), with distance per mm and per vein.
  - Fix: extend the two inferior veins in Slicer (about 1 h, new dated file), or soften `main.tex:79`.
- [CONFIRMED] **C1-2: device inside the LA mask** — cost 0.2–0.35. Rubric: "excluding the device".
  - 16.7 % of both the gamma and the manual device masks lie inside the LA mask. This holds over 23 axial slices, and the whole disc section is inside the LA outline at k = 184.
  - It is a thin layer (about 1 mm, 0.2 mL of wire voxels), but a grader who shows both segments in Slicer will see it.
  - Fix: Slicer → Logical operators → Subtract the device (dilated 1 voxel) from the LA segment, and save as a new dated file. About 10 min.
- [CONFIRMED] **C1-3: naming** — cost 0.1–0.2.
  - `Hugo_Jal_left_atrium_segmentation.nrrd` has no case id; its segment is "Segment_1"; it is tagged "inprogress".
  - `HugoJal_Case3_stl.seg.nrrd` is not an alternative to hand in:
    - it was built from the STL, so it includes the cylinders (+36.8 mL);
    - it has 277 slices, while the CT has 274;
    - its second label is mostly device.
- [WEAKENED] **C1-4: contour ~0.5 mm inside the lumen edge** — cost 0. This is within normal manual tolerance.
- Checked and OK:
  - The mitral valve is included: the mask reaches 7.6 mm past the annulus plane.
  - No leaks.
  - One connected component, no holes.
  - The roof is not flat-cut.
  - The mask is on the CT grid, and its header has no patient data.

### 2. LA meshes (2)
- [WEAKENED] **C2-1: PV cylinders** — cost 0.15–0.25.
  - The cylinders follow the L2 recipe: placed at the PV position, 10–25 mm, sharp ~90° edges.
  - But caps 1 and 2 point about 82° away from the axis of their vein.
  - The cylinders are 1.5–2× the lumen diameter, so they reach into lung on the CT.
  - The examiner rated this "major". The defence lowered it because the method is the taught one.
- [CONFIRMED] **C2-3: mesh not in the CT frame** — cost 0.1–0.2.
  - The mvz STL is rotated into the model frame (`transform_LPS_to_model.json`). A grader who loads it over the CT in Slicer will find it outside the image and cannot check the mitral cut, even though the cut is good.
  - Fix (15 min): add a copy of the STL in the CT frame (only for viewing, labelled as such), or point to `check_mitral_on_ct.png` in the report or README.
- [WEAKENED] **C2-2: two candidate mesh pairs** — cost 0–0.1. Packaging only; solved by blocking issue 3.
- [CONFIRMED, note] **C2-4: mitral cap outline about 20 % smaller than the annulus** — cost 0–0.05. The cut plane is on the annulus (refit within 0.2°). The outline is smaller because the segmentation stops short of the AV groove. Defend it.
- [REFUTED] **C2-5** (a 7th zone at 20°): the slides say "~20–40°" and teach merging; there are exactly 6 zones at 25–40°.
- [REFUTED] **C2-6** (method attribution): `main.tex:79` is accurate.
- [note, counted under C3] **C2-7**: no mesh-independence study.
- Checked and OK:
  - Surface: closed, 0 non-manifold edges.
  - Volume: 307,927 tetrahedra, 0 negative volumes, skewness max 0.885 (none above 0.9), and the BDF boundary is exactly the STL.
  - Caps: exactly 6 zones at 25–80°, flat caps, rim angles 83–97°.
  - The body is not oversmoothed: median distance 0.00 mm to the segmentation surface.

### 3. Simulation (2)
- [WEAKENED] **C3-4: ParaView data delivery** — 0 if the link works, up to 1 if it doesn't. See blocking issue 1.
- [WEAKENED] **C3-1: device not in the fluid domain** — cost 0.05–0.1.
  - The limitation is stated (`main.tex:113`).
  - But `main.tex:111` says the conditions occur "on and around the atrial face of the device". Reword to "on the wall that closes the appendage, where the device face sits".
- [CONFIRMED] **C3-5: ParaView colour bars** — cost 0.05. `open_in_paraview.py:36` sets a white background, but the colour-bar text is also white, so it is invisible. Set the title and label colour to black (5 min).
- [WEAKENED] **C3-2: no mesh or time-step independence study; Re about 5,300 at the MV, solved as laminar** — cost 0–0.05. Course recipe; defend.
- [WEAKENED] **C3-3: generic boundary-condition curves** — cost 0–0.05. In this course "case-specific" means the patient's geometry with the course curves. The scaling is cited, and the limitation is stated.
- [notes, cost 0] **C3-6, C3-7, C3-8**:
  - C3-6: the rigid wall gives almost no PV inflow in systole.
  - C3-7: the MV amplitude is written as 8.9, 9.7 or "up to 10" mm in different places. All are true; the internal notes should be made consistent.
  - C3-8: "renewed slowly" is fine; RRT could back it up.
- Checked and OK:
  - Run: 351 "converged" messages for 350 steps, 0 errors; solver settings match the slides.
  - Flow values: SV 72.9 mL, CO 5.0 L/min, mass balance within 1.3 mL per beat.
  - Mitral motion: along z, and the LA volume change equals the volume swept by the cap.
  - Beats 3 and 4 agree (TAWSS map r = 0.95).
  - Package: every README file exists and it loads headless.

### 4. DRT report (3)
- [WEAKENED] **C4-1: the CT evidence does not explain the dark area at the hub** — cost 0.25–0.4.
  - Fig. 1d shows dark areas on the atrial face next to the hub. They are a thin sheet (0.9 mm) lying in the axial acquisition plane, centred on the hub's slices, so most likely a metal streak. The hub tip touches bright contrast blood, so **"No DRT" stands**.
  - But the report gives no window, no sentence on artefacts or on the hub limitation, and leaves out your own thrombus check (`4_postprocessing/thrombus_check/`).
  - Fix (about 1 h, within 2 pages):
    - one or two sentences: blood at the device face is 321 HU at the 5th percentile; there is no low-density layer; the dark strips are a beam-hardening streak from the hub; a very small thrombus on the hub cannot be fully excluded;
    - give the window in the caption;
    - optionally replace or add a panel from `thrombus_check.png`.
- [CONFIRMED] **C4-2: wrong author first names** — cost 0.1–0.15.
  - In `references.bib`, Zhong 2024 (PMID 37291248) and Vogl 2024 (PMID 39493311) have 12 wrong first names. The correct ones:
    - Zhong: Zhaoyang Zhong, Yiting Gao, Soma Kovács, Lukas Spano, Simon Sonntag;
    - Vogl: Emily Vitale, Sunyoung Ahn, Alejandra Chavez Ponce, Jeremy Collins, Anders Kramer, Yuheng Jia, Davorka Lulic.
  - Fix (10 min): correct them, or switch to initials.
- [WEAKENED] **C4-4: figures** — cost 0.05–0.15. No panel letters inside the images, Fig. 3 colour-bar titles partly hidden, no CT window, the CT evidence panel is small.
- [WEAKENED] **C4-6: two wordings slightly stronger than the data** — cost 0.05–0.1. The weak one is "highest ECAP of the whole atrium": in the last beat only 35 % of the top-1 % ECAP area is within 10 mm of the device.
- [WEAKENED] **C4-3: Morales cited as arXiv** — cost 0–0.05. It is now published as Sci Rep 2026;16:5426, doi:10.1038/s41598-025-34972-7, PMID 41545408. The examiner checked this on PubMed; the defence did not re-check it.
- [WEAKENED] **C4-5: device never named** — counted under C5.
- [WEAKENED] **C4-7, C4-9**, [REFUTED] **C4-8**: cost 0. "Slowest blood" is supported (0.060 vs 0.088 m/s); ECAP is cited; the layout is within the rules.
- Checked and OK:
  - Length: 2 body pages + 1 page of references, 10 pt.
  - Answer: explicit "No DRT" in the abstract, results and conclusion. Presence (CT) is kept separate from risk (CFD).
  - Evidence: images from both the CT and the simulation.
  - References: all 7 exist, with correct DOIs, and all are cited.
  - The report's numbers match the project data.
  - The methods text is accurate.

### 5. Device segmentation (+1)
- [WEAKENED] **C5-1: device type** — cost 0.05–0.1.
  - The CT shows an **Amulet-type** device: two hubs 11.7 mm apart (both above 2500 HU); a flat disc of about 28 mm; a waist; a closed lobe of about 22–24 mm.
  - The earlier "Watchman FLX" note (STATUS 03/11, gamma README line 5) is wrong.
  - The report's words "disc"/"hub" already fit an Amulet. Name the device once in the methods ("Amulet-type occluder, ≈ 22 mm lobe / 28 mm disc").
  - If you have a clinical record saying otherwise, that overrides the CT.
- [CONFIRMED, conditional] **C5-2 / C5-3: the manual mask is solid and has no mm/CT-frame STL** — cost 0.6–0.8 only if it is submitted. See blocking issue 2.
- [WEAKENED] **C5-5: U-Net** — cost 0.05–0.1. 32 % of its voxels are at blood level. Partly expected, because the Amulet lobe is a fabric-covered braid.
- [WEAKENED] **C5-6: gamma** — cost 0.05. The most wire-only, with a clear disc + waist + lobe.
- [CONFIRMED] **C5-4** (no designated file), **C5-7** (hub streaks inside the masks), **C5-8** (small islands) — 0.05 each.
- [duplicate] **C5-9** = C1-2.
- Checked and OK: the gamma and U-Net STLs are in mm, in the CT frame, closed and manifold, and match their .nrrd within 0.5 mm.

## Refuted findings (no action)
- C2-5: a 7th zone at 20° separation.
- C2-6: tool attribution in the methods.
- C4-8: compressed layout.

## Fix plan before 20/11/2026
Ordered by points recovered per hour. None of these needs Fluent or a new simulation.

| # | Fix | Time | Points protected or recovered |
|---|---|---|---|
| 1 | Pick the device STL (gamma or U-Net) and make case-named copies of the LA .nrrd, the mvz mesh pair and the device STL. | 15 min | up to +0.5–0.6 (C5) and +0.1–0.3 (C1, C2) |
| 2 | Share the ParaView package with a tested link, written in the PDF and the README. | 30 min | protects up to 1.0 (C3) |
| 3 | Subtract the device from the LA segment in Slicer (new dated file). | 10 min | +0.2–0.35 (C1) |
| 4 | Report text: the hub-artefact sentences and the CT window; correct the bib names; Morales → Sci Rep; name the device "Amulet-type"; reword `main.tex:111` and the "highest ECAP" sentence; make `main.tex:79` match the veins. | 1–1.5 h | +0.4–0.7 (C4, C3) |
| 5 | A copy of the STL in the CT frame (for viewing), or a pointer to `check_mitral_on_ct.png`. | 15 min | +0.1–0.2 (C2) |
| 6 | `open_in_paraview.py`: black colour-bar text. | 5 min | +0.05 (C3) |
| 7 | Extend the right-inferior and left-inferior veins to their first split in Slicer (new dated file). The mesh and simulation can stay as they are, since the PV cylinders replace that part anyway; mention this. | ~1 h | +0.3–0.45 (C1) |
| 8 | Correct the internal notes that say "Watchman FLX" (STATUS, `gamma_experiment/README.md`). | 5 min | 0, but stops the error spreading |

Fixes 1–6 take about 2.5 h and would bring the likely score to roughly 8.6–8.9 /10, plus about 0.7 extra.

## Things to defend rather than fix
- **PV cylinders**: "Flow extensions were added at each PV ostium as taught (flat caps, 10–25 mm, sharp edges), normal to the ostium."
- **Generic boundary conditions**: "Patient geometry with the course boundary-condition curves; the mitral flow was scaled to a normal cardiac output (Kawel-Boehm 2020) because the annulus cap is larger than the leaflet orifice."
- **No convergence study**: settings follow the course recipe; conclusions use relative contrasts between regions; beats 3 and 4 agree.
- **Device not in the fluid domain**: the wall that closes the appendage stands in for the device face. This limitation is already in the report.
- **Mitral cap smaller than the annulus**: the cut plane was fitted on the CT annulus; the outline follows the segmented wall.

## Open questions for the student
1. Which device file do you want graded: the gamma lattice or the U-Net shell?
2. Is there a clinical record of the device model (where did "Watchman FLX" come from)?
3. Is the patient in atrial fibrillation, and how long after implantation was the CT taken? One sentence on each would strengthen the report.
4. How will the 1.2 GB package be delivered (upload limit, or a link)?
