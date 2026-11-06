"""Mitral outlet narrowed to 5.3 cm2 with a smooth funnel (06/11/2026). Same CT annulus, frame and pipeline as
../mv_aligned_03112026/build_mesh_mvz.py; only the region around the mitral valve changes.

Why: the annulus cut of the mvz mesh is 8.6 cm2, but the mitral valve orifice (open leaflets in diastole) is 4-6 cm2
(course requirement). A first try (first_try_step/) only tapered the extension below the annulus: the LA floor, which
flares out at ~45 deg just above the annulus, then met the converging taper in a concave step (collar).
Input: 2_mesh/HugoJal_Case3.stl (original surface, LPS mm, not modified) and mitral_annulus.json (find_mitral_annulus.py).
1. Erase: cut the LA surface ERASE_H mm above the annulus plane (LA side) and remove everything below; the cut leaves
   one star-shaped outline (checked).
2. Fill: one smooth funnel from that outline to the outlet. In polar coordinates around the valve axis, every outline
   point follows a cubic Hermite curve r(d) that starts with the slope of the LA wall at the cut (C1 junction, no step)
   and ends parallel to the axis TAPER_END mm below the annulus, on the annulus outline (cut on the CT annulus plane)
   scaled to A_OUT about its centroid (same D shape). The slope is limited so that r decreases monotonically.
   Then STRAIGHT_LEN mm straight and a flat cap: the wall meets the cap at 90 deg (Fluent separates it by angle) and
   the moving cap (rigid motion along z, faceted deforming wall) keeps its area.
3. Light weighted Laplacian smoothing of the funnel only: full weight from the erase line to 2 mm before the end of the
   taper, ramping to 0 at BAND mm above the erase line and at the end of the taper (outlet ring and cap untouched).
4. Rotate and translate: annulus centre -> origin, valve axis -> z. Sign: blood flows from LA to LV towards -z,
   so the displacement in 3_simulation/*/motion.prof (negative in systole) moves the annulus towards the LV.
   Isolated creases of the original surface (> 45 deg, away from the caps) are relaxed locally.
5. MeshLab isotropic remeshing to ~0.95 mm triangles, cap rings kept sharp (remesh_surface.py, needs pymeshlab;
   set PYMESHLAB_PYTHON to a Python that has it). Saved as the surface .stl.
6. Gmsh: tetrahedra on that surface (triangles kept), size growing towards the centre, Netgen + Relocate3D
   optimisation. Exported as .bdf (as before: GRID + CTETRA only; Fluent creates the boundary and separates the
   PV/MV caps by angle).
Usage: python build_mesh_mv53.py"""
import os, json, subprocess
import numpy as np, pyvista as pv, gmsh

HERE = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"); MESH = os.path.dirname(HERE)
TAG = "HugoJal_Case3_mv53_06112026"
A_OUT, ERASE_H, TAPER_END, STRAIGHT_LEN, STEP = 530.0, 6.0, 5.0, 1.5, 0.5   # mm2, mm above / below the annulus, mm, layer mm
BAND, H_SURF, H_VOL = 2.0, 0.95, 1.9

J = json.load(open(HERE + "/mitral_annulus.json")); c = np.array(J["centre_LPS_mm"]); n = np.array(J["normal_LA_to_LV"]); n /= np.linalg.norm(n)
s = pv.read(MESH + "/HugoJal_Case3.stl").clean()

# 1. erase: cut ERASE_H mm above the annulus plane (LA side), keep the LA
def ordered_loop(mesh):
    lp = mesh.extract_feature_edges(boundary_edges=True, feature_edges=False, manifold_edges=False, non_manifold_edges=False)
    assert lp.connectivity().cell_data["RegionId"].max() == 0, "the cut must leave exactly one outline"
    E = lp.lines.reshape(-1, 3)[:, 1:]; nxt = {}
    for a_, b_ in E: nxt.setdefault(a_, []).append(b_); nxt.setdefault(b_, []).append(a_)
    order = [E[0, 0]]; prev = None
    while True:
        cand = [k for k in nxt[order[-1]] if k != prev]; prev = order[-1]
        if cand[0] == order[0]: break
        order.append(cand[0])
    return lp.points[order]
