"""run9 surface (15/11/2026): run8 surface with two local repairs, nothing else changed.
1. a conical spur (~4 mm) next to the RIPV extension is smoothed away (local Taubin, weight fades to 0 over a ring);
2. the last PV_REBUILD mm of each PV extension (and its cap) are rebuilt: exact circular cylinder, evenly spaced rings,
   flat cap triangulated from concentric rings (run8 had a ragged rim after MeshLab).
Input: ../run8_07112026/HugoJal_Case3_run8_07112026.stl (model frame, mm) + caps_model_frame.json. Output: HugoJal_Case3_run9_15112026.stl"""
import os, json, numpy as np, pyvista as pv
from scipy.spatial import Delaunay
HERE = os.path.dirname(os.path.abspath(__file__)); R8 = os.path.join(os.path.dirname(HERE), "run8_07112026")
TAG = "HugoJal_Case3_run9a_first_repair_15112026"; H = 0.95; PV_REBUILD = 3.5; SPIKE = np.array([-15.27, -13.40, 68.30])
m = pv.read(R8 + "/HugoJal_Case3_run8_07112026.stl").clean().triangulate()
caps = json.load(open(R8 + "/caps_model_frame.json"))
def bad_edges(s): return s.extract_feature_edges(boundary_edges=True, non_manifold_edges=True, feature_edges=False, manifold_edges=False).n_cells
# 1. spur
d = np.linalg.norm(m.points - SPIKE, axis=1); w = np.clip(1 - (d - 6.0) / 5.0, 0, 1); w = 3 * w**2 - 2 * w**3
Fm = m.faces.reshape(-1, 4)[:, 1:]; nb = [set() for _ in range(m.n_points)]
for t_ in Fm:
    for k_ in range(3): nb[t_[k_]].update((t_[(k_ + 1) % 3], t_[(k_ + 2) % 3]))
sel = np.where(w > 0)[0]; nbl = [list(nb[v]) for v in sel]
P = m.points.copy()
free = np.where(d < 7.0)[0]; nbf = [list(nb[v]) for v in free]                # A. spur region: harmonic fill with the ring d >= 7 mm fixed
for _ in range(2500):
    P[free] += 0.7 * (np.array([P[l].mean(0) for l in nbf]) - P[free])
for _ in range(100):                                                         # B. blend over d < 11 mm: weighted Taubin
    for lam in (0.5, -0.53):
        P[sel] += lam * w[sel, None] * (np.array([P[l].mean(0) for l in nbl]) - P[sel])
m.points = P
# 2. PV ends
def loops(mesh):
    lp = mesh.extract_feature_edges(boundary_edges=True, feature_edges=False, manifold_edges=False, non_manifold_edges=False)
    E = lp.lines.reshape(-1, 3)[:, 1:]; nxt = {}
    for a_, b_ in E: nxt.setdefault(a_, []).append(b_); nxt.setdefault(b_, []).append(a_)
    order = [E[0, 0]]; prev = None
    while True:
        cand = [k for k in nxt[order[-1]] if k != prev]; prev = order[-1]
        if cand[0] == order[0]: break
        order.append(cand[0])
    return lp.points[order], lp.connectivity().cell_data["RegionId"].max() + 1
