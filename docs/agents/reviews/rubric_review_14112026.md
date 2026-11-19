# Rubric review, 14/11/2026

Mock grade written by an AI (five adversary agents, one per criterion, then a defence agent that tried to refute each finding and re-measured the key ones). The real professors may weigh things differently; what to change is the author's decision. Raw findings: `rubric_review_14112026_raw/findings_c1..c5.md`. Deterministic checks: `4_postprocessing/make_submission.py` copies, `checks.json` was run with `.claude/skills/rubric-adversary/scripts/deliverable_checks.py`.

Submission set reviewed (`submission/`, assembled 14/11/2026, run8):

| Rubric item | File |
|---|---|
| 1 LA segmentation | `Case3_LA_segmentation_HugoJal.seg.nrrd` |
| 2 meshes | `HugoJal_Case3_LA_surface_mesh.stl`, `HugoJal_Case3_LA_volume_mesh.bdf` |
| 3 simulation | `HugoJal_Case3_ParaView_package.zip` (564 MB; a download link still has to be created) |
| 4 report | `HugoJal_Case3_report.pdf` (2 pages + 1 references page) |
| 5 device (extra) | `HugoJal_Case3_device_segmentation_gamma.stl` and `..._unet.stl` |

## Scorecard
Likely = adversary cost after the defence pass. Harsh = a grader in a bad mood (adversary prices, and criterion 3 if the link does not work).

| Criterion | Max | Likely | Harsh | Main reason |
|---|---|---|---|---|
| 1 Segmentation | 3 | 2.7 | 2.4 | flat patch ~6 mm inside the lumen on the posterior wall (undocumented); mask ~0.4 mm inside the CT edge; RIPV only just past its bifurcation |
| 2 Meshes | 2 | 1.9 | 1.6 | mitral cap 6.5 mm below the annulus (report says "on its annulus") and smaller than the slide range; model frame; RIPV cap 8.9 mm |
| 3 Simulation | 2 | 1.8 | 1.2 | package is complete and works; risk is the untested download link; generic BCs, no mesh/dt study, A wave absent |
| 4 Report | 3 | 2.5 | 2.2 | text/figure mismatch on retention (Fig. 3a sphere vs 60 % layer), "both next to the hub" wrong, thin-below-3-mm borderline, a few unsourced statements, dense figures |
| Subtotal | 10 | 8.9 | 7.4 | |
| 5 Device (extra) | 1 | 0.75 | 0.5 | hand-edited gamma mask is ~half blood-level voxels; U-Net perforated; two STLs, none named as graded |

No hard fails: the report is 2 body pages with an explicit answer and CT + simulation evidence; all mesh conditions hold (closed, manifold, 6 regions at 20-60 deg, 271 908 tets, skewness 0.907).

## Blocking issues (fix before submitting)
1. **ParaView download link.** The grader receives only a link (the zip is 564 MB, not in git). Upload, test it logged out, write the link in the upload form or the report, keep a smaller fallback (~100 MB: every 5th step + surfaces). Up to 1.5 of 2 points depend on it.
2. Nothing else blocks; everything below is points on the margin.

## Findings by criterion (after the defence pass)
### 1. Segmentation
- [WEAKENED] C1-1 flat posterior patch, ~9 cm2, 4-6 mm of HU 360-430 lumen beyond it (re-measured by the defence) — cost 0.1-0.15 — fix: document as a deliberate coronary-sinus/AV-groove exclusion if it was one (README + one line in the report is not needed); do **not** repaint now, the mesh and the simulation are built on this mask.
- [WEAKENED] C1-2 RSPV root flat cut, bright lobe beyond it, may be the right pulmonary artery — cost 0-0.05 — fix: look in Slicer 3D (5 min); if it is the RPA, say nothing.
- [WEAKENED] C1-3 mask ~0.43 mm inside the CT half-maximum edge — cost 0.03-0.05 — defend as a threshold convention (~300 HU).
- [WEAKENED] C1-4 mitral hinge points 1.6 mm outside the mask on average (max 4.5) — cost 0-0.05 — defend; the mask section at the annulus plane (856 mm2) equals the mesh (855).
- [WEAKENED] C1-5 RIPV just past its bifurcation; LIPV and LSPV clearly past theirs — cost 0-0.05 — defend.
- [CONFIRMED, cost 0] C1-6 README says device overlap 0; gamma overlaps by 37 voxels (0.004 mL); terracing is cosmetic.

