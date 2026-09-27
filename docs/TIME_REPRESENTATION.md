# Time representation in the Mopo planning workflow

How the temporal structure of the model is built, where a user can change it,
and which parts silently assume things that are not true in general.

Written against the IC1 industrial case (BE+NL, 17 sub-national polygons), but
the mechanics are identical in the pan-European (EU) case.

Applies to: `SpineOpt v1.0.0`, `spinedb_api 0.36.x`, `TulipaClustering`.

---

## 1. The short version

The model has **two independent temporal dimensions**:

| dimension | what it is | typical size |
|---|---|---|
| **investment periods** | the years capacity decisions are made for | 3 (2030, 2040, 2050) |
| **representative periods** | the operational snapshots inside each year | EU: 5 x 24 h. IC1 test: 2 x 1 h |

The operational cost of a full year is approximated by solving only the
representative periods and **weighting** them back up to 8760 hours. So the
model "sees" a whole year without paying for 8760 timesteps.

Total operational timesteps solved =
`n_investment_years x n_representatives x period_duration_hours / resolution`

For the current IC1 test: `3 x 2 x 1h / 1h` = **6 timesteps**.
For the EU reference case: `3 x 5 x 24h / 1h` = **360 timesteps**.

---

## 2. Where the settings live

There are **four** files that control time, in pipeline order. Changing time
correctly usually means touching more than one.

### 2.1 `data-pipelines/europe/userconfig.yaml` - investment periods

This is the main user-facing control for the *investment* dimension.

```yaml
    operations_resolution: "1h"   # timestep length inside a period
    planning_resolution: "365D"   # optimization window built per planning year
    planning_years:               # options: 2030, 2040, 2050 (parameter limitation)
      "2030": ["2030-01-01T00:00:00", 10.0]   # start datetime, years represented
      "2040": ["2041-01-01T00:00:00", 10.0]   # 2041 because 2040 is a leap year
      "2050": ["2050-01-01T00:00:00", 10.0]
```

- `planning_years` defines the investment periods. Each entry is
  `[start_datetime, years_represented]`. `years_represented` is the weight used
  to scale that period's operational cost in the objective.
- **Leap years are handled by hand.** 2040 is a leap year, so the config uses
  2041 instead. This matters because most of the downstream code assumes a
  8760-hour year. If you add a leap year here, expect off-by-24 errors.
- The comment `options: 2030, 2040 and 2050 (parameters limitation)` is real:
  other years are not supported without changes elsewhere (see 4.2).

Consumed by `data-pipelines/europe/_ines-builder/ines_target.py` (~line 264),
which writes them into INES_DB as `period` entities and a `solve_pattern`.

### 2.2 `_clustering/tulipa_call.jl` - representative periods

This is the main control for the *operational* dimension.

```julia
number_of_representatives = 2
number_of_timesteps = 4   # period DURATION in hours
```

- `number_of_representatives` - how many representative periods to cluster the
  year into. EU uses 5.
- `number_of_timesteps` - despite the name, this is the **period duration in
  hours**, passed to `split_into_periods!(...; period_duration = ...)`.
  EU uses 24, i.e. whole days.

The clustering method is also set here (`:convex_hull` by default; `k_means`,
`k_medoids`, `conical_hull` are available) along with the distance metric.

### 2.3 `_planning-input-processsing/scenario_config.yml` - resolution override

```yaml
resolution: "1h"
```

Applied by `scenario_run.py` (~line 174) to **every** `resolution` parameter in
the database whose entity name does not contain `planning`. This overrides
whatever `ines_to_spineopt.py` and `clustering_output.py` wrote.

### 2.4 `.spinetoolbox/project.json` - which steps run

The temporal chain is `clustering_input -> run_clustering -> clustering_output`.
Skipping any of them leaves the model in a half-configured state that usually
still "runs" but solves the wrong problem.

---

## 3. How it actually works, step by step

### Step 1 - `ines_target.py` writes the periods

