"""Mitral outlet narrowed to 5.3 cm2, smooth valve region, LA size kept (06/11/2026). Same CT annulus, frame and
pipeline as ../mv_aligned_03112026/build_mesh_mvz.py; only the region around the mitral valve changes.

Why: the annulus cut of the mvz mesh is 8.6 cm2, but the mitral valve orifice (open leaflets in diastole) is 4-6 cm2
(course requirement). Earlier tries, kept for reference (check_step_before_after.png compares them):
  first_try_step/    cosine taper below the annulus starting PARALLEL to the axis: the LA wall, converging at ~45 deg
                     into the annulus, was straightened and then converged again -> a step (collar) at the annulus.
  second_try_erase/  erased the LA from 6 mm above the annulus and lofted a funnel from there: no step, but it narrowed
                     the LA neck (-1.3 cm2 at the annulus) and kept a ~1 mm ridge/groove of the segmentation as grooves.
Input: 2_mesh/HugoJal_Case3.stl (original surface, LPS mm, not modified) and mitral_annulus.json (find_mitral_annulus.py).
1. The LA surface is kept as segmented down to TOP mm above the annulus plane fitted on the CT; below it the surface
   is rebuilt as a structured surface in polar coordinates around the valve axis (centre = centroid of the annulus
   cut; every section is star-shaped about it, checked).
2. TOP mm above -> annulus: each layer (every STEP mm) is the ORIGINAL section r(theta), blended into the same section
   low-pass filtered in angle (Fourier harmonics <= N_LA: the shape and size of the neck are kept, the ~1 mm
   ridge/groove of the segmentation next to the annulus is removed). The blend goes from 0 at TOP (exactly the
   segmented LA, zero slope of the blend: no kink) to 1 at TOP - RAMP mm.
3. Annulus -> TAPER_END mm below: cubic Hermite r(d) per angle that starts with the value AND SLOPE of the smoothed LA
   wall at the annulus (it keeps converging as the wall does: C1, no step) and ends parallel to the axis on the outlet
   outline: the annulus outline with harmonics <= N_HARM (2: a convex oval, the open orifice; the kidney-shaped notch
   of the annulus fades out along the funnel instead of running down it as a groove) scaled to A_OUT. Slope limited to <= 0 (no
   bulging) and by the monotone bound. Then STRAIGHT_LEN mm straight and a flat cap: the wall meets the cap at 90 deg
   (Fluent separates it by angle) and the moving cap (rigid motion along z, faceted deforming wall) keeps its area.
4. Rotate and translate: annulus centre -> origin, valve axis -> z. Sign: blood flows from LA to LV towards -z,
   so the displacement in 3_simulation/*/motion.prof (negative in systole) moves the annulus towards the LV.
   Isolated creases of the original surface (> 45 deg, away from the caps) are relaxed locally.
5. MeshLab isotropic remeshing to ~0.95 mm triangles, cap rings kept sharp (remesh_surface.py, needs pymeshlab;
   set PYMESHLAB_PYTHON to a Python that has it). Then edges shorter than 15 % of the target size (needle triangles
   that MeshLab can leave on the feature rings) are collapsed, MV-rim triangles that cut the 90 deg corner are
   flipped, and the interior MV-cap vertices are relaxed in the cap plane. Saved as the surface .stl.
6. Gmsh: tetrahedra on that surface (triangles kept), size growing towards the centre, Netgen + Relocate3D
   optimisation. Exported as .bdf (as before: GRID + CTETRA only; Fluent creates the boundary and separates the
   PV/MV caps by angle).
Usage: python build_mesh_mv53.py"""
import os, json, subprocess
import numpy as np, pyvista as pv, gmsh

HERE = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"); MESH = os.path.dirname(HERE)
TAG = "HugoJal_Case3_mv53_06112026"
A_OUT, TAPER_END, STRAIGHT_LEN, STEP = 530.0, 5.0, 1.5, 0.5                # mm2, mm below the annulus, mm, layer mm
TOP, RAMP, N_LA, N_HARM = 8.0, 3.0, 10, 2                                   # rebuilt from TOP mm above the annulus; harmonics
H_SURF, H_VOL = 0.95, 1.9

J = json.load(open(HERE + "/mitral_annulus.json")); c = np.array(J["centre_LPS_mm"]); n = np.array(J["normal_LA_to_LV"]); n /= np.linalg.norm(n)
s = pv.read(MESH + "/HugoJal_Case3.stl").clean()

