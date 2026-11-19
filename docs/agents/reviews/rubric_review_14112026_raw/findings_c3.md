# Findings criterion 3 (Simulation, 2 pts), adversary agent a36e6b59709dedf42, saved by the orchestrator (condensed, ids and numbers unchanged)

SUMMARY: 0 hard-fail, 1 major (uncertain), 5 minor, 3 notes. The zip is complete and works (1547 files, testzip None, open_in_paraview.py runs under pvbatch from an extracted copy, 88 steps load, device and LA surfaces in the same frame as the flow). Estimated score 1.6-1.8 of 2 (cost 0.2-0.4); falls to 1.2 or less only if the link fails or the grader reads generic BCs and the RIPV harshly.

## Findings
- C3-1 | major (uncertain, hinges on delivery) | "share with us all files needed for visualization in ParaView"
  claim: package correct, but the grader receives only a link that has not been created or tested, for a 564 MB zip; the project folder is not part of the hand-in.
  evidence: zip is 591,983,371 bytes, unzip ~11 s, testzip None, single top folder HugoJal_Case3_ParaView/. The package README ends with "run python 4_postprocessing/make_paraview_package.py" and "4_postprocessing/run8/README.md in the project repository"; neither exists in the zip.
  cost 0 if the link works, up to 1.5 of 2 if the grader cannot download it.
  fix: create the link, test it logged out, state size and top-folder name, keep a ~100 MB fallback (every 5th step plus surfaces); remove the two dangling repo references from the README.
- C3-2 | minor | "include the mitral valve's longitudinal movement"
  claim: valve-motion numbers inconsistent between documents.
  evidence: 6_paraview_package/README.md says "up to 8.9 mm"; mitral_bc.json says displacement_range_mm 9.8; motion.prof per-beat minimum z: beat 1 -8.9, beat 2 -8.9, beat 3 -9.71, beat 4 -9.25 mm; profile not periodic (z at start of each beat 0, -1.81, -1.01, -2.31 mm; end of beat 1 -1.43 mm). Motion is real: at t = 3.06 s fluid zmin -9.3 mm.
  cost ~0.05. fix: state "about 9 mm (beat 4: 9.25 mm)" in README and mitral_bc.json; note the course file drifts ~1 mm per beat.
- C3-3 | minor | "physiological flow values"
  claim: RIPV is half normal size; gets 9 % of inflow; right/left split 46/54.
  evidence: pv_cuts.json RIPV lumen area 61.2 mm2 (D 8.8 mm) vs 217 mm2 for RSPV; flows.csv beat 4: pv_3 inflow 6.7 of 79.7 mL; Cronin et al., Acad Radiol 2007;14:178-88, PMID 17236990, DOI 10.1016/j.acra.2006.11.004 (CT of 200 AF patients): mean ostial diameters RSPV 17.6, LSPV 16.6, RIPV 17.1, LIPV 14.8 mm; L2 slide "PVs around 10-25mm" also puts 9.0 mm below the course range. Laterality verified (names correct). All four PVs get the same pressure curve, so the split comes purely from cap area.
  cost ~0.1. fix: say whether the RIPV is genuinely small, stenosed or ablated, or truncated by segmentation/cut; if the cut is at fault, defend as patient-specific. (CT not checked.)
- C3-4 | minor | "informative for thrombus risk evaluation"
  claim: no mesh-independence or time-step study; convergence evidence is iterative convergence plus beat 3 vs 4; the quantities that decide the conclusion are not periodic.
  evidence: convergence_summary.json, run8 README: ECAP near device changes 7 % between beats, OSI 10-18 %; independent REVIEW.md: ECAP > 1.4 covers 5.6 % of 0-5 mm area in beat 4 and 0 % in beat 3; retention 25 % (author sphere 2.63 s) vs 63 % (review) vs 61 %, author reconciled to ~60 %; mesh 0.14-4 mm tetrahedra, no inflation layers, dt 0.01 s, review notes nodal WSS under-resolved; report_numbers.json periodicity_ecap_rel_change_near = 0.27 while README quotes 7 %; slide 30 gives continuity 0.005 as the criterion.
  cost ~0.1-0.15. fix: run a coarser/finer mesh or dt = 0.005 s for one beat, or list it in limitations; fix the 0.27 vs 7 % wording.