e1 = np.cross(n, [1.0, 0, 0]); e1 /= np.linalg.norm(e1); e2 = np.cross(n, e1)
uv = lambda P: np.c_[(P - c) @ e1, (P - c) @ e2]
def area_centroid(q):
    u, v = q[:, 0], q[:, 1]; cr = u * np.roll(v, -1) - np.roll(u, -1) * v
    return abs(cr.sum()) / 2, np.array([((u + np.roll(u, -1)) * cr).sum(), ((v + np.roll(v, -1)) * cr).sum()]) / (3 * cr.sum())
def polar(q, g):                                                            # periodic r(theta) of a star-shaped outline
    th = np.arctan2(q[:, 1] - g[1], q[:, 0] - g[0]); r = np.linalg.norm(q - g, axis=1); o = np.argsort(th)
    th, r = th[o], r[o]
    return lambda t: np.interp(np.mod(t + np.pi, 2 * np.pi) - np.pi, np.r_[th - 2 * np.pi, th, th + 2 * np.pi], np.r_[r, r, r])
def section(d):                                                             # outline of the original surface d mm along n
    sl = s.slice(normal=n, origin=c + d * n).strip(); k = int(np.argmax([sl.get_cell(i).n_points for i in range(sl.n_cells)]))
    return uv(sl.get_cell(k).points)
la = s.clip(normal=n, origin=c - ERASE_H * n, invert=True).clean()
Pt = ordered_loop(la); Pt = Pt - np.outer((Pt - c) @ n + ERASE_H, n); m = len(Pt)    # exactly on the erase plane
qt = uv(Pt); At, gt = area_centroid(qt)
th = np.arctan2(qt[:, 1] - gt[1], qt[:, 0] - gt[0]); rt = np.linalg.norm(qt - gt, axis=1)
assert np.all(np.abs(np.diff(np.unwrap(th))) < np.pi / 2) and (np.sign(np.diff(np.unwrap(th))) == np.sign(np.unwrap(th)[-1] - th[0])).mean() > 0.97, "erase outline is not star-shaped"
q1 = section(-ERASE_H - 1.0); r_above = polar(q1, gt)(th)                       # 1 mm further into the LA, same centre
q0 = section(0.0); A0, g0 = area_centroid(q0); k_end = np.sqrt(A_OUT / A0); rb = k_end * polar(q0, g0)(th)
slope = rt - r_above                                                        # dr/dd at the erase line (d increases towards the LV)
slope = np.median(np.stack([np.roll(slope, k) for k in range(-3, 4)]), 0)  # circular median of 7 outline points: removes single outliers
L = ERASE_H + TAPER_END; drop = rt - rb
assert drop.min() > 0, "outlet outline must lie inside the erase outline"
slope = np.maximum(slope, -3 * drop / L)                                    # monotone Hermite (Fritsch-Carlson bound)
print(f"erase outline {At:.1f} mm2 at {ERASE_H} mm above the annulus; annulus {A0:.1f} mm2 -> outlet {A_OUT:.1f} mm2 (scale {k_end:.4f});"
      f" wall slope at the erase line {np.degrees(np.arctan(-slope)).mean():.0f} deg mean")

# 2. fill: Hermite funnel (r, centre) from the erase outline to the outlet, then straight part + flat cap
ds = np.r_[np.arange(-ERASE_H, TAPER_END, STEP), TAPER_END, np.arange(TAPER_END + STEP, TAPER_END + STRAIGHT_LEN, STEP), TAPER_END + STRAIGHT_LEN]
ds = np.unique(ds.round(6))
def ring(d):
    t = np.clip((d + ERASE_H) / L, 0, 1)
    h00, h10, h01 = 2 * t ** 3 - 3 * t ** 2 + 1, t ** 3 - 2 * t ** 2 + t, -2 * t ** 3 + 3 * t ** 2
    r = h00 * rt + h10 * L * slope + h01 * rb
    g = gt + (g0 - gt) * (3 * t ** 2 - 2 * t ** 3)
    return c + d * n + np.outer(g[0] + r * np.cos(th), e1) + np.outer(g[1] + r * np.sin(th), e2)