# 1. helpers; LA kept as segmented above TOP
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
TG = np.linspace(-np.pi, np.pi, 1440, endpoint=False)
def lowpass(rg, nh):
    F = np.fft.rfft(rg); F[nh + 1:] = 0; return np.fft.irfft(F, len(rg))
at = lambda rg, t: np.interp(np.mod(t + np.pi, 2 * np.pi) - np.pi, np.r_[TG - 2 * np.pi, TG, TG + 2 * np.pi], np.r_[rg, rg, rg])
def star(q, g):
    a_ = np.unwrap(np.arctan2(q[:, 1] - g[1], q[:, 0] - g[0])); da = np.diff(a_)
    return abs(a_[-1] - a_[0]) > 1.9 * np.pi and (np.sign(da) == np.sign(a_[-1] - a_[0])).mean() > 0.97

# centre = centroid of the annulus cut; top outline = the segmented LA cut TOP mm above the annulus
_, gt = area_centroid(section(0.0))
la = s.clip(normal=n, origin=c - TOP * n, invert=True).clean()
Pt = ordered_loop(la); Pt = Pt - np.outer((Pt - c) @ n + TOP, n); m = len(Pt)       # exactly on the top plane
qt = uv(Pt); th = np.arctan2(qt[:, 1] - gt[1], qt[:, 0] - gt[0]); rt = np.linalg.norm(qt - gt, axis=1)
assert star(qt, gt), "top outline is not star-shaped about the annulus centroid"

# 2. layers TOP -> annulus: original section blended into its angular low-pass
d_la = np.round(np.arange(-TOP, 0 + 1e-9, STEP), 6)
R_orig, R_lp = [], []
for dd in d_la:
    q = section(dd); assert star(q, gt), f"section {dd} mm is not star-shaped"
    rg = polar(q, gt)(TG); R_orig.append(at(rg, th)); R_lp.append(at(lowpass(rg, N_LA), th))
R_orig, R_lp = np.array(R_orig), np.array(R_lp)
R_orig[0] = rt                                                              # the top layer is exactly the cut outline
beta = np.clip((d_la + TOP) / RAMP, 0, 1); beta = 3 * beta ** 2 - 2 * beta ** 3     # smoothstep: 0 and flat at TOP
R_la = (1 - beta)[:, None] * R_orig + beta[:, None] * R_lp
ra = R_la[-1]                                                               # smoothed outline at the annulus plane
slope = np.polyfit(d_la[-3:], R_la[-3:], 1)[0]                              # dr/dd of the smoothed wall at the annulus (last 1 mm)
# 3. funnel: outlet outline = annulus outline (polar about gt) with harmonics <= N_HARM, scaled to A_OUT
q0 = section(0.0); A0 = area_centroid(q0)[0]; rs = lowpass(polar(q0, gt)(TG), N_HARM)
k_end = np.sqrt(A_OUT / (0.5 * np.sum(rs ** 2) * (2 * np.pi / len(TG)))); rb = at(rs, th) * k_end
L = TAPER_END; drop = ra - rb
assert drop.min() > 0, "outlet outline must lie inside the annulus outline"
slope = np.clip(slope, -3 * drop / L, 0.0)                                  # no bulging out; monotone Hermite (Fritsch-Carlson)
print(f"annulus cut {A0:.1f} mm2 -> outlet {A_OUT:.1f} mm2 ({N_HARM} harmonics, scale {k_end:.4f}); LA wall angle at the annulus "
      f"{np.degrees(np.arctan(-slope)).mean():.0f} deg mean; LA smoothing changes r by max {np.abs(R_la - R_orig).max():.2f} mm")
d_fun = np.unique(np.r_[np.arange(STEP, TAPER_END, STEP), TAPER_END, np.arange(TAPER_END + STEP, TAPER_END + STRAIGHT_LEN, STEP), TAPER_END + STRAIGHT_LEN].round(6))
def r_fun(dd):
    t = min(dd / L, 1.0); return (2 * t ** 3 - 3 * t ** 2 + 1) * ra + (t ** 3 - 2 * t ** 2 + t) * L * slope + (-2 * t ** 3 + 3 * t ** 2) * rb
