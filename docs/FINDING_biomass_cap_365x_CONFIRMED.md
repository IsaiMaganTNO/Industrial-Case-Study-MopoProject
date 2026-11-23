# FINDING: the biomass cap IS 365x too loose - source-data trace (DEFINITIVE)

Date: 2026-10-04. Status: **unit chain traced to source; defect confirmed; remedy partly unverified.**
Supersedes `docs/FINDING_biomass_cap.md` sections 3-6 and `TIME_REPRESENTATION.md` section 7.4.

## 1. The authoritative unit chain

`data-pipelines/europe/_biomass/biomass_DB.py` line 264:

```python
value_converted = float(row["quantity_sum"]) * 277777.77
```

`277,777.78 MWh = 1 PJ`. Source `quantity_sum` is **PJ/yr**; `annual_production`
is therefore **MWh/yr**. Stored in
`EU_case/.spinetoolbox/items/biomass_db/biomass_db.sqlite`, class
`stock__to_commodity__region`, 117 values (one per country per alternative).

NL + BE combined:

| alternative | annual_production | TWh/yr | x0.5 realistic |
|---|---|---|---|
| low_bio | 52,886,395 MWh | 52.9 | 26.4 |
| **medium_bio** (active) | **86,173,831 MWh** | **86.2** | **43.1** |
| high_bio | 112,725,250 MWh | 112.7 | 56.4 |

`scenario_run.py:biomass_limitations()` (line ~341) multiplies
`storage_investment_count_max_cumulative`, `storage_state_fix`,
`storage_investment_count_fix_cumulative` and
`storage_investment_count_initial_cumulative` by
`biomass_potential_realistic: 0.5` (`scenario_config.yml` line 30).

**Intended NL+BE cap = ~43 TWh/yr.** Conservative but defensible against the
~100-150 TWh/yr literature potential, since it is 50% of technical potential.

## 2. The defect, proven from daily `node_state`

`storage_state_fix` refills the stock **at the start of every representative
day**. `biomass-stock_BEC1`, 2050 (`node_state`, not `node_state_longterm`):

```
2050-05-14   start 1088.07 -> end 0.00
2050-09-10   start 1088.07 -> end 0.00
2050-12-24   start 1088.07 -> end 0.00
```

Drained to **exactly 0.00** on all three days, refilled each time. `NLC4`
behaves identically (1689.88 -> 0.00 x3).

Representative-day weights are 100.807 / 159.382 / 104.811, summing to
**exactly 365.000**. Therefore:

```
effective annual availability = 1,088.07 x 365.0 = 397,145
authored annual cap           = 1,088.07
inflation factor              = 365.0   (exact)
```

Same root cause as the `atmosphere` CO2 cap (`TIME_REPRESENTATION.md` section 7):
`make_tiny_model.py` coarsens `operations_y*` to one draw-down. The difference:
`atmosphere` has **no** `storage_state_fix` so it accumulates correctly;
`biomass-stock_*` has one, so it resets.

System consumption 1,043 TWh (2050) against an intended ~43 TWh/yr is a
**~24x overshoot**.

## 3. Why TIME_REPRESENTATION.md section 7.4 is WRONG

Section 7.4 concluded `biomass-stock` was "already per-period -> leave",
inferring this from BEC1 having only **1.5 days of headroom**. But 1.5 days of
headroom is **exactly what a per-day-binding budget looks like**. The doc
mistook the symptom for authoring intent. `tools/patch_biomass_stock.py` already
states this in its docstring; the correction had been written and never
propagated back into `TIME_REPRESENTATION.md`.

## 4. The Group 1 run is UNPATCHED

| database | medium_bio total | state |
|---|---|---|
| `checkpoints/Final_SpineOpt_Model.tiny.5rep.biofix.sqlite` | **68.2** | patched |
| `reports_3day_group1/INPUT_...tiny.3day.group1.sqlite` | **24,899.4** | **unpatched** |

Ratio **365.0** exactly, in all three alternatives (low 365.0, medium 365.1,
high 365.0). The Group 1 result therefore stands on a biomass resource ~365x
larger per year than intended - which is sufficient on its own to explain
`bioST` at 89.7% of 2050 generation.

## 5. Corrections to my own earlier statements TODAY

