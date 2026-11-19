# Extras: Zhong-style 40 mm-diameter sphere ROI at the ostium; TAWSS<0.36 Pa area fraction; flow directional coherence |<u>|/<|u|>
import numpy as np, pyvista as pv, glob, json
from scipy.spatial import cKDTree
R=r'C:/Users/hugoj/Desktop/UNI/3er/MOs/DRT_LAAO_Case3/4_postprocessing/'
OUT=R+'run9/independent_review_15112026/'
C=np.array([0.031326,-0.017721,0.016914]); N=np.array([0.626991,-0.520926,-0.579239]); N/=np.linalg.norm(N)
w=pv.read(OUT+'cache/la_wall_t2.63.vtp'); dev=pv.read(R+'paraview/device_analysis_model_m.stl')
_,cp=dev.find_closest_cell(w.points,return_closest_point=True); dwd=np.linalg.norm(w.points-cp,axis=1)
xw=w.points-C; axw=xw@N; latw=np.linalg.norm(xw-np.outer(axw,N),axis=1); patch=(dwd<1.5e-3)&(latw<16e-3)
O=w.points[patch].mean(0); print('ostium/device-face centroid',O)
tw=cKDTree(w.points); tp=cKDTree(w.points[patch])
files=sorted(glob.glob(OUT+'cache/step_*.npz'),key=lambda f: float(f.split('_')[-1][:-4]))
T=np.array([float(f.split('_')[-1][:-4]) for f in files])
res={}
for b,(lo,hi) in {'beat3':(1.755,2.6251),'beat4':(2.625,3.5001)}.items():
    fb=[f for f,t in zip(files,T) if lo<t<hi]
    x0=np.load(fb[0])['xc'].astype(float); v0=np.load(fb[0])['vol'].astype(float)
    dw,_=tw.query(x0); dp,_=tp.query(x0); y=x0-C; ax=y@N; lat=np.linalg.norm(y-np.outer(ax,N),axis=1)
    fr=(lat<16e-3)&(ax<axw[patch].max())
    rg={'dev0-5':fr&(dp<5e-3),'dev0-10':fr&(dp<10e-3),'nearwall0-5_far(>30mm)':(dw<5e-3)&(dp>30e-3),'body(wall>10mm)':dw>10e-3,
        'sphere40mm_ostium':np.linalg.norm(x0-O,axis=1)<20e-3,'LA':np.ones(len(x0),bool)}
    U=np.zeros((len(x0),3)); S=np.zeros(len(x0)); An=np.zeros(len(x0)); towards=np.zeros(len(x0))
    for f in fb:
        z=np.load(f); _,ii=cKDTree(z['xc']).query(x0); u=z['vel'][ii].astype(float)
        U+=u; S+=np.linalg.norm(u,axis=1); towards+=(u@N>0)
    U/=len(fb); S/=len(fb); towards/=len(fb); coh=np.linalg.norm(U,axis=1)/S
    res[b]={}
    for k,m in rg.items():
        res[b][k]={'vol_mL':float(v0[m].sum()*1e6),'beatmean_speed':float(np.sum(v0[m]*S[m])/v0[m].sum()),
                   'coherence_|<u>|/<|u|>':float(np.sum(v0[m]*coh[m])/v0[m].sum()),
                   'time_frac_flow_towards_device(u.N>0)':float(np.sum(v0[m]*towards[m])/v0[m].sum())}
    # wall: Zhong-style thresholds
    T_=[t for t in T if lo<t<hi]
json.dump(res,open(OUT+'extra_metrics.json','w'),indent=1)
for b in res:
    print('==',b)
    for k,v in res[b].items(): print(' %-24s'%k,{n:round(x,4) for n,x in v.items()})
# wall threshold 0.36 Pa (Zhong 2023, from arterial monocyte-adhesion literature) on recomputed beat-4 TAWSS
m=pv.read(OUT+'wall_metrics_recomputed_beat4.vtp'); c=m.point_data_to_cell_data(); a=c.compute_cell_sizes(length=False,volume=False)['Area']
cc=c.cell_centers().points; _,cpc=dev.find_closest_cell(cc,return_closest_point=True); dc=np.linalg.norm(cc-cpc,axis=1)*1e3
sph=np.linalg.norm(cc-O,axis=1)<20e-3
for nm,k in {'0-5mm':dc<5,'sphere40mm_ostium':sph,'>=20mm':dc>=20,'all':dc>=0}.items():
    A=a[k]; print('wall',nm,'area cm2 %.1f'%(A.sum()*1e4),'TAWSS<0.36 frac %.3f'%(A[c['TAWSS'][k]<0.36].sum()/A.sum()),
      'ECAP>1.4 frac %.4f'%(A[c['ECAP'][k]>1.4].sum()/A.sum()),'mean TAWSS %.3f'%(np.sum(A*c['TAWSS'][k])/A.sum()),
      'mean ECAP %.3f'%(np.sum(A*c['ECAP'][k])/A.sum()),'max ECAP %.2f'%c['ECAP'][k].max(),'ECAP>0.5 frac %.3f'%(A[c['ECAP'][k]>0.5].sum()/A.sum()))
