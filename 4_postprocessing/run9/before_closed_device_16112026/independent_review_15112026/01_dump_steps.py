# pvbatch: dump per-step fluid cell data and wall WSS for beats 3 and 4 to npz (float32)
import sys, os, numpy as np
from paraview.simple import *
from paraview import servermanager as sm
from vtk.util.numpy_support import vtk_to_numpy as v2n
ROOT=r'C:/Users/hugoj/Desktop/UNI/3er/MOs/DRT_LAAO_Case3'
OUT=ROOT+'/4_postprocessing/run9/independent_review_15112026/cache'
r=EnSightReader(CaseFileName=ROOT+'/3_simulation/results/run9_4cycles/all_steps.encas')
times=list(r.TimestepValues)
sel=[t for t in times if t>1.755]   # beats 3 and 4 (1.76..3.50)
fl=ExtractBlock(Input=r); fl.Selectors=['/Root/fluid-1']
flm=MergeBlocks(Input=fl)
p2c=PointDatatoCellData(Input=flm); p2c.PassPointData=0
cs=CellSize(Input=p2c); cs.ComputeVolume=1; cs.ComputeArea=0; cs.ComputeLength=0; cs.ComputeVertexCount=0
cc=CellCenters(Input=cs); cc.VertexCells=0
wl=ExtractBlock(Input=r); wl.Selectors=['/Root/la_wall']
wlm=MergeBlocks(Input=wl)
wlp=CellSize(Input=wlm); wlp.ComputeArea=1; wlp.ComputeVolume=0; wlp.ComputeLength=0; wlp.ComputeVertexCount=0
wlc=CellCenters(Input=wlp)
for t in sel:
    fn=OUT+'/step_%.2f.npz'%t
    if os.path.exists(fn): continue
    cc.UpdatePipeline(t); d=sm.Fetch(cc)
    pd=d.GetPointData()
    g=lambda n: v2n(pd.GetArray(n)).astype(np.float32)
    # wall: point data on wall nodes (WSS components) + point coords + cell areas via centres
    wlm.UpdatePipeline(t); w=sm.Fetch(wlm); wp=w.GetPointData()
    wlc.UpdatePipeline(t); wc=sm.Fetch(wlc)
    np.savez(fn, xc=v2n(d.GetPoints().GetData()).astype(np.float32), vol=g('Volume'),
             vel=g('Velocity'), q=g('Q_Criterion_Normalized'), vort=g('Vorticity_Magnitude'),
             l2=g('Lambda_2_Criterion'),
             wx=v2n(w.GetPoints().GetData()).astype(np.float32),
             wss=np.c_[v2n(wp.GetArray('X_Wall_Shear_Stress')),v2n(wp.GetArray('Y_Wall_Shear_Stress')),v2n(wp.GetArray('Z_Wall_Shear_Stress'))].astype(np.float32),
             wssmag=v2n(wp.GetArray('Wall_Shear_Stress')).astype(np.float32),
             wcx=v2n(wc.GetPoints().GetData()).astype(np.float32), warea=v2n(wc.GetPointData().GetArray('Area')).astype(np.float32))
    print(t, d.GetNumberOfPoints(), w.GetNumberOfPoints(), flush=True)
