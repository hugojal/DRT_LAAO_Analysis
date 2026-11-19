# Rubric review — 17/11/2026 (final hand-in package `submission/`)

This is a mock grade written by AI agents from the rubric text. Five strict "examiner" agents (one per criterion) produced 37 findings, and a defence agent then tried to refute each one. The defence re-measured the key findings itself: the vessel above the right roof cut, and the composition of the device STL. The real professors may weigh things differently, and the decisions on what to change are the author's. Deadline: **20/11/2026 23:59**.

The raw findings, the defence table and `checks.json` are in `rubric_review_17112026_raw/`. The scripts and renders were in the session scratchpad and were not kept.

**Mock grades vary between runs.** This review found things that the 14/11 review (run8 package, likely 8.9/10) did not look for: the right superior vein trunk, and the closed device STL, which is new since 16/11. Part of the drop below therefore comes from the reviewers, not from the work getting worse.

## Submission set reviewed (`submission/`, built 16–17/11/2026, run9)

| Rubric item | File | Byte-identical to |
|---|---|---|
| 1 LA segmentation | `Case3_LA_segmentation_HugoJal.seg.nrrd` | `1_segmentation/la_v2_06112026/…_06112026.seg.nrrd` |
| 2 meshes | `HugoJal_Case3_LA_surface_mesh.stl`, `HugoJal_Case3_LA_volume_mesh.bdf` | `2_mesh/run9_15112026/…` (the files imported into Fluent) |
| 3 simulation | `HugoJal_Case3_ParaView_package.zip` | 605 MB, 1,547 entries, 1.14 GB unpacked, no patient files; **no download link yet** |
| 4 report | `HugoJal_Case3_report.pdf` | `5_report/main.pdf` (same md5) |
| 5 device (extra) | `HugoJal_Case3_device_segmentation_manual.stl` (closed, smoothed, edited gamma) and `…_unet.stl` | `1_segmentation/device/gamma/…closed_both_16112026.stl`, `device/unet/Device_unet_wire.stl` |

## Scorecard

| Criterion | Max | Likely | Harsh | Main reason |
|---|---|---|---|---|
| 1 Segmentation | 3 | 2.25 | 1.8 | The right superior PV trunk is cut flat at the roof, 13–15 mm before it divides. The mesh's "RSPV" sits on a smaller anterior vein. There is also a planar under-cut on the septal wall. |
| 2 Meshes | 2 | 1.75 | 1.5 | The RSPV extension is oversized and off the vein axis. The mesh is in the model frame and the transform is not in `submission/`. The mitral outlet is below the annulus, with no reason given in the report. |
| 3 Simulation | 2 | 1.7 | 1.2 | The package works and the valve motion is correct. The package carries a run8 README that contradicts the report, and the convergence CSV has a parser error. **About 0.7 if no working link reaches the grader.** |
| 4 Report | 3 | 2.1 | 1.5 | "No DRT" is given without a thickness number and without the single-phase caveat. "Highest 5 %" cannot be traced to any file, and RRT is attributed to Vogl. Retention is understated, and Fig. 5a is unreadable. |
| **Total, criteria 1–4** | **10** | **≈ 7.8** | **≈ 6.0** | |
| 5 Device (extra) | +1 | +0.5 | +0.3 | The STL handed in as "manual" is a filled solid: 2.1 mL of non-wire material, 65 % of its voxels at blood level. That breaks "only the device wireframe". |

How the scores were computed:
- **Likely**: full marks minus the defence's cost for each confirmed or weakened finding, counting duplicates once.
- **Harsh**: full marks minus the examiners' own prices (upper end) for the same findings.

No hard fails:
- the report has 2 body pages and an explicit, justified answer, with CT and simulation evidence and 5 verified references;
- the meshes are closed and manifold, separate into 6 zones at 20–60°, and the volume mesh has 274,425 tetrahedra with skewness max 0.875 and 0 negative volumes;
- the segmentation is named after the case and is in one piece;
- the zip opens in ParaView 6.2.