From `userconfig.yaml` it creates in INES_DB:

```
period y2030  start_time = 2030-01-01T00:00:00  years_represented = 10.0
period y2040  start_time = 2041-01-01T00:00:00  years_represented = 10.0
period y2050  start_time = 2050-01-01T00:00:00  years_represented = 10.0
solve_pattern capacity_planning  time_resolution = 1h  duration = 365D
```

### Step 2 - `ines_to_spineopt.py` builds the temporal blocks

Reads the `solve_pattern` and branches on the number of periods
(`ines_to_spineopt.py` ~line 291):

- **one period** -> single temporal block named `operations`, with
  `has_free_start = True`.
- **several periods** -> one block per period, named `operations_{period}`,
  i.e. `operations_y2030`, `operations_y2040`, `operations_y2050`.

Each block gets `resolution` (from `time_resolution`) and spans a full year
(`block_start` .. `block_start + duration`). Leap years are compensated here too
(`+366 days` branch at ~line 330).

At this point the model would solve **8760 hours per investment year**. The
clustering is what makes that tractable.

### Step 3 - `clustering_input.py` exports the profiles

Pulls every `availability_factor` and `demand` time series out of the model,
min-max scales them, then **averages them into 8 aggregate profiles** by keyword:

```
wind, solar, RoR, reservoir, elec, cool, DHW_or_space,
transport_truck_bus_van_car_rail_aviation_maritime
```

Written to `_clustering/profiles/profiles_wy2009.csv`.

> Note: clustering is done on these 8 aggregates, not on the full set of
> regional profiles. Two regions with opposite wind patterns are averaged
> together before the representative periods are chosen.

### Step 4 - `tulipa_call.jl` clusters

Splits the year into periods of `number_of_timesteps` hours
(8760 / duration = number of periods), then finds
`number_of_representatives` medoids. Writes:

- `results/representative_periods.csv` - which period index each representative is
- `results/weights_{alt}.csv` - for every period, how much weight it puts on each
  representative

Weights per period sum to 1, so total weight across all representatives = 8760 / duration.

### Step 5 - `clustering_output.py` writes it back

For each investment year x representative it creates a temporal block
`representative_period_{year}_{n}`, all collected in a group `all_rps`, and sets:

- `resolution` - hardcoded `"1h"` (later overridden by `scenario_config.yml`)
- `block_start` / `block_end` - the actual wall-clock window of that representative
- `weight` - how many real hours it stands for
- `representative_block_index` - a **globally unique** index across years
  (`year_index * total_rps + n`), so 3 years x 2 reps -> indices 1..6

Finally, on each `operations_y{year}` block it writes
`representative_blocks_by_period`: a map with **one entry per period of the year**
(8760 entries for 1-hour periods) giving the weight vector over all 6
representative blocks. The vector is zero outside the block's own year, which is
what keeps the years independent.

This map is the mechanism that makes `operations_y*` blocks cheap: they still
*declare* a full year, but operational variables are only built on the
representative blocks.

---

## 4. Traps and hardcoded assumptions

### 4.1 `number_of_timesteps` was not actually a free parameter (FIXED)

`clustering_output.py` hardcoded `24` in three places:

```python
block_start = year_start + Timedelta(24*3600*(medoid-1) seconds)
block_end   = year_start + Timedelta(24*3600*medoid seconds)
map_rp      = ... time_index[24*(i-1)] ...
```

Consequences of changing `number_of_timesteps` in `tulipa_call.jl` without
touching this file:

- `number_of_timesteps = 4` -> 2190 periods ->
  `24*(2190-1) = 52536` overruns the 8760-hour index ->
  `IndexError: index 8760 is out of bounds for axis 0 with size 8760`.
- worse, any value **below** 24 that did not overrun would have silently produced
  **wrong block boundaries** - blocks placed at the wrong time of year, pointing
  at the wrong weather - with no error at all.

**Fixed** by deriving the duration from the clustering output instead:

