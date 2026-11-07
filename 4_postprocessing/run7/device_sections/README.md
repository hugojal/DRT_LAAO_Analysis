# Flow in front of the device: cross-sections and recirculation (run7, last heartbeat)

07/11/2026. Draft interpretation by the analysis scripts; check it against the figures before using it in the report.

## What was measured
- **Device axis:** the centre and normal of the device disc, taken from the rim fit on the CT and mapped to the simulation frame (`axis.json`).
- **Cross-sections:** planes perpendicular to that axis, 2, 5, 8, 12 and 16 mm from the disc centre towards the atrium.
  - Each section is limited to a column of 20 mm radius around the axis, i.e. the blood that faces the occluder.
  - Only the piece in front of the device is kept; a pulmonary vein can also cross the column.
- **Per section and time step:**
  - mean speed;
  - share of the section slower than 0.05 m/s ("stagnant");
  - share flowing towards the device and share flowing back into the atrium.
- **Recirculation index:** the smaller of those two shares. If a large part of the same section flows both ways at the same time, the blood is turning around: it recirculates instead of passing through.
- **Volume check:** all blood within 10 mm of the device, with its share that is stagnant and its share where the Q-criterion is positive (rotation dominates strain, i.e. inside a vortex).
- **Time:** the analysed heartbeat, t = 2.63–3.50 s, every 0.01 s. "Diastasis" is t = 2.90 s, the slowest moment just before rapid filling; "filling" is t = 3.06 s, the peak of mitral inflow.

## Results

**1. A thin layer of almost still blood covers the device.**
- At 2 mm from the disc, 73 % of the section is slower than 0.05 m/s on average over the beat. The mean speed there is 0.04 m/s.
- Just before rapid filling the whole 2 mm section is nearly still: up to 100 % is stagnant (`sections_stagnant_fraction.png`).
- At 2 mm the flow hardly ever goes both ways at once (recirculation index ≈ 0 for most of the beat; `sections_recirculation_index.png`). This layer is not a vortex. It is blood that barely moves.

**2. A few millimetres further out, the blood recirculates for most of the heartbeat.**
- From 5 to 16 mm, at least 20 % of the section flows each way during 78–98 % of the beat (`summary.json`).
- The recirculation index is highest after the filling peak, at about 0.5 s in the beat: about 45 % of the section goes towards the device while the rest comes back (`sections_towards_away.png`).
- The flow pattern changes direction twice per beat:
  - In diastasis most of the section moves slowly towards the device. The blood drifts into the dead end in front of the occluder.
  - At the filling peak, 80 % of the 12 mm section moves towards the device for a moment.
  - Shortly after, 70 % moves back into the atrium.
- The streamlines show the same thing:
  - `streamlines_side_diastasis_t290.png`: a slow swirl sits directly in front of the device.
  - `section_8mm_diastasis_t290.png`: an in-plane vortex is visible on the 8 mm section.
  - `streamlines_side_filling_t306.png`: during filling, a fast stream sweeps past the device region on its way to the mitral valve, without entering it.

**3. In the blood next to the device, stagnant blood and vortices take turns.**
- Within 10 mm of the device (about 8 mL of blood), 31 % is stagnant on average. This rises to over 70 % just before rapid filling and drops to about 15 % during filling (`near_device_volume.png`).
- About 25 % of that volume is inside vortex cores (Q > 0) for most of the beat.

**4. Mean speed stays low.**
- Mean speed on the sections is 0.04 m/s at 2 mm and 0.09–0.11 m/s at 5–16 mm (`sections_mean_speed.png`).
- The highest values are about 0.2 m/s, only at the filling peak.
- For comparison, the mitral jet reaches about 1 m/s.

## Interpretation
- **Slow layer plus recirculation.** The blood touching the atrial face of the device is almost still, and the blood just in front of it turns around rather than flowing through. Both conditions lengthen the time blood spends next to the device.
- **Link to the wall maps.** This fits the wall-shear results: low and oscillating shear (high ECAP) within 5 mm of the device. Slow and recirculating flow next to a foreign surface is the condition linked to device-related thrombus.
- **Not a thrombus model.** The model does not simulate clotting, so this is a risk indicator, not a prediction. The boundary conditions are generic, so compare the region with the rest of this atrium rather than with fixed thresholds.

## Possible text for the report (Results, "Flow near the device")
> Cross-sections parallel to the device face show that the first 2 mm of blood in front of the device is almost still for most of the heartbeat (73 % of the section slower than 0.05 m/s). A few millimetres further out, part of each section flows towards the device while the rest flows back, so the blood recirculates in front of the device during most of the beat instead of being washed out.

If space allows, one figure is enough: `section_8mm_diastasis_t290.png` (in-plane vortex) or `sections_stagnant_fraction.png`.

## Caveats
- **Brief drop to 0 at 2 mm:** at about 0.82 s in the beat the 2 mm section briefly falls to 0. The moving wall passes the plane and the section almost vanishes. Ignore that point.
- **Device not in the flow:** the device is not a solid object in the flow domain; the domain ends at the segmented atrial wall. The 2 mm plane is therefore partly inside the region the occluder fills, near the occluded orifice.
- **Thresholds:** 0.05 m/s for "stagnant" and 20 % for "recirculating" are working thresholds, not values from the literature. The trends across distances and over time do not depend on them.

## Files
- **Numbers:**
  - `sections.csv`: per section and time step;
  - `near_device_volume.csv`;
  - `summary.json`: beat averages;
  - `axis.json`.
- **Plots** (`plots/`, PNG + PDF, one quantity each, legends outside the axes):
  - `sections_mean_speed`;
  - `sections_stagnant_fraction`;
  - `sections_recirculation_index`;
  - `sections_towards_away`;
  - `near_device_volume`;
  - `sections_area`.
- **ParaView images** (`views/`; the device is not drawn; colour bar below the model):
  - streamlines from the side at diastasis and at filling, and from the atrium;
  - long-axis slice through the device axis, at diastasis and at filling;
  - 8 mm section with in-plane arrows, at diastasis and at filling.
- **Scripts:**
  - `4_postprocessing/device_sections.py`: numbers (reads the EnSight steps, a few minutes);
  - `4_postprocessing/plot_device_sections.py`: plots;
  - `pvbatch --force-offscreen-rendering 4_postprocessing/render_device_views.py`: images;
  - `6_paraview_package/open_device_sections.py`: the same pipeline, interactive in the ParaView GUI.
