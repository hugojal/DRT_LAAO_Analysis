"""run7 mesh (06/11/2026): LA surface rebuilt from the corrected segmentation, PV inlets re-cut along each vein's
trunk, mitral valve narrowed to a 5.3 cm2 orifice. Same CT annulus and model frame as run6
(../mv_aligned_03112026/transform_LPS_to_model.json), so all post-processing works unchanged.

Why (rubric review docs/agents/reviews/rubric_review_06112026.md and the user's decisions of 06/11/2026):
- the course asks for a mitral cross-section of 4-6 cm2 (run6: 8.6 cm2);
- the PV cylinders of HugoJal_Case3.stl (Meshmixer) point 30-60 deg away from their veins and are 2-4x the lumen area,
  so they set wrong inflow jets; they replace the vein stubs entirely, so the veins can only be re-cut from the
  segmentation;
- the segmentation was corrected (device removed, inferior veins extended: 1_segmentation/la_v2_06112026/).
Input: 1_segmentation/la_v2_06112026/Case3_LA_segmentation_HugoJal_06112026.seg.nrrd, mitral_annulus.json (the CT
annulus, same as run6), pv_cuts.json (find_pv_cuts.py: cut point and trunk axis of each vein).
0. Surface from the segmentation: marching cubes + Taubin smoothing (the MeshLab step of the course), no shrinking.
   The atrial body lies on the run6 surface (median distance 0.13 mm).
0b. Each pulmonary vein is cut perpendicular to its trunk before the first branch; a straight extension of the lumen's
   area is added along the trunk axis (PV_LEN mm, flat cap). Its section is the lumen outline smoothed to an oval (2
   harmonics, same area; a circle bulged into a neighbouring structure at the LIPV), reached over PV_T mm starting with
   the vein wall's slope.
1-3. Mitral valve as in ../mv_taper_06112026 (third version): the LA kept down to TOP mm above the annulus, the
   valve region rebuilt as a smooth structured surface (ridge removed, neck size kept), a C1 funnel to a convex
   5.3 cm2 oval, STRAIGHT_LEN mm straight and a flat cap at z = -(TAPER_END + STRAIGHT_LEN).
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
Usage: python build_mesh_run7.py   (set PYMESHLAB_PYTHON to a Python with pymeshlab)"""
import os, json, subprocess
import numpy as np, pyvista as pv, gmsh

HERE = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"); MESH = os.path.dirname(HERE)
TAG = "HugoJal_Case3_run7_06112026"
A_OUT, TAPER_END, STRAIGHT_LEN, STEP = 530.0, 5.0, 1.5, 0.5                # mm2, mm below the annulus, mm, layer mm
TOP, RAMP, N_LA, N_HARM = 8.0, 3.0, 10, 2                                   # rebuilt from TOP mm above the annulus; harmonics
H_SURF, H_VOL = 0.95, 1.9
PV_LEN, PV_T = 10.0, 3.0                                                    # PV cylinder length, transition to circular (mm)
TAUBIN_IT, TAUBIN_PB = 150, 0.02                                            # tested: 60/0.05 left the paint texture, 300/0.01 pinches thin branches
DEV_R, DEV_RAMP = 12.0, 5.0                                                 # local smoothing around the device (mm)

