"""run9 v2 surface (15/11/2026), from the run8 surface (model frame, mm):
 1. spur next to the RIPV removed (harmonic fill + blend);
 2. whole surface smoothed (Taubin, N_GLOBAL passes, volume preserving; the mitral cap and neck are held);
 3. each PV extension rebuilt as a LOFT: exact circle for the last 3.5 mm behind the cap, then a smooth (smoothstep) change of
    centre and outline over L mm into the vein's own outline at a plane T_far behind the cap (chosen where the lumen has not
    yet started to flare: area <= 1.3 x cap area). No step in diameter; the natural outline is kept at the far plane;
 4. needle edges collapsed, edges flipped to raise the minimum angle.
usage: python build_surface_run9v2.py -> HugoJal_Case3_run9_15112026.stl"""
import os, json, numpy as np, pyvista as pv
import scipy.sparse as sp, scipy.sparse.csgraph as cg
from scipy.spatial import Delaunay, cKDTree
HERE = os.path.dirname(os.path.abspath(__file__)); R8 = os.path.join(os.path.dirname(HERE), "run8_07112026")
TAG = os.environ.get("OUT", "HugoJal_Case3_run9_15112026"); H = 0.95; SPIKE = np.array([-15.27, -13.40, 68.30]); N_GLOBAL = 60
T_FIXED = {"RSPV": float(os.environ.get("TFAR_RSPV", 7.0))}
CYL = 3.5; AREA_LIM = 1.3; TFAR_MIN, TFAR_MAX = 9.0, 16.0
sm01 = lambda x: 3 * np.clip(x, 0, 1) ** 2 - 2 * np.clip(x, 0, 1) ** 3
m = pv.read(R8 + "/HugoJal_Case3_run8_07112026.stl").clean().triangulate(); caps = json.load(open(R8 + "/caps_model_frame.json"))
def bad_edges(s): return s.extract_feature_edges(boundary_edges=True, non_manifold_edges=True, feature_edges=False, manifold_edges=False).n_cells
def adjacency(mesh):
    Fm = mesh.faces.reshape(-1, 4)[:, 1:]; nb = [set() for _ in range(mesh.n_points)]
    for t_ in Fm:
        for k_ in range(3): nb[t_[k_]].update((t_[(k_ + 1) % 3], t_[(k_ + 2) % 3]))
    return [np.array(list(s)) for s in nb]
# 1. spur
nbl = adjacency(m); d = np.linalg.norm(m.points - SPIKE, axis=1); w = sm01(1 - (d - 6.0) / 5.0)
P = m.points.copy(); free = np.where(d < 7.0)[0]
for _ in range(2500): P[free] += 0.7 * (np.array([P[nbl[v]].mean(0) for v in free]) - P[free])
sel = np.where(w > 0)[0]
for _ in range(100):
    for lam in (0.5, -0.53): P[sel] += lam * w[sel, None] * (np.array([P[nbl[v]].mean(0) for v in sel]) - P[sel])
# 2. global smoothing (MV neck held)
wg = sm01((P[:, 2] + 3.0) / 1.5); sel = np.where(wg > 1e-6)[0]
for _ in range(N_GLOBAL):
    for lam in (0.5, -0.53): P[sel] += lam * wg[sel, None] * (np.array([P[nbl[v]].mean(0) for v in sel]) - P[sel])
m.points = P
print("spur + global smoothing done", flush=True)
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
def area_xy(q): x, y = q[:, 0], q[:, 1]; return abs((x * np.roll(y, -1) - np.roll(x, -1) * y).sum()) / 2
def is_star(q, g):
    a_ = np.unwrap(np.arctan2(q[:, 1] - g[1], q[:, 0] - g[0])); da = np.diff(a_)
    return abs(a_[-1] - a_[0]) > 1.9 * np.pi and (np.sign(da) == np.sign(a_[-1] - a_[0])).mean() > 0.97
