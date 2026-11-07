"""run7 (oval PV extensions) vs run8 (circular cylinders), 07/11/2026: two views of each, edges shown near the veins.
Writes check_pv_cylinders_run7_vs_run8.png. usage: python render_pv_cylinders.py"""
import os, numpy as np, pyvista as pv
HERE = os.path.dirname(os.path.abspath(__file__)); pv.OFF_SCREEN = True
m7 = pv.read(os.path.join(HERE, "..", "..", "archive", "2_mesh_pre_run8", "run7_06112026", "HugoJal_Case3_run7_06112026.stl")); m8 = pv.read(os.path.join(HERE, "HugoJal_Case3_run8_07112026.stl"))
p = pv.Plotter(shape=(2, 2), window_size=(1800, 1500), border=False)
for r, (m, lab) in enumerate(((m7, "run7: PV extensions end in an oval"), (m8, "run8: PV extensions are circular cylinders"))):
    for c_, eye in enumerate(((-120, -150, 90), (130, 120, 80))):
        p.subplot(r, c_); p.add_mesh(m, color="wheat", show_edges=True, edge_color="#666666", line_width=0.3, smooth_shading=True)
        p.camera_position = [eye, (0, -5, 40), (0, 0, 1)]
        if c_ == 0: p.add_text(lab, font_size=12)
p.screenshot(os.path.join(HERE, "check_pv_cylinders_run7_vs_run8.png")); print("saved")
