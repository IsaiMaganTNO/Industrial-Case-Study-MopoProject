# =============================================================================
# Build-only smoke test - IC1 / eu-case-migration
#
# Purpose: measure peak RAM and locate the expensive phase during MODEL
# CONSTRUCTION, without committing to a multi-hour solve.
#
# `optimize=false` is SpineOpt's own documented flag ("useful for running
# tests"): it builds the complete model and returns before solving.
#
# RUN AS:   powershell tools\run_build_live.ps1 -DbUrl <url>
# NOT AS:   julia ... > log.txt        (see "visibility" below)
#
# --- Design notes, learned the hard way -------------------------------------
# 1. NO IN-PROCESS WATCHDOG. Julia's @async is cooperative and Threads.@spawn on
#    the default pool still shares GC and scheduler with a compute-bound build,
#    so an in-process watchdog silently stops sampling exactly when it matters.
#    The RAM/disk guard lives in an EXTERNAL PowerShell monitor
#    (tools/watch_build.ps1), which cannot be starved by this process.
#
# 2. NO INSTRUMENTATION OF SPINEOPT. SpineOpt already announces every build
#    phase: run_spineopt_basic.jl wraps each phase in `@timelog`, and each
#    individual add_variable_*! / add_constraint_*! prints "- [name]" plus its
#    elapsed time at log_level >= 3. There is nothing to add.
#    (An earlier attempt monkey-patched internals with a `Vararg{Any}` method.
#    That silently added a LESS specific method alongside the original, so
#    dispatch never reached it - instrumentation that looked installed but
#    produced nothing. Deleted.)
#
# 3. VISIBILITY IS A LAUNCHER CONCERN, NOT A CODE CONCERN.
#    Phase messages appeared to hang for 10+ minutes. The cause was NOT SpineOpt
#    and NOT Julia: it was launching via
#        Start-Process -RedirectStandardOutput <file>
#    which BLOCK-buffers the child's stdout, so output sat in a buffer instead
#    of reaching the log. Spine Toolbox never had this problem because it reads
#    the process stream directly. Piping to Tee-Object does the same thing and
#    needs no code here at all - hence tools/run_build_live.ps1.
#    Several elaborate in-process workarounds (custom IO types, pipe readers,
#    idle-flush tickers) were written for this and then deleted: they were
#    solving a problem created by the launcher.
# =============================================================================

using SpineOpt
using Dates
using Printf

const JuMP  = SpineOpt.JuMP
const HiGHS = SpineOpt.HiGHS

_stamp() = Dates.format(now(), "HH:MM:SS")
say(msg) = (println("[$(_stamp())] $msg"); flush(stdout))

total_ram_gb() = Sys.total_memory() / 2^30
used_ram_gb()  = (Sys.total_memory() - Sys.free_memory()) / 2^30

# IIS computation on infeasibility is a memory catastrophe at this size.
@eval SpineOpt _compute_and_print_conflict!(m) = @info "IIS computation disabled"

solver = JuMP.optimizer_with_attributes(
    HiGHS.Optimizer,
    HiGHS.ComputeInfeasibilityCertificate() => false,
    "presolve" => "on",
    "threads"  => 8,
)

baseline = used_ram_gb()
say("BUILD-ONLY smoke test (optimize=false)")
say(@sprintf("  RAM in use : %.1f / %.1f GB", baseline, total_ram_gb()))
say("  guard      : external (tools/watch_build.ps1)")
say("")
say("Phases below are SpineOpt's own log_level=3 output:")
say("  temporal -> stochastic -> [economic] -> independent variables")
say("  -> dependent variables -> expressions -> constraints -> objective")
say("Each '- [name]' line is one variable/constraint family.")
say("")

t0 = time()
m = run_spineopt(ARGS...; mip_solver=solver, lp_solver=solver, optimize=false, log_level=3)
dt = time() - t0

peak = used_ram_gb()
say("")
say(@sprintf("BUILD COMPLETED in %.1f min", dt / 60))
say(@sprintf("  RAM at start : %.1f GB", baseline))
say(@sprintf("  RAM at end   : %.1f GB  (%+.1f GB)", peak, peak - baseline))

try
    jm = m isa JuMP.Model ? m : m.ext[:spineopt].model
    say(@sprintf("  variables    : %d", JuMP.num_variables(jm)))
    say(@sprintf("  constraints  : %d",
        JuMP.num_constraints(jm; count_variable_in_set_constraints=false)))
catch e
    say("could not introspect JuMP model: $e")
end