J = json.load(open(HERE + "/mitral_annulus.json")); c = np.array(J["centre_LPS_mm"]); n = np.array(J["normal_LA_to_LV"]); n /= np.linalg.norm(n)
import nrrd
from skimage import measure
_seg, _h = nrrd.read(os.path.join(os.path.dirname(MESH), "1_segmentation", "la_v2_06112026", "Case3_LA_segmentation_HugoJal_06112026.seg.nrrd"))
_SP = np.diag(np.asarray(_h["space directions"], float)); _O = np.asarray(_h["space origin"], float)
_v, _f, _, _ = measure.marching_cubes(np.pad(_seg > 0, 1).astype(np.float32), 0.5, spacing=tuple(_SP))
s = pv.PolyData(_v - _SP + _O, np.c_[np.full(len(_f), 3), _f].ravel()).clean().smooth_taubin(n_iter=TAUBIN_IT, pass_band=TAUBIN_PB)
# uniform ~0.7 mm triangles before the cuts (MeshLab isotropic remeshing; VTK decimation made non-manifold edges and the
# full-resolution surface gives sliver triangles at the cuts)
_tmp_in, _cache = HERE + "/_seg_taubin.stl", HERE + f"/_seg_remeshed_cache_t{TAUBIN_IT}_{TAUBIN_PB}.stl"      # cache (git-ignored), rebuilt if the segmentation is newer
_segf = os.path.join(os.path.dirname(MESH), "1_segmentation", "la_v2_06112026", "Case3_LA_segmentation_HugoJal_06112026.seg.nrrd")
if not (os.path.exists(_cache) and os.path.getmtime(_cache) > os.path.getmtime(_segf)):
    s.save(_tmp_in)
    subprocess.run([os.environ.get("PYMESHLAB_PYTHON", "python"), HERE + "/remesh_surface.py", _tmp_in, _cache, "0.7", "200000"], check=True)
    os.remove(_tmp_in)
s = pv.read(_cache).clean().triangulate()
# 0a. the device was subtracted from the LA mask (segmentation v2): the wall at the occluded ostium follows the device face
#     but the carving leaves folds where the disc rim meets the atrial wall. Local volume-preserving smoothing: full weight
#     within DEV_R mm of the device centre, fading to 0 at DEV_R + DEV_RAMP mm (the rest of the atrium is not touched)
_dm = pv.read(os.path.join(os.path.dirname(MESH), "1_segmentation", "device", "manual", "Device_manual.stl")); dev_c = np.asarray(_dm.center)
_wd = np.clip(1 - (np.linalg.norm(s.points - dev_c, axis=1) - DEV_R) / DEV_RAMP, 0, 1); _wd = 3 * _wd ** 2 - 2 * _wd ** 3
_sm = s.smooth_taubin(n_iter=100, pass_band=0.02)
s.points = s.points + _wd[:, None] * (_sm.points - s.points)
_e = s.extract_feature_edges(boundary_edges=True, non_manifold_edges=True, feature_edges=False, manifold_edges=False).n_cells
assert _e == 0, f"segmentation surface not closed/manifold ({_e} bad edges)"
s_seg = s.copy()

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

# 0b. pulmonary veins: cut each vein perpendicular to its trunk, before its first branch, and add a cylinder along the
#     trunk axis (pv_cuts.json, from find_pv_cuts.py). The cut outline (the vein lumen) blends over PV_T mm into an oval
#     of the same area (2 harmonics), starting with the slope of the vein wall (no kink), then straight to PV_LEN mm, flat cap.
PVC = json.load(open(HERE + "/pv_cuts.json"))
def fan_cap(ring):                                                          # flat cap as a fan from its centre (keeps every rim edge)
    k_ = len(ring); P_ = np.vstack([ring, ring.mean(0)])
    return pv.PolyData(P_, np.c_[np.full(k_, 3), np.full(k_, k_), np.arange(k_), (np.arange(k_) + 1) % k_].ravel())
def blend_angles(th_raw, w):                                                # ring angles: raw seam (w=0) -> evenly spaced (w=1)
    u = np.unwrap(th_raw); sg = np.sign(u[-1] - u[0]); uni = u[0] + sg * 2 * np.pi * np.arange(len(u)) / len(u)
    return (1 - w) * u + w * uni
