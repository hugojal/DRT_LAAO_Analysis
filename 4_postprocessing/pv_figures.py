"""ParaView (pvbatch) figures for the report. Run:
"C:/Program Files/ParaView 6.2.0/bin/pvbatch.exe" --force-offscreen-rendering 4_postprocessing/pv_figures.py [which]
which: anatomy | flow | vortex | wall | all"""
import os, sys, math
from paraview.simple import *
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace("\\", "/"); OUT = ROOT + "/5_report/figures/"; PVD = ROOT + "/4_postprocessing/paraview/"   # ROOT = project folder (DRT_LAAO_Case3)
WHICH = sys.argv[1] if len(sys.argv) > 1 else "all"
C = [0.0264, -0.1563, 0.8968]                                   # device centroid (m)
N = [0.83, 0.14, 0.55]; nn = math.sqrt(sum(x * x for x in N)); N = [x / nn for x in N]   # LA body -> appendage ostium
B = [-0.0027, -0.1523, 0.8661]                                  # LA body centre
M = [0.0272, -0.1725, 0.8550]                                   # mitral cut centre
T_PEAK, T_LATE = 3.06, 3.40
sub = lambda a, b: [x - y for x, y in zip(a, b)]
cross = lambda a, b: [a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0]]
def unit(a): l = math.sqrt(sum(x * x for x in a)); return [x / l for x in a]
PN = unit(cross(sub(C, B), sub(M, B)))                          # normal of the plane through LA centre, device and mitral valve

def view(w=1000, h=850):
    v = CreateView("RenderView"); v.ViewSize = [w, h]; v.Background = [1, 1, 1]; v.UseColorPaletteForBackground = 0; v.OrientationAxesVisibility = 0
    return v
def bar(d, v, title, fmt="{:.2f}", h=False, labels=None):
    lut = GetColorTransferFunction(d.ColorArrayName[1]); sb = GetScalarBar(lut, v); sb.Title = title; sb.ComponentTitle = ""
    sb.TitleColor = sb.LabelColor = [0, 0, 0]; sb.TitleFontFamily = sb.LabelFontFamily = "Times"; sb.TitleFontSize = 42; sb.LabelFontSize = 38
    sb.Orientation = "Horizontal"; sb.WindowLocation = "Any Location"; sb.Position = [0.14, 0.03]; sb.ScalarBarLength = 0.72; sb.ScalarBarThickness = 28
    pts = lut.RGBPoints; lo, hi = pts[0], pts[-4]
    sb.AutomaticLabelFormat = 0; sb.LabelFormat = fmt; sb.RangeLabelFormat = fmt; sb.UseCustomLabels = 1; sb.CustomLabels = labels if labels else [lo, 0.5 * (lo + hi), hi]; sb.AddRangeLabels = 0; sb.Visibility = 1
def cam(v, pos, focal, up=(0, 0, 1), scale=None):
    Render(v)                                                                # first render resets the camera; do it before placing ours
    d = [f - p for f, p in zip(focal, pos)]; dl = math.sqrt(sum(x * x for x in d)); d = [x / dl for x in d]
    u = list(up); k = sum(a * b for a, b in zip(u, d)); u = unit([a - k * b for a, b in zip(u, d)])
    sh = 0.27 * (scale or 0.05)                                              # lift the model above the colour bar
    pos = [p - sh * w for p, w in zip(pos, u)]; focal = [f - sh * w for f, w in zip(focal, u)]
    c = v.GetActiveCamera(); c.SetPosition(pos); c.SetFocalPoint(focal); c.SetViewUp(u); v.CameraParallelProjection = 1 if scale else 0
    if scale: v.CameraParallelScale = scale * 1.16
def shot(v, name): Render(v); SaveScreenshot(OUT + name, v, ImageResolution=v.ViewSize, TransparentBackground=0); print("saved", name)
def blocks(r, names): return MergeBlocks(Input=ExtractBlock(Input=r, Selectors=["/Root/" + n for n in names]))

