# Flow in front of the device: cross-sections and recirculation (run8, last heartbeat)

07/11/2026. Analysis by `device_sections.py`, `plot_device_sections.py` and `render_device_views.py`. The report figures (Fig. 2, Fig. 3) come from here.

## What was measured
- **Device axis:** the centre and normal of the device disc, from the rim fit on the CT, mapped to the simulation frame (`axis.json`).
- **Cross-sections:** planes perpendicular to the axis, 2, 5, 8, 12 and 16 mm from the disc centre towards the atrium.
  - Each plane is cut to a column of 20 mm radius around the axis, and its largest piece is kept.
  - Smaller pieces belong to a pulmonary vein crossing the column. On 07/11/2026 the earlier rule ("the piece nearest the axis point") picked a vein at 12 mm in run8, so it was replaced.
- **Per section and time step:**
  - mean speed;
  - share slower than 0.05 m/s ("stagnant");
  - shares flowing towards the device and back into the atrium.
- **Two-way flow (recirculation index):** the smaller of those two shares. If a large part of the section flows both ways at once, the blood is turning around.
- **Volume check:** the blood within 10 mm of the device. Measured: its stagnant share and its share with Q > 0 (vortex cores).
- **Phases** (time in the beat = t − 2.625 s):
  - **"valve closed":** t = 2.90 s (0.275 s), ventricular systole. The mitral valve is closed and the atrium fills from the veins.
  - **"filling peak":** t = 3.06 s (0.435 s), the peak of mitral inflow (E wave).

## Results (`summary.json`, `plots/`, `views/`)

| distance | mean speed | stagnant share (beat mean) | share of the beat with ≥ 20 % flowing each way |
|---|---|---|---|
| 2 mm | 0.04 m/s | 70 % | 9 % |
| 5 mm | 0.09 m/s | 29 % | 99 % |
| 8 mm | 0.11 m/s | 19 % | 91 % |
| 12 mm | 0.13 m/s | 13 % | 92 % |
| 16 mm | 0.13 m/s | 16 % | 100 % |

1. **A still layer covers the device.**
   - At 2 mm, 70 % of the blood is slower than 0.05 m/s on average. That share never drops below about 50 %, not even at the filling peak.
   - At 8 and 16 mm, the slow share falls to 10 % or less at the filling peak.
   - The 2 mm layer hardly ever flows both ways, so it is still rather than recirculating.
2. **Recirculation a few millimetres further out.** From 5 to 16 mm, at least 20 % of each section flows each way during more than 90 % of the beat. This is clearest just after the filling peak, at about 0.5 s in the beat.
3. **Streamlines** (`views/`):
   - At the filling peak, a fast stream from the veins passes beside the device towards the valve without entering the space in front of it (`streamlines_side_filling_t306`).
   - With the valve closed, the blood in front of the device is slow and swirls on itself (`streamlines_side_systole_t290`). Flow towards the device and back runs side by side (`longaxis_slice_systole_t290`), and the 8 mm section shows an in-plane vortex (`section_8mm_systole_t290`).
4. **Blood within 10 mm of the device** (8.3 mL): on average 26 % is stagnant and 24 % is in vortex cores.

## Caveats
- **Device not in the flow:** the device is not a solid in the flow domain; the domain ends at the segmented wall. The 2 mm plane sits right at the occluded ostium.
- **Thresholds:** 0.05 m/s and 20 % are working thresholds, not literature values. The trends with distance and over time do not depend on them.
- **Moving wall:** the 2 mm curve has a one-step dip at about 0.82 s in the beat, when the moving wall passes the plane. Ignore it.
