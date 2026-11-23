<!-- filepath: docs/FINDING_co2_network_unidirectional.md -->
# FINDING: the CO2 pipeline network is unidirectional - a SOURCE-DATA defect

**Date:** 2026-10-06 | **Status:** root cause traced end-to-end, read-only
**Explains:** the Belgium-vs-Netherlands cement anomaly
(`FINDING_cement_net_vs_gross.md` S3/S4b)

## 1. Question

Colleague asked: "CO2 pipelines are supposed to be bidirectional, right? Does
the input data match what is in the model?"

**Answer: the model faithfully reproduces its input. The input itself is
one-directional. The defect is in the SOURCE DATA, not in our pipeline code.**

## 2. Evidence - the model

`checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite`, by commodity:

| commodity | connections | edges | **with reverse twin** | multi from/to |
|---|---:|---:|---:|---:|
| HC | 217 | 329 | **329** | 217 |
| MeOH | 217 | 329 | **329** | 217 |
| bio | 217 | 329 | **329** | 217 |
| CH4 | 91 | 91 | **88** | 0 |
| H2 | 89 | 89 | **88** | 0 |
| elec | 79 | 79 | **66** | 0 |
| **CO2** | **35** | **35** | **0** | **0** |

CO2 is the **only** commodity with zero reverse twins. CH4/H2/elec achieve
bidirectionality through **separately named reverse connections**:

| forward | exists | reverse | exists |
|---|---:|---|---:|
| `BEC1_CH4_BEC2` | 1 | `BEC2_CH4_BEC1` | **1** |
| `BEC1_H2_BEC2` | 1 | `BEC2_H2_BEC1` | **1** |
| `BEC7_CO2_BEC2` | 1 | `BEC2_CO2_BEC7` | **0** |
| `BEC3_CO2_BEC6` | 1 | `BEC6_CO2_BEC3` | **0** |

## 3. Evidence - the source data

| source | rows | directed pairs | **reverse twins** | undirected |
|---|---:|---:|---:|---:|
| `Gas_Sectors_Dataset_IC1_placeholder.xlsx` `CH4_Network` | 91 | 91 | **88** | 47 |
| same, `H2_Network` | 89 | 89 | **88** | 45 |
| **`CO2_data_IC1.xlsx` `network`** | **171** | **171** | **0** | **171** |

The gas sheets list each corridor **twice**, once per direction. The CO2 sheet
lists each corridor **exactly once, with no duplicates at all** (171 rows = 171
directed pairs = 171 *undirected* pairs).

## 4. Why this is a data-authoring error, not an intentional model choice

Reading `CO2_data_IC1.xlsx!network` as directed implies, e.g., that
`NLC9 -> BEC6` exists but `BEC6 -> NLC9` is physically impossible. The sheet
carries `km` and a distance-proportional `tariff` - **symmetric physical
quantities**. A corridor with a length and a per-tonne tariff is self-evidently
a two-way pipe; the authors simply listed each pipe once, as an undirected
edge list, exactly as the `km` column implies.

## 5. Where it is baked in

`data-pipelines/europe/_ines-builder/ines_target.py` ~line 1571 iterates the
`network` sheet and writes **one** INES `node__link__node(node1, link, node2)`
per row. There is **no reverse pass**, and INES links are directional. By
contrast the gas builder gets both directions *for free* because its source
already contains both rows. The builder is therefore **not** wrong in
isolation - it is correct for symmetric input and silently wrong for this
asymmetric input.

Note SpineOpt *does* support `connection_type_lossless_bidirectional` (used for
bunker connections in the upstream Pan-European repo), so the capability exists
and is simply not applied here.

## 6. Consequence (the reason this matters)

Directed reachability to a CO2 injector region (`CO2_NLC1/5/6`):

| source | directed closure | reaches injector? | undirected |
|---|---:|---|---:|
| `CO2_BEC6` | **1** (no out-edges at all) | **NO** | 17 |
| `CO2_BEC7` | **8** | **NO** | 17 |
| `CO2_NLC5` | 14 | yes | 17 |

In the source sheet Belgium has only **2** BE->NL rows (`BEC1->NLC7`,
`BEC4->NLC7`, and NLC7 is itself a dead end) against **6** NL->BE rows. Read
as undirected, Belgium is well connected; read as directed, Belgium is a
**carbon cul-de-sac**. Hence all 4,154 t of uncaptured 2050 cement sits in
BEC6/BEC7: Belgian CCS is **infeasible**, not uneconomic.

## 7. Recommendation

**Raise with the data authors**; do not silently patch. Ask: is
`CO2_data_IC1.xlsx!network` intended as an undirected edge list? If yes (near
certain, given `km`), the fix is a one-line reverse pass in the builder, or
mirroring the sheet.

Until resolved: **no Belgian CCS result from this study may be interpreted
economically.** The NL-only CCS outcome is an artefact of edge direction.

**Not yet tested:** whether making the network bidirectional actually moves
Belgian cement to capture. That requires a re-solve and should be registered
as a prediction first.
