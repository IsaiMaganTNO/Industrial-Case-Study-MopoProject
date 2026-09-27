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

const TIME_LIMIT = 3600.0   # 1 hour for this first attempt

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
    "primal_feasibility_tolerance" => 1.0e-7,
    "dual_feasibility_tolerance"   => 1.0e-7,
    "mip_rel_gap"                  => 1.0e-3,
)

baseline = used_ram_gb()
say("STAGE-1 SOLVE - IC1 tiny test model")
say(@sprintf("  RAM in use : %.1f / %.1f GB", baseline, total_ram_gb()))
say(@sprintf("  time limit : %.0f min", TIME_LIMIT / 60))
say("  guard      : external (tools/watch_build.ps1)")
say("  results    : Investment_Results.sqlite")
say("")

t0 = time()
m = run_spineopt(ARGS...; mip_solver=solver, lp_solver=solver, log_level=3)
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
