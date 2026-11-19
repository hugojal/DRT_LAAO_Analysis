# TAWSS, OSI, ECAP, RRT from WSS component time series (beats 3 and 4); bands by distance to device STL
import numpy as np, pyvista as pv, glob, json
from scipy.spatial import cKDTree
R=r'C:/Users/hugoj/Desktop/UNI/3er/MOs/DRT_LAAO_Case3/4_postprocessing/'
OUT=R+'run8/independent_review_10112026/'
w=pv.read(OUT+'cache/la_wall_t2.63.vtp')
dev=pv.read(R+'paraview/device_analysis_model_m.stl')
_,cp=dev.find_closest_cell(w.points,return_closest_point=True); dd=np.linalg.norm(w.points-cp,axis=1)*1e3
files=sorted(glob.glob(OUT+'cache/step_*.npz'),key=lambda f: float(f.split('_')[-1][:-4]))
T=np.array([float(f.split('_')[-1][:-4]) for f in files])
W=[];Wm=[];dmx=[]
for f in files:
    z=np.load(f); dm,ii=cKDTree(z['wx']).query(w.points); dmx.append(np.percentile(dm,[50,99.9,100])); W.append(z['wss'][ii]); Wm.append(z['wssmag'][ii])
W=np.array(W).astype(float); Wm=np.array(Wm).astype(float); dmx=np.array(dmx)
print('per-step wall node mapping distance (m): median of medians',np.median(dmx[:,0]),'max 99.9pct',dmx[:,1].max(),'max',dmx[:,2].max())
print('consistency |components| vs magnitude: median rel diff', np.median(np.abs(np.linalg.norm(W,axis=2)-Wm)/(Wm+1e-9)))
ref=pv.read(R+'paraview/run8_wall_metrics.vtp')
area=w.compute_cell_sizes(length=False,volume=False)['Area']
bands=[(0,5),(5,10),(10,20),(20,40),(40,1e9)]
res={}
for b,(lo,hi) in {'beat3':(1.755,2.6251),'beat4':(2.625,3.5001)}.items():
    tb=(T>lo)&(T<hi); Wb=W[tb]
    tawss=np.linalg.norm(Wb,axis=2).mean(0); mv=np.linalg.norm(Wb.mean(0),axis=1)
    osi=0.5*(1-mv/tawss); ecap=osi/tawss; rrt=1/((1-2*osi)*tawss)
    lowfrac=(np.linalg.norm(Wb,axis=2)<0.4).mean(0)    # extra: fraction of beat with |WSS|<0.4 Pa
    m=w.copy(); m.clear_data()
    for n,a in dict(TAWSS=tawss,OSI=osi,ECAP=ecap,RRT=rrt,LOWF=lowfrac).items(): m.point_data[n]=a
    c=m.point_data_to_cell_data(); cc=c.cell_centers().points
    _,cpc=dev.find_closest_cell(cc,return_closest_point=True); dc=np.linalg.norm(cc-cpc,axis=1)*1e3
    res[b]={'n_steps':int(tb.sum())}
    for lo2,hi2 in bands:
        k=(dc>=lo2)&(dc<hi2); A=area[k]
        r={n:float(np.sum(A*c.cell_data[n][k])/A.sum()) for n in ['TAWSS','OSI','ECAP','RRT','LOWF']}
        r['median_TAWSS']=float(np.median(c.cell_data['TAWSS'][k])); r['median_ECAP']=float(np.median(c.cell_data['ECAP'][k]))
        r['area_cm2']=float(A.sum()*1e4)
        r['areafrac_TAWSS_lt0.4']=float(A[c.cell_data['TAWSS'][k]<0.4].sum()/A.sum())
        r['areafrac_ECAP_gt1.4']=float(A[c.cell_data['ECAP'][k]>1.4].sum()/A.sum())
        r['areafrac_ECAP_gt3']=float(A[c.cell_data['ECAP'][k]>3].sum()/A.sum())
        r['areafrac_OSI_gt0.3']=float(A[c.cell_data['OSI'][k]>0.3].sum()/A.sum())
        res[b]['%g-%g mm'%(lo2,hi2 if hi2<1e8 else 999)]=r
    # whole wall and wall excluding <20 mm
    for nm,k in {'wall_all':dc>=0,'wall_>=20mm':dc>=20}.items():
        A=area[k]; res[b][nm]={n:float(np.sum(A*c.cell_data[n][k])/A.sum()) for n in ['TAWSS','OSI','ECAP','RRT','LOWF']}
        res[b][nm]['median_TAWSS']=float(np.median(c.cell_data['TAWSS'][k])); res[b][nm]['median_ECAP']=float(np.median(c.cell_data['ECAP'][k]))
        res[b][nm]['areafrac_ECAP_gt1.4']=float(A[c.cell_data['ECAP'][k]>1.4].sum()/A.sum())
        res[b][nm]['areafrac_TAWSS_lt0.4']=float(A[c.cell_data['TAWSS'][k]<0.4].sum()/A.sum())
    # percentile rank of device-face (0-5 mm) median TAWSS among all wall cells
    k=dc<5
    res[b]['pct_wall_cells_with_TAWSS_below_dev0-5_median']=float((c.cell_data['TAWSS']<np.median(c.cell_data['TAWSS'][k])).mean())
    res[b]['pct_wall_cells_with_ECAP_below_dev0-5_median']=float((c.cell_data['ECAP']<np.median(c.cell_data['ECAP'][k])).mean())
    if b=='beat4':
        m.point_data['dist_dev_mm']=dd; m.save(OUT+'wall_metrics_recomputed_beat4.vtp')
        print('check vs author vtp (beat4): median |rel diff| TAWSS',np.median(np.abs(tawss-ref['TAWSS_Pa'])/ref['TAWSS_Pa']),
              'OSI max abs diff',np.abs(osi-ref['OSI']).max(),'dist max diff mm',np.abs(dd-ref['dist_to_device_mm']).max())
json.dump(res,open(OUT+'wall_metrics.json','w'),indent=1)
for b in res:
    print('==',b)
    for k,v in res[b].items(): print(' ',k, v if not isinstance(v,dict) else {n:round(x,4) for n,x in v.items()})
