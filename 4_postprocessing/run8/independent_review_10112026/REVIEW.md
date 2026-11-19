# Independent review: is the flow near the LAAO device thrombogenic? (run8, Case 3)

Reviewer: independent agent, 10/11/2026. Sources: CFD data only (EnSight `all_steps.encas`, beats 3 = 1.76–2.62 s and 4 = 2.63–3.50 s; device/LA STLs). I recomputed every number used here except the literature values. I read no author `.md`, report or docs. This review is a draft: the user is responsible for checking it and for the final conclusions.

## Region definitions (mine)
- **Device face**: 420 `la_wall` nodes within 1.5 mm of the device STL and within 16 mm of the device axis. This is the wall cap at the cut ostium, at axial position −3.9 to +1.5 mm (median −1.8 mm) from C along N.
- **dev0-5 / dev0-10**: fluid cells within 5 mm / 10 mm of the device face, within 16 mm of the device axis, on the atrial side. Volumes are 2.4 mL and 5.5 mL.
- **References**:
  - *near-wall far*: cells less than 5 mm from the LA wall and more than 30 mm from the device face (≈44 mL). This control matters because blood near any wall is slow.
  - *body*: cells more than 10 mm from the wall (≈43 mL).
  - *LA*: the whole atrium (158 mL).
  - *sphere40*: sphere of 40 mm diameter centred on the device face (the ROI used by Zhong 2023).
- **Wall bands**: area-weighted, by distance from each wall cell centre to the device STL (8.4 cm² in the 0–5 mm band).
- **Thresholds**: speed 0.1 m/s and 0.05 m/s (no LA-validated value exists for either), and 0.2 m/s from Albors 2024.

## Results table (beat 4 unless stated; beat 3 in brackets)

