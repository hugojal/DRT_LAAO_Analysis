# Device segmentation — Amulet-type LAA occluder

## The device
The occluder in Case 3 is an **Amulet-type** device (Abbott Amplatzer Amulet design). The CT shows:
- two dense hubs on one axis, 11.7 mm apart;
- a braided **disc** of about 28 mm on the LA side, covering the LAA ostium;
- a short **waist**;
- a braided **lobe** of about 22 mm in the LAA (wall about 8 mm long), closed distally by the second hub.

It is **not** a Watchman: a Watchman has a single cage with one hub and no separate disc. Some older notes (before 06/11/2026) wrongly said Watchman FLX.

On this CT (0.45 × 0.45 × 0.5 mm voxels) the braid of the disc and the lobe looks like thin bright sheets, not separate wires. Every wireframe segmentation is therefore about 1 mm thick, because of blooming, while the real braid is much thinner. The course asks that **only the device wireframe** is segmented and that it is exported as an **.stl**.

## The three segmentations
All three are on the CT grid (`.seg.nrrd`, opens in 3D Slicer). Each has an `.stl` in LPS mm, in the same frame as `2_mesh/HugoJal_Case3.stl`. All STLs are closed and manifold.

| folder | method | mL | voxels at blood level (≤ 454 HU) | pieces |
|---|---|---|---|---|
| [`manual/`](manual/) | Manual segmentation in 3D Slicer (user, last edit 23/10/2026). Used in the CFD model (the device position in the figures). | 5.02 | 58 % | 7 (6 islands < 50 voxels) |
| [`gamma/`](gamma/) | Gamma-transformed CT; braided sheets traced in cylindrical coordinates around the hub axis (v4, 06/11/2026). No neural network. | 1.94 | 14 % | 2 |
| [`unet/`](unet/) | Pretrained promptable 3D U-Net (nnInteractive), output intersected with wire-level CT contrast, then edited in Slicer (31/10/2026). | 2.50 | 32 % | 4 |

"Blood level" means CT values like the contrast-filled blood around the device, i.e. not metal. It is a rough measure of how much non-wire material a mask contains.
- The manual mask is a solid plug: it fills the space between the disc and the lobe.
- The gamma segmentation is the closest to "wireframe only".

For the hand-in, use the **manually edited gamma STL** (`gamma/Device_gamma_wire_v4_edited_09112026.stl`, 09/11/2026), or the U-Net STL, not the manual mask. The edited gamma segmentation is also the device used in the analysis since 09/11/2026 (the manual mask before). See `docs/agents/reviews/rubric_review_06112026.md`.

## Files
```
manual/  Device_manual.seg.nrrd  Device_manual.stl  make_stl.py
gamma/   Device_gamma_wire_v4_06112026.{seg.nrrd,stl}  _stats.json  segment_device_gamma.py  qc_device_gamma.py  qc/  README.md
unet/    Device_unet_wire.{seg.nrrd,stl}  README.md
```
Superseded attempts are kept locally in `archive/1_segmentation/` (git-ignored):
- gamma v1–v3, built on the wrong Watchman assumption;
- the U-Net scripts, weights and environment;
- the early threshold/hull masks.

## Smoothed STLs (16/11/2026)
`smooth_device_16112026.py` smooths the voxel staircase of the manual STL and of the edited gamma STL with a volume-preserving Taubin filter (40 passes, no remeshing, no hole filling, no union). Results: `manual/Device_manual_smooth_16112026.stl` and `gamma/Device_gamma_wire_v4_edited_smooth_16112026.stl`. The originals are unchanged. Pieces, triangle count and closed surface are the same as before; volume changes < 0.1 %; points move 0.14 mm (median), 0.42 mm (max). Numbers: `smooth_device_16112026.json`; before/after: `smooth_device_16112026_before_after.png`. Not yet used in the CFD (the mesh in the report uses the unsmoothed STL).

## Clean base + dome (16/11/2026)
`gamma/make_base_dome_16112026.py` rebuilds the edited gamma segmentation as two smooth, closed, separate bodies, guided by the Amulet shape (wide flat disc, cylindrical lobe with rounded closed end). They are split at the waist with a 0.4 mm gap and never joined. Files in `gamma/`: `Device_gamma_wire_v4_edited_clean_base_16112026.stl` (disc, 1.30 mL, rim diameter about 27.6 mm, plate about 2.4 mm), `..._clean_dome_16112026.stl` (lobe, 3.90 mL, a = 2.05–13.5 mm) and `..._clean_both_16112026.stl` (both in one file). Dome: closing, hole fill, opening and smoothing of the CT mask. Base: the hub streaks leave the disc patchy in the CT, so it is rebuilt from the mask (rim radius per direction, thickness per radius). These are solid bodies (the sheets are not hollow), so the volume is larger than the 3.84 mL wire. The original `Device_gamma_wire_v4_edited_09112026.stl` is unchanged. Not used in the CFD or the report. Numbers: `gamma/make_base_dome_16112026.json`.

### Honest smooth version (16/11/2026, replaces the fitted base/dome above for use)
The fitted base looked unnatural and was detached from the dome, so `gamma/make_honest_smooth_16112026.py` only smooths the real edited mask (no model, no closing, no hole filling; specks < 40 voxels removed; volume kept: 3.83 mL). Disc and lobe stay attached as in the CT. Files in `gamma/`: `Device_gamma_wire_v4_edited_smooth_both_16112026.stl` (whole device), `..._smooth_base_16112026.stl` (disc, 1.05 mL) and `..._smooth_dome_16112026.stl` (lobe, 2.78 mL): the same surface cut at the waist plane and capped, closed bodies that touch only at the cut. The `_clean_` files are the earlier fitted attempt and should not be used.

### Closed smooth version (16/11/2026, latest)
`gamma/make_closed_smooth_16112026.py`: closed, hole-free and smooth, built from the real edited mask. Dome: closing, hole fill, opening. Base: the footprint holes of the disc (hub-streak shadows) are closed and filled with the plate thickness the CT mask has at that radius. Base and dome stay attached where the CT attaches them. Files in `gamma/`: `Device_gamma_wire_v4_edited_closed_both_16112026.stl` (5.83 mL, one closed surface), `..._closed_base_...` (disc, 1.62 mL) and `..._closed_dome_...` (lobe, 4.20 mL): the same surface cut at the waist and capped. These are solid bodies, so they are larger than the 3.83 mL wire; the `_smooth_` files (no filling) keep the real holes; `_clean_` is the rejected fitted attempt.
