# Findings C5 (device, extra, max 1) — submission 17/11/2026 — saved by orchestrator from the adversary's reply
Estimate 0.4–0.5/1 (0.4 if "manual" closed STL graded; ~0.7 if U-Net graded). Work: r17/c5/ (vox.py, vox2.py, vox_stats.json, stl_stats.json, longaxis.png, cross.png, 3d_compare.png, hist.png; labels swapped in 3d_closed.png/3d_unet.png — use 3d_compare.png). LA blood median 399 HU (p5 340, p95 455).

## Findings
- C5-1 | major | "Only the device wireframe … extra structures will lower your grade": submitted "manual" STL is a solid closed envelope (disc plate + filled lobe can) including lobe interior / waist (non-opacified LAA contents, blood).
  voxelised composition: submitted closed 5.83 mL, 65.2 % ≤ 454 HU, 21.7 % (1.27 mL) ≤ 200 HU, 13.9 % ≥ 600; source edited gamma mask 3.83 mL, 50.5 %, 3.8 % (0.15 mL), 21.2 %; rejected manual plug 5.02 mL, 58.0 %, 1.5 %, 15.9 %; U-Net 2.50 mL, 31.7 %, 0.8 %, 32.2 %. Closing added 2.13 mL (36 % of file), median 179 HU, 91 % ≤ 454; 1.16 mL > 1 voxel from source, median 101 HU. Lobe interior (r 6–9 mm, 5–9 mm from disc hub, CT 80–150 HU): closed fills 100 %, source 10–31 %, plug 9–22 %. Cause: make_closed_smooth_16112026.py "# dome" (binary_closing 2.5 mm ball + fill_holes) and base footprint fill; json 3.834 → 5.83 mL. Images longaxis.png, cross.png.
  cost 0.4–0.5. fix ~10 min: hand in U-Net or unfilled edited gamma STL (Device_gamma_wire_v4_edited_09112026.stl or _smooth_both_16112026.stl); change make_submission.py l.18 + SUBMISSION.md 5a; keep closed body for CFD distances.
- C5-2 | minor | "matches its expected appearance": lattice, openings and waist gone ("tin can with a flange"); Fig. 1b (5_report/figures_run9/pv_device_segmentation.png) a smooth blob; U-Net and source gamma show disc, lobe, waist struts (3d_compare.png). cost 0.1 (overlaps C5-1). fix: re-render Fig. 1b from wire STL or caption "closed envelope used for distances".
- C5-3 | minor | provenance: file = algorithmic gamma tracing (19,518 vox) + Slicer edits (38,664) + scripted closing (+52 %), but named "manual"; report l.71 "manually in 3D Slicer on a gamma-enhanced CT", caption l.49 "manual segmentation … smoothed"; source .seg.nrrd named _06112026 holds 09/11 edits. cost 0.05. fix 5 min rename + "semi-automatic tracing, edited by hand".
- C5-4 | minor | two device STLs, report designates the closed one ("the one used in the analysis", l.71) = worse by wireframe criterion. cost 0.05 (folded into C5-1).
- C5-5 | minor (if U-Net graded) | holes in disc face and lobe wall, voxel steps, 5 specks (2.431 + ~0.001 mL); report l.71 admits gaps. cost 0.1–0.2. fix 10 min (largest component + light Taubin) or hand in unfilled gamma.
- C5-6 | note | device README table gamma row = unedited v4 (1.94 mL, 14 %), edited used = 3.83 mL, 50.5 %; README says hand in edited_09112026.stl, SUBMISSION says closed_both_16112026.stl; STL header unnamed. cost 0.
- C5-7 | note | closed STL 259/51,878 vertices (0.5 %) inside LA mask; U-Net 0. cost 0.

## Checked and OK
Amulet morphology (hubs 11.68 mm apart; disc 27.1 mm); "Amplatzer-type" consistent; both STLs mm/LPS, sit on device in CT; closed STL 1 piece manifold 5.827 mL; U-Net closed 2.432 mL matches mask; U-Net most wire-only; no .nrrd needed.

## Open questions
1. Closed envelope chosen only for looks? 2. Hand in one wire-only STL, keep closed body for CFD? 3. Describe method as semi-automatic + manual editing?
