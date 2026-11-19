# Case 3 simulation in ParaView (run9, last heartbeat)

- `simulation/run9_last_beat.encas`  EnSight Gold, 88 time steps (t = 2.63-3.50 s): velocity, pressures, vorticity, Q-criterion, lambda-2, wall shear stress, strain rate. Units SI (m, s, Pa).
- `post_process.pvsm`  ParaView state: streamlines from the pulmonary veins (shown), long-axis slice, Q-criterion = 500 1/s2 isosurface (hidden), atrial wall (transparent). Open with File > Load State and choose "Search files under specified directory" pointing to this folder.
- `make_state.py`  script that created the state (`pvbatch make_state.py`).