## Blocking issues (fix before submitting)

1. **ParaView download link** (C3-1). Without a link, the grader gets no ParaView files, which costs about 1 of 2 points. Upload the zip with "anyone with the link" access, test it in a private window, and put the URL in the upload form, plus one line in the report if it fits. `SUBMISSION.md` gives the size as 564 MB; it is 605 MB.
2. **Device STL handed in as "manual"** (C5-1, C5-3).
   - It is the closing step that filled the hollow lobe: 5.83 mL, 21.7 % of voxels at or below 200 HU, against 0.15 mL in the edited mask before closing.
   - Hand in a wire-only STL instead, either the unfilled edited gamma (`Device_gamma_wire_v4_edited_09112026.stl` or `…_smooth_both_16112026.stl`) or the U-Net file alone. Give it an honest name, e.g. `…_device_segmentation_gamma_edited.stl`.
   - Keep the closed body only for the CFD distances. Re-render or re-caption Fig. 1b, and describe the method in `main.tex` l.71 as "semi-automatic tracing on a gamma-enhanced CT, edited by hand".
   - This is worth about +0.4.

## Findings by criterion (after the defence pass)

### 1. Segmentation (3)
- [CONFIRMED] **C1-1: the RSPV trunk is not segmented** — cost 0.5 (examiner 0.5–0.75).
  - The mask ends flat at the right LA roof (z ≈ 889 mm LPS). Beyond it, a lumen of about 10–11 mm at 410–460 HU continues for 13–15 mm before it divides.
  - The defence checked whether this is the right pulmonary artery. It is not:
    - from inside the LA the lumen is continuous along 25 mm, never dropping below 367 HU;
    - a wall (248–297 HU) and fat separate it from the right pulmonary artery;
    - the superior vena cava reads about 1690 HU.
  - So it is a pulmonary vein draining into the LA, running between the vena cava and the right pulmonary artery towards the right upper lobe.
  - The flat roof cut correctly keeps the right pulmonary artery out, but cuts this vein off with it.
  - The mesh's "RSPV" cap sits on a smaller anterior vein, which also stops 3–8 mm before its branches.
  - Fix: in Slicer, threshold-paint the trunk to just past its division (about 30 min, new dated file). The mesh and the simulation would then no longer match the `.nrrd` exactly; say so in one line, or accept the risk.
- [CONFIRMED] **C1-3: planar under-cut on the septal/anterior-inferior wall** — cost 0.1. About 6 cm² of blood-level CT, 3–5 mm deep, lies outside the mask. It is not the mitral cut: the patch centre is 25.5 mm on the atrial side of the annulus plane. The 14/11 review found the same patch.
- [WEAKENED] **C1-2: the "LSPV" horn vein tapers to a point** while its 5–6 mm lumen continues — cost 0.05–0.1. The left side is probably a common trunk plus a small superior vein; be ready to explain that.
- [CONFIRMED] **C1-4: the automatic RIPV extension ends in a blocky stub** — cost 0.05. Cosmetic.
- [note] **C1-5** (= C2-3): the stub of a small accessory vein. **C1-6**: `main.tex` l.71 "four PVs up to their first branch" is not true for the RSPV; this is counted under criterion 4.
- Checked and OK:
  - Mask: one component, genus 0, 156.0 mL.
  - Veins: the RIPV goes about 3 mm past its bifurcation; the LIPV goes past several branches.
  - Mitral valve: included, cut at the open valve.
  - Device: excluded (31 voxels of boundary contact).
  - Right pulmonary artery kept out; no leaks.
  - Header: no patient keys.

