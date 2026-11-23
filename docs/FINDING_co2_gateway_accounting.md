# CO2 accounting: findings, 2026-10-01/02

Session follow-on from `docs/VERIFICATION_co2_pipeline.md` and
`docs/FINDING_fuel_based_emissions.md`. Several earlier conclusions in this
investigation were **wrong and are retracted here**; see "Retractions".

---

## 1. Root cause located: commodity -> node projection drops 5 of 9 CO2 values

`data/Commodities/commodity_data.csv` carries a `CO2_content` column
(ton/MWh, ENTSO-E TYNDP 2024) for nine commodities. It survives into
`commodity_db.sqlite` intact, then **five values are silently lost** on the way
into `INES_DB.sqlite`:

| stage | rows |
| --- | --- |
| `commodity_data.csv` | 9 |
| `.spinetoolbox/items/commodity_db/commodity_db.sqlite` | 9 (intact) |
| `.spinetoolbox/items/ines_db/INES_DB.sqlite` | **4** |

Survivors: `coal` 0.35, `crude` 0.26, `waste` 0.30, `fossil-CH4` 0.20.
Lost: `CH4` 0.20, `HC` 0.24, `MeOH` 0.20, `fossil-HC` 0.24, `CO2` -1.

### Why

Not a filter. `commodity_import.py` is correct and `sysconfig.yaml`'s mapping is
generic:

```yaml
commodities:
  commodity:
      node:
        co2_content: [co2_content,1.0]
        commodity_price: [commodity_price,1.0]
```

The commodity -> node projection only lands where a **global node of that name
exists**. `coal`/`crude`/`waste`/`fossil-CH4`/`U-92`/`global-H2` are global
single nodes and receive their parameters. `CH4`/`HC`/`MeOH`/`bio`/`H2`/`elec`
are **regionalised** - they exist only as `CH4_BEC1`, `HC_NLC3`, ... - so the
commodity-level value has no global node to attach to and is dropped.
`fossil-HC` has no node of any kind.

`commodity_price` is lost the same way, on the same 6 global nodes only.
**One defect, two symptoms.** `process_emissions()` is the victim, not the
cause: it can only key on the four values that survived.

---

## 2. The model uses GATEWAY accounting, and that is mostly correct

Carbon is charged **once, where a raw fuel enters the system**:

| global fuel | consumed by | produces |
| --- | --- | --- |
| `fossil-CH4` | `LNG-terminal` (26), `gas-extraction` | `CH4_*` |
| `crude` | `REF(H2)`, `REF-SMR`, `REF-SMR-MEA` (51) | `HC_*` |
| `coal`, `waste` | 259 industrial units | products directly |

Downstream burners of `CH4_*`/`HC_*` therefore have **no atmosphere row by
design** - charging them too would double-count.

### This makes consumer-side charging ill-posed for shared carriers

A carrier node is fed by fossil *and* non-fossil producers simultaneously:

| carrier | producers | synthetic share (solve) |
| --- | --- | --- |
| `CH4_*` | LNG-terminal, gas-extraction / methanation, bio-diges-up(+CC) | 0% -> 21.9% (2041) -> **44.7% (2050)** |
| `HC_*` | REF(H2), REF-SMR(-MEA) / (BM)FT, (H2)FT-DC, (COEL)FT-MEA | **0.0%** all periods |
| `MeOH_*` | (BM)MeOH, (H2)MeOH-DC, (COEL)MeOH-MEA | no production |

Once mixed in `CH4_BEC1` a "fossil tonne" is indistinguishable from a
methanated one. A flat 0.20 on CH4 consumers would charge `methanation` output
as fossil even though it *consumes* CO2 to make that methane - double-penalising
power-to-gas. **So for CH4/MeOH/bio the existing gateway accounting is correct
and must be left alone.**

---

## 3. The real defect: `patch_co2_in_model_db.py` broke the refinery gateway

The patch replaced every industrial unit's atmosphere coefficient with the
per-route factor from `ind_process_routes_co2_emission`. Correct for terminal
consumers (coal/waste industry). **Wrong for gateways.**

The original 0.26 on `(REF*, atmosphere, crude, REF*)` was load-bearing: it
bundled the refinery's own process emissions AND the downstream combustion
carbon of every unit of refined product. Replacing it with the on-site-only
route factor deleted refined-product carbon from the model:

