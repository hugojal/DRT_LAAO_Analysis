# 06 · Submission & evaluation criteria (from the professors, received 31/10/2026)

Due: **20/11/2026 at 23:59** (professors' email, received 06/11/2026). Lab = 20 % of the MOS grade, scored out of 10 (+1 extra for the device segmentation, criterion 5).
Mock grading against this rubric: skill `/rubric-adversary` (`.claude/skills/rubric-adversary/`).

## 1. Segmentation (3/10)
- Pulmonary veins (PV) well segmented **at least up to the first branch**, plus the **mitral valve (MV)**.
- Surface **smooth**, no obvious artefacts, follows the contour of the whole left atrium (LA) **excluding the device and any thrombi**.
- Save as **.nrrd, named after the case you segmented**.

## 2. LA meshes (2/10)
- PVs and MV **cut as explained in class** (flat cuts), **separable in Ansys with the angle method** — add cylinders as flow extensions (lab slides: MV ≈ 28–42 mm, PV ≈ 10–25 mm, cylinder edges ~90°, transitions smooth).
- MV cut **position and orientation consistent with the anatomy in the CT**.
- Surface mesh: **no non-manifold edges, no negative volumes**; **not over-smoothed** (keep anatomical features).
- Volume mesh **< 500k elements**, good quality.
- Save **surface .stl** and **volume .bdf**.

## 3. Simulation (2/10)
- **Case-specific** simulation; share **all files needed for visualisation in ParaView**.
- Shows **physiological flow values and trajectories**, includes the **MV longitudinal movement**, and is **informative for thrombus risk** in this case.

## 4. Device-related thrombus (3/10)
- Answer whether there is a DRT and justify. **A bare yes/no scores 0.**
- Short text + **screenshots and visualisations from the simulation and the image data** + **proper academic references** (never invent references; verify each).
- **Max 2 pages excluding references. Submit as PDF.**

## Where the project stands against this (31/10/2026) — see STATUS.md for details
- The report draft is a .docx of ~4 pages without references → must become a ≤ 2-page PDF with verified references and CT-based images.
- Free hand given by the user: the original CT (`1_segmentation/5 DS_Coronaires …nrrd`, `data/Case_003/` DICOM) may be re-segmented with a publicly available U-Net, veins cut and cylinders added, meshes smoothed.
- Mesh/time-step convergence was not done (professor's L2 slide shows a convergence table; the user wants values in the report).
