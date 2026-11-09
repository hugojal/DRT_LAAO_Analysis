"""Speed, stagnant blood and vorticity over the analysed heartbeat: whole LA vs blood within 5, 10 and 20 mm of the device
(07/11/2026). Same idea as the first quick-look figures of the project (archive/figures_quicklook/02, 03).
Per time step (steps 263-350 of results/<run>_4cycles), volume-weighted over the fluid cells:
  mean |v| (m/s), share of volume with |v| < 1, 2.5 and 5 cm/s, mean vorticity magnitude (1/s),
  share with Q > 0 (rotation dominates strain) and Q > 500 1/s2 (vortex cores). Vorticity alone also counts the shear next to the
  walls, so near the device it is high even where the blood does not swirl; Q separates swirl from shear.
Writes 4_postprocessing/<run>/near_device_timecourse.csv. usage: python near_device_timecourse.py [run]"""
import os, sys, csv
import numpy as np, pyvista as pv, vtk
from scipy.spatial import cKDTree
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = sys.argv[1] if len(sys.argv) > 1 else "run8"; RES = os.path.join(ROOT, "3_simulation", "results", f"{RUN}_4cycles")
dev = pv.read(os.path.join(ROOT, "4_postprocessing", "paraview", "device_analysis_model_m.stl")); tree = cKDTree(np.asarray(dev.points))
rows = []
for k in range(263, 351):
    r = vtk.vtkEnSightGoldBinaryReader(); r.SetCaseFileName(os.path.join(RES, f"step_{k:03d}.encas")); r.Update()
    f = pv.wrap(r.GetOutput().GetBlock(0)).compute_cell_sizes(length=False, area=False)
    cd = f.point_data_to_cell_data(); V = f["Volume"]; d = tree.query(f.cell_centers().points)[0] * 1000
    vm = np.linalg.norm(cd["Velocity"], axis=1); vo = cd["Vorticity_Magnitude"]; qc = cd["Q_Criterion_Normalized"]   # Fluent q-criterion, 1/s2
    row = dict(step=k, t_in_beat=round(k * 0.01 - 2.625, 3))
    for lab, m in (("all", np.ones(len(V), bool)), ("5mm", d < 5), ("10mm", d < 10), ("20mm", d < 20)):
        w = V[m]; row[f"vmean_{lab}"] = float((vm[m] * w).sum() / w.sum()); row[f"vort_{lab}"] = float((vo[m] * w).sum() / w.sum())
        row[f"qpos_{lab}"] = float(w[qc[m] > 0].sum() / w.sum()); row[f"q500_{lab}"] = float(w[qc[m] > 500].sum() / w.sum())   # rotation-dominated share; Q > 500 1/s2 = vortex cores
        for th in (0.01, 0.025, 0.05): row[f"stag{th}_{lab}"] = float(w[vm[m] < th].sum() / w.sum())
    rows.append(row); print(k, end=" ", flush=True)
out = os.path.join(ROOT, "4_postprocessing", RUN, "near_device_timecourse.csv")
with open(out, "w", newline="") as fo:
    w_ = csv.DictWriter(fo, fieldnames=list(rows[0])); w_.writeheader(); w_.writerows(rows)
A = {k: np.array([r[k] for r in rows]) for k in rows[0]}
for lab in ("all", "5mm", "10mm", "20mm"):
    print(f"\n{lab}: mean|v| beat {A['vmean_'+lab].mean():.3f} m/s, peak {A['vmean_'+lab].max():.3f}; stagnant<2.5cm/s beat {A['stag0.025_'+lab].mean():.2f}, <5cm/s {A['stag0.05_'+lab].mean():.2f}; vorticity beat {A['vort_'+lab].mean():.1f} 1/s, peak {A['vort_'+lab].max():.1f}; Q>0 {A['qpos_'+lab].mean():.2f}, Q>500 {A['q500_'+lab].mean():.3f}")