| # | Variable | Metric | Near-device | Reference | Literature threshold | Verdict | Conf. |
|---|---|---|---|---|---|---|---|
| 1 | Velocity / stasis | Volume-mean speed over the beat, dev0-5 | 0.081 m/s (0.082); dev0-10 0.101 | LA 0.122; body 0.136; near-wall far 0.099; sphere40 0.112 | Cycle-mean below 0.2 m/s "may indicate high risk" (Albors 2024). In that cohort the threshold did **not** separate DRT from controls (5 DRT / 4 controls below it). Here the whole LA (0.12) is also below 0.2, so it does not discriminate. | Thrombogenic (weak, relative only) | Low |
| 1b | | Volume fraction with beat-mean speed < 0.1 m/s | 69 % (68 %) | LA 27 %; near-wall far 53 %; body 7 % | None established | | |
| 1c | | Volume fraction with speed < 0.1 m/s for more than 80 % of the beat | 43 % (46 %) | LA 12 %; near-wall far 29 %; body 0.7 % | None established | | |
| 2 | Residence / washout | Particles still in the LA (not exited through the MV) after 1 beat; 600 volume-weighted seeds per region | dev0-5: 69 % (release 1.76 s), 87 % (2.20 s), 63 % (2.63 s), 80 % after 0.5 beat (3.00 s). After 2 beats (1.76→3.50 s): 50 % | Body: 45 / 51 / 40 / 43 %, 22 % after 2 beats. LA: 51 / 59 / 51 / 60 %, 28 %. Near-wall far: 56 / 66 / 67 / 75 %, 30 % | None established. Zhong 2023 reports residual blood after 6 cycles, which is not comparable. | Thrombogenic (moderate, relative) | Low–Med |
| 3 | Recirculation / vortex | Volume fraction with Q > 0, time-mean | 21 % (21 %) | LA 33 %; body 40 %; near-wall far 23 % | None. Albors 2024: recirculation at < 0.2 m/s seen equally in DRT and controls. | Not thrombogenic (no trapped vortex at the device) | Low–Med |
| 3b | | Directional coherence \|⟨u⟩\|/⟨\|u\|⟩ (1 = steady one-way flow) | 0.65 (0.75) | LA 0.66; body 0.58; near-wall far 0.67 | — | | |
| 3c | | Fraction of the beat with flow directed toward the device face (u·N > 0) | 39 % (44 %) | LA 54 %; body 61 % | — | | |
| 4 | Vorticity | Volume-mean \|ω\| | 50.5 1/s (50.2); dev0-10 44.7 | LA 44.2; body 31.4; near-wall far 58.1 | None | Inconclusive. Dominated by wall shear (∂u/∂n), so it is not a stasis or vortex marker. Near the device it is *lower* than in a generic near-wall layer. | Low |
| 5 | TAWSS | Area-weighted mean, by band (0–5 / 5–10 / 10–20 / 20–40 / > 40 mm) | 0.61 / 0.89 / 0.95 / 0.87 / 0.72 Pa. Beat 3: 0.62 / 0.93 / 0.94 / 0.86 / 0.76 | Wall ≥ 20 mm: 0.77 (0.79) Pa. Median in 0–5 mm: 0.49 vs 0.69 Pa. The 0–5 mm median sits at the 28th percentile of all wall cells. | Below 0.36 Pa (Zhong 2023, taken from arterial monocyte-adhesion work, not validated in the LA): 24 % of 0–5 mm area vs 13 % of wall ≥ 20 mm. Vogl 2024 group means: DRT 1.76 Pa, controls 2.90 Pa. This whole model averages 0.79 Pa, so absolute values are not comparable. | Thrombogenic (weak, relative) | Low |
| 6 | OSI | Area-weighted mean, same bands | 0.216 / 0.149 / 0.156 / 0.196 / 0.215. Beat 3: 0.197 / 0.125 / 0.150 / 0.180 / 0.193 | Wall ≥ 20 mm: 0.208 (0.188). Area with OSI > 0.3: 22 % at 0–5 mm vs 24 % at > 40 mm. | None established. Vogl 2024: 0.19 DRT vs 0.17 controls (significance driven by nodal n). | Not thrombogenic (no local elevation) | Med |
| 7 | ECAP | Area-weighted mean, same bands | 0.57 / 0.28 / 0.21 / 0.29 / 0.48 1/Pa. Beat 3: 0.47 / 0.21 / 0.20 / 0.29 / 0.39. Max 2.97. | Wall ≥ 20 mm: 0.41 (0.35) 1/Pa. Area with ECAP > 1.4: 5.6 % (0 %) at 0–5 mm vs 1.4 % (0.9 %) at ≥ 20 mm. | **> 1.4 1/Pa**: Kelsey et al., as cited by Zhong 2023; primary source not verified by me. Zhong found Amulet ostial positions at 1.2–1.9 % ROI area above it. **> 0.5 1/Pa**: Albors 2024, where it did not discriminate (controls had higher peak ECAP). | Thrombogenic (weak, beat-dependent) | Low |
| 7b | RRT (extra to 7) | 1/((1−2·OSI)·TAWSS), area-weighted | 6.1 1/Pa (5.0) | Wall ≥ 20 mm: 4.6 (4.1); 10–20 mm band: 2.2 | None established | Follows TAWSS; same verdict as 5 | Low |
| E1 | Extra: cycle periodicity | Beat 3 vs beat 4 | dev0-5 mean speed 0.082 vs 0.081 | — | — | Beat-to-beat change < 2 % for volume metrics, but up to 20–100 % for ECAP tail metrics | — |
| E2 | Extra: LA volume (geometry) | Fluid volume | 158 mL | Vogl 2024: DRT 171 ± 69 vs controls 128 ± 34 mL | Group difference only | Weak context, not a CFD finding | Low |

## Overall verdict: **inconclusive, leaning mildly thrombogenic (low confidence)**

The device face is consistently among the least-washed regions of this atrium:
- **Speed**: 0.081 m/s vs 0.122 m/s for the whole LA.
- **Low-speed volume**: 69 % of the volume has a beat-mean speed below 0.1 m/s.
- **Retention**: particle retention near the device is above the atrial body and the whole LA in all four release times. After two beats, 50 % remains vs 22 % for the body.
- **Wall shear**: TAWSS and ECAP in the 0–5 mm band are about 20 % lower and about 40 % higher than the rest of the wall.

The margin over a matched control (near-wall blood far from the device) is small:
- Speed is 18 % lower, and retention is higher in 3 of 4 releases.
- There is no recirculation or vortex trapped at the device: Q > 0 occupies 21 % vs 33 % in the LA, flow is as directionally coherent as elsewhere, and OSI is not elevated.
- The absolute values cannot be mapped onto validated DRT thresholds: the 0.2 m/s and ECAP 0.5 criteria did not separate DRT from controls in Albors 2024, and the Vogl 2024 TAWSS levels come from a different boundary-condition set.