```python
def period_duration_hours():
    alt = read("results/representative_periods.csv").columns[0]
    n_periods = read(f"results/weights_{alt}.csv")["period"].nunique()
    return int(round(8760 / n_periods))
```

The two files can no longer disagree. `number_of_timesteps` is now genuinely
free (verified at 1 h and 4 h).

### 4.2 The investment years are hardcoded in `clustering_output.py`

```python
for year in ["2030","2040","2050"]:
```

appears **twice** (the loop, and the index calculation). This list is *not* read
from `userconfig.yaml`. If you change `planning_years` there, this file will
either crash or silently write blocks for years that do not exist.

This is the "parameters limitation" the `userconfig.yaml` comment refers to.
**Changing the investment years requires editing both files.**

### 4.3 The weather year is hardcoded in three places

`"wy2009"` appears in `clustering_input.py`, `tulipa_call.jl` and in the scenario
list in `scenario_config.yml`. All three must agree.

### 4.4 `resolution` is set three times

`ines_to_spineopt.py` writes it from `solve_pattern.time_resolution`,
`clustering_output.py` hardcodes `"1h"`, and then `scenario_run.py` overwrites
everything that does not contain `planning` with `scenario_config.yml:resolution`.
The last one wins. Changing only `userconfig.yaml:operations_resolution` will
appear to do nothing.

### 4.5 A period shorter than 24 h cannot represent a day

This is a modelling limit, not a bug. With `number_of_timesteps = 4` there is no
day/night cycle; with `= 1` a period is a **single timestep**, so there is no
intra-period dynamics at all and storage cannot charge and discharge within a
period. Such a run is valid for "does the model solve", but no storage, solar or
flexibility result from it is defensible.

Restore `number_of_timesteps = 24` and >= 5 representatives before reporting.

### 4.6 `profiles/` and `results/` must exist

`clustering_input.py` writes to `profiles/` and `clustering_output.py` reads
`results/`. Neither directory is created by the code and both are gitignored
build artefacts, so on a fresh clone the chain fails with
`OSError: Cannot save file into a non-existent directory: 'profiles'`.

Also note `clustering_output.py` guards on `len(os.listdir("results")) != 0` - an
**empty** `results/` directory is silently treated as "clustering not carried
out" and the script exits successfully without writing anything.

---

## 5. Recipes

### Make the model as small as possible (feasibility testing)

```julia
// _clustering/tulipa_call.jl
number_of_representatives = 2
number_of_timesteps = 1
```
-> 6 operational timesteps. Re-run `run_clustering` and `clustering_output`.

### Restore a defensible configuration

```julia
number_of_representatives = 5
number_of_timesteps = 24
```
-> 360 operational timesteps, matching the EU reference case.

### Change the investment years

1. `userconfig.yaml` -> `planning_years`
2. `clustering_output.py` -> **both** `["2030","2040","2050"]` occurrences
3. Re-run from `ines_builder` onwards (the periods are baked into INES_DB).

### Change the operational resolution

`scenario_config.yml` -> `resolution`. Editing `userconfig.yaml` alone will not
take effect (see 4.4).

---

## 6. Quick verification

After `clustering_output`, confirm the structure is what you intended:

```python
from spinedb_api import DatabaseMapping
with DatabaseMapping("sqlite:///.../Final_SpineOpt_Model.sqlite") as db:
    ents = db.get_entity_items()
    reps = [e["name"] for e in ents
            if e["entity_class_name"] == "temporal_block"
            and e["name"].startswith("representative_period")]
    print(len(reps), reps)
    for v in db.get_parameter_value_items(parameter_definition_name="block_start"):
        print(v["entity_byname"][0], v["parsed_value"])
```

Expect `n_years x n_representatives` blocks, each spanning exactly
`number_of_timesteps` hours, and `representative_blocks_by_period` on each
`operations_y*` block with `8760 / number_of_timesteps` entries.

Sanity check: the `weight` values of one year's representatives should sum to
8760 (hours in a year), regardless of how many representatives there are.