ring = lambda dd, r: c + dd * n + np.outer(gt[0] + r * np.cos(th), e1) + np.outer(gt[1] + r * np.sin(th), e2)
rings = [Pt] + [ring(dd, r) for dd, r in zip(d_la[1:], R_la[1:])] + [ring(dd, r_fun(dd)) for dd in d_fun]
pts = np.vstack(rings); faces = []
for k in range(len(rings) - 1):
    for i in range(m):
        a, b = k * m + i, k * m + (i + 1) % m; a2, b2 = a + m, b + m
        faces += [3, a, b, b2, 3, a, b2, a2]
side = pv.PolyData(pts, np.array(faces))
cap = pv.PolyData(pts[-m:], np.hstack([[m], np.arange(m)])).triangulate()
model = (la + side + cap).clean(tolerance=1e-4).triangulate()

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
# 5b. collapse needle edges (< 15 % of H_SURF): both vertices moved to the midpoint, then merged; check closed + manifold
sr = pv.read(rem).clean()
for it in range(5):
    F = sr.faces.reshape(-1, 4)[:, 1:]; E = np.unique(np.sort(np.vstack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]), 1), axis=0)
    Ln = np.linalg.norm(sr.points[E[:, 0]] - sr.points[E[:, 1]], axis=1); short = E[Ln < 0.15 * H_SURF]
    print(f"needle pass {it}: {len(short)} edges shorter than {0.15 * H_SURF:.2f} mm")
    if len(short) == 0: break
    P = sr.points.copy(); used = set()
    for a_, b_ in short:
        if a_ in used or b_ in used: continue
        P[a_] = P[b_] = 0.5 * (P[a_] + P[b_]); used |= {a_, b_}
    sr.points = P; sr = sr.clean(tolerance=0.0).triangulate()
# 5c. MV cap rim: MeshLab can join a cap vertex just inside the rim to a wall vertex, so two triangles cut the 90 deg
#     corner (Fluent would separate them as an extra zone). Flip their shared edge so that the rim edge is restored.
z_cap = -(TAPER_END + STRAIGHT_LEN)
for it in range(5):
    sr = sr.compute_normals(cell_normals=True, point_normals=False, auto_orient_normals=True)
    F = sr.faces.reshape(-1, 4)[:, 1:].copy(); Nc = sr.cell_data["Normals"]; Cc = sr.cell_centers().points
    ang = np.degrees(np.arccos(np.clip(-Nc[:, 2], -1, 1)))
    bad = set(np.where((np.abs(Cc[:, 2] - z_cap) < 0.6) & (ang > 15) & (ang < 75))[0])
    print(f"rim pass {it}: {len(bad)} corner-cutting triangles")
    if not bad: break
    done = set()
    for i in sorted(bad):
        if i in done: continue
        for j in sorted(bad - done - {i}):
            sh = np.intersect1d(F[i], F[j])
            if len(sh) != 2: continue
            oi = np.setdiff1d(F[i], sh)[0]; oj = np.setdiff1d(F[j], sh)[0]
            F[i] = [oi, oj, sh[0]]; F[j] = [oj, oi, sh[1]]; done |= {i, j}; break
    sr = pv.PolyData(sr.points, np.c_[np.full(len(F), 3), F].ravel()).clean()
sr = sr.compute_normals(cell_normals=True, point_normals=False, consistent_normals=True, auto_orient_normals=True)   # consistent outward winding
# 5d. relax the interior vertices of the MV cap in its plane (rim fixed, cap stays flat): evens out the triangles next to
#     the rim after the flips
F = sr.faces.reshape(-1, 4)[:, 1:]; P = sr.points.copy(); on_cap = np.abs(P[:, 2] - z_cap) < 1e-4
rim = np.unique(F[(on_cap[F].sum(1) < 3)][on_cap[F[(on_cap[F].sum(1) < 3)]]])             # cap vertices touching a wall triangle
inner = np.setdiff1d(np.where(on_cap)[0], rim)
nbr = [set() for _ in range(len(P))]
for t in F[on_cap[F].all(1)]:
    for k in range(3): nbr[t[k]].update((t[(k + 1) % 3], t[(k + 2) % 3]))
for _ in range(10):
    P[inner, :2] = np.array([P[list(nbr[v]), :2].mean(0) for v in inner])
sr.points = P
ec = sr.extract_feature_edges(boundary_edges=True, non_manifold_edges=True, feature_edges=False, manifold_edges=False).n_cells
assert ec == 0, f"surface not closed/manifold after needle collapse ({ec} bad edges)"
sr.save(rem, binary=True)

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
