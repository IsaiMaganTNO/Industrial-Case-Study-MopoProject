# FINDING: all fossil carbon is booked UPSTREAM, at the gas gate

**Date:** 2026-10-06 | **Run:** `Investment_Results.3day_routeemis.sqlite`
**Status:** explains a cluster of earlier "missing emissions" flags

## 1. The observation

Post-patch audit asked: which units **consume a carbon fuel but have no
`atmosphere` booking**? Nine families came back:

`CCGT`, `CCGT+CC`, `CCGT-existing`, `OCGT`, `SMR`, `SMR+CC`, `DAC`,
`gas-boiler`, `gas-boiler-existing` - all burning **CH4**.

My earlier note dismissed these as "route-based legitimately". **That was
wrong** - they are not route-based either. They book **nothing at all**.

## 2. Why that is nevertheless CORRECT

Carbon is booked **once, upstream, where fossil gas enters the system**:

| entity | key | factor |
|---|---|---|
| `LNG-terminal_*` | `atmosphere <- fossil-CH4` | **0.2** |
| `gas-extraction_*` | `atmosphere <- fossil-CH4` | **0.2** |

Every downstream CH4 consumer then burns **already-charged** carbon. Booking
them again would **double-count**. The model uses a *gate* convention, not a
*stack* convention.

This is the same reason `REF-SMR`/`CCGT+CC`/`DAC` showed up in the original
naive scan as "unbooked" - the scan's premise was wrong, not the data.

## 3. Consequence: the emissions profile is dominated by two upstream units

2050, gross positive = **157,462**:

| tech | 2030 | 2040 | 2050 |
|---|---|---|---|
| `LNG-terminal` | 89,540 | 111,640 | **111,640** |
| `gas-extraction` | 0 | 6,794 | **20,773** |

Together = **84.1% of all gross 2050 emissions**. Every industrial process in
the entire catalogue combined accounts for the remaining ~16%.

## 4. What this means for reading results

- **Do NOT read per-technology CO2 for gas-fired power.** `CCGT`, `OCGT`,
  `gas-boiler` etc. will always report **0.0**. Their carbon is already in
  `LNG-terminal` / `gas-extraction`. Reporting them as "zero-emission" would be
  a serious misreading.
- The `industry: *` categories **are** genuine per-process bookings and can be
  read directly (this is what the route-emissions patch fixed).
- Sector CO2 **intensities** are only meaningful for the route-keyed industrial
  families, not for anything on the gas chain.

## 5. Open question - NOT resolved here

The gate factor is **0.2** on both. Whether 0.2 tCO2/MWh is the right full
combustion factor for natural gas (literature ~0.18-0.20 tCO2/MWh_th) is
plausible, but the split between extraction and LNG import, and whether
methane leakage is included, has **not** been verified against a source. Flagged,
not concluded.

---

## S6. CORRECTION - S4's warning was WRONG (2026-10-06)

**The user challenged this finding with exactly the right test:** if abated and
unabated gas both book zero carbon, why would the model ever pay for CCGT+CC?

It wouldn't. The challenge was correct and S4 was wrong. Investment proves it:

| tech | 2030 | 2040 | 2050 |
|---|---|---|---|
| **CCGT+CC** | 2.715 | **12.671** | **12.671** |
| CCGT (unabated) | 0.0 | 0.0 | **2.209** |
| SMR+CC | 0.006 | 0.0 | 4.898 |
| DAC | 0.0 | 10.605 | 10.605 |

CCGT+CC is built **~6x more** than unabated CCGT. Capture is clearly rewarded.

### What I missed: capture is an OUTPUT, not a negative atmosphere flow

| unit | inputs | outputs |
|---|---|---|
| `CCGT` | CH4 | elec |
| **`CCGT+CC`** | CH4 | **CO2**, elec |
| `SMR+CC` | CH4 | **CO2**, H2 |
| `DAC` | CH4, elec | **CO2** |

`CCGT+CC_NLC1__CO2_NLC1__CH4_NLC1__CCGT+CC_NLC1 = 0.18` - it diverts
**0.18 tCO2 per MWh CH4** into a physical `CO2` node, which flows to
`CO2-injection-*` and then to `CO2-storage-*` with an `atmosphere` ratio of
**1.0** (the negative term that shows up as -157,084.3).

So the system is a genuine **three-stage mass balance**:

1. **charge** at the gate (`LNG-terminal` / `gas-extraction`, 0.2)
2. **divert** at the plant (`CCGT+CC` -> `CO2` node, 0.18)
3. **sequester** at the sink (`CO2-injection` -> storage, credited -1.0)

2050 closes exactly: gross **+157,462.0**, gross **-157,462.0**, **NET -0.0**.

### The corrected guidance

S4 said "reporting CCGT as zero-emission would be a serious misreading". The
*fact* (per-technology CO2 reads 0.0 for gas plant) is true, but my framing was
misleading. The accurate statement:

- Gas-plant carbon is charged **upstream**, so a per-technology CO2 column will
  show 0.0 for CCGT/OCGT/gas-boiler. That is **correct accounting**, not a
  missing booking.
- **Abatement is still fully represented** - via the `CO2` output node, not via
  the atmosphere ratio. Any audit that looks only at `__atmosphere__` ratios
  will **systematically miss all CCS** and wrongly conclude capture is unpriced.
- The real reporting caveat is narrower: **you cannot attribute system carbon to
  individual gas consumers**, because it is pooled at the gate.

### Methodological lesson

My audit asked "which units consume carbon fuel but have no atmosphere
booking?" and treated every hit as suspicious. That query **cannot see capture**
because capture is an output flow. I drew a strong conclusion from a query whose
blind spot I had not characterised - the same class of error as the orphan-route
blind spot in `patch_route_emissions.py`. In both cases the fix was to ask what
the query *structurally cannot return* before trusting a zero.
