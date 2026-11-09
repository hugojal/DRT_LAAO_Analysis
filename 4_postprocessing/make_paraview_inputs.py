"""Model-frame (m) surfaces for the figures and ParaView package of a run (07/11/2026; run7 or run8, same frame). Writes 4_postprocessing/paraview/:
  la_surface_model_m.stl          LA mesh surface of the run (2_mesh/<mesh dir>), already in the model frame -> m
  device_gamma_wire_model_m.stl   device wire frame, gamma v4 (1_segmentation/device/gamma), LPS mm -> model frame m
  device_unet_wire_model_m.stl    U-Net device segmentation (1_segmentation/device/unet)
  device_manual_model_m.stl       manual device mask (1_segmentation/device/manual), solid plug, used until 07/11/2026
  device_analysis_model_m.stl     gamma wireframe + the user's manual edits (09/11/2026): the device for all distances and figures
Model frame: x = R (x_LPS - c) (2_mesh/run8_07112026/transform_LPS_to_model.json, same as run7), z = mitral valve axis.
Usage: python 4_postprocessing/make_paraview_inputs.py [run]   (default run8)"""
import os, sys, json
import numpy as np, pyvista as pv
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, "4_postprocessing", "paraview"); os.makedirs(OUT, exist_ok=True)
TR = json.load(open(os.path.join(ROOT, "2_mesh", "run8_07112026", "transform_LPS_to_model.json"))); R = np.array(TR["R"]); c = np.array(TR["c_LPS_mm"])
MESHES = {"run7": "run7_06112026", "run8": "run8_07112026"}; RUN = sys.argv[1] if len(sys.argv) > 1 else "run8"; MD = MESHES[RUN]
la = pv.read(os.path.join(ROOT, "2_mesh", MD, f"HugoJal_Case3_{MD}.stl")); la.points = la.points / 1000.0
la.save(os.path.join(OUT, "la_surface_model_m.stl"))
D = os.path.join(ROOT, "1_segmentation", "device")
for src, dst in (("gamma/Device_gamma_wire_v4_06112026.stl", "device_gamma_wire_model_m.stl"), ("unet/Device_unet_wire.stl", "device_unet_wire_model_m.stl"),
                 ("manual/Device_manual.stl", "device_manual_model_m.stl"),
                 ("gamma/Device_gamma_wire_v4_edited_09112026.stl", "device_analysis_model_m.stl")):   # device for all distances since 09/11/2026: gamma + manual edits
    m = pv.read(os.path.join(D, src)); m.points = (m.points - c) @ R.T / 1000.0; m.save(os.path.join(OUT, dst))
print("written to", OUT)
