"""Checks of the 5.3 cm2 tapered-outlet mesh against the course requirements (06/11/2026; copy of ../mv_aligned_03112026/check_mesh_mvz.py).
- mitral cross-section area along the valve axis (cap must be 4-6 cm2)

- volume mesh: element count (< 500k), negative volumes, quality (Gmsh SICN/gamma, Fluent-type equivolume skewness)
- surface (boundary of the tetrahedra): closed, no non-manifold edges, element count, identical to the saved .stl
- angle separation as in Fluent (Separate > Faces by angle 30 deg): caps found, their normals vs z and sizes
- no oversmoothing: distance from the new surface to the original one, away from the mitral extrusion
- mitral cut on the CT: new surface mapped back to LPS and drawn on planes through the valve axis
Writes check_mesh_mv53.json and check_*.png. Usage: python check_mesh_mv53.py"""
import os, json
import numpy as np, pyvista as pv, gmsh, nrrd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from scipy import ndimage as ndi
from scipy.spatial import cKDTree

HERE = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"); MESH = os.path.dirname(HERE); ROOT = os.path.dirname(MESH)
TAG = "HugoJal_Case3_mv53_06112026"
TR = json.load(open(HERE + "/transform_LPS_to_model.json")); R = np.array(TR["R"]); c = np.array(TR["c_LPS_mm"])
out = {}

# volume mesh
gmsh.initialize(); gmsh.option.setNumber("General.Terminal", 0); gmsh.open(HERE + "/" + TAG + ".msh")
et, tags, conn = gmsh.model.mesh.getElements(3)
tet_tags = tags[0]; T = conn[0].reshape(-1, 4) - 1
nt, xyz, _ = gmsh.model.mesh.getNodes(); X = np.zeros((int(nt.max()), 3)); X[nt.astype(int) - 1] = xyz.reshape(-1, 3)
sicn = np.array(gmsh.model.mesh.getElementQualities(tet_tags, "minSICN")); gam = np.array(gmsh.model.mesh.getElementQualities(tet_tags, "gamma"))
gmsh.finalize()
a, b, cc, d = (X[T[:, k]] for k in range(4))
vol = np.einsum("ij,ij->i", np.cross(b - a, cc - a), d - a) / 6
# Fluent-type skewness for tetrahedra: (V_ideal - V) / V_ideal, V_ideal = equilateral tet with the same circumradius
def circumradius(a, b, c_, d):
    A = np.stack([b - a, c_ - a, d - a], 1); rhs = 0.5 * np.einsum("ijk,ijk->ij", A, A)
    return np.linalg.norm(np.linalg.solve(A, rhs[..., None])[..., 0], axis=1)
Rc = circumradius(a, b, cc, d); Vid = 8 * np.sqrt(3) / 27 * Rc ** 3
skew = np.clip((Vid - np.abs(vol)) / Vid, 0, 1)
out["volume_mesh"] = dict(tetrahedra=int(len(T)), nodes=int(len(np.unique(T))), negative_or_zero_volumes=int((vol <= 0).sum()),
                          total_volume_mL=round(float(np.abs(vol).sum()) / 1000, 1),
                          minSICN=dict(min=round(float(sicn.min()), 3), p1=round(float(np.percentile(sicn, 1)), 3), mean=round(float(sicn.mean()), 3)),
                          gamma=dict(min=round(float(gam.min()), 3), mean=round(float(gam.mean()), 3)),
                          skewness=dict(max=round(float(skew.max()), 3), mean=round(float(skew.mean()), 3), n_above_0_8=int((skew > 0.8).sum()), n_above_0_9=int((skew > 0.9).sum()), n_above_0_95=int((skew > 0.95).sum())))

# boundary surface of the tetrahedra
F = np.vstack([T[:, [0, 2, 1]], T[:, [0, 1, 3]], T[:, [1, 2, 3]], T[:, [0, 3, 2]]])
key = np.sort(F, axis=1); u, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True)
bf = F[cnt[inv] == 1]
used = np.unique(bf); remap = -np.ones(len(X), int); remap[used] = np.arange(len(used))
surf = pv.PolyData(X[used], np.hstack([np.full((len(bf), 1), 3), remap[bf]]).ravel()).clean()
surf = surf.compute_normals(cell_normals=True, point_normals=False, auto_orient_normals=True)
e = np.sort(np.vstack([bf[:, [0, 1]], bf[:, [1, 2]], bf[:, [2, 0]]]), axis=1); _, ec = np.unique(e, axis=0, return_counts=True)
out["surface"] = dict(triangles=int(surf.n_cells), edges_used_once=int((ec == 1).sum()), edges_used_more_than_twice=int((ec > 2).sum()),
                      closed=bool((ec == 2).all()), volume_mL=round(float(surf.volume) / 1000, 1))