- C3-5 | minor | "physiological flow values and trajectories"
  claim: waveforms generic, no S/A wave; "valve closed" phase passes 2 mL; PV flow reverses.
  evidence (flows.csv beat 4): MV outflow for t < 0.3 s is 2.07 mL (6.9 mL/s mean), 2.6 % of SV, although Fig. 2c is labelled "valve closed"; PV inflow for t < 0.3 s 10.5 mL vs 68.1 mL in diastole; total PV reverse volume -3.25 mL (RSPV -2.54), reversed velocities -0.20 to -0.32 m/s at t ~0.65-0.72 s; PV cross-section-mean peak velocity 0.74-0.79 m/s at the E wave; LA volume swing 156.8-168.2 mL (6.8 %), set by valve and funnel motion (rigid wall). No PubMed PV velocity range found; pattern consistent with large-LA AF patient (A wave absent) but the report never says so.
  cost ~0.1. fix: one sentence "no A wave and a blunted S wave, as expected in AF with a large LA; 2 mL passes the closed valve in systole"; do not call the phase "closed" without the caveat.
- C3-6 | minor | "case-specific simulation"
  claim: only the geometry is case-specific; BCs are course curves, not scaled.
  evidence: mitral_bc.json scale_factor 1.0, SV 79.7 mL; setup_case_run8.py pressure-inlet on all four PVs with the course profile; the report already says "inflow and outflow curves are generic"; 5.3 cm2 orifice below the slide's MV range 28-42 mm (D = 26 mm), defended by "course range 4-6 cm2"; whole-wall TAWSS 0.79 Pa vs Vogl 1.8-2.9 Pa (not rechecked).
  cost ~0.05-0.1. fix: defend: geometry, device position and valve axis are patient-specific, BCs are the course curves; keep the TAWSS gap in limitations.
- C3-7 | note: device not in the flow domain (flat cap at the ostium); device_sections/README Caveats; review says this probably underestimates local risk; the report states it. cost 0. defend.
- C3-8 | note: wall-metrics .vtp static while the flow moves; four device STLs (README says which is used for what); velocity scalar-bar labels overlapped in the agent's screenshots (maybe driver); device not touching the visible wall in the render (beside the ostium cap). cost 0. optional: put the "which device file" line at the top of the README.
- C3-9 | note: trajectories present and reproducible (streamline render at t = 3.06 shows PV jets merging and turning to the MV; pathlines/*.vtp and pv_pathlines.py in the zip). cost 0.

## Checked and OK
Zip integrity and extraction (11 s); open_in_paraview.py runs (streamline tubes 38,510 points, slice, Q = 500 contour, wall metrics, device STLs load; 88 steps, 2.63-3.50 s). Frame consistency (pvbatch bounds, m): fluid x -0.038..0.049, y -0.051..0.024, z -0.009..0.076; wire frame x 0.0195..0.0467, y -0.033..-0.005, z 0.0004..0.0282; wall metrics z -0.003..0.076; the device sits inside the LA bounding box. Every file listed in the README exists in the zip. Convergence: 350/350 steps meet the residual criteria, median 28 iterations, max 50, mass balance 0.45 mL. Beat-4 integrals match README: MV outflow 79.74 mL, SV 79.7 mL, CO 5.47 L/min, peak MV flow 499 mL/s at 0.435 s, MV outflow differs 0.08 % between beats 3 and 4. LA volume max at 0.265 s as expected. BC provenance: course curves, valve velocity added so flux through the moving cap matches the course, mv_funnel moves rigidly; laminar flow is the slide's choice; residual 0.005 is slide 30's value. PV laterality correct. LA volume 156-168 mL plausible for an AF/LAAO patient.

## Open questions for the student
1. When will the download link exist, tested from a clean browser; what if the grader's limit is below 564 MB? 2. Is the 9 mm RIPV a true anatomical feature, truncated segmentation or wrong cut; stenosis or ablation on CT? 3. Is the patient in AF (missing A wave, large LA)? If so, say so in the report. 4. One extra beat, coarser/finer mesh, or list as limitation? 5. "2 mL leak" caveat for the closed-valve phase, or relabel "valve nearly closed"?
(Scratch files: scratchpad/adv/c3/, extracted zip in x/.)