for cp in caps[1:]:
    c0 = np.array(cp["centre_mm"]); a = np.array(cp["normal"]); a /= np.linalg.norm(a); r_old = cp["radius_mm"]
    b1 = np.cross(a, [0, 0, 1.0]); b1 /= np.linalg.norm(b1); b2 = np.cross(a, b1)
    X = m.points - c0; dpl = X @ a; rho = np.linalg.norm(X - np.outer(dpl, a), axis=1)
    f = np.full(m.n_points, -1.0); reg = (rho < r_old + 1.2) & (dpl > -PV_REBUILD - 2.5); f[reg] = dpl[reg] + PV_REBUILD
    mm = m.copy(); mm.point_data["f"] = f
    kept = mm.clip_scalar(scalars="f", value=0.0, invert=True).extract_surface(algorithm="dataset_surface")
    kept = kept.connectivity(extraction_mode="largest").extract_surface(algorithm="dataset_surface").clean(tolerance=1e-4, absolute=True).triangulate()
    for k in list(kept.point_data.keys()): del kept.point_data[k]
    for k in list(kept.cell_data.keys()): del kept.cell_data[k]
    L, nl = loops(kept); assert nl == 1, (cp["name"], nl)
    # the clip crosses every triangle: its outline has ~2 points per edge (0.4 mm). Collapse neighbouring pairs to their midpoint
    from scipy.spatial import cKDTree
    ids = cKDTree(kept.points).query(L)[1]; Pk = kept.points.copy()
    for i in range(0, len(ids) - 1, 2): Pk[ids[i]] = Pk[ids[i + 1]] = 0.5 * (Pk[ids[i]] + Pk[ids[i + 1]])
    kept.points = Pk; kept = kept.clean(tolerance=0.0).triangulate(); assert bad_edges(kept) > 0
    L, nl = loops(kept); assert nl == 1, (cp["name"], "after collapse", nl)
    X = L - c0; q = np.c_[X @ b1, X @ b2]; g = q.mean(0); r = np.linalg.norm(q - g, axis=1).mean(); th = np.unwrap(np.arctan2(q[:, 1] - g[1], q[:, 0] - g[0]))
    n = len(L); uni = th[0] + np.sign(th[-1] - th[0]) * 2 * np.pi * np.arange(n) / n
    ts = np.linspace(0, PV_REBUILD, 5)                                           # rings at the cut plane ... cap plane
    sm01 = lambda x: 3 * np.clip(x, 0, 1) ** 2 - 2 * np.clip(x, 0, 1) ** 3
    zc = -PV_REBUILD; rings = [L]
    for t in ts[1:]:
        thk = (1 - sm01(t / 1.5)) * th + sm01(t / 1.5) * uni
        rings.append(c0 + (zc + t) * a + np.outer(g[0] + r * np.cos(thk), b1) + np.outer(g[1] + r * np.sin(thk), b2))
    # circle of the last ring: exact; its radius also fixes the loop radius mismatch (rim of the kept part is within ~0.05 mm)
    faces = []
    for k in range(len(rings) - 1):
        for i in range(n):
            a0, b0 = k * n + i, k * n + (i + 1) % n; faces += [3, a0, b0, b0 + n, 3, a0, b0 + n, a0 + n]
    P = np.vstack(rings); side = pv.PolyData(P, np.array(faces))
    # cap: concentric rings from the rim inwards, Delaunay in the plane
    pts2 = [np.c_[r * np.cos(uni), r * np.sin(uni)]]; j = 1
    while r - j * H > 0.6 * H:
        rj = r - j * H; nj = max(6, int(round(2 * np.pi * rj / H))); ang = np.linspace(0, 2 * np.pi, nj, endpoint=False) + 0.3 * j
        pts2.append(np.c_[rj * np.cos(ang), rj * np.sin(ang)]); j += 1
    pts2.append(np.zeros((1, 2))); Q = np.vstack(pts2); tri = Delaunay(Q).simplices
    capP = c0 + np.outer(Q[:, 0] + g[0], b1) + np.outer(Q[:, 1] + g[1], b2)
    capm = pv.PolyData(capP, np.c_[np.full(len(tri), 3), tri].ravel())
    # rim of the cap must coincide with the last ring (same angles): rebuild its first n points from the ring
    capm.points[:n] = rings[-1]
    m = (kept + side + capm).clean(tolerance=1e-4, absolute=True).triangulate()
    print(cp["name"], "ring pts", n, "r", round(r, 2), "radius before", r_old, "bad edges", bad_edges(m))

# 3. slivers left at the seams: collapse needle edges (< 0.4 mm, smooth surface only), then flip edges that raise the minimum angle
def tri_min_angle(P, a, b, c):
    out = 180.0
    for p_, q_, r_ in ((a, b, c), (b, c, a), (c, a, b)):
        u = P[q_] - P[p_]; v = P[r_] - P[p_]; out = min(out, np.degrees(np.arccos(np.clip(u @ v / (np.linalg.norm(u) * np.linalg.norm(v) + 1e-30), -1, 1))))
    return out
