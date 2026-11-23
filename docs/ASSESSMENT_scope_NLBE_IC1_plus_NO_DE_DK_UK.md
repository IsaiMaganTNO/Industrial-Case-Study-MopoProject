# Feasibility: NL+BE at IC1 + NO/DE/DK/UK at country level

Scope asked for: **BE and NL at IC1 resolution (17 clusters) + NO, DE, DK, UK at
country level** = 21 onshore regions. VRE aggregated from PECD2 to country level
for the four neighbours.

## Verdict

**Feasible, and materially easier than the general option B.** Estimated
**1-2 weeks**, down from the 3-6 weeks I originally quoted for "IC1 + NW Europe".
Data coverage is effectively complete; the remaining work is build orchestration,
not data gathering.

**But there is one scope decision that must be made deliberately before building
-- see §4. It is the single biggest threat to the result's credibility, and it is
a modelling choice rather than a data problem.**

## 1. Data coverage for NO / DE / DK / UK -- complete

Checked every sector dataset in `verification/Data - IC1 and PECD1` for all four
target countries:

| dataset | NO | DE | DK | UK |
|---|:--:|:--:|:--:|:--:|
| Hourly electricity demand (`Rdemand`, 197 MB) | OK | OK | OK | OK |
| Buildings - yearly demand | OK | OK | OK | OK |
| Buildings - capacities w/ decommissioning | OK | OK | OK | OK |
| Buildings - peak/yearly ratios | OK | OK | OK | OK |
| Transport fleets | OK | OK | OK | OK |
| Biomass (`nuts0`) | OK | OK | OK | OK |
| Industry production (`nuts0`, 2018 + 30/50) | OK | OK | OK | OK |
| Power plant fleet (geolocated, 158,548 rows) | OK | OK | OK | OK |
| Electricity transmission | OK | OK | OK | OK |
| Cargo network | OK | OK | OK | OK |
| CH4 production | OK | OK | OK | OK |
| CH4 network | OK | OK | OK | OK |
| VRE timeseries + potentials (PECD2) | OK | OK | OK | OK |

**Correction to an earlier pass of this check:** `simplified_capacities_with_
decommissioning_MW.csv` and `peak_to_yearly_demand_ratios_MW_GWh.csv` first came
back as "all four missing". That was **my delimiter detection failing** -- both
files are comma-separated while their siblings are semicolon-separated. On
re-read both contain all 45 regions (17 IC1 + 28 countries). No data gap.

### Apparent gaps that are not gaps

| sheet | missing | assessment |
|---|---|---|
| `CH4_Storage` | NO | **Correct.** Norway has no significant onshore gas storage. |
| `H2_Storage`, `H2_Network` | NO | **Plausibly correct** -- no Norwegian H2 network today. |
| `H2_Production` | NO, DK | Worth querying, but low impact: H2 production is investable, so absence of a 2025 baseline is not fatal. |
| `Hydro Reservoir` | DE, DK, UK | **Correct by construction** -- the sheet lists 18 countries with meaningful reservoir hydro. NO **is** present, which is the one that matters. |
| `Hydro Pump` | DK | Correct -- Denmark has no pumped storage. |

Norway, the country whose system behaviour matters most here, is well
represented: **3,931 GWh/d gas extraction** and four export pipelines
(NO->DK 321.6, NO->FR 570.0, NO->DE 1,246.95, NO->UK 1,499.1 GWh/d), plus
reservoir and pumped hydro.

## 2. VRE aggregation - mechanism confirmed available

VRE is keyed at **PECD2**. The four targets decompose as:

- DE -> 7 regions (DE01-DE07)
- UK -> 6 (UK01-UK05, UKNI)
- NO -> 5 (NON1, NOM1, NOS1-NOS3)
- DK -> 2 (DKW1, DKE1)

`region_transformation.xlsx` already contains a **`PECD2_PECD1`** sheet (126 rows)
covering all 20 of these with `area`, `population`, **`capacity`** and
**`potential`** weight columns. So the aggregation you propose is directly
supported and does not need new mapping data.

**Use `capacity`/`potential` weights, not `area`.** Area-weighting a capacity
factor across DE01-DE07 or NOS1-NOS3 blends dissimilar wind regimes and will
systematically flatten the profile -- which suppresses exactly the low-wind
events that drive firm-capacity need. Note that aggregating 5 Norwegian zones to
one node also removes NO's internal hydro/transmission structure.

## 3. Topology - the scope is well connected internally

96 of 251 transmission links fall fully inside the scope, including every pair
you would expect: BE-NL (8 links), NL-DE (4), BE-DE, DE-DK, DE-NO, DK-NO, DK-UK,
NL-NO, NL-UK, BE-UK, NO-UK. In-scope cross-border capacity **43,980 MW**.

This is a genuine improvement on today's model, where DE/FR/UK/LU are dead stubs
with **exactly zero** net exchange.

