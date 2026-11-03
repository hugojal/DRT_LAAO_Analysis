"""New mitral valve cut + extrusion, model rotated so that z is the valve axis, Gmsh surface and volume mesh (03/11/2026).

Input: 2_mesh/HugoJal_Case3.stl (original surface, LPS mm, not modified) and mitral_annulus.json (find_mitral_annulus.py).
1. Cut the LA surface with the mitral annular plane fitted on the CT (only the part around the valve lies beyond it).
2. Extrude the cut outline (the anatomical annulus shape) 10 mm along the valve axis in 0.8 mm layers and close it
   with a flat cap: the cap meets the extrusion at 90 deg, so Fluent separates it by angle.
3. Smooth only a +-4 mm band around the junction LA wall / extrusion (weighted Laplacian), so the transition is
   smooth; the rest of the atrium and the cap edge are not touched.
4. Rotate and translate: annulus centre -> origin, valve axis -> z. Sign: blood flows from LA to LV towards -z,
   so the displacement in 3_simulation/*/motion.prof (negative in systole) moves the annulus towards the LV.
   Isolated creases of the original surface (> 45 deg, away from the caps) are relaxed locally.
5. MeshLab isotropic remeshing to ~0.95 mm triangles, cap rings kept sharp (remesh_surface.py, needs pymeshlab;
   set PYMESHLAB_PYTHON to a Python that has it). Saved as the surface .stl.
6. Gmsh: tetrahedra on that surface (triangles kept), size growing towards the centre, Netgen + Relocate3D
   optimisation. Exported as .bdf (as before: GRID + CTETRA only; Fluent creates the boundary and separates the
   PV/MV caps by angle).
Usage: python build_mesh_mvz.py"""
import os, json, subprocess
import numpy as np, pyvista as pv, gmsh

HERE = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"); MESH = os.path.dirname(HERE)
TAG = "HugoJal_Case3_mvz_03112026"
EXT_LEN, EXT_STEP, BAND, H_SURF, H_VOL = 10.0, 0.8, 4.0, 0.95, 1.9

J = json.load(open(HERE + "/mitral_annulus.json")); c = np.array(J["centre_LPS_mm"]); n = np.array(J["normal_LA_to_LV"]); n /= np.linalg.norm(n)
s = pv.read(MESH + "/HugoJal_Case3.stl").clean()

# 1. cut at the annulus plane (keep the LA side)
la = s.clip(normal=n, origin=c, invert=True).clean()
loop = la.extract_feature_edges(boundary_edges=True, feature_edges=False, manifold_edges=False, non_manifold_edges=False)
assert loop.connectivity().cell_data["RegionId"].max() == 0, "the cut must leave exactly one outline"
# order the outline points
E = loop.lines.reshape(-1, 3)[:, 1:]; nxt = {}
for a, b in E: nxt.setdefault(a, []).append(b); nxt.setdefault(b, []).append(a)
order = [E[0, 0]]; prev = None
while True:
    cand = [k for k in nxt[order[-1]] if k != prev]; prev = order[-1]
    if cand[0] == order[0]: break
    order.append(cand[0])
P0 = loop.points[order]; P0 = P0 - np.outer((P0 - c) @ n, n)                    # exactly on the plane
m = len(P0)

# 2. extrusion in layers + flat cap
layers = np.arange(0, EXT_LEN + 1e-9, EXT_STEP); layers[-1] = EXT_LEN
pts = np.vstack([P0 + t * n for t in layers]); faces = []
for k in range(len(layers) - 1):
    for i in range(m):
        a, b = k * m + i, k * m + (i + 1) % m; a2, b2 = a + m, b + m
        faces += [3, a, b, b2, 3, a, b2, a2]
side = pv.PolyData(pts, np.array(faces))
cap = pv.PolyData(P0 + EXT_LEN * n, np.hstack([[m], np.arange(m)])).triangulate()
model = (la + side + cap).clean(tolerance=1e-4).triangulate()

# 3. smooth the junction band only (weight 1 at the annulus plane, 0 at +-BAND mm and at the cap)
d = (model.points - c) @ n
w = np.clip(1 - np.abs(d) / BAND, 0, 1)
sm = model.smooth(n_iter=150, relaxation_factor=0.1, feature_smoothing=False, boundary_smoothing=False)
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
