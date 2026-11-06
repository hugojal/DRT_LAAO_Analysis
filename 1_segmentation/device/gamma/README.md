# Device wireframe from a gamma-transformed CT (v4, 06/11/2026)

`Device_gamma_wire_v4_06112026.seg.nrrd` (3D Slicer, CT grid) and `.stl` (LPS mm, the same frame as `2_mesh/HugoJal_Case3.stl`).

This segmentation uses no neural network. It reads only the CT and the LA segmentation. The manual mask (`../manual/Device_manual.seg.nrrd`) is used as an outer limit and for comparison.

## Device
The device is an **Amulet-type** occluder (see `../README.md`):
- two hubs 11.7 mm apart;
- a braided disc of about 28 mm;
- a short waist;
- a braided lobe of about 22 mm.

On this CT the braid shows as thin bright sheets, not as separate struts. Earlier versions (v1–v3, 03/11/2026) wrongly assumed a Watchman FLX and looked for the struts of a cage with a tube filter. This broke the Amulet's sheets into speckles. They are archived locally in `archive/1_segmentation/gamma_v3_03112026/`.

## Method (`segment_device_gamma.py`)
1. **Gamma 0.3**: `g = clip((CT - blood) / (1500 - blood), 0, 1) ** 0.3`, with blood = 399 HU, the median of the LA. The low gamma keeps the faint braid.
2. **Cylindrical resampling** around the line through the two hubs (2.5° × 0.25 mm × 0.25 mm). In every half-plane through the axis, each sheet of the device is a curve: the disc, the lobe wall, the lobe's distal end, and the braid lines inside the lobe (`qc/explore_rz_profile.png`, `qc/QC_sectors_*.png`).
3. **Ridge filter** in each half-plane: 2D Hessian at 0.5 mm, smoothed over ±1 angle step.
4. **Thresholding**:
   - each curve keeps the width where it is at least half of its peak;
   - hysteresis at 25 % / 45 % of the 99th percentile;
   - pieces smaller than 50 bins are removed.
5. **Back to the CT grid**: each voxel takes the value of its (angle, axial, radius) bin.
6. **Axis**: cylindrical coordinates do not work on the axis, so the hubs and the dense bar between them are taken by CT value (≥ 900 HU).
7. **Allowed region**: everything stays inside the manual mask dilated by 1.5 mm.

**Checked and rejected.** The diagonal lines inside the lobe and the bar between the hubs looked like metal streaks at first. Long-axis CT planes through the device (`qc/explore_long_axis_planes_v4.png`) show both identically at every angle. The diagonals also do not follow the CT axial planes through the hubs, where streaks would lie. So they are part of the device and are kept.

## Result
| | mL | inside manual | voxels at blood level (≤ 454 HU) | disc / lobe wall found in 5° sectors |
|---|---|---|---|---|
| **gamma v4** | 1.94 | 94 % | 14 % | 100 % / 100 % |
| gamma v3 (archived, Watchman assumption) | 1.26 | 97 % | about 7 % | rim 100 % |
| manual | 5.02 | | 58 % | |

Limitations:
- About half of the disc is darkened by the hub streaks. It is traced only in patches there.
- A few small spikes remain at the lobe end, near the distal hub.
- The sheets appear about 1 mm thick because of the CT resolution, not because the braid is that thick.

## Files
- `*_stats.json`: numbers and parameters.
- `qc/QC_slices_*.png`: slices parallel to the disc (red = gamma, cyan = manual).
- `qc/QC_3D_*.png`: four views, compared with the manual mask.
- `qc/QC_sectors_*.png`: half-planes (gamma CT, ridge strength, traced curves).
- `qc_volumes.npz`, `qc_cyl_v4.npz`: written by each run for the QC script. They hold CT data, so they are git-ignored.

Run from the project folder, with `MOs/mcp/.venv` (pynrrd, scipy, scikit-image, pyvista):
```
python 1_segmentation/device/gamma/segment_device_gamma.py
python 1_segmentation/device/gamma/qc_device_gamma.py
```
