"""Fluent case on the 5.3 cm2 tapered-outlet mesh (2_mesh/mv_taper_06112026), 06/11/2026. Copy of setup_case_mvz.py:
only the mesh, the output names and the mitral cap position (z = -6.5 mm instead of -10 mm) change.
Run with the profiles of boundary_conditions_4cycles_mv53 (run_cycle.py ... <case> 3_simulation/boundary_conditions_4cycles_mv53).


Part A (mesh): import the .bdf, scale mm -> m, separate the boundary by angle (30 deg, as in the slides),
name the zones like the old case (pv_1..pv_4 matched by position with the old caps, mitral_valve = cap at z = -10 mm,
la_wall, fluid-1, default_interior-1), set the zone types, write cases/mesh_mvz_04112026.cas.h5.
Part B (settings): read the old set-up case (case_dm_v3_16102026), replace its mesh with the new one, so every
setting (models, blood, BC profiles, methods, controls, residuals, dynamic mesh zones) is kept by zone name; update
the remeshing length scales to the new mesh (min edge 0.28 mm, max edge 4.0 mm -> 0.3 / 4.5 mm, same rule as the
old 0.2 / 3.5 mm); write cases/case_mvz_setup_04112026.cas.h5. Old files are only read.
Usage: python setup_case_mvz.py [A|B|AB]"""
import ansys.fluent.core as pf, json, os, sys, time
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/")
BDF = ROOT + "/2_mesh/mv_taper_06112026/HugoJal_Case3_mv53_06112026.bdf"
OLD = ROOT + "/3_simulation/cases/case_dm_v3_16102026.cas.h5"
MESHCASE = ROOT + "/3_simulation/cases/mesh_mv53_06112026.cas.h5"
NEWCASE = ROOT + "/3_simulation/cases/case_mv53_setup_06112026.cas.h5"
# cap centres in the model frame (mm): old caps of run5 mapped with transform_LPS_to_model.json (logs/old_cap_centres_run5.json)
CAPS = {"pv_1": [36.34, 24.06, 38.1], "pv_2": [-23.55, -46.17, 67.18], "pv_3": [-25.95, -5.34, 76.15], "pv_4": [45.76, -24.9, 46.47],
        "mitral_valve": [-0.4, -0.1, -6.5]}
LEN_MIN, LEN_MAX = 0.0003, 0.0045
parts = sys.argv[1] if len(sys.argv) > 1 else "AB"
log = lambda m: print(time.strftime("%H:%M:%S"), m, flush=True)
tui = lambda cmd: s.scheme.eval('(ti-menu-load-string "%s")' % cmd.replace('"', '\\"'))

s = pf.launch_fluent(mode="solver", dimension=3, precision="single", processor_count=4, ui_mode="no_gui", cwd=ROOT + "/logs/fluent", start_transcript=False)
S = s.settings