stl = pv.read(HERE + "/" + TAG + ".stl").clean()
out["surface"]["same_as_saved_stl"] = bool(stl.n_cells == surf.n_cells and np.allclose(np.sort(stl.points, 0), np.sort(surf.points, 0), atol=1e-4))

# angle separation (like Fluent Separate > Faces by angle): region growing across edges with dihedral angle < 30 deg
Fs = surf.faces.reshape(-1, 4)[:, 1:]; Nn = surf.cell_data["Normals"]; A = surf.compute_cell_sizes()["Area"]; Cc = surf.cell_centers().points
es = np.sort(np.vstack([Fs[:, [0, 1]], Fs[:, [1, 2]], Fs[:, [2, 0]]]), axis=1); _, einv = np.unique(es, axis=0, return_inverse=True)
fid = np.tile(np.arange(len(Fs)), 3); o = np.argsort(einv); pr = fid[o].reshape(-1, 2)
ok = np.einsum("ij,ij->i", Nn[pr[:, 0]], Nn[pr[:, 1]]) > np.cos(np.radians(30))
import scipy.sparse as sp, scipy.sparse.csgraph as cg
G = sp.coo_matrix((np.ones(ok.sum()), (pr[ok, 0], pr[ok, 1])), shape=(len(Fs), len(Fs)))
ncomp, lab = cg.connected_components(G, directed=False)
regs = []
for k in np.argsort(-np.bincount(lab, weights=A))[:12]:
    f = lab == k; ar = A[f].sum(); nm = (Nn[f] * A[f, None]).sum(0); nm /= np.linalg.norm(nm); ce = (Cc[f] * A[f, None]).sum(0) / ar
    flat = float(np.abs((Cc[f] - ce) @ nm).max())
    regs.append(dict(area_mm2=round(float(ar), 1), eq_diameter_mm=round(float(2 * np.sqrt(ar / np.pi)), 1), normal=nm.round(3).tolist(),
                     centre=ce.round(1).tolist(), max_out_of_plane_mm=round(flat, 2), angle_to_z_deg=round(float(np.degrees(np.arccos(abs(nm[2])))), 1)))
out["angle_separation_30deg"] = dict(regions=int(ncomp), largest=regs)

# no oversmoothing: distance to the original surface (LPS), outside the mitral region
orig = pv.read(MESH + "/HugoJal_Case3.stl").clean()
P_lps = surf.points @ R + c
n_ax = np.array(TR["valve_axis_LPS"]); dax = (P_lps - c) @ n_ax
far = dax < -8.5                                                            # more than 8.5 mm on the LA side of the annulus (rebuilt region: 8 mm)
dist, _ = cKDTree(orig.points).query(P_lps[far])
# point-to-surface distance (closest point on the original triangles)
cp = orig.find_closest_cell(P_lps[far], return_closest_point=True)[1]; dist = np.linalg.norm(P_lps[far] - cp, axis=1)
out["shape_change_vs_original_mm"] = dict(region="surface > 8.5 mm from the annulus on the LA side", mean=round(float(dist.mean()), 3),
                                          p95=round(float(np.percentile(dist, 95)), 3), max=round(float(dist.max()), 3))
# mitral cross-section area along the valve axis (model frame, z = valve axis, cap at the most negative z)
zc = []
for z in [round(surf.bounds[4] + 0.05, 2), -5.0, -4.0, -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0]:
    sl = surf.slice(normal=[0, 0, 1], origin=[0, 0, z]).strip(); ar = []
    for i in range(sl.n_cells):
        q = sl.get_cell(i).points; ar.append(0.5 * abs(q[:, 0] @ np.roll(q[:, 1], 1) - q[:, 1] @ np.roll(q[:, 0], 1)))
    zc.append(dict(z_mm=z, area_cm2=round(max(ar) / 100, 2)))
out["mitral_sections"] = zc
json.dump(out, open(HERE + "/check_mesh_mv53.json", "w"), indent=1); print(json.dumps(out, indent=1))

