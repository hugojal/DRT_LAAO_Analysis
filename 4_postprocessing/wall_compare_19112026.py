"""Near-device wall (<= 5 mm) against the rest of the wall, per metric and beat (19/11/2026).
median over wall cells; rest = wall >= 20 mm from the device; rank = share of same-area wall patches (disc of the wall around random
centres >= 12 mm from the device) whose median is as extreme (high OSI/RRT/ECAP, low TAWSS) as the near-device wall. -> run9/wall_compare.json"""
import numpy as np, pyvista as pv, json
from scipy.spatial import cKDTree
m = pv.read("paraview/run9_wall_metrics.vtp"); c = m.cell_centers().points; A = m.compute_cell_sizes()["Area"]; d = m["dist_to_device_mm"]
if d.size != len(c): d = m.point_data_to_cell_data()["dist_to_device_mm"]
near = d <= 5; rest = d >= 20; tr = cKDTree(c); rng = np.random.default_rng(1)
ctr = np.where(d >= 12)[0]; ctr = rng.choice(ctr, 3000, replace=False)
r = 0.0165; nb = tr.query_ball_point(c[ctr], r); area_p = np.median([A[i].sum() for i in nb]) * 1e4
out = {"near_area_cm2": float(A[near].sum() * 1e4), "patch_area_cm2": float(area_p), "n_patches": len(ctr)}
for beat, suf in (("beat4", ""), ("beat3", "_prevcycle")):
    for nm, key, low in (("TAWSS", "TAWSS_Pa", True), ("OSI", "OSI", False), ("RRT", "RRT_1_per_Pa", False), ("ECAP", "ECAP_1_per_Pa", False)):
        x = m[key + suf]
        if x.size != len(c): x = m.point_data_to_cell_data()[key + suf]
        n_, r_ = np.median(x[near]), np.median(x[rest]); pm = np.array([np.median(x[i]) for i in nb])
        rank = float((pm <= n_).mean() if low else (pm >= n_).mean())
        out[f"{beat}_{nm}"] = {"near": float(n_), "rest": float(r_), "ratio": float(n_ / r_), "share_of_patches_as_extreme": rank}
json.dump(out, open("run9/wall_compare.json", "w"), indent=1)
for k, v in out.items(): print(k, v if not isinstance(v, dict) else {a: round(b, 3) for a, b in v.items()})
