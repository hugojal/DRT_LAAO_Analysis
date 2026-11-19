# run9 surface (15/11/2026) - status: surface only, waiting for the user's approval
`fix_surface_run9.py` repairs the run8 surface locally: spur next to the RIPV removed (harmonic fill + blend); the last 3.5 mm of each PV extension and its cap rebuilt (exact circle, even rings, concentric cap); needle edges collapsed and flipped. Closed, manifold, 155.9 mL (run8 156.0).

## Do the natural (irregular) vein parts disturb the inflow? (checked on the run8 solution)
- `pv_section_shape.py`: beyond the 5 mm circular part the section turns elliptical (longest/shortest width 1.3-1.7, circularity 0.90-0.96), area within about +/-15 % of the cap area for ~5-16 mm, then it opens into the atrium.
- `pv_flow_run8_check.py` (planes across each vein, peak inflow, step 307): mass flow constant along the vein within 1-5 %; velocity-profile momentum factor beta 1.07 at the cap -> 1.09-1.16 at 10 mm (a parabola would be 1.33); transverse flow <= 0.16 of the axial mean up to 10 mm; no backflow inside the veins at peak.
- `pv_jet_direction_run8.py`: flux-weighted velocity direction deviates from the extension axis by <= 3-4 deg at 10 mm (<= 6 deg at 12 mm, LIPV).
- Limits: low-flow phases show more secondary flow (the ratio uses a small mean); planes deeper than ~10-12 mm are already inside the atrium; run8 only, not rerun on run9.

## v2 (15/11/2026): `build_surface_run9v2.py` -> `HugoJal_Case3_run9_15112026.stl`
From the run8 surface: spur removed; whole atrium smoothed (Taubin, 60 passes, volume kept); each PV extension rebuilt as a loft: exact circle for the last 3.5 mm, then a smoothstep change of centre and outline over 5.5-12.5 mm into the vein's own outline (RSPV 11, LSPV 14, RIPV 14.5, LIPV 16 mm behind the cap; area <= 1.3 x cap area there); seam softened; needle edges collapsed and edges flipped. 44,596 triangles, closed, manifold, 156.7 mL (run8 156.0), min triangle angle 7.8 deg (10 triangles < 10 deg). `HugoJal_Case3_run9a_first_repair_15112026.stl` (first repair) is kept for comparison. `side_views_run9_vs_v2.png` (top run9, bottom v2).
v2 final: RSPV loft ends 7 mm behind the cap (11 mm made a fold on its flare). 44,166 triangles, closed, manifold, 156.5 mL, min triangle angle 25.7 deg. Caps flat and perpendicular, rims sharp.
