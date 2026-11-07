"""Mitral velocity profile for run7 (06/11/2026): the course curve UNSCALED, plus the annulus velocity.

The course profile (../boundary_conditions_4cycles/velocity_outlet.prof, profile velocity_bc_c, sign already inverted)
is a leaflet-tip Doppler-like signal: VTI 15.1 cm per beat, peak 0.945 m/s, beat 0.875 s (68.6 bpm).
run6 applied it on the anatomical annulus cut (8.6 cm2) and had to scale it by 0.56 to keep the cardiac output normal.
The run7 mesh ends in a mitral orifice of 5.3 cm2 (course range 4-6 cm2), so the curve is used as given: stroke
volume ~80 mL, cardiac output ~5.5 L/min, inside the normal resting range (Kawel-Boehm et al. 2020, JCMR 22:87:
CMR reference means men 5.6, women 4.5 L/min).
Moving valve: the mitral cap moves along z (motion.prof, rigid body) and Fluent computes the flux through a moving
inlet relative to the face. To make the flow THROUGH the valve equal to the course curve (zero in systole), the
valve velocity w = dz/dt (backward difference, as Fluent moves the face per step) is added: u_abs = u_course + w
(inward normal of the cap = +z).
Writes velocity_outlet.prof (same profile name velocity_bc_c) and mitral_bc.json; motion.prof and pressure_inlet.prof
are the 4-beat course files (copied from ../boundary_conditions_4cycles_mvz/).
Usage: python make_mitral_bc.py <mesh check json with the mitral cap area>   (default: the run7 mesh)"""
import os, sys, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); SIM = os.path.dirname(HERE); ROOT = os.path.dirname(SIM)
SRC = os.path.join(SIM, "boundary_conditions_4cycles", "velocity_outlet.prof")
CHECK = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "2_mesh", "run8_07112026", "check_mesh_run8.json")   # same 529 mm2 mitral cap as run7
A_MV = json.load(open(CHECK))["angle_separation_30deg"]["largest"][1]["area_mm2"] * 1e-6      # m2, the mitral cap
T_BEAT = 0.875
zt = np.array([[float(x) for x in l.split()] for l in open(os.path.join(HERE, "motion.prof")).read().split("\n")[3:] if l.strip()])
lines = open(SRC).read().split("\n"); head, body = lines[:3], lines[3:]
data = np.array([[float(x) for x in l.split()] for l in body if l.strip()])
t, v = data[:, 0], data[:, 1]; dt = t[1] - t[0]
assert np.allclose(zt[:, 0], t), "motion and velocity profiles must share the time points"
w = np.concatenate([[0.0], np.diff(zt[:, 1]) / dt])
u_abs = v + w
with open(os.path.join(HERE, "velocity_outlet.prof"), "w") as fo:
    fo.write("\n".join(head) + "\n" + "\n".join(f"{a:g}\t{b:.10g}" for a, b in zip(t, u_abs)) + "\n")
last = (t > 3 * T_BEAT + 1e-9) & (t <= 4 * T_BEAT + 1e-9)
sv = -np.sum(v[last]) * dt * A_MV * 1e6
info = dict(scale_factor=1.0, mitral_area_mm2=round(A_MV * 1e6, 1), beat_s=T_BEAT, heart_rate_bpm=round(60 / T_BEAT, 1),
            stroke_volume_mL=round(sv, 1), cardiac_output_L_min=round(sv * 60 / T_BEAT / 1000, 2), peak_velocity_m_s=round(-v.min(), 3),
            peak_flow_mL_s=round(-v.min() * A_MV * 1e6), VTI_cm=round(-np.sum(v[last]) * dt * 100, 2),
            valve_velocity_added=dict(min_m_s=round(w.min(), 4), max_m_s=round(w.max(), 4), displacement_range_mm=round(np.ptp(zt[:, 1]) * 1000, 2)))
json.dump(info, open(os.path.join(HERE, "mitral_bc.json"), "w"), indent=1); print(json.dumps(info, indent=1))