# 3. PV lofts
T_FARS = []
for cp in caps[1:]:
    c0 = np.array(cp["centre_mm"]); a = np.array(cp["normal"]); a /= np.linalg.norm(a); r_c = cp["radius_mm"]; A_cap = np.pi * r_c ** 2
    b1 = np.cross(a, [0, 0, 1.0]); b1 /= np.linalg.norm(b1); b2 = np.cross(a, b1)
    def section(t):                                                          # outline of the vein t mm behind the cap, in (b1, b2) coordinates
        sl = m.slice(normal=a, origin=c0 - t * a).strip(); best = None
        for i in range(sl.n_cells):
            Q = sl.get_cell(i).points; dd = np.linalg.norm(Q.mean(0) - (c0 - t * a))
            if best is None or dd < best[0]: best = (dd, Q)
        return np.c_[(best[1] - c0) @ b1, (best[1] - c0) @ b2]
    T_far = TFAR_MIN
    if cp["vein"] in T_FIXED: T_far = T_FIXED[cp["vein"]]                    # RSPV: the 11 mm plane cuts its flare and the loft made a fold
    else:
      for t in np.arange(TFAR_MIN, TFAR_MAX + 0.01, 0.5):
        q = section(t); g = q.mean(0)
        if area_xy(q) > AREA_LIM * A_cap or not is_star(q, g) or np.linalg.norm(g) > 1.2 * r_c: break
        T_far = t
    T_FARS.append(T_far)
    X = m.points - c0; dpl = X @ a
    Fs =m.faces.reshape(-1, 4)[:, 1:]; cen = m.points[Fs].mean(1); cd = (cen - c0) @ a; cr = np.linalg.norm((cen - c0) - np.outer(cd, a), axis=1)
    beyond = ((dpl[Fs] > -T_far).any(1)) & (cr < 2.0 * r_c + 3.0); idx = np.where(beyond)[0]
    inc = sp.coo_matrix((np.ones(3 * len(idx)), (np.repeat(np.arange(len(idx)), 3), Fs[idx].ravel())), shape=(len(idx), m.n_points)).tocsr()
    _, lab = cg.connected_components(inc @ inc.T, directed=False)
    seed = np.argmin(np.linalg.norm(cen[idx] - c0, axis=1)); region = np.unique(Fs[idx[lab == lab[seed]]])
    f = np.full(m.n_points, -1.0); f[region] = dpl[region] + T_far
    mm = m.copy(); mm.point_data["f"] = f
    kept = mm.clip_scalar(scalars="f", value=0.0, invert=True).extract_surface(algorithm="dataset_surface")
    kept = kept.connectivity(extraction_mode="largest").extract_surface(algorithm="dataset_surface").clean(tolerance=1e-4, absolute=True).triangulate()
    for k in list(kept.point_data.keys()): del kept.point_data[k]
    for k in list(kept.cell_data.keys()): del kept.cell_data[k]
    L, nl = loops(kept); assert nl == 1, (cp["vein"], "open outlines", nl)
    ids = cKDTree(kept.points).query(L)[1]; Pk = kept.points.copy()
    for i in range(0, len(ids) - 1, 2): Pk[ids[i]] = Pk[ids[i + 1]] = 0.5 * (Pk[ids[i]] + Pk[ids[i + 1]])
    kept.points = Pk; kept = kept.clean(tolerance=0.0).triangulate(); L, nl = loops(kept); assert nl == 1
    q = np.c_[(L - c0) @ b1, (L - c0) @ b2]; g = q.mean(0); assert is_star(q, g), cp["vein"]
    th = np.unwrap(np.arctan2(q[:, 1] - g[1], q[:, 0] - g[0])); r_out = np.linalg.norm(q - g, axis=1); n = len(L)
    o = np.argsort(np.mod(th + np.pi, 2 * np.pi)); tb = np.mod(th + np.pi, 2 * np.pi)[o] - np.pi; rb = r_out[o]
    rpol = lambda t_: np.interp(np.mod(t_ + np.pi, 2 * np.pi) - np.pi, np.r_[tb - 2 * np.pi, tb, tb + 2 * np.pi], np.r_[rb, rb, rb])
    uni = th[0] + np.sign(th[-1] - th[0]) * 2 * np.pi * np.arange(n) / n
    nL = int(round((T_far - CYL) / 0.8)) + 1; ts = np.r_[np.linspace(T_far, CYL, nL), np.linspace(CYL, 0, 5)[1:]]
    rings = [L]
    for t in ts[1:]:
        wgt = sm01((t - CYL) / (T_far - CYL)); we = sm01((T_far - t) / 3.0)
        thk = (1 - we) * th + we * uni
        cen_ = wgt * g; rad = (1 - wgt) * r_c + wgt * rpol(thk)
        rings.append(c0 - t * a + np.outer(cen_[0] + rad * np.cos(thk), b1) + np.outer(cen_[1] + rad * np.sin(thk), b2))
    faces = []
    for k in range(len(rings) - 1):
        for i in range(n):
            a0, b0 = k * n + i, k * n + (i + 1) % n; faces += [3, a0, b0, b0 + n, 3, a0, b0 + n, a0 + n]
    side = pv.PolyData(np.vstack(rings), np.array(faces))
    pts2 = [np.c_[r_c * np.cos(uni), r_c * np.sin(uni)]]; j = 1
    while r_c - j * H > 0.6 * H:
        rj = r_c - j * H; nj = max(6, int(round(2 * np.pi * rj / H))); ang = np.linspace(0, 2 * np.pi, nj, endpoint=False) + 0.3 * j
        pts2.append(np.c_[rj * np.cos(ang), rj * np.sin(ang)]); j += 1
    pts2.append(np.zeros((1, 2))); Q = np.vstack(pts2); tri = Delaunay(Q).simplices
    capm = pv.PolyData(c0 + np.outer(Q[:, 0], b1) + np.outer(Q[:, 1], b2), np.c_[np.full(len(tri), 3), tri].ravel()); capm.points[:n] = rings[-1]
    m = (kept + side + capm).clean(tolerance=1e-4, absolute=True).triangulate()
    print(cp["vein"], "T_far %.1f mm, far outline area %.0f mm2 (cap %.0f), ring pts %d, bad edges %d" % (T_far, area_xy(q), A_cap, n, bad_edges(m)), flush=True)
