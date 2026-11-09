"""Cross-sections in front of the device and recirculation check (last beat of a run), 07/11/2026.
Planes perpendicular to the device axis (disc centre and normal of the disc-rim fit, as in ct_wire_figure.py, mapped to the
model frame) at d mm from the disc centre towards the atrium. Each plane is cut to the blood region that touches the
axis and limited to a column of radius RCOL around it (the blood facing the occluder).
Per plane and time step: section area, mean |v|, mean axial velocity, area fraction flowing towards the device and away
from it (both large at the same time = recirculation), area fraction with |v| < 0.05 m/s (stagnant).
Volume check: blood within 10 mm of the device, fraction with |v| < 0.05 m/s and fraction with Q > 0 (vortex-dominated).
Writes 4_postprocessing/<run>/device_sections/{sections.csv, summary.json, near_device_volume.csv, axis.json}; figures: plot_device_sections.py.
usage: python device_sections.py [run]   (default run8; results/<run>_4cycles -> 4_postprocessing/<run>/device_sections)"""
import os, sys, json, csv
import numpy as np, nrrd, pyvista as pv, vtk, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy.spatial import cKDTree
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = sys.argv[1] if len(sys.argv) > 1 else "run8"
RES = os.path.join(ROOT, "3_simulation", "results", f"{RUN}_4cycles"); OUT = os.path.join(ROOT, "4_postprocessing", RUN, "device_sections")
os.makedirs(OUT, exist_ok=True)
STEPS = range(263, 351); DT = 0.01; DS = (2, 5, 8, 12, 16); RCOL = 0.020; VSTAG = 0.05

# device axis in the model frame (m); N points from the atrium into the appendage
h = nrrd.read_header(os.path.join(ROOT, "1_segmentation", "device", "gamma", "Device_gamma_wire_v4_06112026.seg.nrrd"))
D = np.array(h["space directions"], float)[-3:]; O = np.array(h["space origin"], float); SP = np.diag(D)
C = np.array([114.181, 156.072, 98.509]); N = np.array([0.57050955, -0.45992626, 0.68043125]); N /= np.linalg.norm(N)
TR = json.load(open(os.path.join(ROOT, "2_mesh", "run8_07112026", "transform_LPS_to_model.json"))); R = np.array(TR["R"]); c = np.array(TR["c_LPS_mm"])   # same frame for run7 and run8
nl = (N / SP) @ D; nl /= np.linalg.norm(nl)
CM = R @ (O + (C / SP) @ D - c) / 1000.0; NM = R @ nl
json.dump(dict(centre_m=CM.tolist(), normal_into_appendage=NM.tolist(), planes_mm=list(DS), column_radius_mm=RCOL * 1000), open(os.path.join(OUT, "axis.json"), "w"), indent=1)
dev = pv.read(os.path.join(ROOT, "4_postprocessing", "paraview", "device_analysis_model_m.stl")); dtree = cKDTree(np.asarray(dev.points))

def load(k):
    r = vtk.vtkEnSightGoldBinaryReader(); r.SetCaseFileName(os.path.join(RES, f"step_{k:03d}.encas")); r.Update()
    return pv.wrap(r.GetOutput().GetBlock(0))

def section(f, d):
    p = CM - d / 1000.0 * NM
    s = f.slice(normal=NM, origin=p)
    if s.n_points == 0: return None
    s = s.triangulate(); rad = np.linalg.norm(np.cross(s.cell_centers().points - p, NM), axis=1)
    s = s.extract_cells(np.where(rad <= RCOL)[0]).extract_surface(algorithm="dataset_surface")   # column first,
    if s.n_cells == 0: return None
    sub = s.connectivity(extraction_mode="largest").extract_surface(algorithm="dataset_surface")   # then its largest piece (a vein crossing the column is smaller; 07/11/2026: the piece nearest the axis point picked a vein at 12 mm in run8)
    sub = sub.compute_cell_sizes(length=False, volume=False); a = sub["Area"]
    v = sub.point_data_to_cell_data()["Velocity"]; un = v @ NM; vm = np.linalg.norm(v, axis=1); A = a.sum()
    return dict(area_mm2=A * 1e6, vmean=float((vm * a).sum() / A), un_mean=float((un * a).sum() / A),
                frac_towards=float(a[un > 0.005].sum() / A), frac_away=float(a[un < -0.005].sum() / A), frac_stag=float(a[vm < VSTAG].sum() / A))

rows, vol = [], []
for k in STEPS:
    f = load(k); t = round(k * DT, 2)
    for d in DS:
        r = section(f, d)
        if r: rows.append(dict(step=k, t=t, d_mm=d, **r))
    cs = f.compute_cell_sizes(length=False, area=False); cen = cs.cell_centers().points; near = dtree.query(cen)[0] < 0.010
    cd = cs.point_data_to_cell_data(); V = cs["Volume"][near]; vm = np.linalg.norm(cd["Velocity"][near], axis=1); q = cd["Q_Criterion_Normalized"][near]
    vol.append(dict(step=k, t=t, vol_mL=V.sum() * 1e6, frac_stag=float(V[vm < VSTAG].sum() / V.sum()), frac_vortex=float(V[q > 0].sum() / V.sum()),
                    vmean=float((vm * V).sum() / V.sum())))
    print(k, end=" ", flush=True)
with open(os.path.join(OUT, "sections.csv"), "w", newline="") as fo:
    w = csv.DictWriter(fo, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
with open(os.path.join(OUT, "near_device_volume.csv"), "w", newline="") as fo:
    w = csv.DictWriter(fo, fieldnames=list(vol[0])); w.writeheader(); w.writerows(vol)
summ = dict(planes={})
for d in DS:
    R_ = [r for r in rows if r["d_mm"] == d]
    both = [r for r in R_ if min(r["frac_towards"], r["frac_away"]) > 0.2]          # >= 20 % of the section each way = recirculating section
    summ["planes"][d] = dict(area_mm2_median=float(np.median([r["area_mm2"] for r in R_])), vmean_beat=float(np.mean([r["vmean"] for r in R_])),
                             frac_stag_beat=float(np.mean([r["frac_stag"] for r in R_])), frac_time_recirculating=len(both) / len(R_),
                             net_axial_velocity_beat=float(np.mean([r["un_mean"] for r in R_])))
summ["near_device_10mm"] = dict(vol_mL=float(np.mean([v["vol_mL"] for v in vol])), frac_stag_beat=float(np.mean([v["frac_stag"] for v in vol])),
                                frac_vortex_beat=float(np.mean([v["frac_vortex"] for v in vol])), vmean_beat=float(np.mean([v["vmean"] for v in vol])))
json.dump(summ, open(os.path.join(OUT, "summary.json"), "w"), indent=1)
# figures: python plot_device_sections.py (one figure per quantity, legends outside the axes)
print("\n" + json.dumps(summ, indent=1))