dev = STLReader(FileNames=[PVD + "device_frame_m.stl"])          # the segmented device (Device.seg.nrrd)
la = STLReader(FileNames=[PVD + "la_surface_m.stl"])
eye_dev = [C[i] + 0.13 * N[i] - 0.02 * PN[i] for i in range(3)]                          # outside the LA, looking at the device side
eye_front = [B[i] + 0.20 * PN[i] for i in range(3)]

if WHICH in ("anatomy", "all"):
    seg = STLReader(FileNames=[PVD + "device_frame_m.stl"])
    v = view(900, 820); d1 = Show(la, v); d1.ColorArrayName = ["POINTS", ""]; d1.DiffuseColor = [0.78, 0.80, 0.85]; d1.Opacity = 0.35
    d2 = Show(seg, v); d2.ColorArrayName = ["POINTS", ""]; d2.DiffuseColor = [0.85, 0.60, 0.15]; d2.Specular = 0.5
    cam(v, [C[i] + 0.10 * N[i] + 0.04 * PN[i] for i in range(3)], [0.6 * C[i] + 0.4 * B[i] for i in range(3)], (0, 0, 1), 0.045); shot(v, "pv_anatomy_seg.png"); Delete(v)

if WHICH in ("flow", "vortex", "all"):
    r = EnSightReader(CaseFileName=ROOT + "/3_simulation/results/run5_4cycles/all_steps.encas")
    fluid = blocks(r, ["fluid-1"]); wall = blocks(r, ["la_wall"]); pvs = blocks(r, ["pv_1", "pv_2", "pv_3", "pv_4"])

if WHICH in ("flow", "all"):
    for t, vmax, tag in ((T_PEAK, 1.0, "peak"), (T_LATE, 0.12, "late")):
        v = view(1000, 850); v.ViewTime = t
        st = StreamTracerWithCustomSource(Input=fluid, SeedSource=pvs); st.Vectors = ["POINTS", "Velocity"]; st.MaximumStreamlineLength = 0.4; st.IntegrationDirection = "BOTH"
        tb = Tube(Input=st); tb.Radius = 0.00028
        dw = Show(wall, v); dw.ColorArrayName = ["POINTS", ""]; dw.DiffuseColor = [0.80, 0.80, 0.83]; dw.Opacity = 0.15
        ds = Show(tb, v); ColorBy(ds, ("POINTS", "Velocity_Magnitude")); lut = GetColorTransferFunction("Velocity_Magnitude"); lut.ApplyPreset("Turbo", True); lut.RescaleTransferFunction(0.0, vmax); lut.AutomaticRescaleRangeMode = "Never"
        bar(ds, v, "Velocity magnitude (m/s)", "{:.2f}")
        dd = Show(dev, v); dd.ColorArrayName = ["POINTS", ""]; dd.DiffuseColor = [0.85, 0.60, 0.15]
        cam(v, eye_front, B, (0, 0, 1), 0.062); shot(v, f"pv_streamlines_{tag}.png"); Delete(v)
        # slice through LA centre, device and mitral valve, with velocity isolines
        v = view(1000, 850); v.ViewTime = t
        sl = Slice(Input=fluid); sl.SliceType = "Plane"; sl.SliceType.Origin = C; sl.SliceType.Normal = PN
        iso = Contour(Input=sl); iso.ContourBy = ["POINTS", "Velocity_Magnitude"]; iso.Isosurfaces = [0.02, 0.05, 0.10, 0.20, 0.40, 0.80] if tag == "peak" else [0.01, 0.02, 0.05, 0.10]
        dcut = Slice(Input=dev); dcut.SliceType = "Plane"; dcut.SliceType.Origin = C; dcut.SliceType.Normal = PN
        dsl = Show(sl, v); ColorBy(dsl, ("POINTS", "Velocity_Magnitude")); lut = GetColorTransferFunction("Velocity_Magnitude"); lut.ApplyPreset("Turbo", True); lut.RescaleTransferFunction(0.0, vmax); bar(dsl, v, "Velocity magnitude (m/s)", "{:.2f}")
        di = Show(iso, v); di.DiffuseColor = di.AmbientColor = [0, 0, 0]; di.LineWidth = 1.2; di.ColorArrayName = ["POINTS", ""]
        dh = Show(dev, v); dh.ColorArrayName = ["POINTS", ""]; dh.DiffuseColor = [0.85, 0.60, 0.15]
        dc = Show(dcut, v); dc.DiffuseColor = dc.AmbientColor = [0.85, 0.60, 0.15]; dc.LineWidth = 3.0; dc.ColorArrayName = ["POINTS", ""]
        cam(v, [C[i] + 0.2 * PN[i] for i in range(3)], [0.5 * (B[i] + C[i]) for i in range(3)], unit(cross(PN, sub(C, B))), 0.05); shot(v, f"pv_slice_{tag}.png"); Delete(v)

