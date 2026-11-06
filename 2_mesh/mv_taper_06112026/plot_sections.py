"""Cross-sections of the run6 mesh and the current mesh at several heights along the valve axis (z = 0: annulus),
run from the project folder. Writes check_sections.png (06/11/2026)."""
import pyvista as pv, numpy as np, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
fig, axs = plt.subplots(1, 2, figsize=(13, 6.5))
for ax, (name, f) in zip(axs, (("run6 mesh", "2_mesh/mv_aligned_03112026/HugoJal_Case3_mvz_03112026.stl"), ("now", "2_mesh/mv_taper_06112026/HugoJal_Case3_mv53_06112026.stl"))):
    m = pv.read(f)
    for z, col in zip((8, 4, 2, 0, -2, -4, -6.4), plt.cm.viridis(np.linspace(0, 1, 7))):
        sl = m.slice(normal=[0, 0, 1], origin=[0, 0, z]).strip()
        if sl.n_cells == 0: continue
        q = max((sl.get_cell(i).points for i in range(sl.n_cells)), key=len)
        q = np.r_[q, q[:1]]; ax.plot(q[:, 0], q[:, 1], color=col, lw=1.2, label=f"z = {z} mm")
    ax.set_aspect("equal"); ax.set_title(name + ": sections along the valve axis (z = 0: annulus)"); ax.legend(fontsize=7); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig("2_mesh/mv_taper_06112026/check_sections.png", dpi=90)
