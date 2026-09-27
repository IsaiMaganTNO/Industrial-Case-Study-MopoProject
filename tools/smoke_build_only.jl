# =============================================================================
# Build-only smoke test - IC1 / eu-case-migration
#
# Purpose: measure peak RAM and locate the expensive phase during MODEL
# CONSTRUCTION, without committing to a multi-hour solve.
#
# `optimize=false` is SpineOpt's own documented flag ("useful for running
# tests"): it builds the complete model and returns before solving.
#
# --- Design notes, learned the hard way -------------------------------------
# 1. NO IN-PROCESS WATCHDOG. Julia's @async is cooperative and Threads.@spawn
#    still shares the GC and scheduler with a compute-bound build, so an
#    in-process watchdog silently stops sampling exactly when it matters. The
#    RAM/disk guard therefore lives in an EXTERNAL PowerShell monitor
#    (tools/watch_build.ps1) which cannot be starved by this process.
# 2. NO MONKEY-PATCHING for phase reporting. Wrapping SpineOpt internals with a
#    Vararg method silently loses dispatch to the original, more specific method,
#    so the wrapper is never called. SpineOpt already logs every build phase at
#    log_level >= 2; the only real problem was BUFFERING.
# 3. LIVENESS IS MEASURED EXTERNALLY. SpineOpt logs phases with printstyled,
#    which buffers when stdout is a pipe, so a quiet log does NOT mean a hung
#    build. The external monitor's CPU-time and RSS samples are the signal.
# =============================================================================

using SpineOpt
using Dates
using Printf

const JuMP  = SpineOpt.JuMP
const HiGHS = SpineOpt.HiGHS

total_ram_gb() = Sys.total_memory() / 2^30
used_ram_gb()  = (Sys.total_memory() - Sys.free_memory()) / 2^30
ts() = Dates.format(now(), "HH:MM:SS")

say(msg) = (println(msg); flush(stdout))

# On buffering: when stdout is a redirected pipe/file, SpineOpt's phase messages
# (printstyled) can arrive in bursts, so a healthy build can look hung. There is
# no supported way to force-unbuffer Base.stdout from inside the process -
# reaching into its internal `.buffer` field risks silently dropping output,
# which is worse than a late log. Liveness is therefore established by the
# EXTERNAL monitor (rising CPU time and RSS), not by log freshness.
# Our own checkpoints below flush explicitly, so they are always current.

@eval SpineOpt _compute_and_print_conflict!(m) = @info "IIS computation disabled"

solver = JuMP.optimizer_with_attributes(
    HiGHS.Optimizer,
    HiGHS.ComputeInfeasibilityCertificate() => false,
    "presolve" => "on",
    "threads"  => 8,
)

baseline = used_ram_gb()
say(@sprintf("[%s] BUILD-ONLY smoke test (optimize=false)", ts()))
say(@sprintf("[%s]   julia threads : %d", ts(), Threads.nthreads()))
say(@sprintf("[%s]   RAM in use    : %.1f / %.1f GB", ts(), baseline, total_ram_gb()))
say(@sprintf("[%s]   guard         : external (tools/watch_build.ps1)", ts()))
say("")
say("SpineOpt logs each build phase below, in this order:")
say("   temporal structure -> stochastic structure -> [economic structure]")
say("   -> independent variables -> dependent variables -> expressions")
say("   -> constraints -> objective")
say("")

t0 = time()
m = run_spineopt(ARGS...; mip_solver=solver, lp_solver=solver, optimize=false, log_level=3)
dt = time() - t0

peak = used_ram_gb()
say("")
say(@sprintf("[%s] BUILD COMPLETED in %.1f min", ts(), dt/60))
say(@sprintf("   RAM at start : %.1f GB", baseline))
say(@sprintf("   RAM at end   : %.1f GB  (%+.1f GB)", peak, peak - baseline))

try
    jm = m isa JuMP.Model ? m : m.ext[:spineopt].model
    nv = JuMP.num_variables(jm)
    nc = JuMP.num_constraints(jm; count_variable_in_set_constraints=false)
    say(@sprintf("   variables    : %d", nv))
    say(@sprintf("   constraints  : %d", nc))
    say("")
    say("Compare against the EU reference case, which solved successfully.")
catch e
    @warn "could not introspect JuMP model" exception=e
end