pinterp = lambda th_k, th_s, v_s: np.interp(np.mod(th_k + np.pi, 2 * np.pi) - np.pi, *(lambda o: (np.r_[th_s[o] - 2 * np.pi, th_s[o], th_s[o] + 2 * np.pi], np.r_[v_s[o], v_s[o], v_s[o]]))(np.argsort(th_s)))
smooth01 = lambda x: (lambda y: 3 * y ** 2 - 2 * y ** 3)(np.clip(x, 0, 1))
W_EVEN = 1.5                                                                # mm over which the ring points move to even angles
SNAP = 0.15                                                                 # mm: vertices this close to a cut plane are moved onto it
def boundary_loops(mesh):                                                   # every open outline, as ordered point arrays
    lp = mesh.extract_feature_edges(boundary_edges=True, feature_edges=False, manifold_edges=False, non_manifold_edges=False)
    if lp.n_cells == 0: return []
    E = [tuple(e) for e in lp.lines.reshape(-1, 3)[:, 1:]]; inc = {}
    for ei, (a_, b_) in enumerate(E): inc.setdefault(a_, []).append(ei); inc.setdefault(b_, []).append(ei)
    used, loops = set(), []
    for e0 in range(len(E)):                                                # walk edges (not vertices): a vertex shared
        if e0 in used: continue                                             # by two outlines cannot make it loop forever
        a_, b_ = E[e0]; used.add(e0); order = [a_, b_]
        while order[-1] != order[0]:
            nxt_e = [ei for ei in inc[order[-1]] if ei not in used]
            if not nxt_e: break
            ei = nxt_e[0]; used.add(ei); x, y = E[ei]; order.append(y if x == order[-1] else x)
        loops.append(lp.points[order[:-1] if order[-1] == order[0] else order])
    return loops
