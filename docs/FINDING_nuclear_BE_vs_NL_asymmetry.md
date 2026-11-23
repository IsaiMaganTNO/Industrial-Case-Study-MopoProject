# FINDING: why nuclear builds in BE and not NL (vre15)

Status: **mechanism identified and verified.** Supersedes the "unexplained BE/NL
asymmetry" caveat in `docs/RUN_3day_vre15.md`.

## The puzzle

In `3day_vre15`, `nuclear-3` enters at 51,382 GWh in 2050 -- third-largest source
-- built **entirely in Belgium** (BEC1-BEC7, 0 -> 2.545 -> 5.866 GW) and **zero in
the Netherlands**. The external sheet expects BE 0/6/6 GW and NL 0/4/5 GW, so the
BE number looked like striking corroboration. That needed testing before reporting.

## Ruled out: it is not a parameter asymmetry

Checked all `nuclear-3_{BEC1..8, NLC1..9}` (17 investable units) via the Spine API:

| parameter | distinct values across 17 regions |
|---|---|
| `unit_investment_cost` | **1** (16,594.73 / 11,865.18 / 6,948.15 by period) |
| `fom_cost` | 1 |
| `lifetime_technical` / `_economic` | 1 |
| `discount_rate_technology_specific` | 1 |
| `investment_count_max_cumulative` | 1 (**1000.0** -- non-binding) |
| `investment_count_fix_new` | 2030 = 0.0, then **NaN** for 2040/2050/2060 |

So nuclear is **perfectly symmetric** between BE and NL, the per-region cap is
non-binding, and `investment_count_fix_new` forces nothing after 2030 (NaN = free).
**The BE-only buildout is fully endogenous**, not a forced or mispriced input.
This is the key check -- had a hidden floor existed, the "BE 5.87 vs expected 6 GW"
match would have been an artefact.

## The actual mechanism: Belgium runs out of cheap renewable headroom

Offshore wind is not capped by `investment_count_max_cumulative` (1000, slack).
It is capped by **`investment_group` / `investment_count_total_max_cumulative`**,
a per-seabed-zone limit that is easy to miss because it lives on a different
entity class:

| zone | country | FB cap (GW) | built 2050 | utilisation |
|---|---|---|---|---|
| NSBE01 | **BE** | 5.235 | 5.235 | **100%** |
| NSNL011 | NL | 9.805 | 9.805 | **100%** |
| NSNL033 | NL | 5.824 | 5.824 | **100%** |
| NSNL031 | NL | 17.469 | 9.395 | 53.8% |
| NSNL012 | NL | 6.127 | 3.613 | 59.0% |
| NSNL032 | NL | 3.660 | 0.000 | 0.0% |

**Belgium has exactly one offshore zone; the Netherlands has five.** Once the
onshore patch pinned BE onshore wind at 3.60 GW and solar at 12.77 GW (both at
cap, ratio 1.00000), Belgium's only remaining cheap options were its single
seabed zone -- which it exhausts -- after which nuclear is the cheapest firm
source left. The Netherlands still has 17.9 GW of unused seabed allocation
(NSNL031 + NSNL012 + NSNL032), so it never reaches nuclear's cost.

This is a *scarcity ordering* result, not a nuclear-economics result.

## Consequence for the reported number

The BE 5.87 GW vs expected 6 GW agreement is **coincidence, not validation.**
The model arrives at ~6 GW because that is what remains after BE's onshore and
single offshore zone are exhausted, which has nothing to do with the external
sheet's reasoning. **Do not present this as the model reproducing the Belgian
nuclear plan.** The honest statement is that BE nuclear is an artefact of BE
having one seabed zone while NL has five.

## Secondary observation: floating and bottom-fixed double-book the same seabed

While testing the above I found that each zone carries **two independent**
investment groups -- `wind-off-FB_<zone>` and `wind-off-FO_<zone>` -- with
separate caps, and for 4 of 6 zones the two caps are **numerically identical**
(NSBE01 5.235/5.235; NSNL011 9.8048/9.8048; NSNL031 17.4689/17.4689;
NSNL033 5.8237/5.8237). Membership confirms no shared constraint links them.

So bottom-fixed and floating wind can each take a full allocation of the *same*
physical seabed. The model exploits this: BE builds 5.235 GW FB **plus** 3.196 GW
FO in NSBE01 = 8.431 GW, i.e. **1.61x the stated zone cap**.

**Magnitude check before alarm:** implied densities are 2.42 MW/km2 (NSBE01),
1.44 (NSNL033), 0.75 (NSNL011), i.e. **below** typical real-world offshore
densities of ~3-8 MW/km2. So the overbuild is structurally unsound but not
producing physically impossible capacity. It inflates BE offshore by ~3.2 GW,
which *reduces* the nuclear result -- without it, BE nuclear would be larger.
The asymmetry conclusion above is therefore robust to this defect.

Caveat: I have not confirmed with the authors whether FB/FO caps are *intended*
to be mutually exclusive. Two zones (NSNL012, NSNL032) have differing FB/FO caps,
which suggests the caps encode technology-specific suitability (water depth)
rather than a shared area budget -- in which case partial overlap may be
deliberate. **Raise rather than patch.**

## Methodological note

This is the eighth instance of the recurring blind-spot pattern, caught this time
*before* publication. The plausible explanation (nuclear cost/availability differs
BE vs NL) was measured and falsified; the binding constraint lived on a different
entity class (`investment_group`) than the one being queried (`unit`). Lesson
reinforced: **when a cap appears non-binding, check whether a different entity
class carries the real limit** before concluding the technology is unconstrained.
