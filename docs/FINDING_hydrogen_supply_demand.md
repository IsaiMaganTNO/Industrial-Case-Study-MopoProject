# FINDING: hydrogen supply - no electrolysis, and where the H2 goes

**Date:** 2026-10-06 | **Run:** `Investment_Results.3day_routeemis.sqlite`
**Trigger:** colleagues asked why there is no electrolysis and where H2 goes.

## 1. Correcting the premise: electrolysers DO exist in the model

`PEM` is present with **17 units** (one per NUTS3 region), investable, cap
`investment_count_max_cumulative = 1000.0`. It is simply **never built** in this
run. "No electrolysis in the catalogue" is false; "no electrolysis in the
result" is true.

Note `Diaphragm` is classified as `electrolysis` in the reporting category but
is **chlor-alkali**, consumes CH4, and makes chlorine - not H2. Any "electrolysis"
line in a report is this, not hydrogen.

## 2. Where hydrogen comes from (GWh)

| year | total | SMR+CC | LH2-terminal (import) |
|---|---|---|---|
| 2030 | 54 | 54 | 0 |
| 2040 | 42,501 | 0 | **42,501 (100%)** |
| 2050 | 85,406 | 42,905 (50.2%) | **42,501 (49.8%)** |

**PEM = 0 in every year.** Fleet: `SMR+CC` 0.006 -> 0 -> **4.898**,
`LH2-terminal` **4.852** (at its cap of 2.2831 per unit), `PEM` absent entirely.

So 2050 H2 is **half fossil-with-CCS, half imported** - and **zero domestic
green**.

## 3. Why PEM loses despite being CHEAPER in capex

| | PEM | SMR+CC |
|---|---|---|
| `unit_investment_cost` | **613.7** | 1,057.3 |
| `fom_cost` | **0.00137** | 0.00445 |
| conversion | **0.622** H2 per elec | **0.69** H2 per CH4 |

PEM wins on every capital metric, so the decision is driven **entirely by the
feedstock**: it needs **1.61 MWh electricity per MWh H2**.

That electricity must be generated, and (per `FINDING_upstream_carbon_gate.md`)
gas-fired generation is **already carbon-charged upstream at the gate**, while
`SMR+CC` **diverts 0.132 tCO2/MWh CH4 into the CO2 node** and is credited when
injected. Under a binding net-zero scalar the model therefore prefers to burn
gas *with capture* over burning gas *to make electricity to split water*.

Electrolysis only wins if there is surplus **zero-carbon** electricity. VRE in
2050 is ~66%, so marginal power is still gas-fired - and 1.61 MWh of it is more
expensive, in both cost and carbon, than 1.45 MWh of CH4 through SMR+CC.

## 4. Where the hydrogen goes - and this is the striking part

**32 unit families can consume H2. Only FOUR actually run:**

| consumer | 2030 | 2040 | 2050 |
|---|---|---|---|
| `(H2)DRI-EAF` (steel) | 0 | 1,325 | **1,325** |
| `(H2)-CC_gfl` (float glass) | 0 | 231 | 231 |
| `(H2)-CC_gco` (container glass) | 0 | 82 | 82 |
| `(H2)-CC_gfi` (fibre glass) | 0 | 37 | 37 |

**Zero output** from `CCGT-H2`, `OCGT-H2`, `fuelcell`, `REF(H2)`,
`methanation`, `(H2)FT-DC`, `(H2)MeOH-DC`, `(H2)NH3`, `(H2)PE`, `(H2)PEA` and
the rest.

Hydrogen is **not** a power-sector fuel here and **not** an e-fuel feedstock.
It is essentially a **niche industrial reductant** - steel DRI plus a little
glass.

## 5. Is this realistic?

**Defensible:** H2 losing to SMR+CC on a gas-rich, cost-minimising system with a
binding net-zero scalar is economically coherent. H2-DRI for steel is exactly
where real-world H2 is most competitive.

**Questionable, and worth raising:**
- **Zero domestic green H2 by 2050** contradicts NL/BE policy (NL targets 3-4 GW
  electrolysis by 2030). The model has no H2 production target or subsidy.
- **49.8% of 2050 H2 is imported** via `LH2-terminal`, which is at its
  investment cap (2.2831). The import is **cheap and uncapped in carbon terms** -
  see open question below.
- **No H2 in power** at all, despite `CCGT-H2`/`OCGT-H2`/`fuelcell` existing.

## 6. OPEN - not resolved here

Does `LH2-terminal` carry **any** upstream carbon charge? `LNG-terminal` books
`atmosphere <- fossil-CH4 = 0.2`. If imported LH2 books **nothing**, then
imported hydrogen is implicitly **free zero-carbon energy**, which would be a
material accounting asymmetry and would partly explain why it takes ~50% share.
**This has not been verified** and should be checked before any H2 conclusion is
published.

## 7. RESOLVED (same session): the import asymmetry is REAL but PRICED

The S6 open question has been answered. Checking both import gateways:

| | `LNG-terminal` (gas) | `LH2-terminal` (hydrogen) |
|---|---|---|
| source node | `fossil-CH4` | `global-H2` |
| `atmosphere` ratio rows | **17** (0.2 each) | **0** |
| appears in `emis` | yes - **111,640** in 2050 | **absent entirely** |
| `tax_out_unit_flow` 2050 | **0.0215** | **0.1036** |

So imported hydrogen is indeed **carbon-free by construction** - it books no
atmosphere flow at all, whereas imported gas is charged 0.2 at the gate. My S6
suspicion was correct on the carbon side.

**But the asymmetry is NOT a free ride.** `global-H2` carries an import tax of
**0.1036** in 2050 versus **0.0215** for `fossil-CH4` - imported H2 is priced
roughly **4.8x** higher per unit. The model pays a substantial premium for it,
which is a reasonable (if implicit) proxy for the cost of green H2 abroad.

**The defensible criticism is therefore narrower than S6 implied:** the issue is
not that imported H2 is free, but that it is **assumed 100% green with no
upstream emissions whatsoever**. If a meaningful share of 2050 global H2 trade
is blue (SMR+CCS with ~10% slip) or grey, the model understates imported-H2
carbon. That is a **scenario assumption to state explicitly**, not a defect.

### Why PEM still loses - the corrected explanation

`SMR+CC` is credited **11,666 t** of captured CO2 in `co2net` in 2050, and
books **zero** atmosphere emissions itself (its gas is already charged upstream
at `LNG-terminal`). So domestic blue H2 is, from the optimiser's view:

- carbon-neutral at the point of production (charged upstream, captured at plant)
- fed by gas taxed at only 0.0215
- 0.69 MWh H2 per MWh CH4

while PEM needs **1.61 MWh of electricity per MWh H2**, and that electricity is
still partly gas-fired in 2050 (VRE ~66%). PEM's cheaper capex (613.7 vs
1,057.3) cannot overcome that feedstock gap.

**This is an economically coherent outcome, not a bug.** The headline for
colleagues: *the model builds no electrolysis because blue H2 with CCS plus
taxed green imports are both cheaper than splitting water with partly
gas-derived electricity.*