for it in range(4):
    F = m.faces.reshape(-1, 4)[:, 1:]; E = np.unique(np.sort(np.vstack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]), 1), axis=0)
    Ln = np.linalg.norm(m.points[E[:, 0]] - m.points[E[:, 1]], axis=1); short = E[Ln < 0.4]
    # dihedral of an edge: do not collapse cap rims / creases (keep edges whose endpoints sit on a cap plane rim)
    on_rim = np.zeros(m.n_points, bool)
    for cp in caps:
        c_ = np.array(cp["centre_mm"]); n_ = np.array(cp["normal"]); dp = np.abs((m.points - c_) @ n_); on_rim |= (dp < 0.05) & (np.linalg.norm(m.points - c_, axis=1) < cp["radius_mm"] + 0.2) & (np.linalg.norm(m.points - c_, axis=1) > cp["radius_mm"] - 0.15)
        for t_ in ((n_ @ n_) * 0,): pass
    P = m.points.copy(); used = set(); n_c = 0
    for a_, b_ in short:
        if a_ in used or b_ in used or on_rim[a_] or on_rim[b_]: continue
        P[a_] = P[b_] = 0.5 * (P[a_] + P[b_]); used |= {a_, b_}; n_c += 1
    m.points = P; m = m.clean(tolerance=0.0).triangulate(); print("collapse pass", it, n_c, "edges")
    if n_c == 0: break
def flip_pass(m):
    F = m.faces.reshape(-1, 4)[:, 1:].copy(); P = m.points; ed = {}
    for t, (a_, b_, c_) in enumerate(F):
        for u, v in ((a_, b_), (b_, c_), (c_, a_)): ed.setdefault((min(u, v), max(u, v)), []).append(t)
    nrm = lambda t: (lambda x: x / (np.linalg.norm(x) + 1e-30))(np.cross(P[F[t, 1]] - P[F[t, 0]], P[F[t, 2]] - P[F[t, 0]]))
    flips = 0; dead = set()
    for (u, v), ts in list(ed.items()):
        if len(ts) != 2 or ts[0] in dead or ts[1] in dead: continue
        t1, t2 = ts
        c = [x for x in F[t1] if x not in (u, v)][0]; d_ = [x for x in F[t2] if x not in (u, v)][0]
        if (min(c, d_), max(c, d_)) in ed: continue
        if nrm(t1) @ nrm(t2) < np.cos(np.radians(25)): continue
        before = min(tri_min_angle(P, F[t1][0], F[t1][1], F[t1][2]), tri_min_angle(P, F[t2][0], F[t2][1], F[t2][2]))
        n1, n2 = nrm(t1), nrm(t2); nn = (n1 + n2) / 2
        a1 = np.cross(P[d_] - P[c], P[u] - P[c]) @ nn; a2 = np.cross(P[v] - P[c], P[d_] - P[c]) @ nn      # new triangles (c,u,d) and (c,d,v) keep orientation?
        # orient the new triangles like the old ones: old t1 has u->v direction; build (c, u, d_) / (c, d_, v) or the reverse
        i1 = list(F[t1]); k = i1.index(u); fwd = i1[(k + 1) % 3] == v                                              # t1 runs u->v
        T1, T2 = ((u, d_, c), (d_, v, c)) if fwd else ((v, d_, c), (d_, u, c))
        T1, T2 = (T1, T2) if (np.cross(P[T1[1]] - P[T1[0]], P[T1[2]] - P[T1[0]]) @ nn > 0) else ((T1[0], T1[2], T1[1]), (T2[0], T2[2], T2[1]))
        if (np.cross(P[T1[1]] - P[T1[0]], P[T1[2]] - P[T1[0]]) @ nn <= 0) or (np.cross(P[T2[1]] - P[T2[0]], P[T2[2]] - P[T2[0]]) @ nn <= 0): continue
        after = min(tri_min_angle(P, *T1), tri_min_angle(P, *T2))
        if after > before + 1.0:
            F[t1] = T1; F[t2] = T2; dead |= {t1, t2}; flips += 1
    return pv.PolyData(P, np.c_[np.full(len(F), 3), F].ravel()), flips
for it in range(8):
    m, nf = flip_pass(m); print("flip pass", it, nf)
    if nf == 0: break
m = m.compute_normals(cell_normals=True, point_normals=False, consistent_normals=True, auto_orient_normals=True)
for k in list(m.point_data.keys()): del m.point_data[k]
for k in list(m.cell_data.keys()): del m.cell_data[k]
F = m.faces.reshape(-1, 4)[:, 1:]; V = m.points
vol = np.einsum("ij,ij->i", V[F[:, 0]], np.cross(V[F[:, 1]], V[F[:, 2]])).sum() / 6
if vol < 0: m = pv.PolyData(V, np.c_[np.full(len(F), 3), F[:, ::-1]].ravel()); vol = -vol
assert bad_edges(m) == 0
m.save(HERE + "/" + TAG + ".stl", binary=True)
print("triangles", m.n_cells, "volume mL", round(vol / 1000, 3))
