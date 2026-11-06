"""Close-up of the mitral junction for the three versions of the 5.3 cm2 outlet (06/11/2026):
first_try_step/ (step at the annulus), second_try_erase/ (no step but narrower neck, grooves) and the current mesh
(LA as segmented + C1 funnel below the annulus). Sections: red = that mesh, grey = run6 mesh (anatomy reference),
thin grey line = annulus plane. Writes check_step_before_after.png."""
import os, numpy as np, pyvista as pv
HERE = os.path.dirname(os.path.abspath(__file__)); TAG = "HugoJal_Case3_mv53_06112026.stl"
pv.OFF_SCREEN = True
REF = pv.read(os.path.join(os.path.dirname(HERE), "mv_aligned_03112026", "HugoJal_Case3_mvz_03112026.stl"))
V = [(pv.read(os.path.join(HERE, "first_try_step", TAG)), "1st try: step at the annulus"),
     (pv.read(os.path.join(HERE, "second_try_erase", TAG)), "2nd try: neck narrowed, grooves"),
     (pv.read(os.path.join(HERE, TAG)), "now: neck kept, ridge removed, C1 funnel")]
p = pv.Plotter(shape=(3, 3), window_size=(1800, 1500), border=False)
for col, (m, t) in enumerate(V):
    p.subplot(0, col); p.add_mesh(m.clip_box([-40, 40, -40, 40, -10, 25], invert=False), color="wheat", show_edges=True, edge_color="k", line_width=0.3, smooth_shading=True)
    p.add_text(t, font_size=11); p.camera_position = [(55, -55, -25), (0, 0, 2), (0, 0, 1)]
    for row, (nrm, eye, lab) in enumerate((((0, 1, 0), (0, -90, 3), "xz"), ((1, 0, 0), (90, 0, 3), "yz")), start=1):
        p.subplot(row, col)
        p.add_mesh(REF.slice(normal=nrm, origin=(0, 0, 0)), color="gray", line_width=5, opacity=0.5)
        p.add_mesh(m.slice(normal=nrm, origin=(0, 0, 0)), color="red", line_width=2.5)
        ax = np.cross(nrm, (0, 0, 1)); p.add_mesh(pv.Line(-40 * ax, 40 * ax), color="gray", line_width=1)
        p.add_text(f"{lab} section (red) vs run6 (grey)", font_size=10)
        p.camera_position = [eye, (0, 0, 3), (0, 0, 1)]; p.camera.parallel_projection = True; p.camera.parallel_scale = 20
p.screenshot(os.path.join(HERE, "check_step_before_after.png"))
