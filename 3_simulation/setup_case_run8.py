"""Fluent case for run8 (07/11/2026) on 2_mesh/run8_07112026: identical to run7 (setup_case_run7.py) except that the
PV extensions are circular cylinders (course guide). Same old set-up case, zones, funnel motion, remeshing limits.

Part A (mesh): import the .bdf, scale mm -> m, separate the boundary by angle (30 deg, as in the slides), name the zones
  by position (caps_model_frame.json: pv_1 = LIPV, pv_2 = RSPV, pv_3 = RIPV, pv_4 = LSPV as in run6; mitral_valve = cap
  at z = -6.5 mm; la_wall), then split the wall below the annulus plane (z < 0: the funnel and its straight end) into
  its own wall zone mv_funnel (cell register "funnel" + sep-face-zone-mark), set the zone types, write
  cases/mesh_run8_07112026.cas.h5.
Part B (settings): read the old set-up case (case_dm_v3_16102026), replace its mesh, so every setting (models, blood,
  BC profiles, methods, controls, residuals, dynamic-mesh zones) is kept by zone name; add a rigid-body dynamic zone for
  mv_funnel with the SAME motion as the mitral cap (mov_bc_c): the whole valve region moves along the valve axis, so
  the volume swept by the valve motion is the annulus area x displacement (~8 mL), not only the 5.3 cm2 cap (~5 mL);
  the LA wall above the annulus deforms (smoothing + remeshing). Remeshing length scales from the new mesh (edges
  0.14-4.07 mm -> 0.15 / 4.5 mm, same rule as run6). Write cases/case_run8_setup_07112026.cas.h5.
Run: python 3_simulation/run_cycle.py 350 3_simulation/results/run8_4cycles 3_simulation/cases/case_run8_4cycles_DDMMYYYY.cas.h5 \\
       3_simulation/cases/case_run8_setup_07112026.cas.h5 3_simulation/boundary_conditions_4cycles_run7   (same BC as run7)
Usage: python 3_simulation/setup_case_run8.py [A|B|AB]"""
import ansys.fluent.core as pf, json, os, sys, time
import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/")
MESHDIR = ROOT + "/2_mesh/run8_07112026"
BDF = MESHDIR + "/HugoJal_Case3_run8_07112026.bdf"
OLD = ROOT + "/3_simulation/cases/case_dm_v3_16102026.cas.h5"
MESHCASE = ROOT + "/3_simulation/cases/mesh_run8_07112026.cas.h5"
NEWCASE = ROOT + "/3_simulation/cases/case_run8_setup_07112026.cas.h5"
CAPS = json.load(open(MESHDIR + "/caps_model_frame.json"))              # names, centres (mm, model frame), normals
LEN_MIN, LEN_MAX = 0.00015, 0.0045
for f in (MESHCASE, NEWCASE): assert not os.path.exists(f), f"{f} exists: never overwrite, use a new name"
parts = sys.argv[1] if len(sys.argv) > 1 else "AB"
log = lambda m: print(time.strftime("%H:%M:%S"), m, flush=True)
tui = lambda cmd: s.scheme.eval('(ti-menu-load-string "%s")' % cmd.replace('"', '\\"'))

s = pf.launch_fluent(mode="solver", dimension=3, precision="single", processor_count=4, ui_mode="no_gui", cwd=ROOT + "/logs/fluent", start_transcript=False)
S = s.settings

def zone_info(walls):
    rd = S.solution.report_definitions; defs = []
    for i, w in enumerate(walls):
        for c in "xyz":
            n = f"c{i}{c}"; rd.surface.create(n); rd.surface[n].report_type = "surface-areaavg"; rd.surface[n].field = c + "-coordinate"; rd.surface[n].surface_names = [w]; defs.append(n)
        n = f"a{i}"; rd.surface.create(n); rd.surface[n].report_type = "surface-area"; rd.surface[n].surface_names = [w]; defs.append(n)
    vals = {}
    for d in (lambda r: r if isinstance(r, list) else [r])(rd.compute(report_defs=defs)): vals.update(d if isinstance(d, dict) else {})
    for n in defs: del rd.surface[n]
    return {w: dict(centre_mm=[round(vals[f"c{i}{c}"][0] * 1000, 2) for c in "xyz"], area_mm2=round(vals[f"a{i}"][0] * 1e6, 1)) for i, w in enumerate(walls)}

