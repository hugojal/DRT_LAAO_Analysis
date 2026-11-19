"""Zips everything Fluent's calculation activity exported for run9 (all 4 cycles, 350 steps) plus a ParaView state.
Output: submission/HugoJal_Case3_Simulation.zip  (written to a .part file and renamed at the end)"""
import os, zipfile
R = r"C:\Users\hugoj\Desktop\UNI\3er\MOs\DRT_LAAO_Case3"
SRC = os.path.join(R, "3_simulation", "results", "run9_4cycles"); OUT = os.path.join(R, "submission", "HugoJal_Case3_Simulation.zip")
with zipfile.ZipFile(OUT + ".part", "w", zipfile.ZIP_DEFLATED, compresslevel=3, allowZip64=True) as z:
    for f in sorted(os.listdir(SRC)): z.write(os.path.join(SRC, f), "HugoJal_Case3_Simulation/" + f)
    z.write(os.path.join(R, "6_paraview_basic_18112026", "post_process_allsteps.pvsm"), "HugoJal_Case3_Simulation/post_process.pvsm")
os.replace(OUT + ".part", OUT); print("done", os.path.getsize(OUT) // 2**20, "MB")
