"""Model-frame (m) surfaces for the run7 figures and ParaView package (07/11/2026). Writes 4_postprocessing/paraview/:
  la_surface_model_m.stl          run7 LA mesh surface (2_mesh/run7_06112026), already in the model frame -> m
  device_gamma_wire_model_m.stl   device wire frame, gamma v4 (1_segmentation/device/gamma), LPS mm -> model frame m
  device_unet_wire_model_m.stl    U-Net device segmentation (1_segmentation/device/unet)
  device_manual_model_m.stl       manual device mask (1_segmentation/device/manual), used for the distance to the device
Model frame: x = R (x_LPS - c) (2_mesh/run7_06112026/transform_LPS_to_model.json), z = mitral valve axis.
Usage: python 4_postprocessing/make_paraview_inputs.py"""
import os, json
import numpy as np, pyvista as pv
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, "4_postprocessing", "paraview"); os.makedirs(OUT, exist_ok=True)
TR = json.load(open(os.path.join(ROOT, "2_mesh", "run7_06112026", "transform_LPS_to_model.json"))); R = np.array(TR["R"]); c = np.array(TR["c_LPS_mm"])
la = pv.read(os.path.join(ROOT, "2_mesh", "run7_06112026", "HugoJal_Case3_run7_06112026.stl")); la.points = la.points / 1000.0
la.save(os.path.join(OUT, "la_surface_model_m.stl"))
D = os.path.join(ROOT, "1_segmentation", "device")
for src, dst in (("gamma/Device_gamma_wire_v4_06112026.stl", "device_gamma_wire_model_m.stl"), ("unet/Device_unet_wire.stl", "device_unet_wire_model_m.stl"),
                 ("manual/Device_manual.stl", "device_manual_model_m.stl")):
    m = pv.read(os.path.join(D, src)); m.points = (m.points - c) @ R.T / 1000.0; m.save(os.path.join(OUT, dst))
print("written to", OUT)
