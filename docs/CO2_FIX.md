# CO2 route-emission fix - what changed and how to undo it

Branch: `fix/co2-route-emissions`
Commit: `bb288be`
Revert point: tag `pre-co2-emission-fix` (`d9a1b7d`)

Evidence that motivated this: `docs/VERIFICATION_co2_pipeline.md`
(independently re-verified, read-only, before any code was touched).

---

## 1. How to undo everything

Two independent paths, because they fail in different ways. **Neither touches
`checkpoints/` or `reports*/`,** so solved databases and existing plots are safe.

```powershell
# preview first - always
./tools/revert_co2_fix.ps1 -DryRun

# file-based: restores .orig snapshots from backups/pre-co2-fix/
./tools/revert_co2_fix.ps1

# git-based: restores the same files from the tag
./tools/revert_co2_fix.ps1 -Mode Git
```

Nuclear option, discards the whole branch:

```powershell
git checkout session-2026-09-27-guardrails-and-scaling
git branch -D fix/co2-route-emissions
```

Both revert paths were **tested** (a marker string was injected into
`ines_to_spineopt.py` and successfully removed by the file-based revert).

After reverting, rebuild the model DB so no fix-derived values linger.

---

## 2. The defect

The source data was correct all along. Two pipeline defects compounded:

1. **`industry_DB.py` never read `ind_process_routes_co2_emission`.**
   It read life, capex, fom and co2_*capture* - but not emission. So
   route-specific emission factors never entered the pipeline at all.

2. **`ines_to_spineopt.py::process_emissions()` fabricated emissions from fuel.**
   Every unit drawing a commodity with `co2_content` got
   `atmosphere <- fuel = co2_content(fuel)`. Only four values exist
   (coal 0.35, waste 0.30, crude 0.26, fossil-CH4 0.20). This is:
   - **technology-blind** - a CCS-equipped route emits exactly as much as its
     unabated twin, so capture is invisible to emissions accounting;
   - **dimensionally wrong** - applied per MWh of *input* fuel, while the
     source data is per unit of *output*. For refineries (`HC<-crude = 0.64`)
     that is `0.26 x 1.5623 = 0.406` tCO2/MWh HC against a true 0.019,
     i.e. overstated **x21 to x203**.

Consequence in the last good run: 4.52e9 of CO2 slack penalty, 99.8% of the
objective, against ~8.2M of real system cost.

---

## 3. The change

Four files, **pure additions** (60 insertions, 1 deletion - the deletion is a
blank line).

| File | Change |
| --- | --- |
| `data-pipelines/europe/_industry-aidres/industry_DB.py` | New `co2_emitted` block mirroring the existing `co2_captured` block. Writes `CO2_emitted` on `technology__to_commodity__to_commodity = (industry, node, "atmosphere")`. |
| `data-pipelines/europe/_ines-builder/sysconfig.yaml` | Maps `CO2_emitted -> equality_ratio` with factor `1.0`, pattern `[[1],[3],[1],[2]]`, in **both** `industrial_sector` and `other_industrial_sector`. |
| `data-pipelines/europe/_industry-aidres/industry_template_DB.json` | Declares the `CO2_emitted` parameter definition. |
| `ines-spineopt/ines-spineopt/ines_to_spineopt.py` | `process_emissions()` now builds a `route_based_units` set and **skips** those units, so they are not also charged the fuel-based ratio. |

### Why it is dimensionally safe

`CO2_captured` already travels this exact path - same sheet layout, same
`(Industry, to_node)` key, same units, factor `1.0`, no conversion - and lands
in the model DB unchanged (`CO2<-HC = 0.017`). Emissions use the identical key
and unit, so mirroring that path needs **no scaling**.

### Why there is no double-counting

The source emission values are **already net of capture**. Verified:

| route | emitted | captured | sum | unabated sibling |
|---|---:|---:|---:|---:|
| `REF-SMR-MEA` | 0.002 | 0.017 | 0.019 | `REF-SMR` = 0.019 |
| `CEM2-(BMW)MEA` | **-0.308** | 0.650 | 0.342 | `CEM2-(BMW)` = 0.342 |
| `(NG)NH3-DEA` | 0.322 | 1.420 | 1.742 | `(NG)NH3` = 1.742 |

So emission and capture are written as-is, with **no subtraction**.

### Three traps deliberately avoided

1. **The guard is `!= 0.0`, not `> 0.0`.** The capture block uses `> 0.0`.
   Copying that would silently discard `CEM2-(BMW)MEA` (-0.308) and
   `CEM2-(BMW)CaL` (-0.188), the two BECCS routes.
2. **The fuel fallback is preserved** for units with no route data
   (`LNG-terminal`, `SCPC-existing`, boilers, `gas-extraction`).
   Without the skip in `process_emissions()`, those units would be fine but the
   route-backed ones would be charged **twice**.
3. **`CO2-injection-*` units are not affected.** They carry an `atmosphere`
   ratio of 1.0, which looks like a bug but is not - `atmosphere` sits on the
   *input* side (geological removal). The skip rule keys on `byname[1]`, and for
   injection units `byname[1]` is the storage node, so they are correctly
   excluded. Verified explicitly.

Dry-run of the new block against the real sheet: **94 routes written**
(2 negative), 26 zero-valued rows skipped, 120 total. Arithmetic checks out.

---

## 4. Validate BEFORE solving

`tools/validate_co2_fix.py` runs static checks against a built model DB. Use it
instead of discovering problems 78 minutes into a solve.

```powershell
python tools/validate_co2_fix.py checkpoints/<your_model>.sqlite
```

Checks: refinery routes carry 0.019 / 0.002 / 0.016; BECCS routes stay negative;
no route-backed unit still sits on a fuel coefficient; the fuel fallback still
exists for no-route units; no duplicated atmosphere ratios.

**The validator is itself tested:** run against the pre-fix DB
`checkpoints/Final_SpineOpt_Model.tiny.1rep.repfix.sqlite` it exits `1` and
reports 4 failures (269 units on fuel coefficients, all refineries at 0.26).
A validator that cannot detect the known bug would be worthless.

---

## 5. Next steps

1. Rebuild the model DB through the pipeline (merger -> clustering -> scenario
   setup), then make a tiny 1-representative-day model - the known-good
   78-minute configuration.
2. Run `tools/validate_co2_fix.py` on it. **Do not solve if it fails.**
3. Solve, then check **penalties first**:
   `objective_objective_penalties` should fall from 4.52e9 by orders of magnitude.
4. Expect `REF(H2)` to appear in the fleet - it is cheaper than `REF-SMR-MEA`
   (914 vs 1,104) and should win once its lower emissions become visible.

Only after that is confirmed should biomass, DAC and VRE be revisited - those
results are plausibly symptoms of this defect and may partly resolve on their own.

---

## 6. Scope note

`ines_to_spineopt.py` is shared with the EU case, which carries the identical
defect. Direct comparability with the EU case is not required, so the change is
made in-tree. It should still be reported upstream.

The fix is confined to industry, where route data exists. Power and heat units
keep the fuel-based path unchanged.
