# =============================================================================
# Stage-1 solve (investment planning) - IC1 tiny test model
#
# RUN AS:  pwsh tools\run_solve_live.ps1
# NOT AS:  julia ... > log.txt     (Start-Process -RedirectStandardOutput
#                                   block-buffers stdout; see smoke_build_only.jl note 3)
#
# Guards, in order of importance:
#   1. EXTERNAL RAM/disk monitor (tools/watch_build.ps1). Not in-process: a
#      @async/@spawn watchdog shares the scheduler with a compute-bound solve
#      and stops sampling exactly when it matters.
#   2. IIS disabled. The historical crash that left a host pingable but
#      refusing RDP was SpineOpt computing an IIS on infeasibility, with HiGHS
#      re-solving the un-presolved LP by interior point for a dual ray. Both
#      are memory catastrophes at this size, so both are off.
#   3. time_limit. Bounded failure beats an open-ended grind.
# =============================================================================

using SpineOpt
using Dates
using Printf

const JuMP  = SpineOpt.JuMP
const HiGHS = SpineOpt.HiGHS

const TIME_LIMIT = 172800.0  # 48 hours.
# Run C solved in 31 min, but with the atmosphere CO2 cap slack in 2030/2040
# (171x / 36x headroom, i.e. non-binding). Rescaling that cap to a
# per-representative-day basis makes both periods bind, so the LP relaxation no
# longer hands the MIP a near-feasible start and the branch-and-bound tree can
# be far deeper. 1 h was not a safe bound for that.
#
# 2026-09-28: 6 h -> 48 h, after the 3-representative-day run hit TIME_LIMIT at
# 21,600 s with primal: NO_SOLUTION and an EMPTY results DB (0.23 MB vs 67.57 MB
# for a real run). A dual-simplex run that is stopped early yields NOTHING: the
# basis is dual-feasible but primal-infeasible throughout, and primal
# feasibility is attained only at termination. There is no partial credit, so
# the time limit must be generous enough that we are not throwing away the whole
# run.
#
# Sizing evidence, from run_logs/atmfix_solve.out vs run_logs/3rep_solve.out.
# This is a pure LP - atmfix's total solve time (2,297.7 s) equals its simplex
# time exactly, so there is no branch-and-bound tree and extrapolation is far
# more trustworthy than it would be for a MIP.
#
#   atmfix : 893,361 cols, 675,067 iterations, OPTIMAL at 2,297.7 s
#   3rep   : 3,043,463 cols (3.4x), stopped at 1,659,746 iterations / 21,600 s
#
# Three independent estimates of the 3rep solve time:
#   * iteration count - expect 2.3M-3.4M iterations; we reached 1.66M (~50-70%).
#     Late-run rate was ~76 iter/s, so +2.3 h to +6.4 h => 9.5-12 h total.
#   * scaling exponent - already above 1.83 and unfinished; exponent 2.5 => 14 h,
#     exponent 3 => 25 h.
#   * objective progress - reached 1.9315e6, ~75% of atmfix's 2.571e6 optimum,
#     still in the slow phase before the end-of-run acceleration.
#
# So 12 h is about a coin flip and 24 h probably suffices. 48 h is deliberate
# headroom on an estimate, not a prediction. It is a CEILING, not a commitment:
# the run can be stopped at any point, with the same (empty) outcome as any
# other early stop.
#
# NOTE: a flat primal-infeasibility count is NOT a failure signal. atmfix held
# Pr ~27,000-28,700 for 99% of a run that finished OPTIMAL, then collapsed to
# Pr: 0(0) in its last ~20 s. Do not abort a run because Pr is not falling.

_stamp() = Dates.format(now(), "HH:MM:SS")
say(msg) = (println("[$(_stamp())] $msg"); flush(stdout))

total_ram_gb() = Sys.total_memory() / 2^30
used_ram_gb()  = (Sys.total_memory() - Sys.free_memory()) / 2^30

@eval SpineOpt _compute_and_print_conflict!(m) = @info "IIS computation disabled"

