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
