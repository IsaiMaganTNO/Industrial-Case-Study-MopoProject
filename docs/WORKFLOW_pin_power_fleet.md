# Practical workflow: pinning the power fleet for the mixed-resolution run

## The problem in one line
`power_DB.py` assigns every existing plant's retirement year with an **unseeded
`random.choice`**, so each pipeline run yields a different fleet - with swings
(NL y2030 6,273 -> 12,214 MW; BE nuclear y2030 4,710 -> 5,765 MW) far larger than
the mixed-resolution effect we want to measure.
Full diagnosis: `FINDING_random_retirement_dates.md`.

## The decision: pin, don't fix
We are **not** applying a structural fix for this run. Instead the power sector is
made a **controlled variable**: after `power_importer` runs, its `units_existing`
values are overwritten with the exact values the `vre15` run used.

Any difference in the mixed-resolution results is then attributable to the
resolution change, not to a random draw.

Verified: the baseline store is **exactly** the `vre15` fleet (201 existing units,
identical entity sets, no diffs).

## Procedure - run this EVERY time power_importer executes

```powershell
python -m spinetoolbox --execute-only . --select power_importer
python tools/pin_power_fleet.py --apply
python tools/pin_power_fleet.py --check   # must print DIFFERING 0 and exit 0
```

`--check` exits non-zero when unpinned, so it can gate the rest of the build.

**Order matters.** `power_importer` overwrites `Power_DB`, so the pin must come
*after* it and *before* `ines_builder`. Pinning then re-importing silently
reverts to a random fleet.

## Status (8 Oct 2026)
- `Power_DB` pinned and verified: md5 `98310ece7624`, identical to baseline.
- National totals: BE y2030 9,778 MW / y2040 3,746; NL y2030 6,273 / y2040 2,101.
- Read back through the Spine API (`DatabaseMapping` + `from_database`), 42
  `units_existing` series - not just raw SQL.

## Scope and limits - read before quoting results
1. **This pins NL+BE only.** `Power_DB` currently contains no DE/DK/NO/UK units.
   When those countries are enabled, their existing fleets **will be randomly
   drawn** and there is no baseline to pin them to. Their fleet is therefore
   arbitrary-but-reproducible (the seed below), *not* validated.
2. **The seed is now fixed** (`random.seed(20261008)`, `power_DB.py` L61), so new
   countries at least draw the *same* arbitrary fleet every run.
3. **The date-lookup bug is fixed in code** but its effect is overwritten by the
   pin for NL+BE. Fixing it alone retires almost the whole thermal fleet before
   2030 (BE nuclear -> 0) because `DateIn` + catalogue `lifetime` expires for
   plants commissioned in the 1960s-70s and `DateRetrofit` is never read. That
   needs a proper life-extension convention before it can be used - out of scope
   for this run, raise with authors.
4. The pin does not make the baseline fleet *correct*, only *constant*.
