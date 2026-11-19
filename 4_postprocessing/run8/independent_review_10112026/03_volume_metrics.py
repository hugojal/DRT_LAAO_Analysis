# Volume metrics near device vs reference regions, beats 3 and 4, from per-step cell dumps
import numpy as np, pyvista as pv, glob, json
from scipy.spatial import cKDTree
R=r'C:/Users/hugoj/Desktop/UNI/3er/MOs/DRT_LAAO_Case3/4_postprocessing/'
OUT=R+'run8/independent_review_10112026/'
C=np.array([0.031326,-0.017721,0.016914]); N=np.array([0.626991,-0.520926,-0.579239]); N/=np.linalg.norm(N)
w=pv.read(OUT+'cache/la_wall_t2.63.vtp')
dev=pv.read(R+'paraview/device_analysis_model_m.stl')
_,cp=dev.find_closest_cell(w.points,return_closest_point=True)
dwall_dev=np.linalg.norm(w.points-cp,axis=1)
xw=w.points-C; axw=xw@N; latw=np.linalg.norm(xw-np.outer(axw,N),axis=1)
patch=(dwall_dev<1.5e-3)&(latw<16e-3)
print('device-face patch nodes',patch.sum(),'ax mm',np.round(np.percentile(axw[patch]*1e3,[0,50,100]),2))
tw=cKDTree(w.points); tp=cKDTree(w.points[patch])
files=sorted(glob.glob(OUT+'cache/step_*.npz'),key=lambda f: float(f.split('_')[-1][:-4]))
s0=np.load(files[0]); xc0=s0['xc'].astype(float)
dw,_=tw.query(xc0); dp,_=tp.query(xc0)
x=xc0-C; ax=x@N; lat=np.linalg.norm(x-np.outer(ax,N),axis=1)
front=(lat<16e-3)&(ax<axw[patch].max())
reg={'dev0-5':front&(dp<5e-3),'dev0-10':front&(dp<10e-3),
     'nearwall0-5_far(>30mm)':(dw<5e-3)&(dp>30e-3),'body(wall>10mm)':dw>10e-3,'LA':np.ones(len(xc0),bool)}
for k,m in reg.items(): print(k,'cells',m.sum(),'vol mL',s0['vol'][m].sum()*1e6)
def regions(xc):
    dw,_=tw.query(xc); dp,_=tp.query(xc); x=xc-C; ax=x@N; lat=np.linalg.norm(x-np.outer(ax,N),axis=1)
    fr=(lat<16e-3)&(ax<axw[patch].max())
    return {'dev0-5':fr&(dp<5e-3),'dev0-10':fr&(dp<10e-3),'nearwall0-5_far(>30mm)':(dw<5e-3)&(dp>30e-3),'body(wall>10mm)':dw>10e-3,'LA':np.ones(len(xc),bool)}
rows=[]; spd_all=[]; ncell=[]
for f in files:
    s=np.load(f); t=float(f.split('_')[-1][:-4]); xc=s['xc'].astype(float); rg=regions(xc); ncell.append(len(xc))
    v=s['vol'].astype(float); sp=np.linalg.norm(s['vel'],axis=1).astype(float); q=s['q'].astype(float); vo=s['vort'].astype(float)
    row=[t]
    for k,m in rg.items():
        vm=v[m]; row+= [np.sum(vm*sp[m])/vm.sum(), np.sum(vm*(sp[m]<0.1))/vm.sum(), np.sum(vm*(sp[m]<0.05))/vm.sum(),
                        np.sum(vm*(q[m]>0))/vm.sum(), np.sum(vm*vo[m])/vm.sum()]
    rows.append(row)
    _,ii=cKDTree(xc).query(xc0); spd_all.append(sp[ii].astype(np.float32))   # nearest-cell resample onto fixed t=1.76 centroids
print('cell count range',min(ncell),max(ncell))
A=np.array(rows); spd_all=np.array(spd_all); T=A[:,0]
names=['mean_speed','frac_lt0.10','frac_lt0.05','frac_Qpos','mean_vort']
res={}
for b,(lo,hi) in {'beat3':(1.755,2.6251),'beat4':(2.625,3.5001)}.items():
    tb=(T>lo)&(T<hi); res[b]={}
    for i,k in enumerate(reg):
        res[b][k]={n:float(A[tb,1+5*i+j].mean()) for j,n in enumerate(names)}
        res[b][k]['peak_mean_speed']=float(A[tb,1+5*i].max()); res[b][k]['min_mean_speed']=float(A[tb,1+5*i].min())
    # cell-wise beat-mean speed and fraction of beat below 0.1 m/s
    ms=spd_all[tb].mean(0); ft=(spd_all[tb]<0.1).mean(0); v=s0['vol'].astype(float)
    for k,m in reg.items():
        res[b][k]['frac_vol_beatmean_lt0.10']=float(np.sum(v[m]*(ms[m]<0.1))/v[m].sum())
        res[b][k]['frac_vol_beatmean_lt0.05']=float(np.sum(v[m]*(ms[m]<0.05))/v[m].sum())
        res[b][k]['vol_mean_time_frac_lt0.10']=float(np.sum(v[m]*ft[m])/v[m].sum())
        res[b][k]['vol_frac_lt0.10_for_>80pct_beat']=float(np.sum(v[m]*(ft[m]>0.8))/v[m].sum())
        res[b][k]['n_steps']=int(tb.sum())
np.save(OUT+'volume_timeseries.npy',A)
json.dump(res,open(OUT+'volume_metrics.json','w'),indent=1)
for b in res:
    print('==',b)
    for k in res[b]: print(' %-24s'%k, {n:round(vv,4) for n,vv in res[b][k].items()})
