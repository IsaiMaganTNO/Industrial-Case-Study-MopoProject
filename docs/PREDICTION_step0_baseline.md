# PREDICTION: Step 0 baseline reproduction (Toolbox DAG re-run)

Registered BEFORE execution, per working practice. Run date 2026-10-07.

## What is being run
Build chain only, up to and including `Final_SpineOpt_Model`.
**Excluded:** `Run_Model_Planning` (the solve), `Run_Dispatch`, `fix_investments`,
`merge_operations`, `feedback_extremes`, `visualization`.

Order (from `project.connections`, 65 edges, DAG verified acyclic, 59/59 items):

1. 11 importers: `commodity_importer`, `gas_import`, `power_importer`,
   `rdemand_importer`, `heat_importer`, `hydro_importer`, `industry_importer`,
   `biomass_importer`, `cargo_import`, `transmission_importer`,
   `transport_importer`, `VRE_importer`
2. `template_1` -> `SpineOpt_target`
3. `ines_builder` -> `INES_DB`
4. `ines_to_spinetop` -> `SpineOpt_target`
5. `merge_spineopt` -> `Final_SpineOpt_Model`
6. `scenario_setup`, `clustering_input`, `run_clustering`, `clustering_output`

## Acceptance criterion
`Final_SpineOpt_Model` reaches **entity 28,925 / parameter_value 35,814**
(the live 7-day post-scenario-setup state, per corrected Step 0 in the plan).

## Predictions

1. **Every tool exits 0.** Evidence: `commodity_importer` smoke test already
   exited 0 and ran real logic ("Commodity Data Added").
2. **Importers are idempotent.** Evidence: re-running `commodity_importer` left
   counts unchanged at entity 14 / parameter_value 22 - no duplication.
   *This is the single most important assumption; if it fails anywhere, counts
   inflate rather than match.*
3. **`Final_SpineOpt_Model` lands within 1% of 28,925 entities.** Exact match is
   NOT predicted - clustering may be stochastic.
4. **The 17 IC1 regions are unchanged** and no country regions appear
   (`vre_db` stays 17 IC1 + 50 offshore + 0 country). Inputs have not changed yet.
5. **Cross-border guard holds:** `investment_count_initial_cumulative` on class
   `connection`, 327 rows, sum 1522.5048.
6. **Runtime 30-90 min** for the full build chain.

## How I could be wrong
- Idempotency may hold for a 14-entity store but fail for `ines_builder`, which
  does far more work. Counts would then *exceed* the target, not fall short.
- `run_clustering` may re-derive representative days non-deterministically,
  changing temporal entities. If only clustering-related counts differ, that is
  a PASS with caveat, not a failure.
- A tool may exit 0 while silently writing nothing. Guard: compare file mtimes
  and counts, never exit codes alone.
