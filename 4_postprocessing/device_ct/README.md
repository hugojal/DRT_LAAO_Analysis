# Is there a thrombus on the device? CT attenuation analysis (07/11/2026)

Script: `4_postprocessing/device_ct_hu.py`. It reads the CT, the LA segmentation v2 and the manual device segmentation; all stay local and are never committed.

Outputs:
- `device_ct_hu.json`: all numbers;
- `hu_profile`, `hu_rays_map`, `hu_layer_histogram` (PNG + PDF);
- `device_ct_arrays.npz`: input of `make_report_figures.py`.

The analysis does not depend on the simulation run.

## What a thrombus looks like on CT
A device-related thrombus (DRT) on contrast CT is a **hypoattenuating thickening (HAT)** on the atrial face of the device. Clot does not take up the contrast agent, so it is darker than the contrast-filled blood next to it.

- **Agudelo et al. 2021** (EuroIntervention 17:e944, [DOI](https://doi.org/10.4244/EIJ-D-21-00320); Amplatzer/Amulet devices, as here):
  - HAT = an enhancement defect on the atrial surface in the arterial phase.
  - Under 3 mm and laminar = low grade, probably healing. Over 3 mm, irregular or pedunculated = high grade, i.e. definite DRT.
  - The appendage counts as sealed if it is below 100 HU behind the device.
- **Li et al. 2022** (Front Cardiovasc Med 9:809688, [DOI](https://doi.org/10.3389/fcvm.2022.809688)):
  - An appendage/aorta HU ratio of about 0.33 separated thrombus from slow blood.
  - Here it is used only as a rough guide, "darker than a third of the atrial blood", because the reference differs (atrial blood, not aorta).
- **No validated HU cut-off for HAT:** I found none, so everything below is relative to this patient's blood.

## Method
- **Atrial blood:** LA voxels more than 15 mm from the device. Median **401 HU** (IQR 379–423).
- **Rays from the blood to the device (main test):**
  - Lines run parallel to the device axis, 0.5 mm apart.
  - They start in the atrial blood and must reach the device mask within 4 mm of leaving it, so lines that cross the atrial wall or the fat outside are not used.
  - For each ray I take the mean HU over the last 3 mm before the device. If it is dark (< 0.33 × blood), I also record the thickness of the dark segment and its minimum.
- **Profile along the device axis:** mean HU over a 5 mm radius, every 0.5 mm, from the atrium through the device into the appendage.
- **Simple layer:** all voxels 0–3 mm in front of the device mask. Kept only for comparison, because it also catches fat and lung outside the thin atrial wall where the disc is tilted, so it overstates the dark share (31 %).

## Results
**1. Blood in front of the device:** 1545 rays. The 3 mm in front of the device have a median of **375 HU**, i.e. 0.93 × the atrial blood.

**2. Dark rays (8.8 %):** they lie only **on both sides of the metal hub**, a median 4.6 mm from the axis. The hub saturates the scanner at 3071 HU.
- **92 % of them reach below 0 HU** (median minimum −414 HU).
- Thrombus is soft tissue and has positive HU, so these values cannot be clot.
- Dark bands on both sides of a dense metal part are the typical photon-starvation and beam-hardening streak artefact.
- **Thickness:** the dark segment is ≤ 2.5 mm on 90 % of these rays, 3.25 mm at most. Even read as tissue, it would be low-grade HAT at most.

**3. Profile along the axis:** the attenuation stays at the blood level (370–390 HU) right up to the device face. It then rises sharply in the metal.

**4. Behind the device:** the appendage still has about **280 HU**, above the 100 HU threshold for sealed. Contrast may therefore pass the device (residual patency or a peri-device leak). The flow model does not include this, because the appendage is closed in the model.

## Interpretation (as written in the report)
- **No DRT:** blood enhances normally right up to the device face. The only dark spots sit next to the hub, with values a clot cannot have, so I read them as metal artefact.
- **Caveat:** this is one arterial-phase CT. A late-phase scan or TEE would be the clinical way to confirm.
