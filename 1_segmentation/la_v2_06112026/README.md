# LA segmentation v2: Case 3 (06/11/2026)

**This is the LA segmentation to hand in:** `Case3_LA_segmentation_HugoJal_06112026.seg.nrrd`.
- It opens in 3D Slicer, on the CT grid; the segment is named `LA_Case3`.
- `.stl` is a marching-cubes surface in LPS mm, for viewing only.

The original `../Hugo_Jal_left_atrium_segmentation.nrrd` (manual thresholding + masking + paint/erase in Slicer) is not changed. v2 starts from it and applies two fixes from the rubric review and a topology clean-up (`docs/agents/reviews/rubric_review_06112026.md`). Script: `fix_la_segmentation.py`.

| fix | rubric line | what was done | result |
|---|---|---|---|
| C1-2: device excluded | "excluding the device" | The device (manual mask ∪ gamma v4 wireframe, dilated by 1 voxel) is subtracted from the LA. | Device voxels inside the LA: 8 820 of 51 776 (17 %) before → **0** after. This was a layer of about 1 mm on the atrial face of the disc. |
| C1-1: veins to the first branch | "pulmonary veins … at least up to the first branch" | The two inferior veins (RIPV, LIPV) are extended with the same tools as the original segmentation, threshold + mask: CT ≥ 300 HU (the CT inside the LA mask is ≥ 307 HU for 99 % of voxels), connected to the distal vein, beyond its end, at most 10 mm along the lumen. | RIPV +0.75 mL, LIPV +0.85 mL. Both now reach (and pass by a few mm) their first division. The superior veins already reached theirs. |
| topology clean-up | "free of obvious artefacts" | A 1-voxel morphological opening, then the largest component with holes filled. | It removes 1-voxel bridges and spurs that formed small handles or tunnels. **Genus 38 → 0** (the original mask had 11). Changes ≈ 1 900 voxels (0.2 mL). |

- **Volume:** 155.7 → 156.0 mL.
- **Components:** one, closed surface of genus 0, as needed for the CFD mesh.
- **Rim:** on the distal part of the inferior veins, a rim of about 1 voxel was added where the old mask lay about 0.5 mm inside the bright lumen.

**QC:** `qc_la_v2.png`.
- Top two rows: planes through each inferior vein's axis, old outline in cyan, new in red.
- Bottom row: axial slices through the device, old LA in cyan, new LA in red, device in yellow.

**Please check in Slicer** that the vein extensions look right to you. Load the CT, the original segmentation and v2, then look at the inferior veins and at the device. They are automatic and follow the CT; correct them by hand if needed.

**Used for:** the run7 mesh (`2_mesh/run7_06112026/`), which is built from this segmentation.
