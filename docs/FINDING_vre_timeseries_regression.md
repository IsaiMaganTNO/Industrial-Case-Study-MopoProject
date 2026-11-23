# FINDING: VRE time-series regression in the hybrid IC1+PECD1 dataset

Found during PLAN step 2 (VRE aggregation), before writing any aggregation code.
Scripts: `run_logs/_vre5.py` .. `_vre9.py`.

## 1. Two defects in the new files

### (a) Embedded all-NaN junk rows
Several staged files contain rows whose `time` field is a bare `;` and whose data
columns are all NaN. These are not trailing blank lines - they are parsed as real
rows by `pandas.read_csv`.

| file | total rows | junk | good |
|---|---:|---:|---:|
| `wind-on-SP199-HH100/150/200` | 394,032 | 25,848 | 368,184 |
| `wind-on-SP277-HH100`, `-HH200` | 394,488 | 26,304 | 368,184 |
| `wind-on-existing` | 394,488 | 26,304 | 368,184 |
| `solar-PV-no-tracking` | 394,488 | 26,304 | 368,184 |
| the other 11 files | - | 0 | - |

**6 of 18 files affected.** Pre-staging files had **zero** junk rows.

### (b) Weather years truncated 45 -> 42
Good rows fall from 394,488 (45.03 y) to 368,184 (42.03 y). **2022, 2023 and
2024 are absent** from every affected file.

`wind-on-SP277-HH150` is the sole exception: 394,488 good rows, 45 years - so the
new set is **internally inconsistent**, 17 files at 42 y and one at 45 y.

### (c) Date format changes mid-file
First good timestamp `01-01-1980` (DD-MM-YYYY, no time); last `12/31/2021 23:00`
(MM/DD/YYYY with time). Pre-staging files are uniformly `1/1/1980 0:00`.

## 2. Impact on this run: LOW - but only by luck
The active scenario is **wy2009** (`baseline_blended_representative_periods`).

- 2009 is **present and complete: 8,760 hours** in both old and new files.
- IC1 2009 values are **bit-identical** old vs new (BEC1/NLC6/BEC8 maxdiff 0.0e+00).

So the representative-day clustering, which draws on 2009, is unaffected.

**The risk is not to this run but to any run that changes weather year**, and to
any aggregation written naively: a mean over a column containing 26,304 NaNs
silently produces a biased or NaN result. Had I aggregated without checking, the
four new country profiles could have been quietly wrong.

## 3. Required handling
Any code reading these files **must**:
1. Drop rows where `time.strip() == ";"` **before** any arithmetic.
2. Parse dates with `format="mixed"` / `dayfirst` fallback, not a fixed format.
3. Assert the retained row count is a whole multiple of 8,760.
4. Never use `.mean()` on a raw column without an explicit NaN check.

## 4. Recommendation
Proceed with the run - wy2009 is intact and identical. **Do not** use these files
for any multi-weather-year or 2022-24 analysis without regenerating them.

**Raise with authors**: the junk rows, the 42-vs-45-year inconsistency, the
single odd file out, and the mid-file date-format change all point to a flawed
export/concatenation step rather than a modelling choice.
