# =============================================================================
# SpineOpt run wrapper - IC1 / eu-case-migration, LOCAL TESTING CONFIGURATION
# Do NOT upstream this file as-is.
#
# Purpose: run stage 1 (investment planning) without rendering the machine
# unreachable. A previous run on another host left it pingable but refusing
# RDP, which is the signature of memory pressure starving interactive
# services rather than an outright crash.
#
# Three protections, in order of importance:
#   1. RAM watchdog   - aborts the process before the OS starts thrashing.
#   2. Disk watchdog  - result writes are multi-GB; a full system disk makes
#                       Windows unreachable just as effectively as no RAM.
#   3. IIS / dual-ray suppression - the original crash cause (see doc 4.2).
# =============================================================================

using SpineOpt
using Dates
using Printf

const JuMP  = SpineOpt.JuMP
const HiGHS = SpineOpt.HiGHS

# --- Tunables ----------------------------------------------------------------
const RAM_ABORT_FRACTION = 0.70    # abort if total system RAM use exceeds this
const DISK_ABORT_FREE_GB = 20.0    # abort if free space on the output drive drops below
const WATCHDOG_PERIOD_S  = 10      # how often to check
const SOLVER_TIME_LIMIT  = 4 * 3600.0   # 4 hours, per operator request

# --- Helpers -----------------------------------------------------------------
total_ram_gb() = Sys.total_memory() / 2^30
used_ram_gb()  = (Sys.total_memory() - Sys.free_memory()) / 2^30

function free_disk_gb(path::AbstractString)
    try
        drive = splitdrive(abspath(path))[1]
        isempty(drive) && return Inf
        out = read(`powershell -NoProfile -Command "(Get-PSDrive $(drive[1])).Free"`, String)
        return parse(Float64, strip(out)) / 2^30
    catch
        return Inf   # never let the guard itself break the run
    end
end

ts() = Dates.format(now(), "HH:MM:SS")

# --- Watchdog ----------------------------------------------------------------
# Runs on a separate thread. Julia cannot reliably cap its own heap, so instead
# we observe and exit cleanly while the OS is still responsive. exit() here is
# deliberate: a controlled abort we can diagnose beats an unreachable machine.
#
# THREADING REQUIREMENT - this wrapper MUST be launched with more than one
# thread, e.g.  julia --threads=4 --project=jenv run_spineopt.jl ...
#
# `@async` only creates a task on the *current* thread. With the default
# nthreads()==1 that task is cooperative: it runs only when the main task
# yields, so during a long compute-bound model build it can be starved for
# many minutes - measured silent for >10 min during an IC1 build smoke test.
# A starved watchdog cannot abort anything, which is precisely the scenario
# that left the previous host unreachable.
#
# `Threads.@spawn` on a multithreaded runtime puts the watchdog on its own
# thread, where it keeps sampling regardless of what the build is doing.
# The check below refuses to run single-threaded rather than provide a
# guard that only appears to work.
function start_watchdog(outdir::AbstractString)
    if Threads.nthreads() < 2
        error("""
              run_spineopt wrapper started with nthreads() == $(Threads.nthreads()).
              The RAM/disk watchdog cannot run reliably on a single thread: it would
              only be scheduled when the model build yields, which during a long
              build may be never.
              Relaunch with at least 2 threads, e.g.
                  julia --threads=4 --project=jenv <this script> <args>
              """)
    end
    Threads.@spawn begin
        peak = 0.0
        while true
            sleep(WATCHDOG_PERIOD_S)
            used = used_ram_gb()
            tot  = total_ram_gb()
            peak = max(peak, used)
            frac = used / tot

            if frac > RAM_ABORT_FRACTION
                @error @sprintf("[%s] WATCHDOG ABORT: RAM %.1f/%.1f GB (%.0f%%) exceeded %.0f%% limit. Peak %.1f GB.",
                                ts(), used, tot, 100frac, 100RAM_ABORT_FRACTION, peak)
                flush(stderr); flush(stdout)
                exit(97)
            end

            freegb = free_disk_gb(outdir)
            if freegb < DISK_ABORT_FREE_GB
                @error @sprintf("[%s] WATCHDOG ABORT: only %.1f GB free on output drive (limit %.1f GB).",
                                ts(), freegb, DISK_ABORT_FREE_GB)
                flush(stderr); flush(stdout)
                exit(98)
            end

            @info @sprintf("[%s] watchdog: RAM %.1f/%.1f GB (%.0f%%), peak %.1f GB, disk free %.1f GB",
                           ts(), used, tot, 100frac, peak, freegb)
        end
    end