### 2. LA meshes (2)
- [WEAKENED] **C2-1: PV extensions** — cost 0.1. Flat cut, circular end, smooth blend and 90° rims follow the L2 slides, and three of the four caps are within "PVs around 10–25 mm". But the RSPV nozzle has 2–5× the area of the lumen, sits 5.8 mm off its centre and points 46° away from its axis; this shares a root cause with C1-1. The RIPV matches.
- [WEAKENED] **C2-4: mesh in the model frame** — cost 0.05–0.1. `transform_LPS_to_model.json` is only inside the zip, so a grader cannot overlay the mesh on the CT to check the mitral cut. Fix (5 min): copy it into `submission/` with a one-line note, or add a copy of the STL in the CT frame.
- [WEAKENED] **C2-2: mitral outlet** — cost 0.05.
  - The orientation is exact (0.00° to the annulus plane).
  - The cap is 6.5 mm below the annulus, within the 9.3 mm saddle height (leaflet level).
  - Its 32.2 mm long axis is inside the slides' 28–42 mm.
  - The "4–6 cm²" target is in none of the slides. Add half a sentence saying why the outlet is at leaflet level and narrowed (a normal diastolic orifice area, with a source).
- [WEAKENED] **C2-3** (= C1-5): an accessory-vein knob removed — cost 0–0.05, counted once.
- [note → C4] **C2-5**: the report says "a smooth 10 mm tube"; the build has a 3.5 mm circular end on a 7–16 mm loft. [REFUTED] **C2-6**: a binary STL is not penalised.
- Checked and OK:
  - Identity: the STL and BDF are byte-identical to the meshes simulated in Fluent, and the BDF boundary equals the STL.
  - Volume mesh: 274,425 tetrahedra, skewness max 0.875 with none above 0.9.
  - Zones: 6 at 20–60°, planar caps, 90° rims.
  - **Not oversmoothed**: the body lies within 0.19 mm (mean |d|) of the segmentation, the volume is +0.3 %, and the LAA–LSPV ridge is preserved.

### 3. Simulation (2)
- [CONFIRMED, conditional] **C3-1: no download link** — 0 if it is delivered, about 1.0 if not. See blocking issue 1.
- [CONFIRMED] **C3-2: the package's `device_sections/README.md` is the run8 text** — cost 0.1. It describes "a still layer covers the device" and "24 % in vortex cores", its numbers differ from the run9 `summary.json` beside it, and the report says "no vortex is trapped". Regenerate it from run9, or delete its interpretation, then re-zip.
- [CONFIRMED] **C3-5: convergence CSV parser bug** — cost 0.05.
  - The transcript prints iteration numbers of 10,000 and above as "!10003", with no space. The parser misses those lines, so steps 346–350 are marked False and the summary says 344/350.
  - The truth is 349/350: only step 131, in beat 2, hit the cap.
  - `SUBMISSION.md`'s explanation that those lines are missing is also wrong.
- [WEAKENED] **C3-4: generic boundary conditions** — cost 0.05–0.1.
  - The same pressure is applied at all four PVs, so the flow split follows the inlet area: the RIPV gets 6 %.
  - Peak PV inlet velocities are 0.75–0.78 m/s.
  - Inflow is almost all diastolic, because the wall is rigid.
  - Add one sentence.
- [WEAKENED] **C3-3**: near-device magnitudes changed between run8 and run9 (ECAP ratio 1.7 → 2.4) — cost 0.05; already limited to relative claims in the report.
- [notes, 0–0.03 each] **C3-6, C3-7**:
  - colour bars overlap in pvbatch, and one tick-label format prints literally as "%-#.2f";
  - `device_segmentation.stl` is not loaded by `open_in_paraview.py`;
  - the README says "8.9 mm" (the last beat reaches 9.25 mm) and "manual mask used for the distances" (wrong file);
  - `pv_pathlines.py` points at project paths.
- [REFUTED] **C3-8** (laminar at Re ≈ 7,400) and **C3-9** (device not in the domain, disclosed).
- Checked and OK:
  - Scripts: both run in pvbatch (15 and 23 sources, 88 steps), and the Fluent case and data open in ParaView.
  - **Mitral motion along the valve axis**: the cap normal is ±z at every step, the cap position equals `motion.prof` (r = 1.0000), and the funnel moves rigidly with it.
  - Flow values: SV 79.7 mL in every beat, CO 5.47 L/min, mass balance 0.44 mL.
  - Mesh during the run: remeshing kept it at 294k cells, below 500k.
  - Trajectories are in the report and can be reproduced from the package.