### 2. Meshes
- [WEAKENED] C2-1 mitral cap at z = -6.5 mm, 5.3 cm2 (26 mm equivalent, 32 x 19 mm oval); the slide says "around 28-42 mm"; the 4-6 cm2 target is in no slide in `docs/` — cost 0.05-0.1 — fix: report wording "cut 6.5 mm below the annulus plane, narrowed to a physiological 5.3 cm2 orifice" (same length).
- [WEAKENED] C2-2 LA STL/BDF are in the model frame; the transform is only inside the zip — cost 0-0.05 — fix: copy `transform_LPS_to_model.json` into `submission/` (1 min).
- [WEAKENED] C2-3 PV extension is ~5 mm true cylinder then a blend; RIPV cap 8.9 mm (the vein is genuinely 9-10 mm in the CT) — cost 0-0.03 — defend.
- [REFUTED as cost] C2-4 two cells above 0.9 skewness (0.907, limit for "poor" is 0.95); C2-5 no mesh study (not asked in criterion 2).
- [CONFIRMED, cost 0] C2-6 `pv_cuts.json` areas are stale (217/189/61/182 vs caps 247/144/63/133).

### 3. Simulation
- [WEAKENED] C3-1 link not created yet — see blocking issue.
- [WEAKENED] C3-2 valve motion "up to 8.9 mm" vs 9.25 mm in beat 4 and 9.8 in `mitral_bc.json` — cost 0.02.
- [WEAKENED] C3-3 RIPV 9 mm gives 9 % of the inflow (anatomy, confirmed in the CT) — cost 0.03-0.05.
- [WEAKENED] C3-4 no mesh or time-step study; ECAP near the device and retention vary by beat — cost 0.05 — fix: say so in limitations if there is room.
- [WEAKENED] C3-5 no A wave, blunted S wave, ~2 mL (2.6 % of SV) passes the "closed" valve in systole — cost 0.03.
- [WEAKENED] C3-6 BCs are the course curves, only geometry/valve axis/device are case-specific — cost 0.03; the report already says "generic".
- [REFUTED as cost] C3-7 device not in the domain (disclosed).

### 4. Report
- [WEAKENED] C4-1 the 60 % vs 40 % retention is reproducible (5 mm layer: 62 % / 58 %; independent review 63-69 % vs 40-45 %), but Fig. 3a is the 8 mm sphere (64 % / 27 %), and the near-wall control (63 vs 67 % at 2.63 s) is not mentioned — cost 0.1 — fix: one sentence saying the 60 % is for the 5 mm layer, or reseed Fig. 3a.
- [WEAKENED] C4-2 "both right next to the metal hub" is wrong: one piece is at the hub, the other at the device rim (radius 12-17 mm, plate parallel to the face, 39-51 mm3) — cost 0.1 — fix: "one at the hub and one at the rim".
- [WEAKENED] C4-3 "thin, below 3 mm" holds for 96 % of rays (median 1.0, p90 2.6, max 4.4 mm); brightness is in the thrombus range; decision rests on shape — cost 0.1-0.15 — fix: add "hub region indeterminate", keep "no DRT" with the limitation sentence.
- [WEAKENED] C4-4 Fig. 1d is the smallest figure, no L/R labels — cost 0.05. C4-6 Fig. 5a does not mark the device; TAWSS ticks crowded — cost 0.03.
- [WEAKENED] C4-7 "possible but low" has no criterion; the independent review says "inconclusive, leaning mildly thrombogenic" and that the flat device biases the estimate down — cost 0.05-0.1 — fix: one clause on the bias direction.
- [WEAKENED] C4-8 unsourced statements (stroke risk, 80 mL stroke volume, appendage leak, Q-criterion, ECAP origin); Ronneberger cited for nnInteractive is loose — cost 0.05-0.1. The project rule is few references; Dukkipati 2018 and KawelBoehm 2020 are in `references.bib` if one is wanted.
- [WEAKENED] C4-9 "the last beat repeated the previous one": flow, volume and wall medians do (0.1-7 %), washout and ECAP tails do not — cost 0-0.05.
- [REFUTED as cost] C4-5 two-page limit met with 10 pt text, 1.5 cm margins (note: dense).

### 5. Device
- [WEAKENED] C5-1 hand-edited gamma mask: 50 % of voxels at or below 454 HU, 27 % below 340 HU, 14 % above 700 HU (reproduced); edit added ~20 800 voxels at median 339 HU — cost 0.1-0.2 — defend ("on a 0.45 mm CT the braid appears as sheets; the mask is the envelope of the sheets") or hand in the U-Net only.
- [WEAKENED] C5-2 U-Net is purer but perforated (windows in the lobe wall); the report's "merges the wires into thick bands" is contradicted by the thickness numbers (U-Net 0.50 vs gamma 0.63 mm) — cost 0.05 — fix: "the U-Net leaves gaps in the lobe wall and disc".
- [WEAKENED] C5-4 two STLs, nothing says which is graded — cost 0-0.1 — fix: one sentence in the upload form ("graded: ..._gamma.stl; ..._unet.stl is the comparison").
- [REFUTED as cost] C5-3 stray specks (0.55 and 0.83 mm3). [REFUTED, supports the student] C5-5: "Amplatzer-type" is correct; the CT cannot separate Amulet from the Cardiac Plug. [duplicate of C2-2] C5-6 device STLs in the CT frame, LA STL in the model frame.
- [CONFIRMED, cost 0] C5-7 device READMEs still describe the file before the 09/11 edit.

