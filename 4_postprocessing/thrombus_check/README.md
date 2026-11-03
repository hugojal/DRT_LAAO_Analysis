# Thrombus check on the CT (03/11/2026)

**Result: no device-related thrombus (DRT) is visible.** This agrees with the report.

On contrast CT, a DRT appears as a low-density mass (soft tissue, about 50–200 HU) attached to the atrial face of the device. It stands out against the contrast-filled blood, which is about 380 HU here.

## What was done (`thrombus_check.py`)
1. **Display.** The CT was shown with a gamma window for thrombus: [-100, 700] HU, gamma 1.5. Soft tissue appears dark and blood bright. It was viewed in long-axis planes through the device and in planes parallel to its face (`thrombus_check.png`, `explore_candidates.png`).
2. **Low-density search.** Voxels between −50 and 250 HU were searched inside the LA cavity, 0–10 mm in front of the device face.
3. **Blood at the face.** The density of the blood in direct contact with the face was measured.
4. **Profiles.** Density profiles were taken from the lower edge of the device into the LA.

## Findings
- The contrast-filled blood reaches the device face directly. In the first 0.5–3 mm in front of the face, the 5th percentile is 321 HU and only 0.1 % of voxels are below 250 HU. There is no mass and no layer of thickening on the face.
- The profiles from the lower edge go straight from the wire peak to blood (330–400 HU). They never drop into the soft-tissue range.
- Two small low-density pieces were found, and neither looks like thrombus:
  - **252 mm³, median 133 HU, right next to the hub.** It is a thin flat band, about 1.2 × 2.5 × 7 mm, on both sides of the metal hub and along one straight line. This is the dark-streak artefact of the metal. In the long-axis view at 90° it is a straight dark streak running out from the hub.
  - **51 mm³, median 136 HU, at the rim.** It is a thin sliver (0.6 × 0.8 × 3.4 mm) where the device rim meets the atrial wall, caused by partial volume with the wall.
- Behind the device, the appendage is less opacified than the LA. This is expected after occlusion and is not a DRT.

## Limitation
The metal streaks hide the blood in the first 1–2 mm around the proximal hub. A very small thrombus on the hub, a common place for DRT, cannot be completely ruled out on this single CT phase.

Run from the project folder: `python 4_postprocessing/thrombus_check/thrombus_check.py`. It writes `thrombus_check.png` and `thrombus_check.json`.
