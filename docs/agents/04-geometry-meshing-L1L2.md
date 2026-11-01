# 04 · Geometry & meshing reference (L1/L2) — consult only when the mesh is the problem

## L1 — Geometry
- FreeCAD warm-up (Part / Part Design / Sketcher): primitives, extrude, sweep (helix exercise), boolean union.
- **3D Slicer**: load DICOM (select the folder, not the files; "DCM" not "DATA"). Segment Editor: *Thresholding* (read intensities at the structure edge with the data probe) and *Grow from seeds* (needs ≥2 segments; show 3D only at the end). Clean-up: Islands, Smoothing (median), remove extrusions. Export segmentation (`.nrrd`) and surface (`.stl`). Device segmented separately.

## L2 — Meshing pipeline
1. MeshLab: **Taubin smooth**; export STL (ASCII, binary unchecked).
2. Meshmixer: Inspector (repair), Select + `X` to discard, Plane Cut, Erase & Fill, Smooth (shape preserving), Remesh (regularity 100 %, preserve sharp edges), Reduce, Boolean Union (untick Auto-reduce). Optional cylinders as PV extensions (MV ≈ 28–42 mm, PV ≈ 10–25 mm); cylinder edges sharp (~90°), transitions smooth; element sizes of objects to union must be similar.
3. MeshLab: remove self-intersecting faces and non-manifold edges; close holes (lower quality than Meshmixer → return to Meshmixer remesh + reduce).
4. Target ~**50 k surface elements**.
5. Gmsh: import STL → enable *Optimize quality of tetrahedra with Netgen* → Geometry > Elementary entities > Add > Volume (pick via the yellow sphere, key `e`) → Physical Groups > Add > Volume → Mesh > 3D (**< 500 k** elements) → export `.bdf` (type the `.bdf` extension in the name).

## Mesh convergence (slide example, M. I. Pons 2020)
Mean-velocity error vs. 900k-element reference: 500k 2.65 %, 600k 1.97 %, 700k 1.45 %, 800k 1.54 %, 900k 1.39 %; max-velocity error 11.8 % → 4.9 %. Lesson: report a convergence justification for the chosen element count.

## Quality failures to fix upstream (not in Fluent)
Intersecting faces, non-manifold edges/vertices, abrupt transition meshes.