if WHICH in ("vortex", "all"):
    v = view(1000, 850); v.ViewTime = T_PEAK
    q = Contour(Input=fluid); q.ContourBy = ["POINTS", "Q_Criterion_Normalized"]; q.Isosurfaces = [4000.0]; q.ComputeScalars = 0
    pa = PointDatatoCellData(Input=q) if False else q
    dw = Show(wall, v); dw.ColorArrayName = ["POINTS", ""]; dw.DiffuseColor = [0.80, 0.80, 0.83]; dw.Opacity = 0.15
    dq = Show(q, v); ColorBy(dq, ("POINTS", "Velocity_Magnitude")); lut = GetColorTransferFunction("Velocity_Magnitude"); lut.ApplyPreset("Turbo", True); lut.RescaleTransferFunction(0.0, 1.0); bar(dq, v, "Velocity magnitude (m/s) on Q = 4000 1/s2", "{:.2f}")
    dd = Show(dev, v); dd.ColorArrayName = ["POINTS", ""]; dd.DiffuseColor = [0.85, 0.60, 0.15]
    cam(v, eye_front, B, (0, 0, 1), 0.062); shot(v, "pv_qcriterion_peak.png"); Delete(v)

if WHICH in ("wall", "all"):
    w = XMLPolyDataReader(FileName=[PVD + "run5_wall_metrics.vtp"])
    spec = (("TAWSS_Pa", "TAWSS (Pa)", (0.0, 1.0), "Viridis", [0.1, 0.2, 0.4], False, "{:.1f}"),
            ("OSI", "OSI (-)", (0.0, 0.5), "Inferno", [0.2, 0.3, 0.4], False, "{:.1f}"),
            ("ECAP_1_per_Pa", "ECAP (1/Pa)", (0.1, 10.0), "Plasma", [1.0, 2.0, 4.0], True, "{:g}"))
    views = (("dev", [C[i] + 0.10 * N[i] + 0.04 * PN[i] for i in range(3)], [0.6 * C[i] + 0.4 * B[i] for i in range(3)], 0.045), ("front", eye_front, B, 0.062))
    for arr, title, rng, cmap, isov, logc, fmt in spec:
        for vn, eye, foc, sc in views:
            v = view(900, 820)
            ds = Show(w, v); ColorBy(ds, ("POINTS", arr)); lut = GetColorTransferFunction(arr); lut.ApplyPreset(cmap, True)
            lut.RescaleTransferFunction(*rng); lut.AutomaticRescaleRangeMode = "Never"
            if logc: lut.MapControlPointsToLogSpace(); lut.UseLogScale = 1
            bar(ds, v, title, fmt, labels=[0.1, 1.0, 10.0] if logc else None)
            iso = Contour(Input=w); iso.ContourBy = ["POINTS", arr]; iso.Isosurfaces = isov
            di = Show(iso, v); di.ColorArrayName = ["POINTS", ""]; di.DiffuseColor = di.AmbientColor = [1, 1, 1] if arr != "OSI" else [0.1, 0.9, 0.9]; di.LineWidth = 1.6
            dist = Contour(Input=w); dist.ContourBy = ["POINTS", "dist_to_device_mm"]; dist.Isosurfaces = [10.0, 20.0]
            dd2 = Show(dist, v); dd2.ColorArrayName = ["POINTS", ""]; dd2.DiffuseColor = dd2.AmbientColor = [0.0, 0.0, 0.0]; dd2.LineWidth = 2.2
            dd = Show(dev, v); dd.ColorArrayName = ["POINTS", ""]; dd.DiffuseColor = [0.85, 0.60, 0.15]
            cam(v, eye, foc, (0, 0, 1), sc); shot(v, f"pv_wall_{arr.split('_')[0].lower()}_{vn}.png"); Delete(v)

