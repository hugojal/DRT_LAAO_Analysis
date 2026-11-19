"""Pathlines (run8), 10/11/2026. pvbatch only.
Pathlines follow blood particles through the time-varying flow, unlike streamlines, which are drawn in the velocity field frozen at
one instant. Particles are released once, at the start of a beat, and followed for one beat (ParticleTracer, one position per time
step, 0.01 s); those that leave through the mitral valve stop there. The paths are built here from the positions of each ParticleId
(ParaView's ParticlePath filter drew straight artefacts from the vein inlets). Colour = time after release.
  device   200 seeds in a sphere (r 8 mm) 5 mm in front of the device (same seeds as the device streamlines)
  body     the same sphere in the middle of the atrial body (centroid of the fluid), for comparison
  pv       seeds just inside the four pulmonary-vein inlets (whole atrium, same camera as the whole-atrium streamlines)
env PATH_T0 = release time (default 2.63 = start of the last beat; 1.75 = start of beat 3)
writes 4_postprocessing/run8/pathlines/pathlines_<which>_<view>_t<T0>.png, paths_<which>_t<T0>.vtp and pathlines_summary.txt
usage: "C:/Program Files/ParaView 6.2.0/bin/pvbatch.exe" --force-offscreen-rendering 4_postprocessing/pv_pathlines.py [device body pv]"""
import os, sys, math, json
import numpy as np
from paraview.simple import *
from paraview import servermanager as sm
from vtkmodules.util.numpy_support import vtk_to_numpy, numpy_to_vtk
from vtkmodules.vtkCommonDataModel import vtkPolyData, vtkCellArray
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkIOXML import vtkXMLPolyDataWriter
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/")
RUN = os.environ.get("PV_RUN", "run9"); OUT = ROOT + f"/4_postprocessing/{RUN}/pathlines/"; os.makedirs(OUT, exist_ok=True)
WHICH = sys.argv[1:] or ["device", "body", "pv"]
T0 = float(os.environ.get("PATH_T0", "2.63")); BEAT = 0.875; TAG = "t%.2f" % T0
C = np.array([0.031326, -0.017721, 0.016914]); N = np.array([0.626991, -0.520926, -0.579239])
nz = np.array([N[1], -N[0], 0.0]); nz /= np.linalg.norm(nz)                       # side view: normal of the long-axis plane
DEVC = [0.90, 0.45, 0.05]
r = EnSightReader(CaseFileName=ROOT + f"/3_simulation/results/{RUN}_4cycles/all_steps.encas")
fluid = MergeBlocks(Input=ExtractBlock(Input=r, Selectors=["/Root/fluid-1"]))
pvs = MergeBlocks(Input=ExtractBlock(Input=r, Selectors=["/Root/pv_%d" % k for k in range(1, 5)]))
allt = list(r.TimestepValues); i0 = min(range(len(allt)), key=lambda i: abs(allt[i] - T0))
ts = [t for t in allt[i0:] if t <= allt[i0] + BEAT + 1e-6]
sub = ExtractTimeSteps(Input=fluid); sub.SelectionMode = "Select Time Steps"; sub.TimeStepIndices = list(range(i0, len(allt)))   # tracer starts at T0
la = STLReader(FileNames=[ROOT + "/4_postprocessing/paraview/la_surface_model_m.stl"])
dev = STLReader(FileNames=[ROOT + "/4_postprocessing/paraview/device_display_model_m.stl"])   # 16/11/2026: closed, smoothed device, drawn only (seeds do not use it)
# camera of the whole-atrium streamline figures (pv_figures.py, model frame of run8)
_T = json.load(open(ROOT + "/2_mesh/run8_07112026/transform_LPS_to_model.json")); _R = np.array(_T["R"]); _c = np.array(_T["c_LPS_mm"]) / 1000
X = lambda p: _R @ (np.array(p) - _c)
Cf, Bf, Mf = X([0.0264, -0.1563, 0.8968]), X([-0.0027, -0.1523, 0.8661]), X([0.0221, -0.1684, 0.8571])
PN = np.cross(Cf - Bf, Mf - Bf); PN /= np.linalg.norm(PN)

def producer(P):
    pd = vtkPolyData(); pts = vtkPoints(); pts.SetData(numpy_to_vtk(np.ascontiguousarray(P), deep=1)); pd.SetPoints(pts)
    va = vtkCellArray()
    for i in range(len(P)): va.InsertNextCell(1); va.InsertCellPoint(i)
    pd.SetVerts(va); s = PVTrivialProducer(); s.GetClientSideObject().SetOutput(pd); return s
def trace(P):
    """positions of every particle at every step of one beat -> {id: [(age, xyz), ...]}, count at the start and at the end"""
    pt = ParticleTracer(Input=sub, SeedSource=producer(P)); pt.SelectInputVectors = ["POINTS", "Velocity"]
    pt.StaticSeeds = 1; pt.ForceReinjectionEveryNSteps = 0; pt.MeshOverTime = "Different"; pt.ComputeVorticity = 0
    tracks, n = {}, []
    for t in ts:
        pt.UpdatePipeline(t); d = sm.Fetch(pt); n.append(d.GetNumberOfPoints())
        if not n[-1]: continue
        Q = vtk_to_numpy(d.GetPoints().GetData()); ids = vtk_to_numpy(d.GetPointData().GetArray("ParticleId"))
        for i, q in zip(ids.tolist(), Q): tracks.setdefault(i, []).append((t - ts[0], q.copy()))
    Delete(pt); return tracks, n[0], n[-1]
