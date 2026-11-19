"""Device-region figures, 19/11/2026. pvbatch only (last beat of run9).
 vectors_<phase>.png  velocity on the plane through the device axis, within 26 mm of the device: colour = speed, arrows = direction in the plane
 q_<phase>.png        same plane (whole slice) coloured by the Q-criterion (1/s2): red = rotation dominates, blue = shear dominates
usage: pvbatch --force-offscreen-rendering 4_postprocessing/render_device_vectors_q.py   -> 4_postprocessing/run9/device_sections/views_v3/"""
import os, json
from paraview.simple import *
ROOT = r"C:\Users\hugoj\Desktop\UNI\3er\MOs\DRT_LAAO_Case3"; J = lambda *a: os.path.join(ROOT, *a).replace("\\", "/")
OUT = J("4_postprocessing", "run9", "device_sections", "views_v3"); os.makedirs(OUT, exist_ok=True)
ax = json.load(open(J("4_postprocessing", "run9", "device_sections", "axis.json"))); C = ax["centre_m"]; A = ax["normal_into_appendage"]
import numpy as np
A = np.array(A) / np.linalg.norm(A); nz = np.cross(A, [0, 0, 1]); nz = list(nz / np.linalg.norm(nz))          # normal of the plane that contains the device axis and z
R = 0.026
sim = EnSightReader(registrationName="sim", CaseFileName=[J("6_paraview_package", "simulation", "run9_last_beat.encas")])
fluid = MergeBlocks(Input=ExtractBlock(Input=sim, Selectors=["/Root/fluid-1"]))
wall = MergeBlocks(Input=ExtractBlock(Input=sim, Selectors=["/Root/la_wall"]))
dev = STLReader(FileNames=[J("4_postprocessing", "paraview", "device_display_model_m.stl")])
sph = lambda src: (lambda c: (setattr(c, "ClipType", "Sphere"), setattr(c.ClipType, "Center", C), setattr(c.ClipType, "Radius", R), setattr(c, "Invert", 1), c)[-1])(Clip(Input=src))
sl = Slice(Input=fluid); sl.SliceType = "Plane"; sl.SliceType.Origin = C; sl.SliceType.Normal = nz
slc = sl; slclip = sph(sl)
calc = Calculator(Input=slclip, ResultArrayName="vin", Function="Velocity-dot(Velocity,%f*iHat+%f*jHat+%f*kHat)*(%f*iHat+%f*jHat+%f*kHat)" % (*nz, *nz))
gl = Glyph(Input=calc, GlyphType="Arrow"); gl.OrientationArray = ["POINTS", "vin"]; gl.ScaleArray = ["POINTS", "No scale array"]; gl.ScaleFactor = 0.0022; gl.GlyphMode = "Every Nth Point"; gl.Stride = 9
devline = Slice(Input=dev); devline.SliceType = "Plane"; devline.SliceType.Origin = C; devline.SliceType.Normal = nz
v = CreateView("RenderView"); v.ViewSize = [1000, 1000]; v.Background = [1, 1, 1]; v.UseColorPaletteForBackground = 0; v.OrientationAxesVisibility = 0; v.CameraParallelProjection = 1
anim = GetAnimationScene(); anim.UpdateAnimationUsingDataTimeSteps()
vm = GetColorTransferFunction("Velocity_Magnitude"); vm.ApplyPreset("Turbo", True); vm.AutomaticRescaleRangeMode = "Never"; vm.RescaleTransferFunction(0.0, 0.1)
def bar(disp):
    sb = GetScalarBar(vm, v); sb.Title = "speed (m/s)"; sb.ComponentTitle = ""; sb.Orientation = "Horizontal"; sb.WindowLocation = "Any Location"
    sb.Position = [0.1, 0.03]; sb.ScalarBarLength = 0.8; sb.ScalarBarThickness = 44; sb.TitleFontSize = 64; sb.LabelFontSize = 58
    sb.TitleColor = [0, 0, 0]; sb.LabelColor = [0, 0, 0]; sb.AutomaticLabelFormat = 0; sb.LabelFormat = "{:.2f}"; sb.RangeLabelFormat = "{:.2f}"; sb.UseCustomLabels = 1; sb.CustomLabels = [0.075]
    disp.SetScalarBarVisibility(v, True)
def cam(d):
    k = 0.35 * R; c = C
    v.CameraFocalPoint = [c[0], c[1], c[2] - k * 0.6]; v.CameraPosition = [c[i] + 0.3 * d[i] - (k * 0.6 if i == 2 else 0) for i in range(3)]
    v.CameraViewUp = [0, 0, 1]; v.CameraParallelScale = 1.05 * R
qlut = GetColorTransferFunction("Q_Criterion_Normalized"); qlut.ApplyPreset("Cool to Warm", True); qlut.AutomaticRescaleRangeMode = "Never"; qlut.RescaleTransferFunction(-500.0, 500.0)
def bar(disp, lut, title, labels, fmt):
    for l in (vm, qlut): GetScalarBar(l, v).Visibility = 0
    sb = GetScalarBar(lut, v); sb.Title = title; sb.ComponentTitle = ""; sb.Orientation = "Horizontal"; sb.WindowLocation = "Any Location"
    sb.Position = [0.1, 0.03]; sb.ScalarBarLength = 0.8; sb.ScalarBarThickness = 44; sb.TitleFontSize = 64; sb.LabelFontSize = 58
    sb.TitleColor = [0, 0, 0]; sb.LabelColor = [0, 0, 0]; sb.AutomaticLabelFormat = 0; sb.LabelFormat = fmt; sb.RangeLabelFormat = fmt; sb.UseCustomLabels = 1; sb.CustomLabels = labels
    disp.SetScalarBarVisibility(v, True)
def cam():
    f = [C[i] - 0.45 * R * A[i] for i in range(3)]; f[2] -= 0.95 * R
    v.CameraFocalPoint = f; v.CameraPosition = [f[i] + 0.3 * nz[i] for i in range(3)]; v.CameraViewUp = [0, 0, 1]; v.CameraParallelScale = 1.3 * R
Render(v)
PH = [("valve_closed", 2.90), ("E_wave_peak", 3.06), ("late_diastole", 3.40)]
PH = [x for x in PH if x[0] == "valve_closed"]
for nm, t in PH:
    anim.AnimationTime = t
    for o in (slc, gl, devline): Hide(o, v)
    d = Show(slc, v); ColorBy(d, ("POINTS", "Velocity_Magnitude")); vm.RescaleTransferFunction(0.0, 0.1); g = Show(gl, v); g.ColorArrayName = ["POINTS", ""]; g.DiffuseColor = [0, 0, 0]
    cam(); bar(d, vm, "speed (m/s)", [0.05], "{:.2f}"); Render(v); Render(v); SaveScreenshot(OUT + "/vectors_%s.png" % nm, v, ImageResolution=[1000, 1000])
    Hide(gl, v); ColorBy(d, ("POINTS", "Q_Criterion_Normalized")); qlut.RescaleTransferFunction(-500.0, 500.0)
    bar(d, qlut, "Q-criterion (1/s2)", [0.0], "{:.0f}"); Render(v); Render(v); SaveScreenshot(OUT + "/q_%s.png" % nm, v, ImageResolution=[1000, 1000])
    print("done", nm)
