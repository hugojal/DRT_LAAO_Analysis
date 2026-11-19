"""Volume mesh of the run9 v2 surface in Gmsh, as in the course (L2 slides 30-36): import the STL, Netgen optimisation, volume +
physical group, 3D mesh, export .bdf. Settings = run8 step 6 (triangles of the surface kept; 0.95 mm at the wall growing to 1.9 mm
inside; Netgen + Relocate3D passes against slivers). usage: python build_volume_run9v2.py"""
import os, gmsh
HERE = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"); TAG = "HugoJal_Case3_run9_15112026"; H_SURF, H_VOL = 0.95, 1.9
gmsh.initialize(); gmsh.option.setNumber("General.Terminal", 1); gmsh.model.add(TAG)
gmsh.merge(HERE + "/" + TAG + ".stl")
surfs = [t for _, t in gmsh.model.getEntities(2)]
sl = gmsh.model.geo.addSurfaceLoop(surfs); vol = gmsh.model.geo.addVolume([sl]); gmsh.model.geo.synchronize()
f1 = gmsh.model.mesh.field.add("Distance"); gmsh.model.mesh.field.setNumbers(f1, "SurfacesList", surfs); gmsh.model.mesh.field.setNumber(f1, "Sampling", 60)
f2 = gmsh.model.mesh.field.add("Threshold"); gmsh.model.mesh.field.setNumber(f2, "InField", f1)
for k, v in dict(SizeMin=H_SURF, SizeMax=H_VOL, DistMin=1.0, DistMax=7.0).items(): gmsh.model.mesh.field.setNumber(f2, k, v)
gmsh.model.mesh.field.setAsBackgroundMesh(f2)
for k, v in {"Mesh.MeshSizeExtendFromBoundary": 0, "Mesh.MeshSizeFromPoints": 0, "Mesh.MeshSizeFromCurvature": 0, "Mesh.MeshSizeMin": 0.6,
             "Mesh.Algorithm": 6, "Mesh.Algorithm3D": 1, "Mesh.Optimize": 1, "Mesh.OptimizeNetgen": 1, "Mesh.OptimizeThreshold": 0.5, "Mesh.Smoothing": 5}.items():
    gmsh.option.setNumber(k, v)
gmsh.model.mesh.generate(3)
for _ in range(3): gmsh.model.mesh.optimize("Netgen"); gmsh.model.mesh.optimize("Relocate3D")
gmsh.model.addPhysicalGroup(3, [vol], 2)
gmsh.write(HERE + "/" + TAG + ".bdf"); gmsh.write(HERE + "/" + TAG + ".msh"); gmsh.finalize(); print("written", TAG)
