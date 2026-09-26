# Local tooling that does not live in the Spine Toolbox project

## `spineopt-plugin/run_spineopt.jl`

A **patched copy** of the `Run SpineOpt` tool script from the SpineOpt Spine Toolbox
plugin. The plugin is installed per-user, outside this repository, at:

    ~\.spinetoolbox\plugins\SpineOpt\specifications\Tool\run_spineopt.jl

which means it does **not** travel with a clone. The copy here exists so the
configuration is reviewable, diffable and recoverable if a machine is lost.

### Installing it on a new machine

1. Install the SpineOpt plugin in Spine Toolbox (*Plugins > Install plugin... > SpineOpt*).
2. Back up the original:

       $p = "$env:USERPROFILE\.spinetoolbox\plugins\SpineOpt\specifications\Tool\run_spineopt.jl"
       Copy-Item $p "$p.ORIGINAL.bak"

3. Copy this file over it:

       Copy-Item tools\spineopt-plugin\run_spineopt.jl $p -Force

### What it changes, and why

| Change | Reason |
|---|---|
| RAM watchdog, aborts at 80 % system memory (exit code 97) | A run on another host left the machine pingable but refusing RDP - the signature of memory pressure starving interactive services. A controlled abort is diagnosable; an unreachable machine is not. |
| Disk watchdog, aborts below 20 GB free (exit code 98) | Result writes are multi-GB (the EU case Investment_Results is 1.05 GB for a model 1/5 our size). A full system disk makes Windows unreachable just as effectively as exhausted RAM. |
| time_limit 4 h (was 1 h) | One hour was not enough for the model to converge. |
| threads => 8 (of 20) | Leaves cores for the OS so the session stays responsive. |
| IIS computation stubbed out | On infeasibility SpineOpt calls MOI.compute_conflict!; a memory catastrophe at this model size. See docs/EU_CASE_MIGRATION.md 4.2. |
| ComputeInfeasibilityCertificate => false | Otherwise HiGHS re-solves the un-presolved LP by interior point to obtain a dual ray. Same problem. |

The watchdog runs on a separate thread and calls `exit()` directly. Julia cannot
reliably cap its own heap, so the strategy is to observe and exit cleanly *while the
OS is still responsive*.

### Caveats

- **Do not upstream this file as-is.** Suppressing IIS is a local testing hack: it
  removes the most useful diagnostic for an infeasible model. If a run comes back
  infeasible and the cause is not obvious, re-enable it on a small model.
- The watchdog thresholds assume a machine with plenty of RAM. On a smaller host,
  80 % may trigger during normal operation - tune RAM_ABORT_FRACTION.
- `free_disk_gb` shells out to PowerShell and returns `Inf` on any error, so the
  guard can never itself break a run.

## Other things that do not travel with a clone

See `docs/EU_CASE_MIGRATION.md` section 9. In short: the Python virtual environment,
the Julia depot, `.spinetoolbox/local/` (machine-specific interpreter paths), the
`data/` inputs, and the `EU_case/` reference databases.