# 3b. soften the seam where each loft meets the natural vein (light Taubin in a band around the far plane)
SEAM = {}
for cp in caps[1:]:
    SEAM[cp["vein"]] = None
nbl = adjacency(m); wseam = np.zeros(m.n_points)
for cp, tf in zip(caps[1:], T_FARS):
    c0 = np.array(cp["centre_mm"]); a = np.array(cp["normal"]); a /= np.linalg.norm(a); r_c = cp["radius_mm"]
    X = m.points - c0; tt = -(X @ a); rho = np.linalg.norm(X - np.outer(X @ a, a), axis=1)
    wseam = np.maximum(wseam, sm01(1 - np.abs(tt - tf) / 3.0) * (1 - sm01((rho - (r_c + 5.0)) / 3.0)))
Ps = m.points.copy(); sel = np.where(wseam > 1e-3)[0]
for _ in range(40):
    for lam in (0.5, -0.53): Ps[sel] += lam * wseam[sel, None] * (np.array([Ps[nbl[v]].mean(0) for v in sel]) - Ps[sel])
m.points = Ps; print("seam softened", flush=True)
# 4. slivers
def tri_min_angle(P, a, b, c):
    out = 180.0
    for p_, q_, r_ in ((a, b, c), (b, c, a), (c, a, b)):
        u = P[q_] - P[p_]; v = P[r_] - P[p_]; out = min(out, np.degrees(np.arccos(np.clip(u @ v / (np.linalg.norm(u) * np.linalg.norm(v) + 1e-30), -1, 1))))
    return out
