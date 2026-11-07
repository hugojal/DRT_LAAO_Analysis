"""Cross-sections in front of the device and recirculation (run7, last heartbeat), 07/11/2026.
ParaView GUI: View > Python Shell > Run Script > this file   (or: paraview --script=open_device_sections.py from this folder)
Pipeline (press Play to run the heartbeat, t = 2.63-3.50 s):
  axial velocity      u_n = velocity along the device axis (m/s); + = towards the device / appendage, - = back into the atrium
  section d = 2..16   planes perpendicular to the device axis, 2, 5, 8, 12, 16 mm from the disc centre, coloured by u_n.
                      Red and blue on the same section at the same time = blood going both ways = recirculation.
  in-plane arrows     velocity glyphs on the 8 mm section
  long-axis slice     plane through the device axis, with velocity arrows: the vortex in front of the device is visible here
  stagnant |v|<0.05   blood slower than 0.05 m/s (iso-volume) near the device
  streamlines (device) streamlines seeded in a sphere (r 8 mm) 5 mm in front of the device
  la_wall             transparent wall (the device itself is not drawn)
Numbers for the same planes: 4_postprocessing/run7/device_sections/ (device_sections.py) in the project repository.
Frame: metres; z = mitral valve axis; device axis from the CT disc-rim fit."""
import os, inspect
from paraview.simple import *
try: HERE = os.path.dirname(os.path.abspath(__file__))
except NameError: HERE = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
if not os.path.exists(os.path.join(HERE, "simulation")): HERE = os.getcwd()
P = lambda *a: os.path.join(HERE, *a).replace("\\", "/")
C = [0.031326, -0.017721, 0.016914]                 # device disc centre (m)
N = [0.626991, -0.520926, -0.579239]                # device axis, pointing from the atrium into the appendage
DS = (2, 5, 8, 12, 16); RCOL = 0.020; T_SHOW = 2.90  # late diastole/diastasis, when the region in front of the device is slowest
pt = lambda d: [C[i] - d / 1000.0 * N[i] for i in range(3)]

sim = EnSightReader(registrationName="simulation", CaseFileName=P("simulation", "run7_last_beat.encas"))
fluid = MergeBlocks(registrationName="fluid", Input=ExtractBlock(Input=sim, Selectors=["/Root/fluid-1"]))
wall = MergeBlocks(registrationName="la_wall", Input=ExtractBlock(Input=sim, Selectors=["/Root/la_wall"]))
un = Calculator(registrationName="axial velocity", Input=fluid); un.ResultArrayName = "u_axial"
un.Function = "Velocity_X*%f+Velocity_Y*%f+Velocity_Z*%f" % tuple(N)
col = Clip(registrationName="column r=20 mm", Input=un); col.ClipType = "Cylinder"; col.ClipType.Center = C; col.ClipType.Axis = N
col.ClipType.Radius = RCOL; col.Invert = 1
secs = []
for d in DS:
    s0 = Slice(registrationName=f"slice d={d} mm (all pieces)", Input=col); s0.SliceType = "Plane"; s0.SliceType.Origin = pt(d); s0.SliceType.Normal = N
    s = Connectivity(registrationName=f"section d={d} mm", Input=s0); s.ExtractionMode = "Extract Closest Point Region"; s.ClosestPoint = pt(d)
    s.ColorRegions = 0
    secs.append(s)                                   # only the piece in front of the device (a vein can also cross the column)