def recut_pv(surf, p, a, name):
    a = np.asarray(a, float); a /= np.linalg.norm(a); p = np.asarray(p, float)
    # local cut: only the part of the surface that lies beyond the plane AND is connected to the vein there is clipped
    # (region grown over triangles with a vertex beyond the plane, from the vein centre); the rest is never touched
    R_loc = PVC[name]["D_eq_mm"] / 2 + 4.0
    X = surf.points - p; dpl = X @ a; rho = np.linalg.norm(X - np.outer(dpl, a), axis=1)
    surf = surf.copy()
    snap = (np.abs(dpl) < SNAP) & (rho < R_loc)                            # vertices next to the cut plane are moved onto it:
    surf.points[snap] = surf.points[snap] - np.outer(dpl[snap], a); dpl[snap] = 0.0   # the clip then makes no near-duplicate points
    Fs = surf.faces.reshape(-1, 4)[:, 1:]; beyond = (dpl[Fs] > 0).any(1)
    import scipy.sparse as _sp, scipy.sparse.csgraph as _cg
    Fb = Fs[beyond]; nb_ = len(Fb); rows_ = np.repeat(np.arange(nb_), 3); cols_ = Fb.ravel()
    inc_ = _sp.coo_matrix((np.ones(len(rows_)), (rows_, cols_)), shape=(nb_, surf.n_points)).tocsr()
    _, labb = _cg.connected_components(inc_ @ inc_.T, directed=False)          # triangles beyond the plane sharing a vertex
    cen_b = surf.points[Fb].mean(1); start = np.argmin(np.linalg.norm(cen_b - (p + 2.0 * a), axis=1))
    region = np.unique(Fb[labb == labb[start]])
    f_cut = np.full(surf.n_points, -1.0); f_cut[region] = dpl[region]
    surf.point_data["f_cut"] = f_cut
    kept = surf.clip_scalar(scalars="f_cut", value=0.0, invert=True).extract_surface(algorithm="dataset_surface")
    kept = kept.connectivity(extraction_mode="largest").extract_surface(algorithm="dataset_surface").clean(tolerance=1e-4, absolute=True).triangulate()
    for key in list(kept.point_data.keys()): del kept.point_data[key]
    for key in list(kept.cell_data.keys()): del kept.cell_data[key]
    loops = boundary_loops(kept)
    assert len(loops) == 1, f"{name}: the cut leaves {len(loops)} open outlines"
    q3raw = loops[0]; q3 = q3raw - np.outer((q3raw - p) @ a, a)            # on the cut plane (geometry); ring 0 keeps the raw points
    b1 = np.cross(a, [0, 0, 1.0]); b1 /= np.linalg.norm(b1); b2 = np.cross(a, b1)
    q = np.c_[(q3 - p) @ b1, (q3 - p) @ b2]; A_l, g = area_centroid(q)
    assert star(q, g), f"{name}: vein outline at the cut is not star-shaped"
    th_ = np.arctan2(q[:, 1] - g[1], q[:, 0] - g[0]); r0 = np.linalg.norm(q - g, axis=1)
    # vein wall slope just proximal to the cut (loop of the original surface nearest to p, 1 mm back)
    sl = surf.slice(normal=a, origin=p - a).strip(); best = None
    for ci in range(sl.n_cells):
        Q = sl.get_cell(ci).points; d_ = np.linalg.norm(Q.mean(0) - (p - a))
        if best is None or d_ < best[0]: best = (d_, Q)
    qp = np.c_[(best[1] - p) @ b1, (best[1] - p) @ b2]
    slope = r0 - polar(qp, g)(th_) if star(qp, g) and best[0] < 3 else np.zeros_like(r0)
    slope = np.median(np.stack([np.roll(slope, k) for k in range(-3, 4)]), 0)
    rc = np.sqrt(A_l / np.pi); slope = np.clip(slope, -1.0, 1.0)
    rs2 = lowpass(polar(q, g)(TG), 2); rs2 *= np.sqrt(A_l / (0.5 * np.sum(rs2 ** 2) * (2 * np.pi / len(TG))))   # oval end shape, same area
    ts = np.unique(np.r_[np.arange(STEP, PV_T, STEP), PV_T, np.arange(PV_T + STEP, PV_LEN, STEP), PV_LEN].round(6))
    def ring_at(t):
        th_k = blend_angles(th_, smooth01(t / W_EVEN)); u_ = min(t / PV_T, 1.0)
        r = (2 * u_ ** 3 - 3 * u_ ** 2 + 1) * pinterp(th_k, th_, r0) + (u_ ** 3 - 2 * u_ ** 2 + u_) * PV_T * pinterp(th_k, th_, slope) + (-2 * u_ ** 3 + 3 * u_ ** 2) * at(rs2, th_k)
        return p + t * a + np.outer(g[0] + r * np.cos(th_k), b1) + np.outer(g[1] + r * np.sin(th_k), b2)
    rings = [q3raw] + [ring_at(t) for t in ts]
    m_ = len(q3); pts_ = np.vstack(rings); faces_ = []
    for k in range(len(rings) - 1):
        for i in range(m_):
            a0, b0 = k * m_ + i, k * m_ + (i + 1) % m_; faces_ += [3, a0, b0, b0 + m_, 3, a0, b0 + m_, a0 + m_]
    side_ = pv.PolyData(pts_, np.array(faces_)); cap_ = fan_cap(pts_[-m_:])
    out = (kept + side_ + cap_).clean(tolerance=1e-4, absolute=True).triangulate()
    centre_cap = p + PV_LEN * a + g[0] * b1 + g[1] * b2
    print(f"{name}: cut outline {A_l:.1f} mm2 (D_eq {2 * rc:.1f} mm), cylinder {PV_LEN} mm along the trunk axis")
    return out, dict(name=name, fluent_name=PVC[name]["fluent_name"], cut_area_mm2=round(A_l, 1), D_eq_mm=round(2 * rc, 2), r_max_mm=round(float(rs2.max()), 2),
                     cap_centre_LPS=centre_cap.round(3).tolist(), cap_normal_LPS=a.round(4).tolist())
pv_caps = []
for nm_ in ("RSPV", "LSPV", "RIPV", "LIPV"):
    s, info_ = recut_pv(s, PVC[nm_]["cut_point_LPS"], PVC[nm_]["axis_LPS"], nm_); pv_caps.append(info_)
ec_ = s.extract_feature_edges(boundary_edges=True, non_manifold_edges=True, feature_edges=False, manifold_edges=False).n_cells
assert ec_ == 0, f"surface not closed after the PV cuts ({ec_} bad edges)"

