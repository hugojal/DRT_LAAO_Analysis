"""Smooth the device STLs (16/11/2026). Taubin (volume-preserving) smoothing of each STL on its own mesh: no remeshing,
no hole filling, no boolean/union, so no pieces are merged and the topology (disc, hubs, lobe, small islands) is unchanged.
Inputs are only read; outputs are new files *_smooth_16112026.stl next to them. Usage: python smooth_device_16112026.py"""
import os, json
import numpy as np, pyvista as pv
from scipy.spatial import cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
JOBS = {"manual/Device_manual.stl": "manual/Device_manual_smooth_16112026.stl",
        "gamma/Device_gamma_wire_v4_edited_09112026.stl": "gamma/Device_gamma_wire_v4_edited_smooth_16112026.stl"}
NITER, PASSBAND = 40, 0.08
stats = {}
for src, dst in JOBS.items():
    m = pv.read(f"{HERE}/{src}").clean(); n0 = int(m.connectivity("all").cell_data["RegionId"].max()) + 1
    s = m.smooth_taubin(n_iter=NITER, pass_band=PASSBAND, normalize_coordinates=True).compute_normals(auto_orient_normals=False, consistent_normals=True)
    s.save(f"{HERE}/{dst}")
    d = np.linalg.norm(s.points - m.points, axis=1); n1 = int(s.connectivity("all").cell_data["RegionId"].max()) + 1
    ed = s.extract_feature_edges(boundary_edges=True, non_manifold_edges=True, feature_edges=False, manifold_edges=False)
    stats[dst] = dict(triangles=s.n_cells, pieces_before=n0, pieces_after=n1, volume_before_mL=round(abs(m.volume) / 1000, 4), volume_after_mL=round(abs(s.volume) / 1000, 4),
                      displacement_mm=dict(median=round(float(np.median(d)), 3), p99=round(float(np.percentile(d, 99)), 3), max=round(float(d.max()), 3)), open_or_nonmanifold_edges=int(ed.n_cells))
    print(dst, json.dumps(stats[dst]))
json.dump(stats, open(f"{HERE}/smooth_device_16112026.json", "w"), indent=1)
