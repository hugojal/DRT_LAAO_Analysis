"""Shape of each PV cross-section along its axis (run9 surface, model frame): area, hydraulic diameter, circularity, axis ratio."""
import json, numpy as np, pyvista as pv
H="../run8_07112026/"; m=pv.read(__import__("os").environ.get("STL","HugoJal_Case3_run9_15112026.stl")); caps=json.load(open(H+"caps_model_frame.json"))
out={}
for cp in caps[1:]:
    c=np.array(cp["centre_mm"]); a=np.array(cp["normal"]); a/=np.linalg.norm(a); rows=[]
    b1=np.cross(a,[0,0,1.]); b1/=np.linalg.norm(b1); b2=np.cross(a,b1)
    for t in np.arange(0.5,26,1.0):
        sl=m.slice(normal=a,origin=c-t*a).strip()
        best=None
        for i in range(sl.n_cells):
            Q=sl.get_cell(i).points; g=Q.mean(0); d=np.linalg.norm(g-(c-t*a))
            if best is None or d<best[0]: best=(d,Q)
        Q=best[1]; q=np.c_[(Q-c)@b1,(Q-c)@b2]; x,y=q[:,0],q[:,1]
        A=abs((x*np.roll(y,-1)-np.roll(x,-1)*y).sum())/2; P=np.linalg.norm(q-np.roll(q,-1,0),axis=1).sum()
        g=q.mean(0); ang=np.linspace(0,np.pi,90,endpoint=False); w=[np.ptp(q@[np.cos(t_),np.sin(t_)]) for t_ in ang]
        rows.append(dict(t=float(t),A=A,Dh=4*A/P,circ=4*np.pi*A/P**2,feret=max(w)/min(w),off=float(np.linalg.norm(g-np.zeros(2)))))
    out[cp["name"]]=rows
    print(cp["name"],"r_cap",cp["radius_mm"],"A_cap",round(np.pi*cp["radius_mm"]**2))
    print(" t(mm)  A   Dh/Dcap  circ  feret")
    for r in rows[::2]: print(f"{r['t']:5.1f} {r['A']:6.0f} {r['Dh']/(2*cp['radius_mm']):6.2f} {r['circ']:6.3f} {r['feret']:5.2f}")
json.dump(out,open("pv_section_shape.json","w"),indent=1)