### 4. Report (3)
- [WEAKENED] **C4-1: "No DRT" is justified by shape only** — cost 0.3 (examiner 0.5).
  - The project's own ray measurement supports "thin" (≤ 2.5 mm on 90 % of rays, at most 3.25 mm), but the report gives no number against the 3 mm criterion it cites.
  - It also dropped the caveats from both CT analyses: one arterial-phase CT; streaks hide about 1–2 mm at the hub; late-phase CT or TEE would confirm.
  - Fix: one number and one Limitations sentence.
  - **Ground-truth risk**: the hub region is fairly uniform (median 133 HU, only 4 % below 0 HU), which looks more like soft tissue than metal streak. If the instructors' answer for Case 3 is "thrombus present", this answer costs far more than priced here.
- [CONFIRMED] **C4-3: "among the highest 5 % in both beats" cannot be traced to any file** — cost 0.15.
  - A re-ranking of the device band against same-size wall patches puts it at the 96th percentile for RRT, the 93rd for ECAP and the 88th for OSI.
  - Vogl 2024 measured only TAWSS, OSI and ECAP (PMID 39493311), so "RRT … as Vogl found" over-attributes.
  - Fix: give the percentiles or write "among the highest 5–12 %", and drop RRT from the Vogl sentence.
- [CONFIRMED] **C4-4: retention understated** — cost 0.1. "A slightly larger share remains" is 76 % against 56 % in the project's own pathline summary, and "renewed every beat" is too strong. The near-wall comparison far from the device (64 %) partly saves the sentence.
- [CONFIRMED] **C4-5: figures** — cost 0.1. Fig. 5a is about 1.5 cm wide with 4 pt labels, so the 10/20 mm lines cannot be read. Fig. 1c has five circles while the text speaks of "two regions".
- [WEAKENED] **C4-2: the appendage contrast behind the device is not mentioned** — cost 0.1. It reads about 280 HU, so residual patency or a leak is possible. The presence-versus-risk position itself is coherent.
- [CONFIRMED] **C4-6: "In both beats" is undefined** — cost 0.05; Methods say only the last beat was analysed.
- [WEAKENED] **C4-7: the 40–150 HU "thrombus" band in Fig. 1c and the Q threshold have no source** — cost 0.05.
- [wording, ≤ 0.05] l.71: the "four PVs up to their first branch" (C1-6) and the "10 mm tube" (C2-5) need correcting; "Amplatzer-type" → "Amplatzer Amulet-type occluder (lobe + disc)" (C4-8).
- Checked and OK:
  - The submitted PDF is identical to `main.pdf`.
  - Length: 2 body pages plus 1 page of references.
  - Answer: explicit, with CT and CFD evidence; the metal-streak argument is cited (Boas 2012).
  - References: all 5 verified (Vogl 2024, Korsholm 2024, Ronneberger 2015, Isensee 2025, Boas 2012) and all cited.
  - The report's numbers match the run9 data.
  - The methods wording on the segmentation is correct.

### 5. Device segmentation (+1)
- [CONFIRMED] **C5-1: the submitted "manual" STL is a filled solid** — cost 0.4.
  - It is 5.83 mL, with 65 % of voxels at or below 454 HU and 21.7 % at or below 200 HU.
  - The closing added 2.13 mL of median 179 HU. Inside the lobe the file fills 100 % of the voxels, while the source mask fills only 10–31 %.
  - The U-Net STL covers the same bright wires (95 % against 94 %) with 2.43 mL.
  - See blocking issue 2.