# centre = centroid of the annulus cut; top outline = the segmented LA cut TOP mm above the annulus
_, gt = area_centroid(section(0.0))
_dt = (s.points - c) @ n + TOP; _sn = np.abs(_dt) < SNAP                    # snap vertices next to the top plane onto it
s.points[_sn] = s.points[_sn] - np.outer(_dt[_sn], n)
la = s.clip(normal=n, origin=c - TOP * n, invert=True).clean(tolerance=1e-4, absolute=True)
Pt_raw = ordered_loop(la); Pt = Pt_raw - np.outer((Pt_raw - c) @ n + TOP, n); m = len(Pt)   # on the top plane (geometry); ring 0 keeps the raw points
qt = uv(Pt); th = np.arctan2(qt[:, 1] - gt[1], qt[:, 0] - gt[0]); rt = np.linalg.norm(qt - gt, axis=1)
assert star(qt, gt), "top outline is not star-shaped about the annulus centroid"

# 2. layers TOP -> annulus: original section blended into its angular low-pass
d_la = np.round(np.arange(-TOP, 0 + 1e-9, STEP), 6)
TH_K = [blend_angles(th, smooth01((dd + TOP) / W_EVEN)) for dd in d_la]     # raw seam angles at TOP -> even within W_EVEN mm
th_even = blend_angles(th, 1.0)
R_orig, R_lp = [], []
for dd, th_k in zip(d_la, TH_K):
    q = qt if dd == d_la[0] else section(dd); assert star(q, gt), f"section {dd} mm is not star-shaped"   # TOP: the cut outline itself
    rg = polar(q, gt)(TG); R_orig.append(at(rg, th_k)); R_lp.append(at(lowpass(rg, N_LA), th_k))
R_orig, R_lp = np.array(R_orig), np.array(R_lp)
R_orig[0] = rt                                                              # the top layer is exactly the cut outline
assert RAMP > W_EVEN and np.allclose(TH_K[-3], th_even)                     # the last layers (slope fit) are on even angles
beta = np.clip((d_la + TOP) / RAMP, 0, 1); beta = 3 * beta ** 2 - 2 * beta ** 3     # smoothstep: 0 and flat at TOP
R_la = (1 - beta)[:, None] * R_orig + beta[:, None] * R_lp
ra = R_la[-1]                                                               # smoothed outline at the annulus plane
slope = np.polyfit(d_la[-3:], R_la[-3:], 1)[0]                              # dr/dd of the smoothed wall at the annulus (last 1 mm)
# 3. funnel: outlet outline = annulus outline (polar about gt) with harmonics <= N_HARM, scaled to A_OUT
q0 = section(0.0); A0 = area_centroid(q0)[0]; rs = lowpass(polar(q0, gt)(TG), N_HARM)
k_end = np.sqrt(A_OUT / (0.5 * np.sum(rs ** 2) * (2 * np.pi / len(TG)))); rb = at(rs, th_even) * k_end
L = TAPER_END; drop = ra - rb
assert drop.min() > 0, "outlet outline must lie inside the annulus outline"
slope = np.clip(slope, -3 * drop / L, 0.0)                                  # no bulging out; monotone Hermite (Fritsch-Carlson)
print(f"annulus cut {A0:.1f} mm2 -> outlet {A_OUT:.1f} mm2 ({N_HARM} harmonics, scale {k_end:.4f}); LA wall angle at the annulus "
      f"{np.degrees(np.arctan(-slope)).mean():.0f} deg mean; LA smoothing changes r by max {np.abs(R_la - R_orig).max():.2f} mm")
d_fun = np.unique(np.r_[np.arange(STEP, TAPER_END, STEP), TAPER_END, np.arange(TAPER_END + STEP, TAPER_END + STRAIGHT_LEN, STEP), TAPER_END + STRAIGHT_LEN].round(6))
def r_fun(dd):
    t = min(dd / L, 1.0); return (2 * t ** 3 - 3 * t ** 2 + 1) * ra + (t ** 3 - 2 * t ** 2 + t) * L * slope + (-2 * t ** 3 + 3 * t ** 2) * rb