| tech | n | original | patched | factor |
| --- | ---: | ---: | ---: | ---: |
| `REF-SMR-MEA` | 17 | 0.26 | 0.00128 | /203 |
| `REF-SMR` | 17 | 0.26 | 0.01216 | /21 |
| `REF(H2)` | 17 | 0.26 | 0.01024 | /25 |

### Consequence: oil-fired generation became the cheapest way to meet a binding cap

`oil-eng` burns `HC_*` -> `elec_*` at 35%; `HC_*` comes from crude at 0.64, so
1 MWh_el pulls 1/0.64/0.35 = 4.46 MWh crude.

| route | tCO2 / MWh_el |
| --- | ---: |
| CCGT (via LNG-terminal, 0.2) | 0.3448 |
| `oil-eng` via `REF-SMR` | 0.0543 |
| `oil-eng` via `REF-SMR-MEA` | **0.0057** |
| `oil-eng` at correct 0.26 | **1.1607** |

Oil was charged **60x less carbon per MWh than gas**, and 200x less than
physical. Fuel cost is no deterrent in a cap-bound system: oil-eng is the
*most* expensive fuel (0.165 EUR/MWh_el vs CCGT 0.037), yet the model happily
paid 4.5x to buy cap headroom. Result in `Investment_Results.1rep_co2patch`:
**23.5 GW of new `oil-eng` (24.9% of 2050 generation) and 173.6 GW of
`REF-SMR-MEA`** as a carbon-laundering route. The reported 2050 net zero is an
artefact. **Treat commit `9f12741` results as invalid.**

---

## 4. Second, pre-existing laundering channel: CCS without an emission row

`CO2-injection-*` takes **`atmosphere` as an INPUT** at ratio 1.0, and
`atmosphere` is a storage node with a cumulative cap (165.4 / 36.8 / 0.0). Every
injected tonne therefore *decrements the budget*.

So any unit that outputs to `CO2_*` but has **no** atmosphere row earns a free
negative emission. **225 of 288 capturing units are in that state**, including
fossil ones: `CCGT+CC` (17), `SMR+CC` (17), `(NG)PE-MEA`/`(NG)PEA-MEA` (24),
`(COEL)FT-MEA`/`(COEL)MeOH-MEA` (34), `(LN)O-MEA`/`(MeOH)O-MEA` (14).

Legitimately in that state: `DAC` (17) and BECCS - `CEM2-(BMW)*`,
`LC3-(BMW)*`, `bio-diges-up+CC` (41 total).

This is **pre-existing**, not from the patch, and it is being used
(`(NG)NH3-MVR-DEA` captures 15.21/rep-day in 2050).

### BECCS needs no negative coefficients

There are currently **zero** negative coefficients in the DB. Once bio
combustion is correctly zero-emission (the source CSV leaves `bio` blank, which
*is* the carbon-neutral convention), BECCS emerges from topology alone:
bio in -> no atmosphere row -> `CO2_*` out -> injection -> storage. Adding a
negative atmosphere row *and* keeping the capture flow would double-count the
removal. The earlier -0.308 / -0.188 figures must **not** be used.

---

## 5. Not the cause: why VRE looks odd

The 1-day summer representative period, not emissions, drives the mix.

| family | avail. 08-19 | annual mean | ratio |
| --- | ---: | ---: | ---: |
| wind-off-FB | 0.3225 | 0.5098 | 0.63 |
| wind-off-FO | 0.3404 | 0.5107 | 0.67 |
| wind-on | 0.1585 | 0.3506 | **0.45** |
| solar-PV | 0.2702 | 0.1395 | **1.94** |

A low-wind/high-sun day gives solar ~2x its annual average and wind ~0.45x - a
~4x swing in relative economics. Offshore wind **is** investable (12 units,
`investment_count_max_cumulative` = 1000, non-binding) but never built. No
emission fix will change this; it needs more representative days.

Installed electricity capacity, 2050 (`capacity_per_unit` = 1.0 for all 355
electricity-supplying units, so unit counts are GW):
solar 195.8 (73.8%), wind 22.7 (8.6%), thermal fossil 34.1 (12.9%),
nuclear 5.3 (2.0%), storage/other 7.3 (2.7%); total 265.2 GW.

