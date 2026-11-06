# Device wireframe from a promptable U-Net (31/10/2026)

Device: Amulet-type occluder (see `../README.md`).

`Device_unet_wire.seg.nrrd` (CT grid, 3D Slicer) and `Device_unet_wire.stl` (LPS mm, the same frame as `2_mesh/HugoJal_Case3.stl`).

## Method
1. A pretrained promptable 3D U-Net, nnInteractive v1.0 (Isensee, Rokuss et al., DKFZ, 2025), was used on the CT. There is no model trained for LAAO devices, so it was prompted with automatic points:
   - positive points on clearly bright wire voxels;
   - negative points on blood and tissue around the wires.
2. On its own the network also fills the blood between the wires. Its output was therefore used only as the device region and intersected with wire-level CT contrast:
   - hysteresis at 60/220 on CT minus a 9-voxel median;
   - plus CT > 600.
3. Hub streaks were clipped with a cylinder around the device axis, and the largest connected piece was kept.
4. The result was saved from 3D Slicer on 31/10/2026. This saved version (25 224 voxels, 2.50 mL) differs from the automatic output (28 839 voxels) by 5 425 voxels. The STL was made from this saved version (marching cubes, Gaussian smoothing 0.5 voxel).

The scripts, model weights and Python environment of this attempt are kept locally in `archive/1_segmentation/device_unet_attempt/`, which is not in the repository.
