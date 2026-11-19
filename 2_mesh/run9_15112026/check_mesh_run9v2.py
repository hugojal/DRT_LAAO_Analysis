"""Checks of the run9 v2 mesh: element count (< 500k), negative volumes, quality (SICN, equivolume skewness), boundary = saved STL,
closed/manifold surface, Fluent-type angle separation (30 deg) -> wall, MV cap, 4 PV caps. Writes check_mesh_run9v2.json."""
import os, json
import numpy as np, pyvista as pv, gmsh
import scipy.sparse as sp, scipy.sparse.csgraph as cg
HERE = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"); TAG = "HugoJal_Case3_run9_15112026"; out = {}
gmsh.initialize(); gmsh.option.setNumber("General.Terminal", 0); gmsh.open(HERE + "/" + TAG + ".msh")
et, tags, conn = gmsh.model.mesh.getElements(3); tet_tags = tags[0]; T = conn[0].reshape(-1, 4) - 1
nt, xyz, _ = gmsh.model.mesh.getNodes(); X = np.zeros((int(nt.max()), 3)); X[nt.astype(int) - 1] = xyz.reshape(-1, 3)
sicn = np.array(gmsh.model.mesh.getElementQualities(tet_tags, "minSICN")); gam = np.array(gmsh.model.mesh.getElementQualities(tet_tags, "gamma")); gmsh.finalize()
a, b, cc, d = (X[T[:, k]] for k in range(4)); vol = np.einsum("ij,ij->i", np.cross(b - a, cc - a), d - a) / 6
A_ = np.stack([b - a, cc - a, d - a], 1); rhs = 0.5 * np.einsum("ijk,ijk->ij", A_, A_)
Rc = np.linalg.norm(np.linalg.solve(A_, rhs[..., None])[..., 0], axis=1); Vid = 8 * np.sqrt(3) / 27 * Rc ** 3; skew = np.clip((Vid - np.abs(vol)) / Vid, 0, 1)
out["volume_mesh"] = dict(tetrahedra=int(len(T)), nodes=int(len(np.unique(T))), negative_or_zero_volumes=int((vol <= 0).sum()), total_volume_mL=round(float(np.abs(vol).sum()) / 1000, 2),
    minSICN=dict(min=round(float(sicn.min()), 3), p1=round(float(np.percentile(sicn, 1)), 3), mean=round(float(sicn.mean()), 3)), gamma_min=round(float(gam.min()), 3),
    skewness=dict(max=round(float(skew.max()), 3), mean=round(float(skew.mean()), 3), n_above_0_8=int((skew > 0.8).sum()), n_above_0_9=int((skew > 0.9).sum()), n_above_0_95=int((skew > 0.95).sum())))
F = np.vstack([T[:, [0, 2, 1]], T[:, [0, 1, 3]], T[:, [1, 2, 3]], T[:, [0, 3, 2]]]); key = np.sort(F, axis=1); u, inv, cnt = np.unique(key, axis=0, return_inverse=True, return_counts=True)
bf = F[cnt[inv] == 1]; used = np.unique(bf); remap = -np.ones(len(X), int); remap[used] = np.arange(len(used))
surf = pv.PolyData(X[used], np.hstack([np.full((len(bf), 1), 3), remap[bf]]).ravel()).clean(); surf = surf.compute_normals(cell_normals=True, point_normals=False, auto_orient_normals=True)
e = np.sort(np.vstack([bf[:, [0, 1]], bf[:, [1, 2]], bf[:, [2, 0]]]), axis=1); _, ec = np.unique(e, axis=0, return_counts=True)
stl = pv.read(HERE + "/" + TAG + ".stl").clean()
out["surface"] = dict(triangles=int(surf.n_cells), closed=bool((ec == 2).all()), edges_used_once=int((ec == 1).sum()), edges_used_more_than_twice=int((ec > 2).sum()),
    same_as_saved_stl=bool(stl.n_cells == surf.n_cells and np.allclose(np.sort(stl.points, 0), np.sort(surf.points, 0), atol=1e-4)))
Fs = surf.faces.reshape(-1, 4)[:, 1:]; Nn = surf.cell_data["Normals"]; Ar = surf.compute_cell_sizes()["Area"]; Cc = surf.cell_centers().points
es = np.sort(np.vstack([Fs[:, [0, 1]], Fs[:, [1, 2]], Fs[:, [2, 0]]]), axis=1); _, einv = np.unique(es, axis=0, return_inverse=True)
fid = np.tile(np.arange(len(Fs)), 3); o = np.argsort(einv); pr = fid[o].reshape(-1, 2)
res = {}
for th in (20, 30, 45, 60):
    ok = np.einsum("ij,ij->i", Nn[pr[:, 0]], Nn[pr[:, 1]]) > np.cos(np.radians(th))
    ncomp, lab = cg.connected_components(sp.coo_matrix((np.ones(ok.sum()), (pr[ok, 0], pr[ok, 1])), shape=(len(Fs), len(Fs))), directed=False)
    res[th] = int(ncomp)
    if th == 30:
        regs = []
        for k in np.argsort(-np.bincount(lab, weights=Ar))[:8]:
            f = lab == k; ar = Ar[f].sum(); nm = (Nn[f] * Ar[f, None]).sum(0); nm /= np.linalg.norm(nm); ce = (Cc[f] * Ar[f, None]).sum(0) / ar
            regs.append(dict(area_mm2=round(float(ar), 1), eq_diameter_mm=round(float(2 * np.sqrt(ar / np.pi)), 1), centre=ce.round(1).tolist(), max_out_of_plane_mm=round(float(np.abs((Cc[f] - ce) @ nm).max()), 3)))
out["angle_separation"] = dict(regions_by_threshold_deg=res, largest_regions_30deg=regs)
json.dump(out, open(HERE + "/check_mesh_run9v2.json", "w"), indent=1); print(json.dumps(out, indent=1))