The data support "relatively stagnant near-wall region at the device", not "thrombogenic flow" in an absolute sense.

## Strongest arguments AGAINST a thrombogenic conclusion
1. **The comparison is mostly with near-wall flow.** Against near-wall blood elsewhere (0.099 m/s, 53 % below 0.1 m/s), the device slab differs only modestly. Much of the "low velocity" is generic near-wall slowing.
2. **No vortex or recirculation is trapped at the device.** The Q > 0 fraction is the lowest of all regions. Coherence (0.65–0.75) is equal to or higher than in the body. Flow points at the device face only 39–44 % of the time. Flow sweeps past the face rather than circulating over it.
3. **OSI is not elevated** (0.216 vs 0.208). The ECAP elevation therefore comes entirely from lower TAWSS.
4. **The high-ECAP area is unstable between beats.** ECAP > 1.4 covers 5.6 % of the 0–5 mm area in beat 4 and 0 % in beat 3. The mean (0.57 vs 0.47) straddles the 0.5 threshold of Albors 2024.
5. **TAWSS near the device is low, but not extreme.** Its median sits at the 28th percentile of wall cells. The far wall (> 40 mm) has a similar mean (0.72 Pa) and more area below 0.4 Pa (26 % vs 33 % in the 0–5 mm band).
6. **Published thresholds are unvalidated or did not discriminate:**
   - 0.2 m/s and ECAP 0.5: did not separate DRT from controls in the Albors 2024 cohort.
   - 0.36 Pa and ECAP 1.4: come from the arterial or aneurysm literature.
   - Vogl 2024: reports group differences only, and states that thresholds are still to be identified.
7. **Residence time depends strongly on release phase.** Device-slab retention after one beat varies from 63 % to 87 % with release time. One release (2.63 s) gives lower retention than the near-wall control (63 % vs 67 %). One beat is not enough to judge, and even two beats leave 50 % of seeds in the LA.

## Model limitations and which verdict they affect
- **The device is not modelled; the disc is a flat wall cap at the ostium.** No hub or screw cove, no disc rim or lateral surface, no uncovered ridge or cul-de-sac. Zhong 2023 found the hub cove and the device's lateral surface to be where low-TAWSS and high-ECAP spots concentrate. Affects 1–7, likely biasing toward *under*-estimating local risk.
- **Generic boundary conditions, rigid wall, no atrial contraction.** Absolute speeds and TAWSS are uncertain: whole-wall TAWSS is 0.79 Pa vs 1.8–2.9 Pa in Vogl 2024. Affects the comparison of 1, 5 and 7 with literature. Relative comparisons within the atrium are more robust.
- **Laminar, Newtonian blood; only 3 prior beats.** The flow is periodic to within 2 % in volume metrics, but the wall tail metrics (ECAP > 1.4) are not. Affects 7.
- **dt = 0.01 s and nodal WSS on a ~1 mm wall mesh.** Under-resolves near-wall gradients. Affects 4–7.
- **My particle tracker.** Inverse-distance interpolation (k = 8) from cell centres, RK2 with 4 substeps. Particles pushed outside the wall were clamped back: 79–295 clamps per run of 3,000 seeds. Exit through the MV was detected when a particle came within 1.5 mm of the moving outlet and within a 25 mm radius of its centre. Affects 2.
- **Discrepancy with the author's pathlines.** The author's `pathlines_summary.txt` gives 25 % retention for device seeds released at 2.63 s; I get 63 %. At 1.75 s they get 61 % and I get 69 %. The author's seeding and tracker differ, and I did not reconcile them. Treat any 25 % figure with caution.
- **Region limits are my choices.** The 16 mm lateral limit, 1.5 mm patch tolerance and 5 or 10 mm slabs shift the numbers by about 10–20 %. The ranking of regions held for both slab thicknesses.
- **Only one patient, no clinical outcome.** Nothing here is validated against DRT occurrence.