for it in range(4):
    F = m.faces.reshape(-1, 4)[:, 1:]; E = np.unique(np.sort(np.vstack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]), 1), axis=0)
    Ln = np.linalg.norm(m.points[E[:, 0]] - m.points[E[:, 1]], axis=1); short = E[Ln < 0.4]
    on_rim = np.zeros(m.n_points, bool)
    for cp in caps:
        c_ = np.array(cp["centre_mm"]); n_ = np.array(cp["normal"]); dp = np.abs((m.points - c_) @ n_); rr = np.linalg.norm(m.points - c_, axis=1)
        on_rim |= (dp < 0.05) & (rr < cp["radius_mm"] + 0.2) & (rr > cp["radius_mm"] - 0.15)
    P = m.points.copy(); used = set(); n_c = 0
    for a_, b_ in short:
        if a_ in used or b_ in used or on_rim[a_] or on_rim[b_]: continue
        P[a_] = P[b_] = 0.5 * (P[a_] + P[b_]); used |= {a_, b_}; n_c += 1
    m.points = P; m = m.clean(tolerance=0.0).triangulate(); print("collapse pass", it, n_c, flush=True)
    if n_c == 0: break
def flip_pass(m):
    F = m.faces.reshape(-1, 4)[:, 1:].copy(); P = m.points; ed = {}
    for t, (a_, b_, c_) in enumerate(F):
        for u, v in ((a_, b_), (b_, c_), (c_, a_)): ed.setdefault((min(u, v), max(u, v)), []).append(t)
    nrm = lambda t: (lambda x: x / (np.linalg.norm(x) + 1e-30))(np.cross(P[F[t, 1]] - P[F[t, 0]], P[F[t, 2]] - P[F[t, 0]]))
    flips = 0; dead = set()
    for (u, v), tt in list(ed.items()):
        if len(tt) != 2 or tt[0] in dead or tt[1] in dead: continue
        t1, t2 = tt; c = [x for x in F[t1] if x not in (u, v)][0]; d_ = [x for x in F[t2] if x not in (u, v)][0]
        if (min(c, d_), max(c, d_)) in ed: continue
        n1, n2 = nrm(t1), nrm(t2)
        if n1 @ n2 < np.cos(np.radians(25)): continue
        before = min(tri_min_angle(P, *F[t1]), tri_min_angle(P, *F[t2])); nn = (n1 + n2) / 2
        i1 = list(F[t1]); k = i1.index(u); fwd = i1[(k + 1) % 3] == v
        T1, T2 = ((u, d_, c), (d_, v, c)) if fwd else ((v, d_, c), (d_, u, c))
        if np.cross(P[T1[1]] - P[T1[0]], P[T1[2]] - P[T1[0]]) @ nn <= 0: T1, T2 = (T1[0], T1[2], T1[1]), (T2[0], T2[2], T2[1])
        if (np.cross(P[T1[1]] - P[T1[0]], P[T1[2]] - P[T1[0]]) @ nn <= 0) or (np.cross(P[T2[1]] - P[T2[0]], P[T2[2]] - P[T2[0]]) @ nn <= 0): continue
        if min(tri_min_angle(P, *T1), tri_min_angle(P, *T2)) > before + 1.0: F[t1] = T1; F[t2] = T2; dead |= {t1, t2}; flips += 1
    return pv.PolyData(P, np.c_[np.full(len(F), 3), F].ravel()), flips
for it in range(8):
    m, nf = flip_pass(m); print("flip pass", it, nf, flush=True)
    if nf == 0: break
m = m.compute_normals(cell_normals=True, point_normals=False, consistent_normals=True, auto_orient_normals=True)
for k in list(m.point_data.keys()): del m.point_data[k]
for k in list(m.cell_data.keys()): del m.cell_data[k]
F = m.faces.reshape(-1, 4)[:, 1:]; V = m.points; vol = np.einsum("ij,ij->i", V[F[:, 0]], np.cross(V[F[:, 1]], V[F[:, 2]])).sum() / 6
if vol < 0: m = pv.PolyData(V, np.c_[np.full(len(F), 3), F[:, ::-1]].ravel()); vol = -vol
assert bad_edges(m) == 0
m.save(HERE + "/" + TAG + ".stl", binary=True); print("triangles", m.n_cells, "volume mL", round(vol / 1000, 3), flush=True)
