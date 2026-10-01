# Session handover - SpineOpt industrial case (IC1)

**Purpose.** Distilled continuity notes from the previous Copilot Chat session
(269 exchanges, 26 Sep - 1 Oct 2026). The full transcript is preserved in
`chat-backup/` but is ~175k tokens and mostly superseded debugging - this file
is the part worth carrying forward.

**Read alongside** (these hold the detail; this file is the index):

| Doc | Covers |
| --- | --- |
| `docs/EU_CASE_MIGRATION.md` | Migration from the EU case |
| `docs/TIME_REPRESENTATION.md` | How temporal settings work and where to change them |
| `docs/WORKFLOW_AND_LESSONS.md` | The "our style" way of working (portable to other machines) |
| `docs/RUNBOOK.md` | How to launch a run |
| `docs/GUROBI_VS_HIGHS.md` | Solver comparison |
| `docs/TEST_RUN_FINDINGS.md` | Early test-run findings |
| `docs/FINDING_fuel_based_emissions.md` | **The current blocker** - see section 3 |

---

## 1. Where the work stands

A reduced-size ("tiny") SpineOpt model of the IC1 regions (NL + BE, 17 NUTS
regions; years 2030 / 2040 / 2050) solves to optimality with CCS, multi-period
CO2 caps and representative-period clustering all functioning. Investment
(first-stage) only - the second-stage hourly operational run is deliberately
**not** used.

Latest substantive run: `checkpoints/Investment_Results.1rep_repfix.sqlite`
(OPTIMAL, 78 min). Gurobi is installed and licensed (expiry ~Oct 2026) and is
faster than HiGHS on this model.

## 2. Established practices (do not regress these)

1. **Always run the "tiny" model.** Without the tiny-model path the build falls
   back to all 8760 hours and model construction blows up. This caused the first
   failure and must not be reintroduced.
2. **Rescale annual caps for representative periods.** With N representative
   periods covering the year, annual budgets expressed per-year are effectively
   multiplied by the repetition factor. The CO2 atmosphere cap is patched by
   /365 for a 1-representative-day run. Any change in temporal resolution
   requires revisiting this scaling. Biomass caps are affected by the same
   mechanism (see section 4).
3. **Slack/penalty on `atmosphere`.** A high-cost emission slack prevents hard
   infeasibility. Treat a non-zero penalty as a *diagnostic signal*, not success.
4. **Value flooring.** Very small coefficients (~1e-8, e.g. some FOM costs) are
   floored to avoid solver scaling problems. Solver scaling options were tried
   and reverted - they caused solve issues.
5. **Checkpoint before clustering.** The merger tool snapshots the DB
   pre-clustering so clustering can be re-run without rebuilding from scratch.
   `checkpoints/` holds named snapshots for each configuration.
6. **Disk space alarms are usually false.** Free space drops due to **volume
   shadow storage**, then self-resets to ~78-95 GB. Do not start emergency
   deletion. (A genuine disk-fill did occur once during a build; a disk guard
   was added.)
7. **Machine fragility.** This is a remote desktop with no physical access. Long
   solves have crashed/rebooted it. Use generous but bounded time limits, and
   avoid anything that risks losing RDP control.

## 3. The open blocker - emissions are fuel-based

Status: **confirmed, reproducible, upstream**. Full write-up in
`docs/FINDING_fuel_based_emissions.md`.

Emission coefficients are assigned per **fuel**, never per **technology**. A
CCS-equipped process therefore emits exactly as much to `atmosphere` as its
unabated twin - carbon capture is invisible to emissions accounting.

- DB has `REF-SMR`, `REF-SMR-MEA`, `REF(H2)` all at `atmosphere<-crude = 0.26`.
- Source data (`ind_process_routes_co2_emission`) holds the correct per-route
  factors (MEA: 0.002 emitted + 0.017 captured, about 89% capture). Never read.
- The EU case has identical values - upstream, not an IC1 regression.
- Consequence: refineries cannot decarbonise; the run pays **4.52e9 in CO2 slack
  penalties (99.8% of objective)** against only ~8.2M of real system cost.

**This likely explains the long tail of disappointing results** - implausible DAC
dominance, excessive biomass, weak industrial decarbonisation investment. Those
were probably symptoms, repeatedly misdiagnosed as separate problems.

Where the previous session stopped: mid-way through scoping the fix. Findings:

- Process-route data is complete and good quality across sectors, including
  negative factors for BECCS (e.g. `CEM2-(BMW)MEA = -0.308`).
- **Unit conventions differ by sector**: most are `tco2_t` (per tonne of
  product), others `tco2_mwh`. This is the main hazard for the fix.
- The existing capture path is a working template: `CO2_captured` is written
  per unit of output with no conversion, and that is how `CO2<-HC = 0.017`
  reached the DB. So an output-keyed convention already works.

**Next action:** implement per-route emission factors on the `atmosphere` flow,
sourced from `ind_process_routes_co2_emission`, with explicit per-sector unit
handling. Then re-run a 1-representative-day case and confirm the slack penalty
collapses.

## 4. Secondary open items

- **Biomass cap.** Many fix attempts; the agreed direction is an annual (not
  per-period) cap so the model can allocate freely across periods within a
  yearly budget. A speculative x10 factor was added then removed. The EU case
  assumes 50% of technical potential - worth matching. Re-evaluate after
  section 3: over-use is plausibly a symptom of the emissions bug.
- **VRE.** Solar appears; wind largely absent for NL/BE, which is implausible.
  Renewable potential caps and VRE profiles flagged as suspect, only partly
  investigated.
- **Storage.** No storage investment appears in any run. Unresolved.
- **DAC.** Dominates carbon removal. Capping or disabling was discussed - again,
  revisit only after section 3 is fixed.
- **Representative-day selection.** Runs keep selecting Jan/Feb days; forcing a
  summer day was done via a dedicated summer checkpoint.

## 5. Known tooling annoyances

- Long-running shell commands in chat frequently **stalled**, which is how the
  previous session ended. Prefer short, bounded commands; redirect long output
  to a file under `logs/` and read the file.
- SpineOpt build-stage progress (variables vs. constraints) is not surfaced as
  readably as in Spine Toolbox; extra logging was added.

---

## 6. If you want the original chat

- Full transcript: `chat-backup/spineopt-chat-session.20261001-195314.md`
- Your prompts only (~9k tokens, a usable chronological index):
  `chat-backup/prompts-only.md`
- Raw session + editing-state JSON: same folder (gitignored).