## Literature used (verified via PubMed)
- Vogl BJ et al. Flow dynamic factors correlated with DRT after LAAO. JACC Adv 2024;3(11):101339. PMID 39493311. https://doi.org/10.1016/j.jacadv.2024.101339. Methods: 0-gauge pressure at the PVs, MV velocity outlet, about 14 M elements, FE-deployed device. **Not comparable** in absolute terms with this model.
- Zhong Z et al. Clin Res Cardiol 2024;113(10):1405–1418. PMID 37291248. https://doi.org/10.1007/s00392-023-02228-x. Methods: PV velocity inflow, MV 0-pressure outlet, rigid wall, single patient, sphere ROI of 40 mm diameter. This is the closest set-up to run8. Source of the 0.36 Pa and 1.4 1/Pa thresholds, both quoted from other work.
- Albors C et al. PLoS Comput Biol 2024;20(9):e1011546. PMID 39325818. https://doi.org/10.1371/journal.pcbi.1011546. Source of the 0.2 m/s and ECAP 0.5 criteria. The paper states that velocities and ECAP did not predict DRT with high accuracy in its cohort.
- **Not verified, not used as a threshold:**
  - Di Achille et al. (ECAP definition): not indexed in PubMed, so the definition was used without checking the primary source.
  - Kelsey et al. (ECAP 1.4): seen only through Zhong's citation.

## Scripts (all in `4_postprocessing/run8/independent_review_10112026/`) and exact outputs
1. **`01_dump_steps.py`** (pvbatch)
   - Dumps cell-centred velocity, Q, vorticity and λ2, cell volumes, and wall WSS components for 175 steps (1.76–3.50 s) to `cache/step_*.npz`.
   - Fluid cell count changes between steps (287 175–290 650) because of the dynamic mesh, so every metric is computed step by step. Cell-wise beat means use nearest-cell resampling onto the 1.76 s centroids.
   - The cache (≈2.1 GB) was deleted after the analysis; rerun this script to regenerate it.
2. **`02_save_wall_geom.py`** (pvbatch)
   - Saves the `la_wall` surface at 2.63 s (19 542 nodes), with the same node set as the author's `run8_wall_metrics.vtp`.
3. **`03_volume_metrics.py`**
   - Produces `volume_metrics.json` and `volume_timeseries.npy`.
   - Beat-4 time-mean values:

     | Region | Speed (m/s) | Vol. frac. < 0.1 m/s | Vol. frac. < 0.05 m/s | Q > 0 | \|ω\| (1/s) |
     |---|---|---|---|---|---|
     | dev0-5 | 0.0807 | 0.719 | 0.367 | 0.215 | 50.5 |
     | dev0-10 | 0.1008 | 0.608 | 0.249 | 0.287 | 44.7 |
     | near-wall far | 0.0988 | 0.684 | 0.378 | 0.232 | 58.1 |
     | body | 0.1356 | 0.434 | 0.119 | 0.398 | 31.4 |
     | LA | 0.1217 | 0.547 | 0.219 | 0.334 | 44.2 |

   - Beat-mean speed below 0.1 m/s: dev0-5 0.691, near-wall far 0.527, body 0.067, LA 0.270.
   - Beat 3: dev0-5 0.0820 m/s, near-wall far 0.1064, body 0.1442, LA 0.1266 m/s.
4. **`04_wall_metrics.py`**
   - Produces `wall_metrics.json` and `wall_metrics_recomputed_beat4.vtp`.
   - TAWSS matches the author's vtp (median relative difference 1.7e-6). OSI differs by at most 0.032; mapping 6 dynamic-mesh nodes is the likely cause.
   - Band values are in table rows 5–7 above.
   - Area fraction with TAWSS < 0.4 Pa: 0–5 mm 0.329, > 40 mm 0.258, all wall 0.173.
5. **`05_particle_retention.py`**
   - Produces `particle_retention.json` (values in row 2).
   - Clamps: 295 (1.76 s release, 2 beats), 214 (2.20 s), 162 (2.63 s), 79 (3.00 s).
6. **`06_extra_metrics.py`**
   - Produces `extra_metrics.json`: coherence, flow-toward-device fraction, sphere40 ROI.
   - Beat-4 wall values:

     | Wall region | TAWSS < 0.36 Pa | ECAP > 1.4 | ECAP > 0.5 | Mean TAWSS (Pa) | Mean ECAP (1/Pa) |
     |---|---|---|---|---|---|
     | 0–5 mm | 0.237 | 0.056 | 0.476 | 0.611 | 0.573 |
     | sphere40 | 0.177 | 0.032 | 0.345 | 0.637 | 0.463 |
     | ≥ 20 mm | 0.128 | 0.014 | 0.326 | 0.773 | 0.412 |
     | all wall | 0.118 | 0.014 | 0.299 | 0.791 | 0.391 |
