"""STL of the manual device segmentation (06/11/2026), made the same way as the gamma and U-Net STLs:
marching cubes on the label map lightly smoothed (Gaussian 0.5 voxel), vertices in LPS mm (the frame of
2_mesh/HugoJal_Case3.stl). The .seg.nrrd itself is only read.
Usage: python make_stl.py"""
import os, struct
import numpy as np, nrrd
from scipy import ndimage as ndi
from skimage.measure import marching_cubes

HERE = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/"); NAME = "Device_manual"
mask, h = nrrd.read(HERE + "/" + NAME + ".seg.nrrd"); mask = (mask > 0).astype(np.float32)
SP = np.diag(h["space directions"]).astype(float); ORG = np.asarray(h["space origin"], float)
idx = np.argwhere(mask); a = np.maximum(idx.min(0) - 3, 0)
crop = mask[tuple(slice(p, q + 4) for p, q in zip(a, idx.max(0)))]
v, fc, _, _ = marching_cubes(ndi.gaussian_filter(crop, 0.5), 0.5); v = (v + a) * SP + ORG
tri = v[fc]; nrm = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0]); nrm /= np.linalg.norm(nrm, axis=1, keepdims=True) + 1e-12
rec = np.zeros(len(fc), dtype=np.dtype([("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])); rec["n"] = nrm; rec["v"] = tri
with open(HERE + "/" + NAME + ".stl", "wb") as f:
    f.write(NAME.encode().ljust(80, b" ")); f.write(struct.pack("<I", len(fc))); f.write(rec.tobytes())
print(f"{NAME}.stl: {len(fc)} triangles, {int(mask.sum())} voxels ({mask.sum() * SP.prod() / 1000:.2f} mL)")
