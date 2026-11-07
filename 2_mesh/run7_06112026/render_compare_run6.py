"""run6 vs run7 mesh (06/11/2026): whole atrium from two sides with the PV cap normals (inflow direction, arrows) and a
close-up of the device region. Writes check_run6_vs_run7.png. Usage (from the project folder): python 2_mesh/run7_06112026/render_compare_run6.py"""
import os, json
import numpy as np, pyvista as pv
HERE = os.path.dirname(os.path.abspath(__file__)); MESH = os.path.dirname(HERE); ROOT = os.path.dirname(MESH)
pv.OFF_SCREEN = True
TR = json.load(open(os.path.join(HERE, "transform_LPS_to_model.json"))); R = np.array(TR["R"]); c = np.array(TR["c_LPS_mm"])
run6 = pv.read(os.path.join(ROOT, "archive", "2_mesh_pre_run7", "mv_aligned_03112026", "HugoJal_Case3_mvz_03112026.stl"))   # archived (local only)
run7 = pv.read(os.path.join(HERE, "HugoJal_Case3_run7_06112026.stl"))
caps6 = json.load(open(os.path.join(HERE, "run6_caps_reference.json")))["angle_separation_30deg"]["largest"][1:6]
caps7 = json.load(open(os.path.join(HERE, "check_mesh_run7.json")))["angle_separation_30deg"]["largest"][1:6]
dev = pv.read(os.path.join(ROOT, "1_segmentation", "device", "manual", "Device_manual.stl")); dev.points = (dev.points - c) @ R.T
dc = np.asarray(dev.center)
p = pv.Plotter(shape=(2, 3), window_size=(2100, 1300), border=False)
views = [((140, -140, 70), (0, 0, 30)), ((-140, 140, 70), (0, 0, 30))]
for row, (mesh, caps, lab) in enumerate(((run6, caps6, "run6 (Meshmixer PV cylinders, mitral cap 8.6 cm2)"), (run7, caps7, "run7 (PV extensions along the vein trunks, mitral 5.3 cm2)"))):
    for col, (eye, foc) in enumerate(views):
        p.subplot(row, col); p.add_mesh(mesh, color="wheat", smooth_shading=True)
        for cp in caps:
            cc = np.array(cp["centre"]); nn = np.array(cp["normal"])
            p.add_mesh(pv.Arrow(cc + 18 * nn, -nn, scale=18), color="red" if cp["area_mm2"] < 400 else "blue")
        p.camera_position = [eye, foc, (0, 0, 1)]
        if col == 0: p.add_text(lab + "\nred arrows: PV inflow direction (cap normal); blue: mitral outflow", font_size=9)
    p.subplot(row, 2); box = list(np.ravel([[x - 25, x + 25] for x in dc]))
    p.add_mesh(mesh.clip_box(box, invert=False), color="wheat", show_edges=True, edge_color="k", line_width=0.2, smooth_shading=True)
    p.add_mesh(dev, color="orange", opacity=0.35)
    p.camera_position = [dc + np.array([-10, -70, 25]), dc, (0, 0, 1)]
    p.add_text("device region (device in orange)", font_size=9)
p.screenshot(os.path.join(HERE, "check_run6_vs_run7.png"))
print("written check_run6_vs_run7.png")