- [CONFIRMED] **C5-2** (lattice and waist lost, Fig. 1b is a blob; folded into C5-1) and **C5-3** ("manual" name vs gamma tracing + hand edits + scripted closing) — 0.05 each.
- [WEAKENED] **C5-5**: U-Net gaps and specks — matters only if that file is the one graded; the report admits the gaps.
- [notes / refuted] **C5-4, C5-6, C5-7**:
  - C5-4: two STLs and no single designated one (folded into C5-1);
  - C5-6: the device README is inconsistent;
  - C5-7: boundary contact only.
- Checked and OK:
  - Device type: Amulet-type morphology (hubs 11.7 mm apart, disc 27 mm).
  - Frame: both STLs are in mm, in the CT frame, and sit on the device.
  - Integrity: closed and manifold.

## Refuted findings (no action)
- C2-6: binary STL.
- C3-8: laminar model.
- C3-9: device as a flat wall (disclosed).
- C4-9: dense layout, preprint, link (counted under C3).
- C5-7: device–LA contact.

## Fix plan before 20/11/2026
Ordered by points per hour. None of these needs Fluent or a new run. After any change, rebuild with `python 4_postprocessing/make_submission.py` and update `SUBMISSION.md`.

| # | Fix | Time | Points |
|---|---|---|---|
| 1 | Upload the zip, test the link in a private window, put the URL in the upload form (+ the report if one line fits). | 20 min | protects ~1.0 (C3) |
| 2 | Hand in one wire-only device STL with an honest name; keep the closed body for the CFD only; re-render or re-caption Fig. 1b; fix the method sentence at l.71. | 30 min | +0.4 (C5) |
| 3 | Report text, within 2 pages: hub thickness ≤ 2.5–3.25 mm and one caveat sentence (single arterial phase, hub streak, appendage at ~280 HU); percentiles in place of "highest 5 %"; drop RRT from Vogl; retention 76 vs 56 % (64 % near-wall); define "beats 3 and 4"; l.71 wording (veins, tube, Amulet); half a sentence on the mitral outlet. | 1–1.5 h | +0.5–0.7 (C4, C2) |
| 4 | Extend the RSPV trunk in Slicer to just past its division (and optionally the LSPV horn vein), as a new dated `.nrrd`; one line saying the mesh was built before this extension. | 30–45 min | +0.4–0.5 (C1) |
| 5 | Package: regenerate `device_sections/README.md` from run9; fix the convergence parser (349/350); fix the colour bars, the three README lines and loading `device_segmentation.stl`; re-zip. | 45 min | +0.15–0.2 (C3) |
| 6 | Copy `transform_LPS_to_model.json` into `submission/`, with one line on how to apply it. | 5 min | +0.05–0.1 (C2) |

Fixes 1–3 and 6 take about 2.5 h and would bring the likely score to about 8.5–8.7/10, plus about 0.9 extra. Fixes 4 and 5 add about 0.6 more.

## Things to defend rather than fix
- **PV extensions**: "Each PV was cut at its ostium and extended by a short circular inlet, as taught (flat cap, sharp rim, smooth blend)." Changing them now would need a new mesh and run.
- **Generic boundary conditions**: the same pressure at all veins (so the split follows the inlet area) and E-wave-only mitral flow are the course set-up; the latter is consistent with AF. Only relative comparisons are claimed.
- **No mesh-independence study**: not required; beats 3 and 4 agree; the ranking near the device held across run8 and run9.
- **Device not in the fluid domain**: the wall that closes the appendage stands in for the device face. This is already in Limitations.
- **Accessory vein stub closed**: only the four main PVs carry inflow.
- **Laminar model at Re ≈ 7,400 at the E peak**: the course set-up and common in LA CFD.

## Open questions for the author
1. Which vessel do you call the RSPV, the anterior vein the mesh uses or the trunk entering the roof? Did the flat roof cut aim only at excluding the right pulmonary artery?
2. Do you read the left side as a common trunk plus a small superior vein?
3. Hub region: are you confident in "no DRT"? Its density (median 133 HU, few voxels below 0 HU) is the strongest argument a grader could raise against it.
4. Where will the link go, and does the upload form have a size limit?