if WHICH in ("ct", "all"):
    ct = XMLImageDataReader(FileName=[PVD + "ct_crop_m.vti"]); laseg = STLReader(FileNames=[PVD + "la_seg_m.stl"]); seg = STLReader(FileNames=[PVD + "device_frame_m.stl"])
    def grey(d):
        ColorBy(d, ("POINTS", "HU")); lut = GetColorTransferFunction("HU"); lut.ApplyPreset("Grayscale", True); lut.RescaleTransferFunction(-150.0, 650.0); lut.AutomaticRescaleRangeMode = "Never"; d.SetScalarBarVisibility(GetActiveView(), False) if False else None
    # (a) 3D: axial CT plane at the device level + LA segmentation (transparent) + device segmentation
    v = view(900, 820); ax = Slice(Input=ct); ax.SliceType = "Plane"; ax.SliceType.Origin = C; ax.SliceType.Normal = [0, 0, 1]
    da = Show(ax, v); grey(da); dl = Show(laseg, v); dl.ColorArrayName = ["POINTS", ""]; dl.DiffuseColor = [0.55, 0.75, 0.95]; dl.Opacity = 0.35
    ds = Show(seg, v); ds.ColorArrayName = ["POINTS", ""]; ds.DiffuseColor = [0.85, 0.60, 0.15]
    eye = [B[0] + 0.05, B[1] - 0.16, B[2] + 0.13]; c_ = v.GetActiveCamera(); c_.SetPosition(eye); c_.SetFocalPoint([0.5 * (B[i] + C[i]) for i in range(3)]); c_.SetViewUp([0, 0, 1]); v.CameraParallelProjection = 1; v.CameraParallelScale = 0.060
    shot(v, "pv_ct_3d.png"); Delete(v)
    # (b) oblique CT plane along the device axis with the segmentation outlines (LA blue, device orange)
    U = unit(cross(N, [0, 0, 1])); NRM = unit(cross(N, U))
    v = view(900, 820); ob = Slice(Input=ct); ob.SliceType = "Plane"; ob.SliceType.Origin = C; ob.SliceType.Normal = NRM
    do = Show(ob, v); grey(do)
    lc = Slice(Input=laseg); lc.SliceType = "Plane"; lc.SliceType.Origin = C; lc.SliceType.Normal = NRM; dlc = Show(lc, v); dlc.ColorArrayName = ["POINTS", ""]; dlc.DiffuseColor = dlc.AmbientColor = [0.35, 0.65, 1.0]; dlc.LineWidth = 4.0
    sc_ = Slice(Input=seg); sc_.SliceType = "Plane"; sc_.SliceType.Origin = C; sc_.SliceType.Normal = NRM; dsc = Show(sc_, v); dsc.ColorArrayName = ["POINTS", ""]; dsc.DiffuseColor = dsc.AmbientColor = [1.0, 0.65, 0.1]; dsc.LineWidth = 4.0
    c_ = v.GetActiveCamera(); c_.SetPosition([C[i] + 0.2 * NRM[i] for i in range(3)]); c_.SetFocalPoint([C[i] - 0.010 * N[i] for i in range(3)]); c_.SetViewUp(U); v.CameraParallelProjection = 1; v.CameraParallelScale = 0.017
    shot(v, "pv_ct_oblique.png"); Delete(v)
print("done", WHICH)
