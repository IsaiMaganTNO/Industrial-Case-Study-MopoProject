# VERIFICATION: `verification/` inputs vs current model settings

Scanned 2026-10-07. Scripts: `run_logs/_v1.py` .. `_v7.py`.
Files: `global_constraints_industry_case_study.xlsx` (sheets `userconfig.yaml`,
`scenario_config.yaml`), `CO2_network(direct_link_ines_builder)/CO2_data_IC1_{low,high}_cost.xlsx`.

## 1. CO2 annual budget - MATCHES (good news)

Verification sheet, wrt 1990, factors 0.45 (2030) / 0.10 (2040) / 0.0 (2050):

| | 1990 | 2030 | 2040 | 2050 |
|---|---:|---:|---:|---:|
| NL | 221.78 | 99.801 | 22.178 | 0 |
| BE | 145.84 | 65.628 | 14.584 | 0 |
| **NL+BE** | | **165.429** | **36.762** | **0** |

Model `atmosphere` levels observed in every run: 453.1507 / 100.8219 / 0.0 **day-units**;
x365 = **165,400 / 36,800 / 0 kt**.

| year | verification (Mt) | model (Mt) | ratio |
|---|---:|---:|---:|
| 2030 | 165.429 | 165.400 | **0.9998** |
| 2040 | 36.762 | 36.800 | **1.0010** |
| 2050 | 0 | 0 | - |

**Verdict: correct to ~0.1%.** Also independently confirms the **/365 day-unit convention**
documented in `TIME_REPRESENTATION.md` S7 - a useful cross-check of that interpretation.

## 2. fossil-CH4 limit - THERE IS AN IC1-SPECIFIC VALUE WE ARE NOT USING

The sheet's `limited_commodity` block gives **two columns, Pan-EU and IC1**:

| year | Pan-EU (GWh) | **IC1 (GWh)** | IC1 (TWh) |
|---|---:|---:|---:|
| 2030 | 2,500,000 | **1,102,262** | **1,102.3** |
| 2040 | 1,000,000 | 440,905 | **440.9** |
| 2050 | 500,000 | 220,452 | **220.5** |

IC1/Pan-EU = **0.440905** exactly (the factor appears in the sheet).

**The model carries only the Pan-EU numbers**, in the **inactive** `limited_fossil-CH4`
alternative. So the IC1-scaled budget - the one actually intended for this study - has
**never been applied**.

**This is directly relevant to the gas work just completed.** Comparison of ceilings:

| | 2030 | 2040 | 2050 |
|---|---:|---:|---:|
| unpatched model consumption | 434.1 | 624.4 | 662.1 |
| our `af=0.50` patch ceiling | 279.1 | 279.1 | 279.1 |
| **intended IC1 budget** | **1,102.3** | **440.9** | **220.5** |

So the authors' intent is a **declining trajectory**, not a flat cap:
- **2030:** IC1 budget (1,102) is far looser than our 279 - our patch is **~4x too strict**.
- **2040:** 440.9 vs our 279 - still looser.
- **2050:** 220.5 vs our 279 - our patch is **~27% too loose**.

**Our flat `af=0.50` is the wrong SHAPE.** It over-constrains the near term (plausibly
explaining the perverse 2030 coal switch, `SCPC-existing` 2,989 -> 33,793) and
under-constrains 2050. **Recommendation: replace the flat availability factor with the IC1
budget trajectory**, implemented either as a declining `availability_factor` time series or
by activating `limited_fossil-CH4` with IC1 values - but see the **365x storage-stock
hazard** in `PROPOSAL_reduce_gas_supply.md` before choosing the budget route.

## 3. Nuclear - verification expects capacity we never build

Sheet `set_technology_buildout`, "maximum invested capacity in GW":

| | 2030 | 2040 | 2050 |
|---|---:|---:|---:|
| NL | 0 | **4** | **5** |
| BE | 0 | **6** | **6** |
| UK | 6 | 11 | 13 |
| total | 6 | 21 | 24 |

Model has a single **pan-EU** `investment_count_total_max_cumulative` 120/150/180 on
`nuclear-3`, in the **inactive** `limited_nuclear-3` alternative. Model builds **0 GW
nuclear in every run**.

