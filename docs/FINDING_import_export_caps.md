# FINDING: external trade links - investigation and retractions

**Status:** closed. Verified against `reports_3day_co2rebuild` (3-day run, OPTIMAL).
**Conclusion: the import/export machinery is NOT broken.** No fix required.

This note records several wrong intermediate claims because they were acted on
in discussion and because the underlying mistakes are easy to repeat.

## 1. Caps exist and bind - for CH4 / H2 / elec

`capacity_per_connection` has 327 rows and does cover external links. An earlier
probe reported 0 rows because the filter was applied to column 0 of the
parameter frame, which is `entity_id` (an integer), not the entity name.

Every external link carries `capacity_per_connection = 1.0`, so the limit is
`connections_invested_available x 1.0`. Peak hourly flow sits exactly on it:

| link | peak hourly | invested available |
|---|---|---|
| BEC6_CH4_DE | 22.58 | 22.583 |
| BEC3_CH4_FR | 7.50 | 7.500 |
| NLC3_CH4_DE | 6.90 | 6.896 |
| BEC7_elec_FR | 2.70 | 2.700 |

Of 110 external connections: CH4 (21), H2 (19), elec (19) are capped;
HC (17), MeOH (17), bio (17) have no `capacity_per_connection`.

## 2. Electricity exchange is proportionate

Net exchange vs domestic generation, per representative day:

| period | day | net GWh | gen GWh | net % | peak hourly import share |
|---|---|---|---|---|---|
| 2030 | 14 May | -47.8 | 743.3 | -6.4% | 18.3% |
| 2030 | 10 Sep | -15.5 | 726.5 | -2.1% | 23.7% |
| 2030 | 24 Dec | +69.6 | 609.4 | +11.4% | 36.9% |
| 2050 | 14 May | -21.2 | 804.5 | -2.6% | 7.8% |
| 2050 | 10 Sep | +20.9 | 775.3 | +2.7% | 12.3% |
| 2050 | 24 Dec | -11.4 | 770.4 | -1.5% | 12.2% |

Exports in May/Sep, imports in Dec - the expected seasonal signature. Reliance
*falls* over time, the opposite of what a storage-substitution story predicts.

Caveat: the denominator is `to_node` at domestic elec nodes, which includes
inter-regional arrivals, so generation is somewhat overstated. Against demand
(240-320 GWh/day) the 24 Dec 2030 figure is nearer 27%. Pick the denominator
deliberately before quoting.

## 3. RETRACTED: "biomass is imported, 1,181 TWh from nowhere"

**Wrong.** `bio` and `MeOH` external links carry *exactly zero* flow in every
period (total |flow| = 0.00 across 14,688 rows each). The links exist as
entities but are never used.

Biomass comes from **domestic `biomass-stock_*` nodes**
(`biomass-stock_NLC4` -> `bio_NLC4` 616,807 GWh in 2050; BEC1 397,145).
The cap is `storage_state_max` x `storage_investment_count_max_cumulative`
(~992-1032/region), not `node_state_cap` - which is why a `node_state_cap`
query returned nothing and was misread as "uncapped".

**The biomass fix is working and binds hard**: stock is drawn to exactly 0.0 on
nearly every representative day in 2050. Biomass is a scarce binding resource.

Residual (minor, real): each representative day resets the stock to full, so the
annual implied biomass is "daily limit x 365". Worth checking against the
intended annual potential, but this is a representative-period artifact, not a
bug in the fix.

## 4. RETRACTED: "foreign node_state goes negative = free energy creation"

**Wrong, and the proposed fix would have been harmful.**

Foreign `node_state` is the **cumulative running total of net trade** with that
country, not a physical inventory. Verified on `elec_DE`, 14 May 2030:
state equals the cumulative sum of signed hourly connection flow, correlation
**1.000**, identical to 3 decimals.