## Fix plan before 20/11/2026 (points per hour)
| # | Action | Time | Points | Needs |
|---|---|---|---|---|
| 1 | Upload the zip, test the link in a private window, put it in the upload form (and optionally the report); optional ~100 MB fallback | 30-60 min | protects up to 1.5 | the author |
| 2 | Report text (same page count): "one at the hub, one at the rim"; "cut 6.5 mm below the annulus plane"; 60 % is the 5 mm layer; "hub region indeterminate"; U-Net sentence; bias direction of the flat device; Dukkipati/KawelBoehm if room | 45 min | 0.3-0.4 | rebuild PDF + `make_submission.py` |
| 3 | Add `transform_LPS_to_model.json` to `submission/`; one line in the upload form: "graded device = gamma; U-Net is the comparison; device STLs in CT/LPS mm, LA mesh in model frame" | 5 min | 0.05-0.15 | none |
| 4 | Fix the package README (two dangling references, "about 9 mm"), rebuild the zip, re-upload | 20 min | 0.02-0.05 | do before step 1 |
| 5 | Look at the RSPV root and the posterior patch in Slicer; document the patch as a deliberate exclusion if it was one | 20 min | 0-0.15 | the author (Slicer) |
| 6 | Optional: erode/threshold the added device voxels or hand in the U-Net only | 30 min | 0.1-0.2 | decision |
| 7 | Correct the project documents (list below) | 30 min | 0 | none |

Nothing here needs Fluent or a re-run. Do not change the LA segmentation, meshes or simulation now: they depend on each other.

## Things to defend rather than fix
- Mask a fraction of a voxel inside the CT edge: threshold/partial-volume convention (boundary ~300 HU).
- RIPV 9 mm: the vein is genuinely 9-10 mm in the CT; the inflow share follows from the cap area.
- Generic BCs: the class method uses the course curves; geometry, valve axis and device are the patient's.
- 5.3 cm2 mitral orifice: functional orifice area; the cap sits below the annulus in a funnel.
- No mesh/time-step study: not asked by the rubric; solver convergence on all 350 steps is shown.
- Device as flat wall: stated in the report; it probably underestimates local risk.
- Gamma mask is an envelope of the braid sheets at 0.45 mm resolution.

## Facts to correct in the project documents (from the defence pass)
1. `thrombus_check/README.md` and `size_sd_mm`: values are standard deviations, not sizes (extents ~5 x 9 x 27 mm and 2.6 x 3.1 x 10 mm); thickness along the device axis median 1.0, p90 2.6, max 4.4 mm.
2. `main.tex` 3.1: "both right next to the metal hub" -> one at the hub, one at the rim; piece 1 is a plate parallel to the face.
3. `device_ct_hu.json` "atrial_face_layer fraction_below_150HU 0.33" conflicts with "blood reaches the face over its whole surface": define the layer before citing it.
4. `2_mesh/run8_07112026/pv_cuts.json` areas are stale (217/189/61/182; caps 247/144/63/133).
5. `6_paraview_package/README.md`: "up to 8.9 mm" -> about 9 mm (beat 4: 9.25; `mitral_bc.json`: 9.8); remove the references to `make_paraview_package.py` and `4_postprocessing/run8/README.md`.
6. LA and device READMEs: gamma/LA overlap is 37 voxels (0.004 mL), not 0; gamma is 3.84 mL and ~50 % at or below 454 HU, not 1.94 mL / 14 %.
7. The "2.3 mm mean offset" for the mitral hinge points belongs to a deleted mesh; on run8 it is 1.6 mm mean, 4.5 mm max.
8. `main.tex` l.72 wording (see fix 2).
9. The "4-6 cm2 MV orifice, course requirement" is not in `docs/*.pdf` (slide 23: MV around 28-42 mm): cite the source or reword.
10. "7 % of PV paths reach the device region" (24 of 368 pathlines, `paths_pv_t2.63.vtp`) is only in `run8/README.md`; the summary file does not carry it.
11. `report_numbers.json` `periodicity_ecap_rel_change_near` = 0.27 is mean-based; footnote it next to "7 %".
