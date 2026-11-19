import sys, json, numpy as np, pyvista as pv
from PIL import Image
H="../run8_07112026/"; caps=json.load(open(H+"caps_model_frame.json"))[1:]; files=sys.argv[1:3]; out=sys.argv[3]
tiles=[]
for f in files:
    m=pv.read(f)
    for cp in caps:
        c=np.array(cp["centre_mm"]); a=np.array(cp["normal"]); a/=np.linalg.norm(a); side=np.cross(a,[0,0,1.]); side/=np.linalg.norm(side)
        p=pv.Plotter(off_screen=True,window_size=(420,330)); p.add_mesh(m,color="lightgray",smooth_shading=True)
        fp=c-9*a; p.camera.focal_point=fp; p.camera.position=fp+side*60; p.camera.up=np.cross(side,a) if False else (0,0,1)
        p.camera.parallel_projection=True; p.camera.parallel_scale=17
        img=p.screenshot(); p.close(); tiles.append(Image.fromarray(img))
W=Image.new("RGB",(420*4,330*len(files)),"white")
for i,t in enumerate(tiles): W.paste(t,((i%4)*420,(i//4)*330))
W.save(out)
