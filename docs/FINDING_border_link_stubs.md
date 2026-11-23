# FINDING: P4 failed - "leaked" countries are pre-existing border links

Date: 2026-10-08.

## The prediction and why it was wrong

I predicted (`PREDICTION_mixedres_build.md` P4) that the 31 data-free gas
regions would not appear in `INES_DB`, having verified that `define_polygons`
returns 21 onshore polygons and none of the 31.

`INES_DB` nonetheless contains entities suffixed AT, CH, CZ, FI, FR, IE, LU,
PL, SE - 111 entities across 3 classes: 44 `link`, 44 `node__link__node`,
23 `node` (e.g. `BEC3_elec_FR`, `BEC6_CH4_LU`).

## Blind spot in my check

I verified the loop that creates **regional entities** and stopped there. But
`ines_target.py` has a *second*, independent path - the cross-border link
builder - which walks transmission/pipeline rows and creates a node + link for
whatever foreign endpoint it finds, regardless of `polygons`. This is the same
category of error as the directed/undirected traversal one: I confirmed one
code path governed the outcome without asking whether another also wrote.

## Why it is benign - measured, not assumed

Baseline (`backups/.../ines_db.sqlite`, 14,966 entities) foreign suffixes:
`DE 64, DK 12, FR 50, LU 15, NO 12, UK 44`.

So FR and LU border nodes were **already there before any of my changes**, and
so were DE/DK/NO/UK as *border stubs*. The mechanism is pre-existing: it is how
BE/NL trade with neighbours outside the modelled area. AT/CH/CZ/FI/IE/PL/SE
appeared now because the full gas workbook carries more network rows than the
IC1 placeholder did.

New counts: `DE 499, DK 419, NO 410, UK 506` - these four have grown ~8-35x
because they are now **full modelled regions** (48 nodes each + their own
technologies), exactly as intended. FR 50->56 and LU 15->17 remain stubs.

## Conclusion

Not a defect. The 9 small-count countries are border stubs carrying
import/export links, consistent with baseline behaviour. No action needed.
Worth a note to the authors that the gas network sheet determines which
foreign stubs exist, so swapping the gas workbook silently changes the set.