if "A" in parts:
    s.tui.file.import_.nastran.bulkdata(BDF)
    tui("/mesh/scale 0.001 0.001 0.001")
    tui("/define/boundary-conditions/zone-type solid-1 fluid")
    tui("/define/boundary-conditions/zone-name solid-1 fluid-1")
    tui("/mesh/modify-zones/sep-face-zone-angle default_exterior-1 30 yes")
    S.solution.initialization.standard_initialize()                       # makes the surface reports available
    st = S.setup.boundary_conditions.get_state()
    walls = list(st["wall"].keys()); interiors = list(st.get("interior", {}).keys())
    info = zone_info(walls); log("zones: " + json.dumps(info))
    assert len(walls) == 6, f"expected 6 boundary zones after the angle separation, got {walls}"
    big = max(info, key=lambda k: info[k]["area_mm2"]); rename = {big: "la_wall"}
    for cp in CAPS:
        cand = [w for w in info if w != big]
        best = min(cand, key=lambda w: np.linalg.norm(np.array(info[w]["centre_mm"]) - cp["centre_mm"]))
        d = np.linalg.norm(np.array(info[best]["centre_mm"]) - cp["centre_mm"]); assert d < 3, f"{cp['name']}: nearest zone {best} is {d:.1f} mm away"
        rename[best] = cp["name"]
    assert len(set(rename.values())) == 6
    for old, new in rename.items():
        if old != new: tui(f"/define/boundary-conditions/zone-name {old} {new}")
    if interiors and interiors[0] != "default_interior-1": tui(f"/define/boundary-conditions/zone-name {interiors[0]} default_interior-1")
    # the valve region below the annulus plane (funnel + straight end) as its own wall zone
    S.solution.cell_registers.create(name="funnel")
    S.solution.cell_registers["funnel"].type.set_state({"option": "hexahedron", "hexahedron": {"min_point": [-0.06, -0.06, -0.06], "max_point": [0.06, 0.06, 0.0], "inside": True}})
    tui("/mesh/modify-zones/sep-face-zone-mark la_wall funnel")
    walls = list(S.setup.boundary_conditions.get_state()["wall"].keys())
    new = [w for w in walls if w not in rename.values()]; assert len(new) == 1, f"funnel split gave {new}"
    tui(f"/define/boundary-conditions/zone-name {new[0]} mv_funnel")
    del S.solution.cell_registers["funnel"]
    for z in ["pv_1", "pv_2", "pv_3", "pv_4"]: tui(f"/define/boundary-conditions/zone-type {z} pressure-inlet")
    tui("/define/boundary-conditions/zone-type mitral_valve velocity-inlet")
    walls = list(S.setup.boundary_conditions.get_state()["wall"].keys()); info2 = zone_info(walls + ["mitral_valve", "pv_1", "pv_2", "pv_3", "pv_4"])
    json.dump(dict(rename=rename, zones=info2), open(ROOT + "/logs/mesh_run8_zones_07112026.json", "w"), indent=1)
    log("final zones: " + json.dumps(info2))
    S.file.write_case(file_name=MESHCASE); log("written " + MESHCASE)

if "B" in parts:
    S.file.read_case(file_name=OLD)
    tui(f'/mesh/replace "{MESHCASE}" yes')
    st = S.setup.boundary_conditions.get_state()
    log("after replace: " + json.dumps({k: list(v.keys()) for k, v in st.items() if k in ("wall", "pressure_inlet", "velocity_inlet", "interior")}))
    dz = S.setup.dynamic_mesh.dynamic_zones; before = set(dz.get_state().keys())
    mv = [v for v in dz.get_state().values() if v.get("zone") == "mitral_valve"][0]
    dz.create(name="mv-funnel"); k_new = (set(dz.get_state().keys()) - before).pop()   # Fluent names it dynamic-zone-N
    dz[k_new].zone.set_state("mv_funnel"); dz[k_new].type.set_state("rigid-body")
    dz[k_new].motion.set_state(mv["motion"]); dz[k_new].meshing.set_state(mv["meshing"])
    rm = S.setup.dynamic_mesh.methods.remeshing.settings
    rm.length_min = LEN_MIN; rm.length_max = LEN_MAX
    dm = S.setup.dynamic_mesh.get_state()
    log("dynamic zones: " + json.dumps({k: (v.get("zone"), v.get("type"), v.get("motion", {}).get("motion_def")) for k, v in dm["dynamic_zones"].items()}))
    log("remeshing: " + json.dumps(dm["methods"]["remeshing"]["settings"]))
    log("MV BC: " + json.dumps(st["velocity_inlet"]["mitral_valve"]["momentum"]["velocity_magnitude"]))
    log("PV BC: " + json.dumps({z: st["pressure_inlet"][z]["momentum"]["gauge_total_pressure"] for z in ["pv_1", "pv_2", "pv_3", "pv_4"]}))
    tui("/mesh/check")
    S.file.write_case(file_name=NEWCASE); log("written " + NEWCASE)
s.exit()
