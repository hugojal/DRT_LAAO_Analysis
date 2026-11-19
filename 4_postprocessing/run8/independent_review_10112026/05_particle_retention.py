# Independent massless-particle tracking on cached cell-centre velocity (IDW k=8, RK2, 4 substeps per 0.01 s)
# Seeds volume-weighted in regions; retention = fraction not exited through the mitral valve.
import numpy as np, pyvista as pv, glob, json
from scipy.spatial import cKDTree
R=r'C:/Users/hugoj/Desktop/UNI/3er/MOs/DRT_LAAO_Case3/4_postprocessing/'
OUT=R+'run8/independent_review_10112026/'
C=np.array([0.031326,-0.017721,0.016914]); N=np.array([0.626991,-0.520926,-0.579239]); N/=np.linalg.norm(N)
w=pv.read(OUT+'cache/la_wall_t2.63.vtp'); dev=pv.read(R+'paraview/device_analysis_model_m.stl')
_,cp=dev.find_closest_cell(w.points,return_closest_point=True); dwd=np.linalg.norm(w.points-cp,axis=1)
xw=w.points-C; axw=xw@N; latw=np.linalg.norm(xw-np.outer(axw,N),axis=1); patch=(dwd<1.5e-3)&(latw<16e-3)
tw=cKDTree(w.points); tp=cKDTree(w.points[patch])
files=sorted(glob.glob(OUT+'cache/step_*.npz'),key=lambda f: float(f.split('_')[-1][:-4]))
T=np.array([float(f.split('_')[-1][:-4]) for f in files])
cache={}
def field(i):
    if i not in cache:
        if len(cache)>3: cache.pop(min(cache))
        z=np.load(files[i]); x=z['xc'].astype(float); cache[i]=(cKDTree(x),z['vel'].astype(float),x[:,2].min(),x)
    return cache[i]
def vel(i,p):
    tr,v,_,_=field(i); d,j=tr.query(p,k=8); wgt=1/(d+1e-5)**2; return (v[j]*wgt[...,None]).sum(1)/wgt.sum(1)[:,None], d[:,0]
def regions(x):
    dw,_=tw.query(x); dp,_=tp.query(x); y=x-C; ax=y@N; lat=np.linalg.norm(y-np.outer(ax,N),axis=1)
    fr=(lat<16e-3)&(ax<axw[patch].max())
    return {'dev0-5':fr&(dp<5e-3),'dev0-10':fr&(dp<10e-3),'nearwall0-5_far(>30mm)':(dw<5e-3)&(dp>30e-3),
            'body(wall>10mm)':dw>10e-3,'LA':np.ones(len(x),bool)}
rng=np.random.default_rng(0); NS=600
def track(t0,nbeats):
    i0=int(np.argmin(abs(T-t0))); z=np.load(files[i0]); x=z['xc'].astype(float); v=z['vol'].astype(float); rg=regions(x)
    seeds={}; 
    for k,m in rg.items():
        idx=np.flatnonzero(m); pick=rng.choice(idx,NS,p=v[idx]/v[idx].sum()); seeds[k]=x[pick]+rng.normal(0,2e-4,(NS,3))
    names=list(seeds); P=np.vstack([seeds[k] for k in names]); lab=np.repeat(np.arange(len(names)),NS)
    alive=np.ones(len(P),bool); exit_t=np.full(len(P),np.nan); clamps=0
    iend=min(len(T)-1,i0+int(round(nbeats*87.5)))
    snap={}
    for i in range(i0,iend):
        a,b=i,i+1; dt=(T[b]-T[a])/4
        for s in range(4):
            f0=s/4; fm=(s+.5)/4
            def V(p,f):
                va,da=vel(a,p); vb,_=vel(b,p); return (1-f)*va+f*vb, da
            q=P[alive]; k1,_=V(q,f0); qm=q+0.5*dt*k1; k2,_=V(qm,fm); q=q+dt*k2
            _,dnear=vel(b,q); zmin=field(b)[2]
            out_mv=(q[:,2]<zmin+1.5e-3)&(np.hypot(q[:,0],q[:,1])<0.025)
            lost=(dnear>1.5e-3)&~out_mv
            if lost.any():   # pulled outside a wall by interpolation: clamp to nearest cell centre
                _,j=field(b)[0].query(q[lost]); q[lost]=field(b)[3][j]; clamps+=lost.sum()
            ia=np.flatnonzero(alive); P[ia]=q; exit_t[ia[out_mv]]=T[a]+(s+1)*dt; alive[ia[out_mv]]=False
        for nb in (1,2):
            if abs(T[b]-(T[i0]+nb*0.875))<0.006: snap[nb]=alive.copy()
    snap['end']=alive.copy()
    res={'t_release':float(T[i0]),'t_end':float(T[iend]),'seeds_per_region':NS,'clamps':int(clamps)}
    for nb,al in snap.items():
        res['retained_after_%s'%nb]={k:float(al[lab==j].mean()) for j,k in enumerate(names)}
    return res
out={'release_1.76_2beats':track(1.76,2),'release_2.63_1beat':track(2.63,1)}
# extra releases inside beat 4 / beat 3 at other phases to judge phase sensitivity
out['release_2.20_1beat']=track(2.20,1); out['release_3.00_0.5beat']=track(3.00,0.5)
json.dump(out,open(OUT+'particle_retention.json','w'),indent=1)
print(json.dumps(out,indent=1))
