"""ParaView wall file of a run (analysis cycle + previous cycle): TAWSS, OSI, ECAP, RRT, wall vorticity, distance to the device.
Same arrays as 4_postprocessing/paraview/run5_wall_metrics.vtp; report_quant.py adds LowShearTimeFraction afterwards.
usage: python make_wall_vtp.py <run>   (reads 4_postprocessing/<run>/results.npz, writes 4_postprocessing/paraview/<run>_wall_metrics.vtp)"""
import os, sys, numpy as np, pyvista as pv
from scipy.spatial import cKDTree
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/"); RUN = sys.argv[1]
Z = np.load(ROOT + f"/4_postprocessing/{RUN}/results.npz"); ref, tri = Z["ref_pts"], Z["tri"]; A, B = int(Z["ncyc"]) - 2, int(Z["ncyc"]) - 1
surf = pv.PolyData(ref, np.hstack([np.full((len(tri), 1), 3), tri]).ravel())
for n, q in (("TAWSS_Pa", "tawss"), ("OSI", "osi"), ("ECAP_1_per_Pa", "ecap"), ("RRT_1_per_Pa", "rrt"), ("WallVorticity_1_per_s", "wallvort")):
    surf.point_data[n] = Z[f"c{B}_{q}"]; surf.point_data[n + "_prevcycle"] = Z[f"c{A}_{q}"]
surf.point_data["dist_to_device_mm"] = cKDTree(Z["dev"] / 1000.0).query(ref)[0] * 1000
surf.save(ROOT + f"/4_postprocessing/paraview/{RUN}_wall_metrics.vtp"); print("written", f"{RUN}_wall_metrics.vtp", surf.n_points, "points")