ring = lambda dd, r, th_k: c + dd * n + np.outer(gt[0] + r * np.cos(th_k), e1) + np.outer(gt[1] + r * np.sin(th_k), e2)
rings = [Pt_raw] + [ring(dd, r, th_k) for dd, r, th_k in zip(d_la[1:], R_la[1:], TH_K[1:])] + [ring(dd, r_fun(dd), th_even) for dd in d_fun]
pts = np.vstack(rings); faces = []
for k in range(len(rings) - 1):
    for i in range(m):
        a, b = k * m + i, k * m + (i + 1) % m; a2, b2 = a + m, b + m
        faces += [3, a, b, b2, 3, a, b2, a2]
side = pv.PolyData(pts, np.array(faces))
cap = fan_cap(pts[-m:])
model = (la + side + cap).clean(tolerance=1e-4, absolute=True).triangulate()
_ec = model.extract_feature_edges(boundary_edges=True, non_manifold_edges=True, feature_edges=False, manifold_edges=False).n_cells
assert _ec == 0, f"surface not closed after the mitral step ({_ec} bad edges)"

# 3b. remove isolated creases of the original surface (Meshmixer artefacts, dihedral > 45 deg) away from the caps:
#     only the crease vertices and their 2-ring are relaxed; cap rings (~90 deg) stay sharp
from scipy.spatial import cKDTree
def edges_dihedral(mesh):
    mesh = mesh.compute_normals(cell_normals=True, point_normals=False, auto_orient_normals=True, split_vertices=False)   # keep point ids
    F = mesh.faces.reshape(-1, 4)[:, 1:]; N = mesh.cell_data["Normals"]
    e = np.sort(np.vstack([F[:, [0, 1]], F[:, [1, 2]], F[:, [2, 0]]]), axis=1); u, inv = np.unique(e, axis=0, return_inverse=True)
    fid = np.tile(np.arange(len(F)), 3); o = np.argsort(inv); pr = fid[o].reshape(-1, 2)
    return u[inv[o][::2]], np.degrees(np.arccos(np.clip(np.einsum("ij,ij->i", N[pr[:, 0]], N[pr[:, 1]]), -1, 1))), F, N
def flat_caps(mesh, F, N):                                     # vertices of planar patches > 40 mm2 (PV caps and MV cap)
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
        if A[reg].sum() > 40: vids.append(np.unique(F[reg]))
    return np.concatenate(vids)
for it in range(0):   # run7: no crease pass (the surface comes from the segmentation, not Meshmixer; the slivers at the seams are
                      # handled by the vertex merge before the MeshLab remesh)
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
# 5c. cap rims (MV and 4 PVs): MeshLab can join a cap vertex just inside the rim to a wall vertex, so two triangles cut
#     the 90 deg corner (Fluent would separate them as an extra zone). Their shared edge is flipped to restore the rim.
CAPS_M = [dict(name="mitral_valve", centre=np.array([0.0, 0.0, -(TAPER_END + STRAIGHT_LEN)]), normal=np.array([0.0, 0.0, -1.0]), radius=16.0)]
for pc in pv_caps:
    CAPS_M.append(dict(name=pc["fluent_name"], vein=pc["name"], centre=(np.array(pc["cap_centre_LPS"]) - c) @ R.T,
                       normal=R @ np.array(pc["cap_normal_LPS"]), radius=pc["r_max_mm"]))
# 5b2. creases after the remesh (seams of the cut/rebuild steps): vertices around edges sharper than CREASE_DEG, away
#      from the cap rims, are relaxed (2-ring, Laplacian); otherwise Fluent's 30 deg separation makes tiny extra zones
def near_rims(P, margin=1.2):
    out = np.zeros(len(P), bool)
    for cp in CAPS_M:
        dpl_ = (P - cp["centre"]) @ cp["normal"]; rad_ = np.linalg.norm(P - cp["centre"] - np.outer(dpl_, cp["normal"]), axis=1)
        out |= (np.abs(dpl_) < margin) & (rad_ < cp["radius"] + 3)
    return out