## 4. The decision that must be made first: the boundary severs more than it keeps

33 links have exactly one end in scope. Severed capacity by external country:

| country | MW | links |
|---|---:|---:|
| **FR** | **23,200** | 12 |
| SE | 13,520 | 6 |
| AT | 10,800 | 2 |
| CH | 8,400 | 2 |
| PL | 6,000 | 2 |
| LU | 5,960 | 4 |
| CZ | 4,200 | 2 |
| IE | 3,500 | 2 |

**Total severed 75,580 MW vs 43,980 MW retained -- 63.2% of the interconnection
capacity touching the scope would be cut.** France alone (23,200 MW) exceeds half
of everything retained, and French nuclear is the dominant price-setter for
Belgian and Dutch imports.

This matters for a specific, already-live conclusion. `vre15` builds ~5.9 GW of
Belgian nuclear, and `docs/FINDING_nuclear_BE_vs_NL_asymmetry.md` shows the cause
is Belgium exhausting its one offshore zone and having nothing cheaper left.
**A model that cannot import from France is strongly predisposed to build firm
capacity in Belgium.** Adding DE/NO/DK/UK while still excluding FR could easily
move that number without the mechanism being any more realistic.

Three options, in order of preference:

1. **Add FR** (and ideally LU, 5,960 MW and landlocked between BE/DE). Data is
   present for both -- FR appears in every dataset checked. Cost: ~2 more
   regions. This is the recommended fix.
2. **Price-taking boundary**: represent FR/SE/AT/CH/PL/LU/CZ/IE as fixed-price
   import/export nodes at their stated link capacities rather than dropping them.
   Cheaper than full modelling, far better than zero.
3. **Accept the island and say so.** Defensible only if stated as a headline
   caveat, not a footnote.

**Doing nothing is the one option that is not safe**, because it changes the
answer silently.

> Note on the standing "do not change electricity trade" instruction: this scope
> cannot be built without touching cross-border components -- creating real
> counterparties for DE/UK/NO/DK *is* the deliverable. Flagging explicitly, as
> with option B generally.

## 5. Effort and risk

| item | estimate |
|---|---|
| VRE PECD2->PECD1 aggregation (4 countries, 20 regions) | 1-2 days |
| Enable countries in `userconfig.yaml` + `define_polygons` | hours -- DE/DK/UK/NO **already uncommented** at `ines_target.py` L65 |
| Run sector pipelines at mixed resolution | **3-5 days, highest variance** |
| `ines_target.py` build + SpineOpt conversion | 1-2 days |
| Re-apply the four standing patches | 1 day |
| Solve + validate | 2-3 days |

**Dominant risk is unchanged and is not about data:** the pipeline is a Spine
Toolbox DAG that has never been run end-to-end in this engagement, and all our
working practice to date is direct `DatabaseMapping` patching of built artefacts.

> **CORRECTED (7 Oct 2026).** The claim above is false. The **repo root is itself
> a Spine Toolbox project** and `.spinetoolbox/items/` holds populated per-sector
> databases (`ines_db` 656 MB / 14,966 entities, `vre_db` 403 MB, `transport_db`
> 418 MB, `spineopt_target` 156 MB, plus every other sector store). **The pipeline
> has been run end-to-end on this machine.** I had searched only
> `data-pipelines/europe/**` and `EU_case/` and treated absence there as absence
> everywhere; `EU_case/` is indeed an empty skeleton, but it is not the project
> that was used.
>
> This demotes orchestration from first to fourth risk and cuts the estimate to
> **6-9 working days**. Solve time (below) becomes the dominant risk. See
> `docs/PLAN_mixed_resolution_run.md`.

**Second risk: solve time.** 21 onshore regions vs 17, but the four new ones are
large and bring full generation fleets; unit count plausibly 1.5-2.5x. At 3
representative days we are already at ~88 min on a barrier solve, which scales
superlinearly. Budget for multi-hour solves, and resist dropping representative
days to compensate -- temporal resolution is already the weakest link behind the
nuclear and offshore conclusions.

**Patches must be ported, not re-run blindly.** `patch_gas_availability.py`
hard-codes 17 LNG units and 9 extraction units; `patch_onshore_vre_potential.py`
hard-codes BE/NL country totals. Both will silently under-apply on a 21-region
model. The cross-border guard (`investment_count_initial_cumulative`, 327 rows,
sum 1522.5048) **will legitimately change** and needs a new baseline.

## 6. Recommendation

**Yes, build it -- but add FR and LU**, making it NL+BE at IC1 plus
NO/DE/DK/UK/FR/LU at country level (23 regions). That removes the single largest
distortion (63% severed interconnection) for roughly 10% more regions, and the
data is already present.

Before committing, still do the de-risking step from the earlier assessment:
**prove the pipeline runs end-to-end at the current 17-region scope first.**
Every estimate above is conditional on that, and it has never been demonstrated.
