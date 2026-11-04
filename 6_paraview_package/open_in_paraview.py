"""Opens the Case 3 left-atrium simulation (run6) in ParaView with a ready-made pipeline.
ParaView GUI: View > Python Shell > Run Script > this file   (or: paraview --script=open_in_paraview.py from this folder)
Pipeline (toggle the eye icons; press Play to run the heartbeat, t = 2.63-3.50 s):
  simulation      run6_last_beat.encas: velocity, pressure, vorticity, Q-criterion, wall shear stress per time step
  fluid / la_wall the fluid volume and the atrial wall (wall shown transparent)
  streamlines     streamlines seeded at the four pulmonary-vein inlets, coloured by velocity
  long-axis slice velocity on the plane through the mitral valve axis (z) and the device
  vortices        Q-criterion = 500 1/s2 (Morales et al. 2025, arXiv:2505.09746)
  wall metrics    TAWSS, OSI, ECAP, RRT over the last heartbeat (choose the array in 'Coloring'); dist_to_device_mm
  device          wire frame from the gamma-transformed CT, U-Net (nnInteractive) segmentation and manual mask (hidden by default)
Frame: metres; z = mitral valve axis (+z from the valve into the atrium), origin = centre of the mitral annulus.
The 'Q_Criterion_Normalized' array is Fluent's q-criterion in 1/s2 (only the EnSight label says 'normalized')."""
import os, inspect
from paraview.simple import *
try: HERE = os.path.dirname(os.path.abspath(__file__))
except NameError: HERE = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
if not os.path.exists(os.path.join(HERE, "simulation")): HERE = os.getcwd()
P = lambda *a: os.path.join(HERE, *a).replace("\\", "/")
T_PEAK = 3.06
DEVICE_C = [0.0332, -0.0191, 0.0150]                                          # device centre in this frame (m)

sim = EnSightReader(registrationName="simulation", CaseFileName=P("simulation", "run6_last_beat.encas"))
blk = lambda names, nm: MergeBlocks(registrationName=nm, Input=ExtractBlock(Input=sim, Selectors=["/Root/" + n for n in names]))
fluid = blk(["fluid-1"], "fluid"); wall = blk(["la_wall"], "la_wall"); pvs = blk(["pv_1", "pv_2", "pv_3", "pv_4"], "pv_inlets")
st = StreamTracerWithCustomSource(registrationName="streamlines", Input=fluid, SeedSource=pvs)
st.Vectors = ["POINTS", "Velocity"]; st.MaximumStreamlineLength = 0.4; st.IntegrationDirection = "BOTH"
tube = Tube(registrationName="streamline tubes", Input=st); tube.Radius = 0.00028
n = [-DEVICE_C[1], DEVICE_C[0], 0.0]; ln = (n[0] ** 2 + n[1] ** 2) ** 0.5; n = [x / ln for x in n]
sl = Slice(registrationName="long-axis slice", Input=fluid); sl.SliceType = "Plane"; sl.SliceType.Origin = DEVICE_C; sl.SliceType.Normal = n
q = Contour(registrationName="vortices Q=500", Input=fluid); q.ContourBy = ["POINTS", "Q_Criterion_Normalized"]; q.Isosurfaces = [500.0]; q.ComputeScalars = 0
wm = XMLPolyDataReader(registrationName="wall metrics (last beat)", FileName=[P("surfaces", "wall_metrics_last_beat.vtp")])
wire = STLReader(registrationName="device wire frame", FileNames=[P("surfaces", "device_wire_frame.stl")])
man = STLReader(registrationName="device manual mask", FileNames=[P("surfaces", "device_manual_mask.stl")])
unet = STLReader(registrationName="device U-Net", FileNames=[P("surfaces", "device_unet.stl")])

v = GetActiveViewOrCreate("RenderView"); v.Background = [1, 1, 1]; v.UseColorPaletteForBackground = 0
anim = GetAnimationScene(); anim.UpdateAnimationUsingDataTimeSteps(); anim.AnimationTime = T_PEAK
vel = GetColorTransferFunction("Velocity_Magnitude"); vel.ApplyPreset("Turbo", True); vel.RescaleTransferFunction(0.0, 0.6); vel.AutomaticRescaleRangeMode = "Never"
dw = Show(wall, v); dw.ColorArrayName = ["POINTS", ""]; dw.DiffuseColor = [0.8, 0.8, 0.83]; dw.Opacity = 0.15
dt = Show(tube, v); ColorBy(dt, ("POINTS", "Velocity_Magnitude")); dt.SetScalarBarVisibility(v, True)
ds = Show(sl, v); ColorBy(ds, ("POINTS", "Velocity_Magnitude")); Hide(sl, v)
dq = Show(q, v); ColorBy(dq, ("POINTS", "Velocity_Magnitude")); Hide(q, v)
de = Show(wm, v); ColorBy(de, ("POINTS", "ECAP_1_per_Pa")); ecap = GetColorTransferFunction("ECAP_1_per_Pa"); ecap.ApplyPreset("Plasma", True)
ecap.RescaleTransferFunction(0.1, 10.0); ecap.MapControlPointsToLogSpace(); ecap.UseLogScale = 1; ecap.AutomaticRescaleRangeMode = "Never"; Hide(wm, v)
for src, col in ((wire, [0.85, 0.6, 0.15]), (man, [0.85, 0.6, 0.15]), (unet, [0.8, 0.3, 0.8])):
    d = Show(src, v); d.ColorArrayName = ["POINTS", ""]; d.DiffuseColor = col; Hide(src, v)
v.CameraPosition = [0.02, -0.25, 0.06]; v.CameraFocalPoint = [0.005, -0.01, 0.035]; v.CameraViewUp = [0, 0, 1]; ResetCamera(v)
SetActiveSource(tube); Render(v)
print("Loaded run6 (last heartbeat). Shown: streamlines at t = %.2f s. Other items are in the Pipeline Browser (eye icons)." % T_PEAK)