Negative therefore means *NL+BE is a cumulative net exporter* - correct and
desirable. Setting `node_state_min = 0`, as I proposed, would have forbidden net
export. **Do not do this.**

## 5. RETRACTED: "there is no cyclic / net-zero constraint"

**Wrong.** `cyclic_condition` exists on `node__temporal_block`: 3,528 rows, 93
on foreign nodes (one per node per operational year), all **true**. Every
representative day returns to its starting state - visible as the exact 0.00
boundary rows at `05-13`, `09-09`, `12-23`.

## 6. Root cause of several of these errors: list_value IDs

`storage_active`, `storage_longterm_active` and `cyclic_condition` store a
**`list_value_id`**, not a value. The recurring "= 5" in earlier notes is a
foreign key; `list_value.id = 5` resolves via `boolean_value_list` to **`true`**.

Anywhere an earlier note says one of these is "5", read "**true**".

Related: `node_state` lives on `report__node__stochastic_scenario`, so the node
is **`dim1`**. Querying `dim0` returns a single pseudo-node `default_report`.
An earlier claim ("import nodes explode: HC_DE 5.3 -> 712") came from that
mistake and is void.

## 7. Remaining genuine loose ends

- **HC links are uncapped and actively used** (984,782 GWh total, peak 4,942.8/h;
  gross imports 33 -> 94 -> 118 TWh). Unlike bio/MeOH this is not harmless.
  Confirm whether the missing `capacity_per_connection` is intended.
- HC domestic production (815 TWh) far exceeds domestic consumption (56 TWh) in
  2050, driven by `REF-SMR`. Worth a sanity check on refinery sizing.
- `storage_longterm_active` is **true** on 126 entities, so the earlier suspicion
  that long-term storage is "unwired" rests on a misread and must be re-checked
  from scratch. The caverns still never cycle - reason still unknown.

## 8. HC investigated - no fix warranted (added 2026-10-03)

**The "HC overproduction" (815 TWh produced vs 56 TWh consumed) was my
artifact.** I counted only `unit` demand. The real 2050 sinks are reached via
`connection`:

| sink | TWh |
|---|---|
| `int-maritime` (NLC6 329.0 + BEC1 245.6) | 574.6 |
| `int-aviation` (NLC5) | 95.1 |
| units (crackers, industry) | 55.8 |
| export to DE | 118.5 |

International bunkers consume ~670 TWh. Refinery sizing is consistent with
Rotterdam/Antwerp bunker demand. Not an anomaly.

**The missing cap is real but inert.** HC external connections have no
`capacity_per_connection` *and* no investment parameters at all (CH4/H2/elec
all carry `investment_count_max_cumulative`, `lifetime_*`, etc.). However:

- Only **1 of 17** HC links carries flow: all 984,782 GWh is on `NLC3_HC_DE`.
- **0 of 216 hours** have both directions nonzero - genuine directional trade,
  no round-tripping.
- Net annual = **0.0** in every period. Seasonal: +576 GWh (May 2050),
  -743 GWh (Sep 2050), +576 GWh (Dec 2050).
- Peak 24-31 GWh/h, comparable to the capped gas links.

**Why that one link:** `NLC3_HC_DE` has `connection_flow_cost` = **0.0004**,
~30x cheaper than siblings (`NLC1_HC_DE` 0.0117, `NLC8_HC_DE` 0.0119,
`BEC6_HC_DE` 0.0123). The optimiser routes all HC trade through it. **This cost
outlier is a more likely data error than the missing cap** - check upstream.

**Verdict: no fix needed.** Adding `capacity_per_connection` to HC links would
improve symmetry but would not change this solution.

Open caveats:
- +-743 GWh daily swing is large vs 56 TWh unit demand. If bunker demand is
  flat-profiled, HC trade may be doing seasonal balancing a finer model would
  place elsewhere.
- Not checked whether `int-maritime` / `int-aviation` demand is exogenous. If
  endogenous, the "realistic bunker demand" reading weakens.
