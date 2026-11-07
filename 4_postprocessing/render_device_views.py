"""Separate ParaView images of the region in front of the device (last beat of a run; PV_RUN, default run8), 07/11/2026. pvbatch only.
Uses the pipeline of 6_paraview_package/open_device_sections.py; one item per image, the device itself is not drawn,
colour bar horizontal below the model (never on top of it).
usage: pvbatch --force-offscreen-rendering 4_postprocessing/render_device_views.py
writes 4_postprocessing/<run>/device_sections/views/*.png"""
import os, inspect
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))))
PKG = os.path.join(ROOT, "6_paraview_package"); RUN = os.environ.get("PV_RUN", "run8")                                    # the package must hold this run (make_paraview_package.py)
OUT = os.path.join(ROOT, "4_postprocessing", RUN, "device_sections", "views"); os.makedirs(OUT, exist_ok=True)
os.chdir(PKG); exec(open(os.path.join(PKG, "open_device_sections.py")).read())
v.OrientationAxesVisibility = 0; v.ViewSize = [1000, 1000]; v.CameraParallelProjection = 1
ALL = secs + [gl, la, lag, stag, st, tube]
def bar(lut, title):
    sb = GetScalarBar(lut, v); sb.Title = title; sb.ComponentTitle = ""; sb.Orientation = "Horizontal"
    sb.WindowLocation = "Any Location"; sb.Position = [0.1, 0.03]; sb.ScalarBarLength = 0.8; sb.ScalarBarThickness = 44
    sb.TitleFontSize = 64; sb.LabelFontSize = 58; sb.TitleColor = [0, 0, 0]; sb.LabelColor = [0, 0, 0]   # readable when printed at 1/5 page width
    sb.AutomaticLabelFormat = 0; sb.LabelFormat = "{:.2f}"; sb.RangeLabelFormat = "{:.2f}"
    lo_, hi_ = (-0.15, 0.15) if lut is ua else (0.0, 0.3); sb.UseCustomLabels = 1; sb.CustomLabels = [round((lo_ + hi_) / 2, 3)]   # min, middle, max only
def fit(items, name, pad=1.6):
    """camera along the preset direction, centred on the shown items, parallel scale from their extent"""
    B = None
    for o in items:
        o.UpdatePipeline(anim.AnimationTime); bb = o.GetDataInformation().GetBounds()
        B = list(bb) if B is None else [min(B[i], bb[i]) if i % 2 == 0 else max(B[i], bb[i]) for i in range(6)]
    c = [(B[2 * i] + B[2 * i + 1]) / 2 for i in range(3)]; r = 0.5 * max(B[1] - B[0], B[3] - B[2], B[5] - B[4])
    d = dict(side=nz, atrium=[-x for x in N], oblique=[0.6 * nz[i] - 0.8 * N[i] for i in range(3)])[name]
    sc = pad * r; k = 0.35 * sc                         # shift down: model above the colour bar
    v.CameraFocalPoint = [c[0], c[1], c[2] - k]; v.CameraPosition = [c[i] + 0.3 * d[i] - (k if i == 2 else 0) for i in range(3)]
    v.CameraViewUp = [0, 0, 1]; v.CameraParallelScale = sc
def shot(fname, items, t, camname, lut, title, show_disp, pad=1.6):
    for o in ALL: Hide(o, v)
    anim.AnimationTime = t
    for o in items: Show(o, v)
    fit(items, camname, pad)
    for b in ("u_axial", "Velocity_Magnitude"): GetScalarBar(GetColorTransferFunction(b), v).Visibility = 0
    GetDisplayProperties(show_disp, v).SetScalarBarVisibility(v, True); bar(lut, title)
    ua.RescaleTransferFunction(-0.15, 0.15); vm.RescaleTransferFunction(0.0, 0.3)
    Render(v); SaveScreenshot(os.path.join(OUT, fname), v, ImageResolution=[1000, 1000]); print("saved", fname)
VEL, AX = "speed (m/s)", "axial velocity (m/s)"
for g in (gl, lag): g.ScaleArray = ["POINTS", "No scale array"]; g.GlyphMode = "Every Nth Point"
gl.ScaleFactor = 0.0018; gl.Stride = 4; lag.ScaleFactor = 0.0018; lag.Stride = 10
shot("streamlines_side_systole_t290.png", [tube], 2.90, "side", vm, VEL, tube)
shot("streamlines_side_filling_t306.png", [tube], 3.06, "side", vm, VEL, tube)
shot("streamlines_from_atrium_systole_t290.png", [tube], 2.90, "atrium", vm, VEL, tube)
shot("longaxis_slice_systole_t290.png", [la, lag], 2.90, "side", ua, AX, la)
shot("longaxis_slice_filling_t306.png", [la, lag], 3.06, "side", ua, AX, la)
shot("section_8mm_systole_t290.png", [secs[2], gl], 2.90, "atrium", ua, AX, secs[2], 1.6)
shot("section_8mm_filling_t306.png", [secs[2], gl], 3.06, "atrium", ua, AX, secs[2], 1.6)
