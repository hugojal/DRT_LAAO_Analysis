"""Mitral velocity profile for the new mesh (mitral cut on the annulus, 2_mesh/mv_aligned_03112026), 04/11/2026.

The course profile (../boundary_conditions_4cycles/velocity_outlet.prof, profile velocity_bc_c, sign already
inverted) is a leaflet-tip-like Doppler signal: VTI 15.1 cm per beat, peak 0.945 m/s, beat 0.875 s (68.6 bpm).
Applied unchanged on the new mitral cap (861 mm2, the anatomical annulus) it would give 130 mL/beat and
8.9 L/min, above the normal resting range. The mitral FLOW is what has to be physiological: the same flow that
crosses the leaflet tips crosses the wider annulus at a lower velocity (continuity, Q = v A).
The profile is multiplied by one constant so that cardiac output = 5.0 L/min (between the CMR reference means of
men 5.6 and women 4.5 L/min, Kawel-Boehm et al. 2020, J Cardiovasc Magn Reson 22:87); shape and timing are kept.
Moving annulus: the MV cap moves along z (motion.prof, rigid body) and Fluent computes the flux through a moving inlet
relative to the face. To make the flow THROUGH the annulus equal to the scaled profile (zero in systole, closed valve),
the annulus velocity w = dz/dt (backward difference, as Fluent moves the face per step) is added:
u_abs = f * u_course + w (inward normal of the cap = +z). The LA volume change of the annulus motion then comes from
the pulmonary veins (reservoir phase), not through the closed valve.
Usage: python scale_mitral_velocity.py"""
import os, json
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); SRC = os.path.join(os.path.dirname(HERE), "boundary_conditions_4cycles", "velocity_outlet.prof")
A_MV = 861.4e-6          # m2, area of the mitral cap of HugoJal_Case3_mvz_03112026 (check_mesh_mvz.json)
CO_TARGET, T_BEAT = 5.0, 0.875
zt = np.array([[float(x) for x in l.split()] for l in open(os.path.join(HERE, "motion.prof")).read().split("\n")[3:] if l.strip()])
lines = open(SRC).read().split("\n"); head, body = lines[:3], lines[3:]
data = np.array([[float(x) for x in l.split()] for l in body if l.strip()])
t, v = data[:, 0], data[:, 1]; dt = t[1] - t[0]
last = (t > 3 * T_BEAT + 1e-9) & (t <= 4 * T_BEAT + 1e-9)
sv0 = -np.sum(v[last]) * dt * A_MV * 1e6                          # mL/beat with the unscaled profile
sv_target = CO_TARGET * 1000 * T_BEAT / 60
f = sv_target / sv0
assert np.allclose(zt[:, 0], t), "motion and velocity profiles must share the time points"
w = np.concatenate([[0.0], np.diff(zt[:, 1]) / dt])                  # annulus velocity along z (m/s), backward difference
u_abs = v * f + w
with open(os.path.join(HERE, "velocity_outlet.prof"), "w") as fo:
    fo.write("\n".join(head) + "\n" + "\n".join(f"{a:g}\t{b:.10g}" for a, b in zip(t, u_abs)) + "\n")
info = dict(scale_factor=round(f, 4), mitral_area_mm2=A_MV * 1e6, beat_s=T_BEAT, heart_rate_bpm=round(60 / T_BEAT, 1),
            unscaled=dict(stroke_volume_mL=round(sv0, 1), cardiac_output_L_min=round(sv0 * 60 / T_BEAT / 1000, 2), peak_velocity_m_s=round(-v.min(), 3)),
            scaled=dict(stroke_volume_mL=round(sv_target, 1), cardiac_output_L_min=CO_TARGET, peak_velocity_m_s=round(-v.min() * f, 3),
                        peak_flow_mL_s=round(-v.min() * f * A_MV * 1e6), VTI_cm=round(-np.sum(v[last]) * dt * f * 100, 2)),
            annulus_velocity_added=dict(min_m_s=round(w.min(), 4), max_m_s=round(w.max(), 4), swept_volume_mL=round(np.ptp(zt[:, 1]) * A_MV * 1e6, 1)))
json.dump(info, open(os.path.join(HERE, "scaling.json"), "w"), indent=1); print(json.dumps(info, indent=1))