---

## 6. Structural proof: SpineOpt accepts inserted entities

Needed for any future consumer-side fix. Inserting
`unit_flow__unit_flow (oil-eng_NLC1, atmosphere, HC_NLC1, oil-eng_NLC1)` by
hand:

- `PRAGMA foreign_keys` must be **OFF** - Spine ships its DBs that way and
  *relies* on it. Both dimensions of `unit_flow__unit_flow` declare the
  `unit_flow` **superclass** (class 14) while `entity_element` rows point at
  `unit__to_node`/`node__to_unit` entities (classes 44/45). FK enforcement
  rejects that legitimate indirection.
- ids must come from a **running counter**, not `MAX(id)+1` per call.
- Result is byte-equivalent in shape to a native sibling row, resolves via
  `spinedb_api`, and SpineOpt passed `Checking data structure`, generated
  `variable_unit_flow`, and proceeded through constraint generation.

`tools/test_build_only.jl` with `optimize=false` segfaults in PyCall teardown
(`_do_close_db_handler`, Python 3.14) - an environment bug, unrelated to the
inserted rows. Use a short `SPINEOPT_TIME_LIMIT` on the normal solve script
instead.

---

## Retractions

Earlier claims in this investigation that were **wrong**:

1. "389 units burn fossil fuel with no atmosphere row - ~169,000 t/yr
   unaccounted." **Wrong.** That is gateway design. The unaccounted figure was
   reverse double-counting.
2. "The electricity system is ~400x too small." **Wrong.** Demand rows are per
   period (3 per node); summed correctly it is ~160 TWh/yr for NL+BE, which is
   right. Units are GWh/GW and the x365 rep-day convention holds.
3. "Coefficients 0.20 / 0.26 / 0.24 are my assumptions." **Wrong on two
   counts** - they exist in source (`CH4` 0.20, `HC` **0.24**, `MeOH` **0.20**),
   and my HC/MeOH values were shifted by one row. Applying them would have
   over-charged oil units ~8% and methanol units 20%.
4. "Fix bio/BECCS first as a self-contained step." **Wrong.** Doing it alone
   leaves 150+ fossil CCS units earning unearned negative emissions.

---

## Applied: option 1 (`tools/revert_refinery_gateway.py`)

Restores the 51 `(REF*, atmosphere, crude, REF*)` coefficients to crude's
`CO2_content` = **0.26**. Pure UPDATEs, no new entities, trivially reversible.

- in: `checkpoints/Final_SpineOpt_Model.tiny.1rep.co2patch.sqlite`
- out: `checkpoints/Final_SpineOpt_Model.tiny.1rep.gwfix.sqlite`
- verified: all three refinery families now read `[0.26]`

**Known limitation:** `REF-SMR` and `REF-SMR-MEA` now emit identically, so
refinery CCS has no incentive in this run. That is pre-patch behaviour, not a
new defect - but **do not read CCS conclusions from this solve.**

### Option 2 (deferred, ~4-6 h)

Charge the 75 `HC_*` consumers at 0.24 and zero the refinery gateway. Preserves
the CCS incentive. Mechanically de-risked (section 6) and smaller than once
thought - CH4/MeOH/bio need **no** change (section 2), so only HC is in scope.
Blocked on a model-structure decision: `HC_*` is shared with `(BM)FT` /
`(H2)FT-DC`, so a flat fossil 0.24 would mis-charge synthetic HC. Safe today
(0.0% synthetic) but a landmine - `CH4_*` at 44.7% synthetic by 2050 shows why.
Proper fix is to split fossil/synthetic carrier nodes, or keep producer-side
accounting.

### Still open

- Per-region CO2 budgets: emissions pool into a **single global `atmosphere`
  node** while capture is region-locked (`CO2_NLC1`...). Asymmetry loosens the
  constraint. Worth fixing; will not affect the VRE mix.
- `solar-PV-existing` 90.2 GW in 2030 vs ~33 GW actual for NL+BE, and it does
  not reproduce its own generation (90.2 x 0.27 = 24.4 GW avg vs 12.2 GW
  reported). Suspect double-count in
  `investment_count_initial_cumulative`. New-build figures are unaffected.
- The commodity -> node projection defect (section 1) is still **unfixed in the
  pipeline**; a rebuild reintroduces it.