end

# --- Crash protection (see EU_CASE_MIGRATION.md 4.2) -------------------------
# On infeasibility SpineOpt computes an IIS, and HiGHS re-solves the un-presolved
# LP by interior point to get a dual ray. Both are memory catastrophes on a model
# this size. The atmosphere balance_penalty slack should make infeasibility
# unlikely, but this stays as a backstop.
@eval SpineOpt _compute_and_print_conflict!(m) = @info "IIS computation disabled (local testing configuration)"

# --- Solver -------------------------------------------------------------------
# IMPORTANT: passing mip_solver/lp_solver here means SpineOpt uses THIS solver and
# never reads `solver_mip_options` from the database. See SpineOpt
# src/run_spineopt.jl: `_solver(f::Function, given_solver) = given_solver`,
# documented as "If given solver is not `nothing`, just return it."
#
# Consequence: the EU case's DB settings - including Gurobi's NumericFocus=2 -
# are inert for us. Every solver option we want must be set HERE.
#
# Numerical conditioning: the EU model spans |v| in [3.3e-08, 2.5e+06], a dynamic
# range of ~7.5e13, and still solves - under Gurobi with NumericFocus=2. HiGHS has
# no direct equivalent, so we approximate it:
#   * simplex_scale_strategy=4 (max scaling) attacks the range directly, which is
#     the right lever for a badly-scaled matrix - better than floors on input data,
#     which would distort the economics to fix a symptom.
#   * tolerances tightened 1e-7 -> 1e-9 so "optimal" means optimal in absolute
#     terms too. This targets the reported "optimal but discarded on tolerance"
#     symptom, which is what you see when a solution passes a relative test while
#     still violating constraints absolutely.
#   * mip_rel_gap 1e-4 -> 1e-3. Deliberately LOOSER: a 0.1 % optimality gap is far
#     below the uncertainty in the input data, and insisting on 0.01 % can cost
#     hours of branching for a difference nobody can defend.
#
# Algorithm selection is left to HiGHS (`solver` stays at its default "choose",
# `simplex_strategy` at 1 = dual). We do not pin the method: this model has never
# solved, so removing an option HiGHS might need is premature.
#
# But ipm_optimality_tolerance MUST be tightened alongside the feasibility
# tolerances. Its default is 1e-8, i.e. LOOSER than the 1e-9 we demand, so if
# HiGHS chooses interior point it would stop at a point that cannot satisfy our
# own feasibility bar - reproducing the "optimal but discarded" symptom exactly.
# IPM is demonstrably reachable here: the dual-ray computation that crashed the
# previous host was HiGHS re-solving the LP by interior point (see doc 4.2).
solver = JuMP.optimizer_with_attributes(
    HiGHS.Optimizer,
    HiGHS.ComputeInfeasibilityCertificate() => false,
    "presolve"                     => "on",
    "time_limit"                   => SOLVER_TIME_LIMIT,
    "threads"                      => 8,        # leave cores for the OS so RDP stays responsive
    "parallel"                     => "on",
    "simplex_scale_strategy"       => 4,        # default 2; 4 = max scaling
    "primal_feasibility_tolerance" => 1.0e-9,   # default 1e-7
    "dual_feasibility_tolerance"   => 1.0e-9,   # default 1e-7
    "ipm_optimality_tolerance"     => 1.0e-9,   # default 1e-8; must match the above
    "mip_feasibility_tolerance"    => 1.0e-7,   # default 1e-6
    "mip_rel_gap"                  => 1.0e-3,   # default 1e-4, loosened on purpose
)

@info @sprintf("[%s] starting run_spineopt | RAM %.1f GB total | time_limit %.0f s | RAM abort at %.0f%% | disk abort below %.0f GB",
               ts(), total_ram_gb(), SOLVER_TIME_LIMIT, 100RAM_ABORT_FRACTION, DISK_ABORT_FREE_GB)

start_watchdog(pwd())

m = run_spineopt(ARGS...; mip_solver=solver, lp_solver=solver)

@info @sprintf("[%s] run_spineopt returned. Peak RAM observed %.1f GB.", ts(), used_ram_gb())
