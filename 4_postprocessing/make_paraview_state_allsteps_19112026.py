import os
from paraview.simple import *
HERE=r"C:/Users/hugoj/Desktop/UNI/3er/MOs/DRT_LAAO_Case3/3_simulation/results/run9_4cycles"; P=lambda *a: os.path.join(HERE,*a).replace("\\","/")
sim=EnSightReader(registrationName="simulation",CaseFileName=[P("all_steps.encas")])
blk=lambda names,nm: MergeBlocks(registrationName=nm,Input=ExtractBlock(Input=sim,Selectors=["/Root/"+n for n in names]))
fluid=blk(["fluid-1"],"fluid"); wall=blk(["la_wall"],"la_wall"); pvs=blk(["pv_1","pv_2","pv_3","pv_4"],"pv_inlets")
st=StreamTracerWithCustomSource(registrationName="streamlines",Input=fluid,SeedSource=pvs); st.Vectors=["POINTS","Velocity"]; st.MaximumStreamlineLength=0.4
sl=Slice(registrationName="slice",Input=fluid); sl.SliceType="Plane"; sl.SliceType.Origin=[0.0332,-0.0191,0.015]; sl.SliceType.Normal=[0.4,0.917,0]
q=Contour(registrationName="Q-criterion",Input=fluid); q.ContourBy=["POINTS","Q_Criterion_Normalized"]; q.Isosurfaces=[500.0]
v=GetActiveViewOrCreate("RenderView"); v.Background=[1,1,1]; v.UseColorPaletteForBackground=0
a=GetAnimationScene(); a.UpdateAnimationUsingDataTimeSteps(); a.AnimationTime=3.06
lut=GetColorTransferFunction("Velocity_Magnitude"); lut.ApplyPreset("Turbo",True); lut.RescaleTransferFunction(0,0.6); lut.AutomaticRescaleRangeMode="Never"
w=Show(wall,v); ColorBy(w,("POINTS","Wall_Shear_Stress")); w.Opacity=0.3; Hide(wall,v)
d=Show(st,v); ColorBy(d,("POINTS","Velocity_Magnitude")); d.SetScalarBarVisibility(v,True)
Show(sl,v); ColorBy(GetDisplayProperties(sl,v),("POINTS","Velocity_Magnitude")); Hide(sl,v)
Show(q,v); ColorBy(GetDisplayProperties(q,v),("POINTS","Velocity_Magnitude")); Hide(q,v)
dw=Show(wall,v); dw.ColorArrayName=["POINTS",""]; dw.DiffuseColor=[.8,.8,.83]; dw.Opacity=0.15
v.CameraPosition=[0.02,-0.25,0.06]; v.CameraFocalPoint=[0.005,-0.01,0.035]; v.CameraViewUp=[0,0,1]; ResetCamera(v); Render(v)
SaveState(r"C:/Users/hugoj/Desktop/UNI/3er/MOs/DRT_LAAO_Case3/6_paraview_basic_18112026/post_process_allsteps.pvsm")