solver = JuMP.optimizer_with_attributes(
    HiGHS.Optimizer,
    HiGHS.ComputeInfeasibilityCertificate() => false,
    # output_flag only controls PRINTING - it cannot change the search or the
    # solution. Without it, branch-and-bound is silent and we cannot tell
    # "converging slowly" from "stuck", which is the same blind-log problem we
    # hit during the build.
    "output_flag"                  => true,
    "log_to_console"               => true,
    "presolve"                     => "on",
    "time_limit"                   => TIME_LIMIT,
    "threads"                      => 8,     # leave cores for the OS so RDP stays responsive
    "simplex_scale_strategy"       => 4,     # model spans ~7.5e13 in magnitude
    # 1e-7 -> 1e-6. In the 3rep run the DUAL infeasibility sum drifted steadily
    # upward across the whole solve while nominally "converged":
    #        28.5 s  Du: 0(8.26e-07)
    #     9,991   s  Du: 0(3.08e-06)
    #    21,148   s  Du: 0(3.66e-06)
    # i.e. it ends ~37x above the 1e-7 bar. HiGHS still accepts this via its
    # RELATIVE tests, but holding that bar forces repeated refactorisation and
    # re-perturbation, which is pure overhead. 1e-6 remains orders of magnitude
    # tighter than the uncertainty in the input data.
    #
    # Note this reverses direction from docs/EU_CASE_MIGRATION.md section 6A.4,
    # which tightened to 1e-9 on the principle "tolerances are tightened, not
    # relaxed" to avoid an "optimal" answer hiding violated energy balances.
    # That principle still stands; this is a knowing, documented exception for a
    # model that does not converge at all. If the solve succeeds, CHECK
    # objective_objective_penalties (it was 0.00 for atmfix) to confirm no
    # balance violation was absorbed as slack.
    "primal_feasibility_tolerance" => 1.0e-6,
    "dual_feasibility_tolerance"   => 1.0e-6,
    "mip_rel_gap"                  => 1.0e-3,
)

baseline = used_ram_gb()
say("STAGE-1 SOLVE - IC1 tiny test model")
say(@sprintf("  RAM in use : %.1f / %.1f GB", baseline, total_ram_gb()))
say(@sprintf("  time limit : %.0f min", TIME_LIMIT / 60))
say("  guard      : external (tools/watch_build.ps1)")
say("  results    : Investment_Results.sqlite")
say("")

# Results alternative name.
#
# Spine Toolbox' own "Run SpineOpt" item writes results into an alternative
# called "<scenario>__<tool name>@<ISO timestamp>". The downstream
# visualization code (src/_visualization/visualization.py:125) *splits on "@"*
# to recover the scenario and the run timestamp, so a bare "Base" alternative
# makes it raise ValueError. We call run_spineopt directly, so we have to
# supply the same convention ourselves.
const SCENARIO = get(ENV, "IC1_SCENARIO", "ic1_tiny__Run_Model_Planning")
const RESULT_ALTERNATIVE = string(SCENARIO, "@", Dates.format(now(), "yyyy-mm-ddTHH:MM:SS"))
say("  alternative: $RESULT_ALTERNATIVE")

t0 = time()
m = run_spineopt(
    ARGS...;
    mip_solver=solver,
    lp_solver=solver,
    log_level=3,
    alternative=RESULT_ALTERNATIVE,
)
dt = time() - t0

say("")
say(@sprintf("RUN FINISHED in %.1f min", dt / 60))
say(@sprintf("  RAM at start : %.1f GB", baseline))
say(@sprintf("  RAM at end   : %.1f GB", used_ram_gb()))

try
    jm = m isa JuMP.Model ? m : m.ext[:spineopt].model
    say("  termination  : $(JuMP.termination_status(jm))")
    say("  primal       : $(JuMP.primal_status(jm))")
    if JuMP.primal_status(jm) == JuMP.MOI.FEASIBLE_POINT
        say(@sprintf("  objective    : %.6g", JuMP.objective_value(jm)))
    end
catch e
    say("could not read solution status: $e")
end
