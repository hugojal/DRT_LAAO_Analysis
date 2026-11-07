"""Builds 6_paraview_package/: everything needed to look at the run7 simulation in ParaView (course criterion 3), 07/11/2026.
Copies (never moves) from the project:
  simulation/  EnSight Gold of the analysed heartbeat (steps 263-350, t = 2.63-3.50 s) + run7_last_beat.encas (time series)
  fluent/      final Fluent case + data of the 4-heartbeat run (also readable in ParaView with the Fluent CFF reader)
  surfaces/    wall_metrics.vtp (TAWSS, OSI, ECAP, RRT of the last beat + distance to the device), LA surface,
               device wire frame (gamma CT), U-Net (nnInteractive) device and manual device mask, all in the simulation frame (m)
  flows.csv, mitral_bc.json, transform_LPS_to_model.json, convergence/ (residuals per step, from check_convergence.py), device_sections/ (sections and recirculation in front of the device)
The full 4-heartbeat EnSight (350 steps, 4.3 GB) stays in 3_simulation/results/run7_4cycles/.
usage: python make_paraview_package.py"""
import os, shutil, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RUN = "run7"; RES = os.path.join(ROOT, "3_simulation", "results", "run7_4cycles"); PKG = os.path.join(ROOT, "6_paraview_package")
FIRST, LAST, DT = 263, 350, 0.01
sim = os.path.join(PKG, "simulation"); os.makedirs(sim, exist_ok=True)
for f in os.listdir(RES):
    m = re.match(r"step_(\d{3})\.(?!encas|xml)", f)
    if m and FIRST <= int(m.group(1)) <= LAST: shutil.copy2(os.path.join(RES, f), sim)
head = open(os.path.join(RES, "all_steps.encas")).read().split("TIME")[0]
n = LAST - FIRST + 1
with open(os.path.join(sim, "run7_last_beat.encas"), "w") as fo:
    fo.write(head + f"TIME\ntime set: 1\nnumber of steps: {n}\nfilename start number: {FIRST}\nfilename increment: 1\ntime values:\n"
             + "\n".join(f"{(FIRST + i) * DT:.2f}" for i in range(n)) + "\n")
flu = os.path.join(PKG, "fluent"); os.makedirs(flu, exist_ok=True)
cases = os.path.join(ROOT, "3_simulation", "cases")
for f in os.listdir(cases):
    if f.startswith("case_run7_4cycles_07112026") and "partial" not in f: shutil.copy2(os.path.join(cases, f), flu)
srf = os.path.join(PKG, "surfaces"); os.makedirs(srf, exist_ok=True)
PV = os.path.join(ROOT, "4_postprocessing", "paraview")
for src, dst in ((f"{RUN}_wall_metrics.vtp", "wall_metrics_last_beat.vtp"), ("la_surface_model_m.stl", "la_surface.stl"),
                 ("device_gamma_wire_model_m.stl", "device_wire_frame.stl"), ("device_manual_model_m.stl", "device_manual_mask.stl"),
                 ("device_unet_wire_model_m.stl", "device_unet.stl")):
    shutil.copy2(os.path.join(PV, src), os.path.join(srf, dst))
shutil.copy2(os.path.join(RES, "flows.csv"), PKG)
shutil.copy2(os.path.join(ROOT, "3_simulation", "boundary_conditions_4cycles_run7", "mitral_bc.json"), os.path.join(PKG, "mitral_bc.json"))
shutil.copy2(os.path.join(ROOT, "2_mesh", "run7_06112026", "transform_LPS_to_model.json"), PKG)
conv = os.path.join(ROOT, "4_postprocessing", RUN, "convergence")
if os.path.isdir(conv): shutil.copytree(conv, os.path.join(PKG, "convergence"), dirs_exist_ok=True)
ds = os.path.join(ROOT, "4_postprocessing", RUN, "device_sections")          # cross-sections in front of the device (device_sections.py)
if os.path.isdir(ds): shutil.copytree(ds, os.path.join(PKG, "device_sections"), dirs_exist_ok=True)
print("package written:", PKG)
