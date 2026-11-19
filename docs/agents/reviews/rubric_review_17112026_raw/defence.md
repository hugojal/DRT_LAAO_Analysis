# Defence verdicts — submission/ 17/11/2026 (saved by the orchestrator from the defence agent's reply)
Re-scored by the defence: C1 2.3/3 · C2 1.75/2 · C3 1.7/2 (≈0.7 without a working link) · C4 2.2/3 · C5 0.5/1.
Scripts/renders were in the session scratchpad (r17/defence/: rpa1.py, rpa5.py, rpa_axial.png, rpa_sag.png, dev1.py); not kept.

| id | verdict | right cost | reason | evidence |
|---|---|---|---|---|
| C1-1 | CONFIRMED | 0.5 | Vessel above the flat roof cut is a pulmonary vein: LA→vessel min 367/379 HU over 25.6/21.7 mm (continuous lumen); vessel→RPA wall dip 248 HU (z 898) / 297 HU (z 896); fat ≥ z 902; SVC 1686 HU. Larger than the "wing" vein the mesh calls RSPV. One of four veins, ostium in mask → low end. | rpa5.py, rpa1.py |
| C1-2 | WEAKENED | 0.05–0.1 | Real taper, but 5 mm vessel; left anatomy likely common trunk + small superior vein. | c1/xsec_LSPVhorn.png |
| C1-3 | CONFIRMED | ~0.1 | Not the mitral cut plane: patch centre 25.5 mm on the LA side of the annulus plane, ~30 mm from valve centre. Same patch as 14/11 C1-1. | mitral_annulus.json + patch centre |
| C1-4 | CONFIRMED | 0.05 | Cosmetic blocky RIPV end. | c1/close_RIPV_end_sm.png |
| C1-5 | CONFIRMED (note) = C2-3 | 0 | Accessory vein knob. | c1/obl2_bump.png |
| C1-6 | CONFIRMED | 0 here (≤ 0.05 in C4 with C2-5) | main.tex l.71 contradicted by C1-1. | main.tex l.71 |
| C2-1 | WEAKENED | 0.1 | Method follows L2; caps 17.7/13.5/13.0 in 10–25 mm (RIPV 9.0 just below); oversized off-axis RSPV nozzle shares root with C1-1. | caps_model_frame.json; L2 slide |
| C2-2 | WEAKENED | 0.05 | Orientation exact; cap within 9.26 mm saddle height (leaflet level); 32.2 mm long axis inside 28–42 mm (optional-cylinder slide); 4–6 cm² not in slides. Missing half-sentence only. | pdftotext; mitral_annulus.json |
| C2-3 | WEAKENED (= C1-5) | 0–0.05 once | Removing a knob of an unsegmented accessory vein. | c2/r_spur_laa_ct.png |
| C2-4 | WEAKENED | 0.05–0.1 | Model frame not forbidden, but overlay on CT fails; transform only in zip. | checks.json |
| C2-5 | CONFIRMED (note → C4) | 0 here | "10 mm tube" wording vs 3.5 mm circle + 7–16 mm loft. | run9 README; main.tex l.71 |
| C2-6 | REFUTED | 0 | Binary STL not penalised. | rubric |
| C3-1 | CONFIRMED (conditional) | 0 with link; ~1.0 without | Delivery task; zip 605 MB (SUBMISSION.md says 564). | checks.json |
| C3-2 | CONFIRMED | 0.1 | Package device_sections README is run8 text contradicting report l.113 and its own summary.json. | zip device_sections/README.md l.1, 30, 38 |
| C3-3 | WEAKENED | 0.05 | run8→run9 changed geometry too; not asked; Limitations l.121 restricts to relative claims. | main.tex l.121 |
| C3-4 | WEAKENED | 0.05–0.1 | Course BCs; values physiological if high in PVs; only missing sentence on area-driven split. | c3/report.txt |
| C3-5 | CONFIRMED | 0.05 | Parser bug: transcript has "solution is converged" for 346–350 (iteration numbers ≥ 10000 printed "!10003", no space); CSV False, summary 344/350; SUBMISSION.md explanation wrong too. Residuals below criteria. | transcript.trn l.85915–87009 |
| C3-6 | CONFIRMED (note) | 0–0.03 | Overlapping colour bars/labels. | c3/open_default.png |
| C3-7 | CONFIRMED (note) | 0–0.03 | README/script inaccuracies. | c3/dist.py |
| C3-8 | REFUTED | 0 | Laminar = course set-up. | slides |
| C3-9 | REFUTED | 0 | Disclosed. | main.tex l.121 |
| C4-1 | WEAKENED | 0.3 | Answer justified (Korsholm criteria, shape, streak link, Boas, Fig. 1c); project rays ≤ 2.5 mm on 90 %, max 3.25 mm support "thin"; SD×√12 reading unreliable. Gaps: no number, dropped caveats (single arterial phase; LAA ~280 HU). Ground-truth risk remains: hub region median 133 HU, only 4 % < 0 HU looks soft-tissue-like. | device_ct README l.40, 44, 48; thrombus_check.json |
| C4-2 | WEAKENED | 0.1 | Presence-vs-risk position coherent (l.124); omission = LAA contrast behind device. | main.tex l.124 |
| C4-3 | CONFIRMED | 0.15 | Vogl measured TAWSS/OSI/ECAP only (PMID 39493311); "highest 5 %" untraceable, supported only for RRT (96th; ECAP 93rd, OSI 88th). | c4/patchrank.py |
| C4-4 | CONFIRMED | 0.1 | "Slightly larger share" (76 vs 56 %) and "renewed every beat" understate retention; near-wall comparison (64 %) partly saves it. | pathlines_summary.txt |
| C4-5 | CONFIRMED | 0.1 | Fig. 5a unreadable; Fig. 1c circles vs "two regions". | c4/fig5.png, fig1c.png |
| C4-6 | CONFIRMED | 0.05 | "Both beats" undefined. | main.tex l.77, 115, 118 |
| C4-7 | WEAKENED | 0.05 | Stroke sentence common knowledge; 40–150 HU band and Q threshold unsourced. | thrombus_report_figure.py l.72 |
| C4-8 | CONFIRMED (note) | 0 | Amplatzer vs Amulet wording. | main.tex l.71 |
| C4-9 | REFUTED | 0 | Layout/preprint fine; link = C3-1. | checks.json |
| C5-1 | CONFIRMED | 0.4 | Reproduced: 5.83 mL, 21.7 % ≤ 200 HU, 65.2 % ≤ 454, median 375 HU; U-Net 2.43 mL covers 95 % of the bright wires (vs 94 %), median 523 HU. Filling the lobe ≠ "only the device wireframe". | dev1.py |
| C5-2 | CONFIRMED (in C5-1) | 0.05 | Lattice/waist lost; Fig. 1b blob. | c5/3d_compare.png |
| C5-3 | CONFIRMED | 0.05 | "manual" name vs gamma + edits + closing. | SUBMISSION.md; main.tex l.71 |
| C5-4 | CONFIRMED (in C5-1) | 0 | Report designates closed STL. | main.tex l.71 |
| C5-5 | WEAKENED | 0–0.05 | Only if U-Net graded; gaps admitted. | main.tex l.71 |
| C5-6 | CONFIRMED (note) | 0 | Inconsistent device README. | device/README.md |
| C5-7 | REFUTED | 0 | Boundary contact. | checks.json |

Duplicates: C1-5 = C2-3; C1-6 = C2-5 = C4 methods wording; C2-1 (RSPV) shares root with C1-1, C3-4 split is its downstream effect; C4-9 = C3-1; C5-2, C5-4 fold into C5-1.
