"""LA segmentation v3 (17/11/2026): v2 + the right superior pulmonary vein (RSPV) trunk.

v2 ends with a flat cut at the right LA roof (z ~ 889 mm LPS). The cut keeps the right
pulmonary artery (RPA) out, but it also cuts off the RSPV trunk, which runs upward between
the SVC (in front) and the RPA (behind) for ~15 mm before it divides
(docs/agents/reviews/rubric_review_17112026.md, finding C1-1).

Method, same tools as the original segmentation (threshold + mask), done slab by slab so it
cannot leak into the RPA, which touches the trunk through a thin wall:
  1. Threshold 300-900 HU (LA blood ~400 HU; the SVC with dense contrast is ~1700 HU).
  2. Follow the trunk from the roof cut along its axis in 0.5 mm slabs; in each slab keep
     only the connected piece nearest the current centre (radius 7 mm), then move the
     centre to that piece. Stop at s = 15.5 mm, just past the division.
  3. Opening (2 iterations, 18-connectivity) of the added part to drop thin bits along the
     RPA wall; keep the piece connected to the LA; fill holes.
v2 is not changed (no voxel removed). Result: one component, Euler number 1 (genus 0).

Run from the project folder with the shared venv:
  ../mcp/.venv/Scripts/python.exe 1_segmentation/la_v3_17112026/fix_rspv_trunk.py
"""
from pathlib import Path
import json

import nrrd
import numpy as np
from scipy import ndimage as ndi
from skimage.measure import euler_number

ROOT = Path(__file__).resolve().parents[2]
CT = ROOT / "1_segmentation" / "5 DS_Coronaires  0.75  B26f  BestDiast 78 %.nrrd"
V2 = ROOT / "1_segmentation" / "la_v2_06112026" / "Case3_LA_segmentation_HugoJal_06112026.seg.nrrd"
OUT = Path(__file__).resolve().parent / "Case3_LA_segmentation_HugoJal_17112026.seg.nrrd"

ct, h = nrrd.read(str(CT))
m, hs = nrrd.read(str(V2))
m = m > 0
O = np.array(h["space origin"], float)
sp = np.diag(np.array(h["space directions"], float))
vox_ml = float(np.prod(sp)) / 1000.0
I = lambda p: np.rint((np.array(p) - O) / sp).astype(int)

# working box around the right roof
lo, hi = I((-80, -190, 875)), I((-20, -130, 935))
sl = tuple(slice(a, b + 1) for a, b in zip(lo, hi))
c = ct[sl].astype(float)
mm = m[sl]
thr = (c >= 300) & (c <= 900) & ~mm
X = O + sp * (np.indices(c.shape).transpose(1, 2, 3, 0) + lo)

a = np.array((-0.45, -0.06, 0.89)); a /= np.linalg.norm(a)   # trunk axis (LA -> lung)
p0 = np.array((-45.0, -162.0, 889.0))                        # centre of the roof cut
s = (X - p0) @ a
cen = p0.copy()
added = np.zeros(c.shape, bool)
for S in np.arange(-1.0, 15.51, 0.5):
    d = X - cen
    rr = np.linalg.norm(d - (d @ a)[..., None] * a, axis=-1)
    sec = (np.abs(s - S) <= 0.26) & thr & (rr < 7.0)
    lab, n = ndi.label(sec)
    if n == 0:
        continue
    cents = [O + sp * (np.array(q) + lo) for q in ndi.center_of_mass(sec, lab, range(1, n + 1))]
    dist = [np.linalg.norm((q - cen) - ((q - cen) @ a) * a) for q in cents]
    k = int(np.argmin(dist)) + 1
    added |= lab == k
    cen = cents[k - 1]

added = ndi.binary_opening(added, ndi.generate_binary_structure(3, 2), iterations=2)
new = m.copy()
new[sl] |= added
lab, _ = ndi.label(new)
new = lab == lab[tuple(np.argwhere(m)[0])]
new = ndi.binary_fill_holes(new)

stats = {
    "added_mL": round(float((new & ~m).sum()) * vox_ml, 3),
    "removed_voxels": int((m & ~new).sum()),
    "volume_v2_mL": round(float(m.sum()) * vox_ml, 2),
    "volume_v3_mL": round(float(new.sum()) * vox_ml, 2),
    "components": int(ndi.label(new)[1]),
    "euler_number": int(euler_number(new, connectivity=3)),
}
idx = np.argwhere(new)
hs = dict(hs)
hs["Segment0_Extent"] = " ".join(f"{a} {b}" for a, b in zip(idx.min(0), idx.max(0)))
nrrd.write(str(OUT), new.astype(np.int16), hs)
(OUT.parent / "la_v3_stats.json").write_text(json.dumps(stats, indent=1))
print(OUT.name, stats)
