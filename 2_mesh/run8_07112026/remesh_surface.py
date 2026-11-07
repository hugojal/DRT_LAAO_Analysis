"""Isotropic surface remeshing with MeshLab (pymeshlab), the MeshLab step of the course pipeline (03/11/2026).

Isotropic explicit remeshing (split / collapse / flip / tangential relaxation, nodes re-projected on the input
surface) to ~1 mm triangles. Edges sharper than 60 deg (the PV and MV cap rings, ~90 deg) are kept as features,
so the caps stay flat and separable. Then: remove duplicated/degenerate faces, check manifoldness.
Needs pymeshlab (pip install pymeshlab). Usage: python remesh_surface.py in.stl out.stl [target_edge_mm] [pre_decimate_faces or 0] [merge_mm]
(pre_decimate_faces: quadric edge-collapse decimation, topology preserved, before the remeshing; for very fine inputs)"""
import sys
import pymeshlab as ml

src, dst = sys.argv[1], sys.argv[2]; h = float(sys.argv[3]) if len(sys.argv) > 3 else 1.0
ms = ml.MeshSet(); ms.load_new_mesh(src)
ms.meshing_remove_duplicate_vertices(); ms.meshing_remove_duplicate_faces(); ms.meshing_remove_null_faces()
merge = float(sys.argv[5]) if len(sys.argv) > 5 else 0.0
if merge > 0:                     # merge near-coincident vertices (seams of cut-and-extrude steps), then drop null faces
    ms.meshing_merge_close_vertices(threshold=ml.PureValue(merge)); ms.meshing_remove_null_faces()
    ms.meshing_repair_non_manifold_edges(); ms.meshing_repair_non_manifold_vertices(); ms.meshing_remove_unreferenced_vertices()
if len(sys.argv) > 4 and int(sys.argv[4]) > 0:
    ms.meshing_decimation_quadric_edge_collapse(targetfacenum=int(sys.argv[4]), preservetopology=True, preservenormal=True, qualitythr=0.5)
ms.meshing_isotropic_explicit_remeshing(iterations=12, targetlen=ml.PureValue(h), featuredeg=60, checksurfdist=True,
                                        maxsurfdist=ml.PureValue(0.1), splitflag=True, collapseflag=True, swapflag=True,
                                        smoothflag=True, reprojectflag=True)
ms.meshing_remove_null_faces(); ms.meshing_remove_unreferenced_vertices()
if merge > 0:                     # needles left on the feature rings: merge vertices < 15 % of h apart, repair, short re-remesh
    for _ in range(2):
        ms.meshing_merge_close_vertices(threshold=ml.PureValue(0.15 * h)); ms.meshing_remove_null_faces()
        ms.meshing_repair_non_manifold_edges(); ms.meshing_repair_non_manifold_vertices(); ms.meshing_remove_unreferenced_vertices()
        ms.meshing_isotropic_explicit_remeshing(iterations=3, targetlen=ml.PureValue(h), featuredeg=60, checksurfdist=True,
                                                maxsurfdist=ml.PureValue(0.1), splitflag=True, collapseflag=True, swapflag=True,
                                                smoothflag=True, reprojectflag=True)
        ms.meshing_remove_null_faces(); ms.meshing_remove_unreferenced_vertices()
topo = ms.get_topological_measures()
print({k: topo[k] for k in ("faces_number", "vertices_number", "non_two_manifold_edges", "non_two_manifold_vertices", "boundary_edges", "is_mesh_two_manifold", "number_holes")})
ms.save_current_mesh(dst, binary=True)