# figures: (1) surface with caps coloured, z axis; (2) close-up of the mitral extrusion with edges; (3) volume slice
pv.OFF_SCREEN = True
surf.cell_data["region"] = lab
p = pv.Plotter(shape=(1, 3), window_size=(1800, 640))
p.subplot(0, 0); p.add_mesh(surf, scalars="region", cmap="tab20", show_scalar_bar=False, smooth_shading=True)
p.add_mesh(pv.Arrow(start=(0, 0, 0), direction=(0, 0, -1), scale=30), color="red"); p.add_axes()
p.add_text("Fluent-like separation at 30 deg; red arrow = flow LA->LV (-z)", font_size=9); p.camera_position = [(140, -140, 60), (0, 0, 25), (0, 0, 1)]
p.subplot(0, 1); p.add_mesh(surf, color="wheat", show_edges=True, edge_color="k", line_width=0.3)
p.add_text("tapered mitral extension, surface elements", font_size=9); p.camera_position = [(45, -45, -30), (0, 0, -3), (0, 0, 1)]
p.subplot(0, 2)
grid = pv.UnstructuredGrid({pv.CellType.TETRA: T}, X)
grid.cell_data["skewness"] = skew
cut = grid.clip(normal=(0, 1, 0), origin=(0, 0, 0), crinkle=True)
p.add_mesh(cut, scalars="skewness", cmap="viridis", clim=[0, 1], show_edges=True, edge_color="k", line_width=0.2, scalar_bar_args=dict(title="skewness"))
p.add_text("volume mesh cut through the valve axis", font_size=9); p.camera_position = [(0, -150, 20), (0, 0, 20), (0, 0, 1)]
p.screenshot(HERE + "/check_mesh_views.png"); p.close()

# CT check: radial planes through the valve axis with the new surface (red) and the original surface (cyan)
ct, h = nrrd.read(ROOT + "/1_segmentation/5 DS_Coronaires  0.75  B26f  BestDiast 78 %.nrrd"); ct = ct.astype(np.float32)
SP = np.diag(h["space directions"]).astype(float); ORG = np.asarray(h["space origin"], float)
new_lps = surf.copy(); new_lps.points = P_lps
fig, axs = plt.subplots(2, 3, figsize=(15, 10))
aa = np.cross(n_ax, [0, 0, 1.]); aa /= np.linalg.norm(aa); bb = np.cross(n_ax, aa)
for k, phi in enumerate(np.radians([0, 30, 60, 90, 120, 150])):
    dd = np.cos(phi) * aa + np.sin(phi) * bb; t = np.arange(-35, 35.01, 0.25); Xg, Yg = np.meshgrid(t, t, indexing="ij")
    Pp = c + Xg[..., None] * n_ax + Yg[..., None] * dd
    img = ndi.map_coordinates(ct, ((Pp - ORG) / SP).transpose(2, 0, 1), order=1, mode="nearest")
    ax_ = axs.ravel()[k]; ax_.imshow(np.clip((img + 160) / 1000, 0, 1).T, cmap="gray", origin="lower", extent=[t[0], t[-1], t[0], t[-1]])
    pn = np.cross(n_ax, dd)                                                  # normal of the radial plane
    for mesh_, col, lab_ in [(orig, "c", "original surface"), (new_lps, "r", "new surface")]:
        sl = mesh_.slice(normal=pn, origin=c)
        if sl.n_points:
            q = sl.points - c; lines = sl.lines.reshape(-1, 3)[:, 1:]
            for i0, i1 in lines: ax_.plot([q[i0] @ n_ax, q[i1] @ n_ax], [q[i0] @ dd, q[i1] @ dd], color=col, lw=0.8)
            ax_.plot([], [], color=col, label=lab_)
    hp = np.array(json.load(open(HERE + "/mitral_annulus.json"))["hinge_points"]) - c
    inpl = np.abs(hp @ pn) < 1.5; ax_.plot(hp[inpl] @ n_ax, hp[inpl] @ dd, "o", mfc="none", mec="y", ms=6, label="annulus hinge points")
    ax_.set_xlim(-35, 35); ax_.set_ylim(-35, 35); ax_.set_title(f"plane through the valve axis, {np.degrees(phi):.0f} deg (left = LA, right = LV)", fontsize=8)
    if k == 0: ax_.legend(fontsize=7, loc="lower left")
plt.suptitle("Mitral cut on the CT: new surface (red: valve region rebuilt from 8 mm above the annulus, 5.3 cm2 outlet 6.5 mm below) vs original (cyan)", fontsize=10)
plt.tight_layout(); plt.savefig(HERE + "/check_mitral_on_ct.png", dpi=90)