The verification figures read as an intended **buildout** (NL 4-5 GW, BE 6 GW by 2040/2050).
Whether these are caps or floors is ambiguous from the sheet, but since the model builds
zero on economics, **a cap changes nothing - only a floor would**. This is the concrete
answer to the earlier "why no nuclear" question: the study intends ~10-11 GW in NL+BE and
the model has no mechanism to deliver it.

## 4. CO2 network costs - we are on the LOW-COST variant

**`data-pipelines/europe/_ines-builder/CO2_data_IC1.xlsx` network tariffs are
numerically identical to `CO2_data_IC1_low_cost.xlsx`** (verified elementwise,
`_v7.py`, re-confirmed `_d17.py`).

> **Wording correction (7 Oct 2026).** An earlier revision of this section said
> "byte-identical". That is **false** and was never what was measured: the files
> differ on disk (md5 `9d4fd6d0c235`, 28.4 KB active vs `19d475e3d56d`, 32.7 KB
> low-cost) -- the workbooks carry different formatting/metadata. What *was*
> verified, and still holds, is that **every numeric value matches** sheet by
> sheet: `network` (171x6), `network_to_storage` (28x4) and `storage` (72x7) all
> compare equal to the low-cost variant and unequal to high-cost (except
> `storage`, which is identical in all three). The substantive conclusion is
> unchanged; only the claim's precision was wrong.

| variant | network tariff mean | min | max | net_to_storage mean |
|---|---:|---:|---:|---:|
| current == **low** | 27.374 | 1.639 | 115.592 | 26.880 |
| **high** | **87.711** | 9.837 | 229.260 | **92.555** |

high/low ratio: mean **4.83x**, range 1.0-6.0x. **Storage cost columns (`low`/`medium`/
`high`, mean 4.08/7.34/10.26) are IDENTICAL across all three files** - only the *network*
and *network-to-storage* tariffs differ. So the "low/high cost" naming refers to
**transport**, not storage.

**Implication:** every CO2-network conclusion so far - the bidirectional patch result, the
BE->NL export surge, 4.4x throughput growth - rests on the **cheapest** transport
assumption. The high-cost variant is a ~4.8x tariff increase and is an obvious, cheap
sensitivity: it would test whether BE->NL CO2 export survives realistic tariffs.

## 5. Not yet checked
- `include_refinery_trajectory` bio/syn shares (0.10/0.02, 0.25/0.20, 0.25/0.65) and the
  note "NL refineries ~2800 PJ/yr ... implying quite high potentials for NL; we might want
  to restrict this?" - **not compared** against model refinery capacity.
- `comfort_industry: 0.2`, `flex_industry: 0.1` - **not compared**; note the active scenario
  does include a `flex_industry` alternative.
- Whether `storage` sheet `low`/`medium`/`high` columns select by the `medium_CO2`-style
  alternatives, and which column the current model actually ingested.

## 6. Recommended priority
1. **Adopt the IC1 fossil-CH4 trajectory** (1102.3 / 440.9 / 220.5 TWh) in place of our flat
   `af=0.50`. Highest value: it is the authors' own number, it fixes the wrong-shape
   problem, and it likely removes the 2030 coal artefact.
2. **Run the high-cost CO2 network variant** as a sensitivity - cheap, and it stress-tests
   the most prominent recent finding.
3. **Raise nuclear with the authors** - clarify cap vs floor; if floor, it must be
   implemented, since economics alone will never build it.
4. Check refinery and flex assumptions (S5).

## 7. Caveats
- Both workbooks are **spreadsheet notes with merged/unlabelled cells**, read positionally.
  The nuclear cap-vs-floor reading in S3 is **genuinely ambiguous** and should be confirmed
  with the authors rather than assumed.
- The 0.9998/1.0010 CO2 agreement uses the x365 reconstruction; it is consistent but assumes
  the day-unit convention, which S1 then treats as confirmed. That is mild circularity -
  though the agreement to 0.1% across two independent years makes coincidence implausible.
- I have **not** verified which of `low`/`medium`/`high` storage columns the built model
  ingested; S4 only establishes that the *network* tariffs match the low variant.
