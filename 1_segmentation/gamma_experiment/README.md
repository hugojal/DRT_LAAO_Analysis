# Device wire frame from a gamma-transformed CT (03/11/2026)

This device segmentation uses no neural network. It reads only the CT and the LA segmentation. The manual `../Device.seg.nrrd` is used as an outer limit and for comparison.

The device is a **Watchman FLX type** occluder:
- a flat proximal face with a rim of about 14 mm radius (a 27 mm device);
- a strut cage of about 11 mm radius that closes distally;
- a hub at each end.

Result: `Device_gamma_wire_v3_03112026.seg.nrrd` (3D Slicer, CT grid) and `.stl` (LPS mm, the same frame as `2_mesh/HugoJal_Case3.stl`).

## Method (`segment_device_gamma_v3.py`)
1. **Gamma 0.3**: `g = clip((CT - blood) / (1500 - blood), 0, 1) ** 0.3`, with blood = 399, the median of the LA. The low gamma keeps the faint struts and the whole rim.
2. **Ridge (wire) filter**: Sato tubeness on `g` at 0.3–0.7 mm scales. Thin lines respond; sheets and blobs respond much less.
3. **Allowed region**:
   - the device outline in axial/radius coordinates around the device axis (`qc/explore_rz_profile.png`);
   - inside the manual mask dilated by 1.5 mm, which removes the hub streaks ("antennae").
4. **Local maximum rule**: a voxel is kept only if its ridge value is at least 50 % of the maximum within 1.5 mm. Each region keeps its own struts and loses the background between them, however bright the CT is there.
5. **Hysteresis threshold** at the 60th/85th percentile of the ridge values. Hub cores (CT ≥ 1500) are added and pieces smaller than 30 voxels are removed.

## How it was tuned (images in `qc/`)
Earlier versions used a white top-hat with one global threshold. v1 had gamma 0.6 and no shape prior; v2 had gamma 0.3 and the shape prior. Their files are not in the repository.

| step | image | what was seen | change |
|---|---|---|---|
| 0 | `iter0_v2_4views.png` | v2 was solid on one side and open on the other. The face was 25–81 % filled per 45° sector and the wall 17–63 %. | look for wires instead of bright voxels |
| 1 | `iter1_ridge_vs_rank.png` | The ridge filter gives a wire-like face (spokes and ring). Forcing the same fill in every sector creates speckles. | ridge filter |
| 2 | `iter2_ridge_scales.png`, `iter2_wall_unwrapped.png` | Finer scales are better. One wall panel stays solid: the CT is blurred there, but the struts are still separable, about 15–20° apart. | threshold relative to the local maximum |
| 3 | `iter3_local_max.png` | At 50 %/1.5 mm every part looks like struts and the rim is a closed ring. At 60 % the rim breaks. | 50 %, 1.5 mm |

`explore_unwrapped.png` shows why gamma 0.3 was chosen: with gamma 0.6, part of the rim fell below the threshold.

| | mL | inside manual | face fill per sector | wall fill per sector | base rim |
|---|---|---|---|---|---|
| **v3 (this)** | 1.26 | 97 % | 12–27 % | 8–29 % | 100 % |
| v2 | 2.60 | 96 % | 25–81 % | 17–63 % | 100 % |
| manual | 5.02 | | | | |

v3 is a wire frame, so it overlaps the solid manual mask much less (Dice 0.39).

Remaining limitations:
- The wall sector between 45° and 90° has few struts, because they are faint in the CT there.
- A short metal streak crosses the face next to the proximal hub.
- The wires appear about 1 mm thick, because of blooming on the CT and not the real wire size.

## Files
- `*_stats.json`: numbers and parameters.
- `qc/QC_slices_*.png`: slices parallel to the face (red = gamma, cyan = manual).
- `qc/QC_3D_*.png`: four views, compared with the manual mask.
- `qc_volumes.npz`: written by each run for the QC script. It holds a CT crop, so it is git-ignored.

Run from the project folder:
```
python 1_segmentation/gamma_experiment/segment_device_gamma_v3.py
python 1_segmentation/gamma_experiment/qc_device_gamma.py
```
