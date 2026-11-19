"""Assembles submission/ (git-ignored) with the files to hand in for Case 3, named after the case and the author, 14/11/2026.
  HugoJal_Case3_report.pdf                       DRT report (<= 2 pages + references)
  Case3_LA_segmentation_HugoJal.seg.nrrd         LA segmentation (v3, 17/11/2026: v2 + RSPV trunk; the mesh was built from v2)
  HugoJal_Case3_LA_surface_mesh.stl              surface mesh (run9)
  HugoJal_Case3_LA_volume_mesh.bdf               volume mesh (run9)
  HugoJal_Case3_device_segmentation_manual.stl    manual device segmentation (gamma-enhanced CT, closed and smoothed), used in the analysis, Fig. 1b (extra point)
  HugoJal_Case3_device_segmentation_unet.stl     device segmentation with the U-Net (nnInteractive), Fig. 1a
  HugoJal_Case3_ParaView_package.zip             simulation files for ParaView (6_paraview_package/, too big for most upload forms: use a link)
Copies only; nothing in the project is moved. Refuses to run if a patient-data file is found in the package.
usage: python make_submission.py [--no-zip]"""
import os, sys, shutil, zipfile, hashlib
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__))); OUT = os.path.join(ROOT, "submission")
J = lambda *a: os.path.join(ROOT, *a)
FILES = [(J("5_report", os.environ.get("REPORT_PDF", "main.pdf")), "HugoJal_Case3_report.pdf"),
         (J("1_segmentation", "la_v3_17112026", "Case3_LA_segmentation_HugoJal_17112026.seg.nrrd"), "Case3_LA_segmentation_HugoJal.seg.nrrd"),
         (J("2_mesh", "run9_15112026", "HugoJal_Case3_run9_15112026.stl"), "HugoJal_Case3_LA_surface_mesh.stl"),
         (J("2_mesh", "run9_15112026", "HugoJal_Case3_run9_15112026.bdf"), "HugoJal_Case3_LA_volume_mesh.bdf"),
         (J("1_segmentation", "device", "gamma", "Device_gamma_wire_v4_edited_closed_both_16112026.stl"), "HugoJal_Case3_device_segmentation_manual.stl"),
         (J("1_segmentation", "device", "unet", "Device_unet_wire.stl"), "HugoJal_Case3_device_segmentation_unet.stl")]
BAD = (".mrml", ".dcm", ".vti")                                  # Slicer scenes, DICOM, CT crops: never hand in
os.makedirs(OUT, exist_ok=True)
for src, dst in FILES:
    assert os.path.exists(src), src
    shutil.copy2(src, os.path.join(OUT, dst)); print("copied", dst, os.path.getsize(src) // 1024, "kB")
PKG = J("6_paraview_package")
bad = [f for r, _, fs in os.walk(PKG) for f in fs if f.lower().endswith(BAD) or "DS_Coronaires" in f]
assert not bad, f"patient data in the package: {bad}"
if "--no-zip" not in sys.argv:
    z = os.path.join(OUT, "HugoJal_Case3_ParaView_package.zip")
    with zipfile.ZipFile(z, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
        for r, ds, fs in os.walk(PKG):
            ds[:] = [d for d in ds if d != "__pycache__"]
            for f in fs: zf.write(os.path.join(r, f), os.path.join("HugoJal_Case3_ParaView", os.path.relpath(os.path.join(r, f), PKG)))
    print("zip", os.path.getsize(z) // 2**20, "MB")
print("done ->", OUT)