def polylines(tracks, name, jump=0.012):
    pts, age, lines = [], [], vtkCellArray()
    for tr in tracks.values():
        seg = [0]
        for k in range(1, len(tr) + 1):
            if k == len(tr) or np.linalg.norm(tr[k][1] - tr[k - 1][1]) > jump:          # never seen so far; kept as a guard
                if len(seg) > 1 or k - seg[0] > 1:
                    idx = list(range(seg[0], k)); base = len(pts)
                    lines.InsertNextCell(len(idx))
                    for j, kk in enumerate(idx): pts.append(tr[kk][1]); age.append(tr[kk][0]); lines.InsertCellPoint(base + j)
                seg = [k]
    pd = vtkPolyData(); p = vtkPoints(); p.SetData(numpy_to_vtk(np.array(pts), deep=1)); pd.SetPoints(p); pd.SetLines(lines)
    a = numpy_to_vtk(np.array(age), deep=1); a.SetName("age"); pd.GetPointData().AddArray(a)
    w = vtkXMLPolyDataWriter(); w.SetFileName(OUT + name); w.SetInputData(pd); w.Write()
    return XMLPolyDataReader(FileName=[OUT + name])
def render(paths, name, eye_dir, focal, up, scale, size=(1000, 1000), show_dev=True):
    v = CreateView("RenderView"); v.ViewSize = list(size); v.Background = [1, 1, 1]; v.UseColorPaletteForBackground = 0; v.OrientationAxesVisibility = 0
    dw = Show(la, v); dw.ColorArrayName = ["POINTS", ""]; dw.DiffuseColor = [0.80, 0.80, 0.83]; dw.Opacity = 0.15
    if show_dev: dd = Show(dev, v); dd.ColorArrayName = ["POINTS", ""]; dd.DiffuseColor = DEVC
    tb = Tube(Input=paths); tb.Radius = 0.0002; tb.NumberofSides = 8
    dt = Show(tb, v); ColorBy(dt, ("POINTS", "age")); lut = GetColorTransferFunction("age"); lut.ApplyPreset("Inferno", True)
    lut.RescaleTransferFunction(0.0, BEAT); lut.AutomaticRescaleRangeMode = "Never"
    sb = GetScalarBar(lut, v); sb.Title = "time after release (s)"; sb.ComponentTitle = ""; sb.Orientation = "Horizontal"; sb.WindowLocation = "Any Location"
    sb.Position = [0.15, 0.03]; sb.ScalarBarLength = 0.7; sb.ScalarBarThickness = 32; sb.TitleFontSize = 50; sb.LabelFontSize = 44
    sb.TitleColor = sb.LabelColor = [0, 0, 0]; sb.TitleFontFamily = sb.LabelFontFamily = "Times"; sb.AutomaticLabelFormat = 0; sb.LabelFormat = "{:.1f}"
    sb.RangeLabelFormat = "{:.1f}"; sb.UseCustomLabels = 1; sb.CustomLabels = [0.4]; sb.AddRangeLabels = 1; sb.Visibility = 1
    Render(v); c = v.GetActiveCamera(); f = np.array(focal) - 0.30 * scale * np.array(up)    # model lifted above the colour bar
    c.SetFocalPoint(list(f)); c.SetPosition(list(f + 0.3 * np.array(eye_dir))); c.SetViewUp(list(up)); v.CameraParallelProjection = 1; v.CameraParallelScale = scale
    Render(v); SaveScreenshot(OUT + name, v, ImageResolution=list(size)); print("saved", name, flush=True); Delete(v)

rng = np.random.default_rng(0)
def ball(c, n=200, rad=0.008):
    x = rng.uniform(-1, 1, (n * 3, 3)); x = x[np.linalg.norm(x, axis=1) <= 1][:n]; return np.asarray(c) + rad * x
summary = []
for w in WHICH:
    if w == "device": P = ball(C - 0.005 * N)
    elif w == "body":
        fluid.UpdatePipeline(ts[0]); Pf = vtk_to_numpy(sm.Fetch(fluid).GetPoints().GetData()); P = ball(Pf.mean(0))
    else:                                                    # vein inlets: points of the inlet faces moved 1.5 mm towards the atrial body
        pvs.UpdatePipeline(ts[0]); Pv = vtk_to_numpy(sm.Fetch(pvs).GetPoints().GetData()); Pv = Pv[rng.permutation(len(Pv))[:400]]
        fluid.UpdatePipeline(ts[0]); cen = vtk_to_numpy(sm.Fetch(fluid).GetPoints().GetData()).mean(0)
        P = Pv + 0.0015 * (cen - Pv) / np.linalg.norm(cen - Pv, axis=1)[:, None]
    tracks, n0, n1 = trace(P); paths = polylines(tracks, f"paths_{w}_{TAG}.vtp")
    summary.append("%s release %.2f s  %-6s inside the fluid %4d, still in the LA after one beat %4d (%.0f %%)" % (TAG, T0, w, n0, n1, 100.0 * n1 / max(n0, 1)))
    print(summary[-1], flush=True)
    if w in ("device", "body"):
        render(paths, f"pathlines_{w}_side_{TAG}.png", nz, [0.45 * C[0], 0.45 * C[1], 0.028], [0, 0, 1], 0.050)
    else:
        render(paths, f"pathlines_pv_front_{TAG}.png", PN, Bf, [0, 0, 1], 0.058, (1000, 1000), show_dev=False)
open(OUT + "pathlines_summary.txt", "a").write("".join(s + "\n" for s in summary))
