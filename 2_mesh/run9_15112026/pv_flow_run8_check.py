"""Does the natural (non-extruded) vein shape disturb the inflow? Run8 solution, planes across each PV at several depths
from the cap: axial-velocity uniformity (CV, momentum factor beta) and secondary flow, at 3 steps of the analysed beat
(peak total PV inflow, and two others). usage: python pv_flow_run8_check.py"""
import os, ast, json, csv, numpy as np, pyvista as pv, vtk
ROOT="C:/Users/hugoj/Desktop/UNI/3er/MOs/DRT_LAAO_Case3"; RES=ROOT+"/3_simulation/results/run8_4cycles"
caps=json.load(open(ROOT+"/2_mesh/run8_07112026/caps_model_frame.json"))[1:]
rows=list(csv.DictReader(open(RES+"/flows.csv"))); tot={}
for r in rows:
    k=int(r["step"])
    if 263<=k<=350: tot[k]=sum(ast.literal_eval(r[f"mf_pv_{i}"])[0] for i in (1,2,3,4))
kpk=max(tot,key=tot.get); ks=[kpk-12, kpk, kpk+12]; print("steps",ks,[round(tot[k]*1000,2) for k in ks],"g/s")
depths=[1,4,7,10,13,16]
for k in ks:
    rd=vtk.vtkEnSightGoldBinaryReader(); rd.SetCaseFileName(RES+f"/step_{k:03d}.encas"); rd.Update()
    f=pv.wrap(rd.GetOutput().GetBlock(0)); print(f"\nstep {k}  (t in beat {k*0.01-2.625:.2f} s)  total PV inflow {tot[k]*1000:.2f} g/s")
    for cp in caps:
        c=np.array(cp["centre_mm"])/1000; a=np.array(cp["normal"]); a/=np.linalg.norm(a); rcap=cp["radius_mm"]/1000
        print(f" {cp['vein']:5s} depth(mm)  Q(g/s)  CV(u)  beta   sec/u  back%")
        for t in depths:
            o=c-t/1000*a; sl=f.slice(normal=a,origin=o)
            if sl.n_points==0: continue
            P=np.asarray(sl.points); d=np.linalg.norm((P-o)-np.outer((P-o)@a,a),axis=1)
            sl=sl.connectivity(extraction_mode="closest",closest_point=tuple(o))
            sl=sl.compute_cell_sizes(length=False,area=True,volume=False).point_data_to_cell_data()
            A=sl["Area"]; v=sl["Velocity"]; u=-(v@a); vp=v+np.outer(u,a)         # inflow = -a
            Um=(u*A).sum()/A.sum(); cv=np.sqrt(((u-Um)**2*A).sum()/A.sum())/abs(Um); beta=(u**2*A).sum()/A.sum()/Um**2
            sec=np.sqrt((np.linalg.norm(vp,axis=1)**2*A).sum()/A.sum())/abs(Um); back=A[u<0].sum()/A.sum()*100
            print(f"   {t:5.0f} {(u*A).sum()*1000*1060:9.2f} {cv:6.2f} {beta:6.2f} {sec:6.2f} {back:5.1f}")