rings = [Pt] + [ring(d) for d in ds[1:]]
pts = np.vstack(rings); faces = []
for k in range(len(rings) - 1):
    for i in range(m):
        a, b = k * m + i, k * m + (i + 1) % m; a2, b2 = a + m, b + m
        faces += [3, a, b, b2, 3, a, b2, a2]
side = pv.PolyData(pts, np.array(faces))
cap = pv.PolyData(pts[-m:], np.hstack([[m], np.arange(m)])).triangulate()
model = (la + side + cap).clean(tolerance=1e-4).triangulate()

# 3. light smoothing of the funnel only (LA above the erase line + BAND and the straight part + cap untouched)
d = (model.points - c) @ n
w = np.clip(np.minimum((d + ERASE_H + BAND) / BAND, (TAPER_END - d) / 2.0), 0, 1)
sm = model.smooth(n_iter=60, relaxation_factor=0.1, feature_smoothing=False, boundary_smoothing=False)
model.points = model.points + w[:, None] * (sm.points - model.points)

# 3b. remove isolated creases of the original surface (Meshmixer artefacts, dihedral > 45 deg) away from the caps:
#     only the crease vertices and their 2-ring are relaxed; cap rings (~90 deg) stay sharp
from scipy.spatial import cKDTree
def edges_dihedral(mesh):
    mesh = mesh.compute_normals(cell_normals=True, point_normals=False, auto_orient_normals=True)
    F = mesh.faces.reshape(-1, 4)[:, 1:]; N = mesh.cell_data["Normals"]
    e = np.sort(np.vstack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]), axis=1); u, inv = np.unique(e, axis=0, return_inverse=True)
    fid = np.tile(np.arange(len(F)), 3); o = np.argsort(inv); pr = fid[o].reshape(-1, 2)
    return u[inv[o][::2]], np.degrees(np.arccos(np.clip(np.einsum("ij,ij->i", N[pr[:, 0]], N[pr[:, 1]]), -1, 1))), F, N
def flat_caps(mesh, F, N):                                     # vertices of planar patches > 150 mm2 (PV caps and MV cap)
    A = mesh.compute_cell_sizes()["Area"]; C = mesh.cell_centers().points
    e = np.sort(np.vstack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]), axis=1); _, inv = np.unique(e, axis=0, return_inverse=True)
    fid = np.tile(np.arange(len(F)), 3); o = np.argsort(inv); pr = fid[o].reshape(-1, 2)
    nb = [[] for _ in F]
    for p_, q_ in pr: nb[p_].append(q_); nb[q_].append(p_)
    used = np.zeros(len(F), bool); vids = []
    for seed in np.argsort(-A):
        if used[seed]: continue
        reg, st = {seed}, [seed]
        while st:
            f = st.pop()
            for g in nb[f]:
                if g not in reg and N[g] @ N[seed] > np.cos(np.radians(2)) and abs((C[g] - C[seed]) @ N[seed]) < 0.15: reg.add(g); st.append(g)
        reg = np.array(list(reg)); used[reg] = True
        if A[reg].sum() > 150: vids.append(np.unique(F[reg]))
    return np.concatenate(vids)
for it in range(6):
    eu, dih, F, N = edges_dihedral(model)
    capv = flat_caps(model, F, N)
    near_cap = cKDTree(model.points[capv]).query(model.points)[0] < 1.5
    bad = eu[(dih > 45) & ~near_cap[eu].any(1)]
    print(f"crease pass {it}: {len(bad)} sharp edges away from the caps")
    if len(bad) == 0: break
    adj = [set() for _ in range(model.n_points)]
    for tri in F:
        for i_ in range(3): adj[tri[i_]].update((tri[(i_ + 1) % 3], tri[(i_ + 2) % 3]))
    sel = set(bad.ravel())
    for _ in range(2): sel |= set().union(*[adj[v] for v in sel])
    sel = np.array([v for v in sel if not near_cap[v]])
    for _ in range(10):
        newp = np.array([model.points[list(adj[v])].mean(0) for v in sel]); model.points[sel] = 0.5 * model.points[sel] + 0.5 * newp