| claim | verdict |
|---|---|
| "add bioST -> atmosphere link" | **WRONG.** Biomass is net-zero at stack; only BECCS warrants a flow. |
| "cap is 365x too loose" (first version) | **RIGHT**, but I withdrew it under pressure from the stale section 7.4. |
| "no scaling bug; cap ~9,088 TWh; 11.5% used" | **WRONG.** I measured `node_state_longterm` at milestone boundaries, which hides the per-day refill. Must use `node_state`. |
| "cap binds only regionally, slack system-wide" | **WRONG.** It binds to 0.00 on every rep day in 2050. |

Method error: I used the wrong result variable (`node_state_longterm` instead of
`node_state`) and then trusted a doc section over my own measurement. The
milestone-boundary series is aliased - it samples only the refilled values.

## 6. Remedy - and the part that is NOT verified

`tools/patch_biomass_stock.py` (10,504 B) does:

1. REMOVE `storage_state_fix` (the refill)
2. REMOVE `storage_investment_count_fix_cumulative` (the second pin)
3. SCALE the remaining caps by `HORIZON_YEARS` (default **10**)

Its own docstring says:

> `*** THE x10 IS A GUESS. TREAT IT AS PROVISIONAL. ***`
> It is NOT verified against any specification, upstream data file, or the EU case.

Steps 1-2 are now **confirmed correct** by the source trace. Step 3 is **not**.
The x10 rests on the assumption that the authored cap is annual and each
milestone stands for 10 years (`years_represented = 10.0` in
`userconfig.yaml`). That is plausible but must be checked against how SpineOpt
actually weights `operations_y*` cost and state before it is trusted - get it
wrong and the model swings from 365x too loose to 10x too tight.

## 7. Open items

1. **Verify the x10 horizon factor** before re-running. Highest priority.
2. Re-run Group 1 with the biomass patch applied; expect `bioST` to collapse
   and VRE to appear. This is now the single highest-value experiment.
3. Fix `TIME_REPRESENTATION.md` section 7.4 in place - it is actively
   misleading and caused this error.
4. Model power unit (GW?) still unverified from the pipeline, though the MWh/PJ
   trace above makes the energy side solid.
5. `NLC5` wind group cap 0.2887 vs 2nd-best CF 0.535 - unrelated, still open.

## 9. Follow-ups resolved after initial write-up (2026-10-04)

### 9.1 `storage_state_fix` is the discriminator - only ONE other family at risk

Nodes carrying `storage_state_fix` in the Group 1 input DB:

| family | rows |
|---|---|
| `biomass-stock_*` | 51 |
| `CH4-geo-formation_*` | 17 |

**No others.** So the 365x refill trap can only affect these two.

### 9.2 `CH4-geo-formation` has the same defect but it is LATENT, not active

`node_state` across all 17 `CH4-geo-formation_*` nodes bottoms out at
**exactly 0.9000 of full** (16,003.33 -> 14,403.00) on every representative day.
The stock is never drawn below 90%, so the cap **never binds** and the 365x
inflation has no effect on the result. `TIME_REPRESENTATION.md` section 7.4's
"leave" verdict is therefore correct *in outcome* for CH4, though for the wrong
reason. It should still be patched if biomass is patched, for consistency -
but it will not change any number.

### 9.3 Evidence on the x10 horizon factor - SUGGESTIVE, still not conclusive

`weight` on the `operations_y*` temporal blocks is **10.0** for all three
periods, and `model_start` 2030-01-01 / `model_end` 2060-01-01 spans 30 years
across 3 milestones. This is consistent with each milestone standing for 10
years, which is the assumption behind `patch_biomass_stock.py`'s `HORIZON_YEARS`.

**This does not by itself prove the x10 is right.** The `weight` parameter is
applied by SpineOpt to *operational cost* aggregation; whether it also scales a
storage **state** balance is a different question and has not been verified in
the SpineOpt source. The resource is a physical stock, not a cost term.

Two readings remain open:
- If the stock must cover a 10-year milestone -> x10 is correct.
- If the stock is an annual budget and the milestone weight only annualises
  cost -> x10 makes the cap **10x too tight**.

Until this is settled, treat `patch_biomass_stock.py` output as provisional, per
its own docstring warning. Resolving it requires reading how SpineOpt builds the
node state balance for `storage_longterm_active` nodes, not more DB queries.