if "A" in parts:
    s.tui.file.import_.nastran.bulkdata(BDF)
    tui("/mesh/scale 0.001 0.001 0.001")
    tui("/define/boundary-conditions/zone-type solid-1 fluid")
    tui("/define/boundary-conditions/zone-name solid-1 fluid-1")
    tui("/mesh/modify-zones/sep-face-zone-angle default_exterior-1 30 yes")
    st = S.setup.boundary_conditions.get_state()
    walls = list(st["wall"].keys()); interiors = list(st.get("interior", {}).keys())
    log(f"after separation: walls {walls}, interiors {interiors}")
    log("boundary-condition keys: " + json.dumps({k: list(v.keys()) for k, v in st.items() if isinstance(v, dict) and v and all(isinstance(x, dict) for x in v.values())}))
    S.solution.initialization.standard_initialize()                       # makes the surface reports available
    rd = S.solution.report_definitions; defs = []
    for i, w in enumerate(walls):
        for c in "xyz":
            n = f"c{i}{c}"; rd.surface.create(n); rd.surface[n].report_type = "surface-areaavg"; rd.surface[n].field = c + "-coordinate"; rd.surface[n].surface_names = [w]; defs.append(n)
        n = f"a{i}"; rd.surface.create(n); rd.surface[n].report_type = "surface-area"; rd.surface[n].surface_names = [w]; defs.append(n)
    vals = {}
    for d in (lambda r: r if isinstance(r, list) else [r])(rd.compute(report_defs=defs)): vals.update(d if isinstance(d, dict) else {})
    info = {w: dict(centre_mm=[round(vals[f"c{i}{c}"][0] * 1000, 2) for c in "xyz"], area_mm2=round(vals[f"a{i}"][0] * 1e6, 1)) for i, w in enumerate(walls)}
    for n in defs: del rd.surface[n]
    log("zones: " + json.dumps(info))
    big = max(info, key=lambda k: info[k]["area_mm2"])
    rename = {big: "la_wall"}
    for name, cc in CAPS.items():
        cand = [w for w in info if w != big]
        best = min(cand, key=lambda w: np.linalg.norm(np.array(info[w]["centre_mm"]) - cc))
        d = np.linalg.norm(np.array(info[best]["centre_mm"]) - cc); assert d < 3, f"{name}: nearest zone {best} is {d:.1f} mm away"
        rename[best] = name
    assert len(set(rename.values())) == 6 and len(walls) == 6, f"expected 6 boundary zones, got {walls}"
    for old, new in rename.items():
        if old != new: tui(f"/define/boundary-conditions/zone-name {old} {new}")
    if interiors and interiors[0] != "default_interior-1": tui(f"/define/boundary-conditions/zone-name {interiors[0]} default_interior-1")
    for z in ["pv_1", "pv_2", "pv_3", "pv_4"]: tui(f"/define/boundary-conditions/zone-type {z} pressure-inlet")
    tui("/define/boundary-conditions/zone-type mitral_valve velocity-inlet")
    json.dump(dict(rename=rename, zones=info), open(ROOT + "/logs/mesh_mv53_zones_06112026.json", "w"), indent=1)
    st = S.setup.boundary_conditions.get_state()
    log("final zones: " + json.dumps({k: list(v.keys()) for k, v in st.items() if k in ("wall", "pressure_inlet", "velocity_inlet", "interior")}))
    S.file.write_case(file_name=MESHCASE); log("written " + MESHCASE)

if "B" in parts:
    S.file.read_case(file_name=OLD)
    tui(f'/mesh/replace "{MESHCASE}" yes')
    st = S.setup.boundary_conditions.get_state()
    log("after replace: " + json.dumps({k: list(v.keys()) for k, v in st.items() if k in ("wall", "pressure_inlet", "velocity_inlet", "interior")}))
    rm = S.setup.dynamic_mesh.methods.remeshing.settings
    rm.length_min = LEN_MIN; rm.length_max = LEN_MAX
    dm = S.setup.dynamic_mesh.get_state()
    log("dynamic zones: " + json.dumps({k: (v.get("zone"), v.get("type"), v.get("motion", {}).get("motion_def")) for k, v in dm["dynamic_zones"].items()}))
    log("remeshing: " + json.dumps(dm["methods"]["remeshing"]["settings"]))
    log("MV BC: " + json.dumps(st["velocity_inlet"]["mitral_valve"]["momentum"]["velocity_magnitude"]))
    log("PV BC: " + json.dumps({z: st["pressure_inlet"][z]["momentum"]["gauge_total_pressure"] for z in ["pv_1", "pv_2", "pv_3", "pv_4"]}))
    log("cell zone: " + json.dumps(S.setup.cell_zone_conditions.get_state()["fluid"]["fluid-1"]["general"]))
    tui("/mesh/check")
    S.file.write_case(file_name=NEWCASE); log("written " + NEWCASE)
s.exit()
