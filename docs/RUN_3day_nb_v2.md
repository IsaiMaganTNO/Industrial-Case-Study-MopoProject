# RUN 3day_nb_v2 - NL+BE IC1 on current data (2026-10-09)
Built by `tools/reduce_to_nlbe.py SRC REF DST`:
- SRC = `checkpoints/Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite` (current data, all patches incl. storage /365, noDAC+LNG 1.0, nuclear caps, 2041 restamp)
- REF = `runs/3day_nn_fix/input/...nn_fix.sqlite` (old NL+BE model; used ONLY for structure and non-regional data)
Rule: drop DE/DK/NO/UK full regions and AT/CH/CZ/IE/PL/SE/FI stubs plus CO2 links to neighbours; restore the old border stubs (elec/CH4/H2/HC/MeOH/bio/bunker _DE/_DK/_NO/_UK). Non-regional parameters (stubs, atmosphere budget, temporal blocks, representative weights, group caps) are taken from REF. All NL+BE regional parameters are kept from SRC.
Model: `checkpoints/Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite`.

## Verification (run_logs/_nbv1.py, _nbv2.py) - all PASS
| Check | Result |
|---|---|
| C1 old entities present | all except 58 known data-driven (DAC CH4 input -> heat, (LN+EL)O link) |
| Extra vs old | 153 = harber-bosch + NH3 nodes (data update) |
| C2 no foreign full-region entities | 0 |
| C3 NL+BE params identical to mixedres | 0 diffs, 0 missing |
| C4 stubs/global/temporal identical to old NL+BE | 0 diffs |
| Cross-border guard | **327 / 1522.5048** (= old NL+BE) |
| integrity_check | ok (foreign_key_check rows are the same pre-existing pattern as in both source DBs: 8494 / 11694) |
| Preflight | PASSED; days 134/253/358, weights 100.81/159.38/104.81 (= old NL+BE clustering) |
| Assumptions readback | CO2 budget 0.453/0.101/0; storage high_CO2 NSNL012 0.0575, NSNL031 0.0068->0.017 incl. 2040 point; nuclear BE 0/6/6, NL 0/4/5; DAC 0; LNG 1.0; one scenario |

Solve started 19:25 with the scenario filter active; log `run_logs/3day_nb_v2_solve.out`, results `checkpoints/Investment_Results.3day_nb_v2.sqlite`.