CREASE_DEG = 25.0
for it in range(8):
    sr = sr.clean().triangulate(); F = sr.faces.reshape(-1, 4)[:, 1:]
    fe = sr.extract_feature_edges(feature_angle=CREASE_DEG, boundary_edges=False, non_manifold_edges=False, manifold_edges=False)
    ids = cKDTree(sr.points).query(fe.points)[1]; eu = ids[fe.lines.reshape(-1, 3)[:, 1:]] if fe.n_cells else np.zeros((0, 2), int)
    keep_rim = near_rims(sr.points)
    bad = eu[~keep_rim[eu].any(1)] if len(eu) else eu
    print(f"crease pass {it}: {len(bad)} edges sharper than {CREASE_DEG:.0f} deg away from the cap rims")
    if len(bad) == 0: break
    adj = [set() for _ in range(sr.n_points)]
    for tri in F:
        for i_ in range(3): adj[tri[i_]].update((tri[(i_ + 1) % 3], tri[(i_ + 2) % 3]))
    sel = set(bad.ravel())
    for _ in range(2): sel |= set().union(*[adj[v] for v in sel])
    sel = np.array([v for v in sel if not keep_rim[v]])
    P = sr.points.copy()
    for _ in range(5):
        P[sel] = 0.5 * P[sel] + 0.5 * np.array([P[list(adj[v])].mean(0) for v in sel])
    sr.points = P
def cap_tris(Cc, Nc, cp, lo, hi):
    dpl = np.abs((Cc - cp["centre"]) @ cp["normal"]); rad = np.linalg.norm(Cc - cp["centre"], axis=1)
    ang = np.degrees(np.arccos(np.clip(Nc @ cp["normal"], -1, 1)))
    return np.where((dpl < 0.6) & (rad < cp["radius"] + 3) & (ang > lo) & (ang < hi))[0]
for it in range(5):
    sr = sr.compute_normals(cell_normals=True, point_normals=False, consistent_normals=True, auto_orient_normals=True)
    F = sr.faces.reshape(-1, 4)[:, 1:].copy(); Nc = sr.cell_data["Normals"]; Cc = sr.cell_centers().points
    bad = set(np.concatenate([cap_tris(Cc, Nc, cp, 15, 75) for cp in CAPS_M]).tolist())
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
# 5d. relax the interior vertices of every cap in its plane (rim fixed, cap stays flat)
F = sr.faces.reshape(-1, 4)[:, 1:]; P = sr.points.copy()
for cp in CAPS_M:
    on_cap = (np.abs((P - cp["centre"]) @ cp["normal"]) < 1e-3) & (np.linalg.norm(P - cp["centre"], axis=1) < cp["radius"] + 3)
    part = on_cap[F].sum(1); rim = np.unique(F[(part > 0) & (part < 3)][on_cap[F[(part > 0) & (part < 3)]]])
    inner = np.setdiff1d(np.where(on_cap)[0], rim)
    nbr = [set() for _ in range(len(P))]
    for t in F[on_cap[F].all(1)]:
        for k in range(3): nbr[t[k]].update((t[(k + 1) % 3], t[(k + 2) % 3]))
    for _ in range(10):
        newp = np.array([P[list(nbr[v])].mean(0) for v in inner]) if len(inner) else np.zeros((0, 3))
        if len(inner): P[inner] = newp - np.outer((newp - cp["centre"]) @ cp["normal"], cp["normal"])
sr.points = P
json.dump([dict(name=cp["name"], vein=cp.get("vein", "MV"), centre_mm=np.round(cp["centre"], 3).tolist(), normal=np.round(cp["normal"], 4).tolist(),
                radius_mm=round(float(cp["radius"]), 2)) for cp in CAPS_M], open(HERE + "/caps_model_frame.json", "w"), indent=1)
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
