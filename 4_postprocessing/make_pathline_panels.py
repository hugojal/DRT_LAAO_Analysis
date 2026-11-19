"""Report panels from the last-beat pathlines (pv_pathlines.py, release 2.63 s), 10/11/2026.
Each panel is cropped to the model (its own colour bar removed); the colour bar of the device panel is saved once, to go below the row.
in : 4_postprocessing/run8/pathlines/pathlines_{device_side,body_side,pv_front}_t2.63.png
out: 5_report/figures_run8/path_{device,body,pv}.png, path_bar.png
usage: python 4_postprocessing/make_pathline_panels.py"""
import os
import numpy as np
from PIL import Image
HERE = os.path.dirname(os.path.abspath(__file__)); RUN = os.environ.get("PV_RUN", "run9"); SRC = os.path.join(HERE, RUN, "pathlines"); FIG = os.path.join(HERE, "..", "5_report", f"figures_{RUN}")
def ink(a): return np.abs(a.astype(int) - 255).sum(2) > 24
def split(path):
    """model part (above the bar title) and bar part of one ParaView image"""
    a = np.asarray(Image.open(path).convert("RGB")); m = ink(a)
    txt = (a.max(2) < 150) & (a.max(2) - a.min(2) < 12)                   # black text: first line of the bar title
    rows = [k for k in np.where(txt.any(1))[0] if k > 0.7 * a.shape[0]]; cut = rows[0] - 10
    return a, m, cut
def box(m, r0, r1, pad=8):
    rr = np.where(m[r0:r1].any(1))[0] + r0; cc = np.where(m[r0:r1].any(0))[0]
    return max(cc[0] - pad, 0), max(rr[0] - pad, 0), cc[-1] + pad, rr[-1] + pad
side = [split(os.path.join(SRC, f"pathlines_{w}_side_t2.63.png")) for w in ("device", "body")]
b = [box(m, 0, cut) for a, m, cut in side]; B = (min(x[0] for x in b), min(x[1] for x in b), max(x[2] for x in b), max(x[3] for x in b))
for (a, m, cut), w in zip(side, ("device", "body")): Image.fromarray(a).crop(B).save(os.path.join(FIG, f"path_{w}.png"))
a, m, cut = split(os.path.join(SRC, "pathlines_pv_front_t2.63.png")); Image.fromarray(a).crop(box(m, 0, cut)).save(os.path.join(FIG, "path_pv.png"))
a, m, cut = side[0]; Image.fromarray(a).crop(box(m, cut, a.shape[0], 4)).save(os.path.join(FIG, "path_bar.png"))
print("saved path_device, path_body, path_pv, path_bar")