gl = Glyph(registrationName="in-plane arrows (8 mm)", Input=secs[2], GlyphType="Arrow"); gl.OrientationArray = ["POINTS", "Velocity"]
gl.ScaleArray = ["POINTS", "Velocity_Magnitude"]; gl.ScaleFactor = 0.08; gl.GlyphMode = "Every Nth Point"; gl.Stride = 15
# long-axis plane: contains the device axis and the mitral axis z
nz = [N[1], -N[0], 0.0]; l = (nz[0] ** 2 + nz[1] ** 2) ** 0.5; nz = [x / l for x in nz]
la = Slice(registrationName="long-axis slice (device)", Input=un); la.SliceType = "Plane"; la.SliceType.Origin = C; la.SliceType.Normal = nz
lag = Glyph(registrationName="long-axis arrows", Input=la, GlyphType="Arrow"); lag.OrientationArray = ["POINTS", "Velocity"]
lag.ScaleArray = ["POINTS", "No scale array"]; lag.ScaleFactor = 0.002; lag.GlyphMode = "Every Nth Point"; lag.Stride = 12
stag = Threshold(registrationName="stagnant |v|<0.05 near device", Input=col); stag.Scalars = ["POINTS", "Velocity_Magnitude"]
stag.LowerThreshold = 0.0; stag.UpperThreshold = 0.05
st = StreamTracer(registrationName="streamlines (device)", Input=fluid, SeedType="Point Cloud")
st.SeedType.Center = pt(5); st.SeedType.Radius = 0.008; st.SeedType.NumberOfPoints = 200
st.Vectors = ["POINTS", "Velocity"]; st.MaximumStreamlineLength = 0.045; st.IntegrationDirection = "BOTH"
v = GetActiveViewOrCreate("RenderView"); v.Background = [1, 1, 1]; v.UseColorPaletteForBackground = 0; v.OrientationAxesVisibility = 1
anim = GetAnimationScene(); anim.UpdateAnimationUsingDataTimeSteps(); anim.AnimationTime = T_SHOW
ua = GetColorTransferFunction("u_axial"); ua.ApplyPreset("Cool to Warm", True); ua.RescaleTransferFunction(-0.15, 0.15); ua.AutomaticRescaleRangeMode = "Never"
vm = GetColorTransferFunction("Velocity_Magnitude"); vm.ApplyPreset("Turbo", True); vm.RescaleTransferFunction(0.0, 0.3); vm.AutomaticRescaleRangeMode = "Never"
tube = Tube(registrationName="streamline tubes (device)", Input=st); tube.Radius = 0.0002
dw = Show(wall, v); dw.ColorArrayName = ["POINTS", ""]; dw.DiffuseColor = [0.8, 0.8, 0.83]; dw.Opacity = 0.12
for d, s in zip(DS, secs):
    ds = Show(s, v); ColorBy(ds, ("POINTS", "u_axial")); Hide(s, v)
dg = Show(gl, v); ColorBy(dg, None); dg.DiffuseColor = [0.1, 0.1, 0.1]; Hide(gl, v)
dl = Show(la, v); ColorBy(dl, ("POINTS", "u_axial")); Hide(la, v)
dlg = Show(lag, v); ColorBy(dlg, None); dlg.DiffuseColor = [0.1, 0.1, 0.1]; Hide(lag, v)
dsg = Show(stag, v); ColorBy(dsg, None); dsg.DiffuseColor = [0.2, 0.4, 1.0]; dsg.Opacity = 0.5; Hide(stag, v)
Show(st, v); Hide(st, v)
dt = Show(tube, v); ColorBy(dt, ("POINTS", "Velocity_Magnitude"))
for b in ("u_axial", "Velocity_Magnitude"):
    sb = GetScalarBar(GetColorTransferFunction(b), v); sb.Title = {"u_axial": "axial velocity (m/s), + towards device", "Velocity_Magnitude": "velocity (m/s)"}[b]
    sb.ComponentTitle = ""; sb.TitleColor = [0, 0, 0]; sb.LabelColor = [0, 0, 0]; sb.TitleFontSize = 14; sb.LabelFontSize = 12; sb.ScalarBarLength = 0.3; sb.WindowLocation = "Any Location"; sb.Position = [0.82, 0.08]; sb.AutomaticLabelFormat = 0; sb.LabelFormat = "%-#.2f"; sb.RangeLabelFormat = "%-#.2f"
ua.RescaleTransferFunction(-0.15, 0.15); vm.RescaleTransferFunction(0.0, 0.3)
HideScalarBarIfNotNeeded(ua, v); [GetDisplayProperties(o, v).SetScalarBarVisibility(v, False) for o in secs + [la]]; dt.SetScalarBarVisibility(v, True)
F = pt(6)
def view(name):
    """camera presets: 'side' looks along the long-axis plane normal (device on the right), 'atrium' looks at the device face
    from the atrium, 'oblique' in between. In the Python Shell: view('side'); Render()"""
    d = dict(side=nz, atrium=[-x for x in N], oblique=[0.6 * nz[i] - 0.8 * N[i] for i in range(3)])[name]
    v.CameraFocalPoint = F; v.CameraPosition = [F[i] + 0.17 * d[i] for i in range(3)]; v.CameraViewUp = [0, 0, 1]; v.CameraViewAngle = 30
view("side"); SetActiveSource(tube); Render(v)
print("Device region loaded at t = %.2f s: streamlines seeded in front of the device. Tick sections / long-axis slice / stagnant blood in the Pipeline Browser. Camera: view('side'|'atrium'|'oblique')" % T_SHOW)