# 4. rotation: valve axis n -> -z (flow LA->LV along -z), annulus centre -> origin
def rot(a, b):
    v = np.cross(a, b); cth = a @ b; K = np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])
    return np.eye(3) + K + K @ K / (1 + cth)
R = rot(n, np.array([0, 0, -1.]))
model.points = (model.points - c) @ R.T
T = np.eye(4); T[:3, :3] = R; T[:3, 3] = -R @ c
json.dump(dict(description="x_new = R (x_LPS - c); LPS mm -> model mm. Inverse: x_LPS = R^T x_new + c",
               R=R.round(8).tolist(), c_LPS_mm=c.round(4).tolist(), matrix_4x4=T.round(8).tolist(),
               valve_axis_LPS=n.round(5).tolist(), flow_LA_to_LV="-z"), open(HERE + "/transform_LPS_to_model.json", "w"), indent=1)
pre = HERE + "/_premesh.stl"; model.save(pre)

# 5. MeshLab isotropic remeshing (~0.95 mm, cap rings kept sharp): remesh_surface.py, run with a Python that has pymeshlab
rem = HERE + "/" + TAG + ".stl"
subprocess.run([os.environ.get("PYMESHLAB_PYTHON", "python"), HERE + "/remesh_surface.py", pre, rem, str(H_SURF)], check=True)
os.remove(pre)

# 6. gmsh: tetrahedra on the remeshed surface (its triangles are kept as they are), size growing towards the centre
gmsh.initialize(); gmsh.option.setNumber("General.Terminal", 0); gmsh.model.add(TAG)
gmsh.merge(rem)                                                             # one discrete surface = the STL triangles (as in HugoJal_Case3.geo)
surfs = [t for _, t in gmsh.model.getEntities(2)]
sl = gmsh.model.geo.addSurfaceLoop(surfs); vol = gmsh.model.geo.addVolume([sl]); gmsh.model.geo.synchronize()
f1 = gmsh.model.mesh.field.add("Distance"); gmsh.model.mesh.field.setNumbers(f1, "SurfacesList", surfs); gmsh.model.mesh.field.setNumber(f1, "Sampling", 60)
f2 = gmsh.model.mesh.field.add("Threshold"); gmsh.model.mesh.field.setNumber(f2, "InField", f1)
for k, v in dict(SizeMin=H_SURF, SizeMax=H_VOL, DistMin=1.0, DistMax=7.0).items(): gmsh.model.mesh.field.setNumber(f2, k, v)
gmsh.model.mesh.field.setAsBackgroundMesh(f2)
for k, v in {"Mesh.MeshSizeExtendFromBoundary": 0, "Mesh.MeshSizeFromPoints": 0, "Mesh.MeshSizeFromCurvature": 0,
             "Mesh.MeshSizeMin": 0.6, "Mesh.Algorithm": 6, "Mesh.Algorithm3D": 1, "Mesh.Optimize": 1, "Mesh.OptimizeNetgen": 1,
             "Mesh.OptimizeThreshold": 0.5, "Mesh.Smoothing": 5}.items():
    gmsh.option.setNumber(k, v)
gmsh.model.mesh.generate(3)
for _ in range(3):                                                          # remove slivers
    gmsh.model.mesh.optimize("Netgen"); gmsh.model.mesh.optimize("Relocate3D")
gmsh.model.addPhysicalGroup(3, [vol], 2)
gmsh.write(HERE + "/" + TAG + ".bdf")
gmsh.write(HERE + "/" + TAG + ".msh")
gmsh.finalize()
print("written", TAG + ".stl and .bdf")
