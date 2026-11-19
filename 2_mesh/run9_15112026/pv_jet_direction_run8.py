"""Run8, peak inflow step 307: angle between the flux-weighted velocity vector and the extension axis, across each vein."""
import json, numpy as np, pyvista as pv, vtk
ROOT="C:/Users/hugoj/Desktop/UNI/3er/MOs/DRT_LAAO_Case3"; RES=ROOT+"/3_simulation/results/run8_4cycles"
caps=json.load(open(ROOT+"/2_mesh/run8_07112026/caps_model_frame.json"))[1:]
rd=vtk.vtkEnSightGoldBinaryReader(); rd.SetCaseFileName(RES+"/step_307.encas"); rd.Update(); f=pv.wrap(rd.GetOutput().GetBlock(0))
for cp in caps:
    c=np.array(cp["centre_mm"])/1000; a=np.array(cp["normal"]); a/=np.linalg.norm(a); out=[]
    for t in (1,5,8,10,12):
        o=c-t/1000*a; sl=f.slice(normal=a,origin=o).connectivity(extraction_mode="closest",closest_point=tuple(o)).compute_cell_sizes(length=False,area=True,volume=False).point_data_to_cell_data()
        A=sl["Area"]; v=sl["Velocity"]; u=-(v@a); Vm=((v*A[:,None]).sum(0)/A.sum()); ang=np.degrees(np.arccos(np.clip(Vm@(-a)/np.linalg.norm(Vm),-1,1)))
        out.append(f"{t} mm: {ang:4.1f} deg")
    print(cp["vein"].ljust(5), " | ".join(out))
