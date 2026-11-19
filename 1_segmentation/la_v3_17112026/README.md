# LA segmentation v3: Case 3 (17/11/2026)

**This is the LA segmentation to hand in:** `Case3_LA_segmentation_HugoJal_17112026.seg.nrrd`. `make_submission.py` copies it to `submission/Case3_LA_segmentation_HugoJal.seg.nrrd`.
- It opens in 3D Slicer on the CT grid. The segment is `LA_Case3`.
- The header is the same as v2's.

**What changed from v2** (`../la_v2_06112026/`, not modified): only the **right superior pulmonary vein (RSPV) trunk** was added (+1.68 mL). No voxel of v2 was removed.

**Why.** v2 ends with a flat cut at the right atrial roof (z ≈ 889 mm LPS). The cut correctly keeps the right pulmonary artery (RPA) out, but it also cut off the RSPV trunk. In the CT, the trunk runs upward between the SVC (in front) and the RPA (behind) for about 15 mm before it divides:
- its lumen is continuous with the LA, at about 400 HU;
- a wall and fat separate it from the RPA.

This was finding C1-1 of `docs/agents/reviews/rubric_review_17112026.md`, against the rubric line "pulmonary veins … at least up to the first branch".

**How** (`fix_rspv_trunk.py`). It uses the same tools as the original segmentation, threshold + mask:
1. CT between 300 and 900 HU. The SVC, full of contrast, is about 1700 HU, so it is excluded.
2. The trunk is followed from the roof cut in 0.5 mm slabs along its axis. Each slab keeps only the piece nearest the current centre, within 7 mm. This is what stops the growth leaking into the RPA, which touches the trunk through a thin wall. It stops at 15.5 mm, just past the division.
3. A small opening removes thin bits along the RPA wall, then the holes are filled.

**Result.**
- Volume 156.03 → 157.71 mL.
- One component, Euler number 1 (genus 0).
- Numbers in `la_v3_stats.json`.

**QC.**
- `qc_rspv_slices.png`: coronal and sagittal CT slices, v2 dashed red, v3 green. The new part fills the trunk and stays out of the RPA.
- `qc_rspv_3d.png`: 3D view of the right roof, before and after.

**Not changed.** The mesh (`2_mesh/run9_15112026/`) and the simulation were built from v2, and they were left as they are on purpose. The PV inlets of the mesh are cut and extended with cylinders anyway, so they do not depend on how far the vein is segmented.

**Still open.** The small vein the mesh calls LSPV (the roof "horn" behind the device) still ends at its ostium. In review 17/11 this was a minor finding (C1-2).

**Please check in Slicer.** Load the CT and this segmentation and look at the right roof. The extension is automatic; correct it by hand if needed.
