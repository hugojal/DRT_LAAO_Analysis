import numpy as np, sys
from paraview.simple import *
from paraview import servermanager as sm
from vtkmodules.util.numpy_support import vtk_to_numpy, numpy_to_vtk
from vtkmodules.vtkCommonDataModel import vtkPolyData, vtkCellArray
from vtkmodules.vtkCommonCore import vtkPoints
R="C:/Users/hugoj/Desktop/UNI/3er/MOs/DRT_LAAO_Case3"
C=np.array([0.031326,-0.017721,0.016914]); N=np.array([0.626991,-0.520926,-0.579239])
r=EnSightReader(CaseFileName=R+"/3_simulation/results/run8_4cycles/all_steps.encas")
f=MergeBlocks(Input=ExtractBlock(Input=r,Selectors=["/Root/fluid-1"]))
allt=list(r.TimestepValues)
def run(T0, mode):
    i0=min(range(len(allt)),key=lambda i:abs(allt[i]-T0)); ts=allt[i0:i0+88]
    f.UpdatePipeline(ts[0]); P=vtk_to_numpy(sm.Fetch(f).GetPoints().GetData())
    rel=P-C; ax=-(rel@N); rad=np.linalg.norm(rel+np.outer(ax,N),axis=1)
    if mode=="slab": m=(ax>-0.002)&(ax<0.005)&(rad<0.016)
    else: m=np.linalg.norm(P-(C-0.005*N),axis=1)<0.008
    S=P[m]; S=S[np.random.default_rng(0).permutation(len(S))[:400]]
    if mode.startswith("uni"):
        g=np.random.default_rng(1); u=g.uniform(-1,1,(20000,3))
        e2=np.cross(N,[0,0,1.0]); e2/=np.linalg.norm(e2); e3=np.cross(N,e2)
        if mode=="uni_slab":
            a=g.uniform(-0.002,0.005,20000); rr=0.016*np.sqrt(g.uniform(0,1,20000)); th=g.uniform(0,2*np.pi,20000)
            Q=C-np.outer(a,N)+np.outer(rr*np.cos(th),e2)+np.outer(rr*np.sin(th),e3)
        else:
            u=u[np.linalg.norm(u,axis=1)<=1]; Q=(C-0.005*N)+0.008*u
        from vtkmodules.vtkCommonDataModel import vtkCellLocator
        loc=vtkCellLocator(); fd=sm.Fetch(f); loc.SetDataSet(fd); loc.BuildLocator()
        ins=np.array([loc.FindCell(list(q))>=0 for q in Q[:6000]]); S=Q[:6000][ins][:400]
    pd=vtkPolyData(); pts=vtkPoints(); pts.SetData(numpy_to_vtk(np.ascontiguousarray(S),deep=1)); pd.SetPoints(pts); va=vtkCellArray()
    for i in range(len(S)): va.InsertNextCell(1); va.InsertCellPoint(i)
    pd.SetVerts(va); src=PVTrivialProducer(); src.GetClientSideObject().SetOutput(pd)
    sub=ExtractTimeSteps(Input=f); sub.SelectionMode="Select Time Steps"; sub.TimeStepIndices=list(range(i0,len(allt)))
    pt=ParticleTracer(Input=sub,SeedSource=src); pt.SelectInputVectors=["POINTS","Velocity"]; pt.StaticSeeds=1; pt.ForceReinjectionEveryNSteps=0; pt.MeshOverTime="Different"
    n=[]
    for t in ts: pt.UpdatePipeline(t); n.append(sm.Fetch(pt).GetNumberOfPoints())
    print(mode,T0,"seeds",len(S),"start",n[0],"end",n[-1],"retained %.0f%%"%(100*n[-1]/n[0]),"min",min(n),flush=True); Delete(pt)
for T0 in (1.76,2.63):
    for mode in ("uni_slab","uni_sphere"): run(T0,mode)
