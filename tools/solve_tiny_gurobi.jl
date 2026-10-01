# filepath: c:\Users\maganih\Documents\github-repos\Industrial-Case-Study-MopoProject\tools\solve_tiny_gurobi.jl
# =============================================================================
# Stage-1 solve (investment planning) - IC1 tiny test model - GUROBI VARIANT
#
# This is a COPY of tools/solve_tiny.jl with the solver swapped from HiGHS to
# Gurobi. solve_tiny.jl is deliberately left untouched so the HiGHS results
# remain reproducible.
#
# PURPOSE: controlled comparison. Same model, same checkpoint, ONE variable
# changed (the solver). The reference is the summer run:
#     checkpoints/Final_SpineOpt_Model.tiny.summer.sqlite
#     HiGHS: OPTIMAL, objective 3,019,450, 65.5 min, 547,497 iterations
# If Gurobi returns a materially different objective, that is evidence the
# HiGHS answer is conditioning-limited rather than a property of the model.
#
# WHY TRY GUROBI AT ALL: docs/EU_CASE_MIGRATION.md records that the EU case
# relied on Gurobi with NumericFocus=2. We inherited the model WITHOUT that
# conditioning fix, because HiGHS has no equivalent knob. The scaling warnings
# persist in every run (Cost [3e-07, 2e+06], Bound [4e-07, 1e+07]).
#
# RUN AS:
#   pwsh tools\run_solve_live.ps1 -Script tools\solve_tiny_gurobi.jl `
#        -Db checkpoints\Final_SpineOpt_Model.tiny.summer.sqlite `
#        -Out checkpoints\Investment_Results.summer_gurobi.sqlite `
#        -LogPath run_logs\summer_gurobi_solve.out -Threads 8
#
# Guards are unchanged from solve_tiny.jl:
#   1. EXTERNAL RAM/disk monitor (tools/watch_build.ps1), not in-process.
#   2. IIS disabled. Computing an IIS on this model is a memory catastrophe.
#   3. TimeLimit. Bounded failure beats an open-ended grind.
# =============================================================================

using SpineOpt
using Dates
using Printf

const JuMP = SpineOpt.JuMP
using Gurobi

const TIME_LIMIT = 172800.0  # 48 hours - same ceiling as the HiGHS script.

# NumericFocus: 0 = default (speed), 1-3 = progressively more care with
# numerics at the cost of time. The EU case used 2. We start at 0 so the FIRST
# comparison against HiGHS changes exactly one thing (the solver). Override
# with IC1_NUMERIC_FOCUS=2 for the follow-up run.
const NUMERIC_FOCUS = parse(Int, get(ENV, "IC1_NUMERIC_FOCUS", "0"))

# Method: -1 = concurrent (Gurobi runs dual simplex, primal simplex and barrier
# in parallel and takes whichever finishes first). HiGHS ran dual simplex only.
# Concurrent is Gurobi's real advantage on a badly scaled LP, so we leave it,
# but note this means the comparison is "best-effort vs best-effort", not
# "dual simplex vs dual simplex". Set IC1_GUROBI_METHOD=1 to force dual simplex
# if a like-for-like algorithmic comparison is wanted.
const METHOD = parse(Int, get(ENV, "IC1_GUROBI_METHOD", "-1"))

_stamp() = Dates.format(now(), "HH:MM:SS")
say(msg) = (println("[$(_stamp())] $msg"); flush(stdout))

total_ram_gb() = Sys.total_memory() / 2^30
used_ram_gb()  = (Sys.total_memory() - Sys.free_memory()) / 2^30

@eval SpineOpt _compute_and_print_conflict!(m) = @info "IIS computation disabled"

# -----------------------------------------------------------------------------
# GUROBI LICENCE LOCATION - this is load-bearing, do not remove.
#
# Gurobi finds a WLS licence via GRB_LICENSE_FILE, or by probing a few default
# locations. On this machine the licence lives at C:\gurobi1203\gurobi.lic,
# which is NOT one of the probed defaults, so the variable is REQUIRED.
#
# It must be set BEFORE julia starts. Setting ENV["GRB_LICENSE_FILE"] from
# inside Julia does NOT work - verified both before and after `using Gurobi`,
# both fail - because the native Gurobi library reads the real process
# environment, which Julia's ENV dict does not write through to.
#
# So we can only VALIDATE here, not repair. This check is why the original
# failure was finally diagnosed: the variable had been set in one interactive
# shell and never persisted, so every launched run started without it and died
# minutes in with "Gurobi Error 10009: No Gurobi license found". Isolated tests
# all passed because they ran in the shell that happened to have it - which is
# what made a deterministic bug look intermittent.
#
# It is now persisted at User scope, so shells started fresh inherit it. Note a
# child process inherits its PARENT's environment block, so a shell that was
# already open before the variable was persisted will still not have it.
let lic = get(ENV, "GRB_LICENSE_FILE", "")
    if isempty(lic)
        error("""
        GRB_LICENSE_FILE is not set in this process.

        Gurobi will NOT find the licence at C:\\gurobi1203\\gurobi.lic without
        it, and this cannot be fixed from inside Julia - the native library
        reads the real process environment.

        Set it in the shell BEFORE launching, e.g.:
            \$env:GRB_LICENSE_FILE = "C:\\gurobi1203\\gurobi.lic"

        It is persisted at User scope, so a NEWLY opened shell already has it.
        """)
    elseif !isfile(lic)
        error("GRB_LICENSE_FILE points at a missing file: $lic")
    else
        println("[gurobi] licence file: $lic")
    end
end
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# SHARED GUROBI ENVIRONMENT - this is load-bearing, do not remove.
#
# Passing `Gurobi.Optimizer` bare makes Gurobi.jl create a NEW Env (= a fresh
# WLS licence checkout over the network) every time an optimizer is
# instantiated. SpineOpt instantiates TWICE (mip_solver and lp_solver), several
# minutes into the run, after the 160 MB DB read - so a licence problem
# surfaced only after minutes of wasted build time.
#
# Creating ONE Env up front (the pattern Gurobi.jl documents) checks the
# licence out exactly once, at second 0, where a failure is immediate and
# obvious. Keep this even though the original licence fault is now fixed: it
# both halves the checkouts and makes any future failure fail fast.
#
# The checkout is ALSO retried, as cheap insurance against a genuinely flaky
# network checkout (WLS is a web licence). Note the retries did NOT save the
# original failure, because that cause - a missing GRB_LICENSE_FILE - was
# deterministic, not transient. The retry loop's real value was its diagnostic:
# printing GRB_LICENSE_FILE=<unset> is what identified the actual bug.
function _gurobi_env_with_retry(; attempts::Int=6, delay::Float64=10.0)
    local lasterr
    for i in 1:attempts
        try
            env = Gurobi.Env()
            i > 1 && println("[gurobi] licence checked out on attempt $i")
            return env
        catch err
            lasterr = err
            println("[gurobi] licence checkout attempt $i/$attempts failed; ",
                    "retrying in $(delay)s")
            flush(stdout)
            i < attempts && sleep(delay)
        end
    end
    println("[gurobi] licence checkout FAILED after $attempts attempts.")
    println("[gurobi] Check: gurobi_cl --license   (GRB_LICENSE_FILE=",
            get(ENV, "GRB_LICENSE_FILE", "<unset>"), ")")
    throw(lasterr)
end

const GRB_ENV = _gurobi_env_with_retry()
# -----------------------------------------------------------------------------

solver = JuMP.optimizer_with_attributes(
    () -> Gurobi.Optimizer(GRB_ENV),
    # Printing only - cannot change the search or the solution. Without it the
    # solve is silent and we cannot tell "converging slowly" from "stuck".
    "OutputFlag"     => 1,
    "LogToConsole"   => 1,
    "TimeLimit"      => TIME_LIMIT,
    "Threads"        => 8,          # leave cores for the OS so RDP stays responsive
    "Method"         => METHOD,
    "NumericFocus"   => NUMERIC_FOCUS,
    "Presolve"       => -1,         # automatic
    # Tolerances matched to the HiGHS run (1e-6) so the comparison is fair.
    # Gurobi's FeasibilityTol/OptimalityTol default to 1e-6 anyway; stated
    # explicitly so a future change to solve_tiny.jl does not silently
    # desynchronise the two scripts.
    "FeasibilityTol" => 1.0e-6,
    "OptimalityTol"  => 1.0e-6,
    "MIPGap"         => 1.0e-3,
    # Write a solver-side log alongside ours, for iteration counts and the
    # numerical-condition messages Gurobi emits that HiGHS does not.
    "LogFile"        => get(ENV, "IC1_GUROBI_LOGFILE", "run_logs/gurobi_solver.log"),
)

baseline = used_ram_gb()
say("STAGE-1 SOLVE - IC1 tiny test model - GUROBI")
say(@sprintf("  RAM in use  : %.1f / %.1f GB", baseline, total_ram_gb()))
say(@sprintf("  time limit  : %.0f min", TIME_LIMIT / 60))
say(@sprintf("  Method      : %d  (-1 = concurrent)", METHOD))
say(@sprintf("  NumericFocus: %d", NUMERIC_FOCUS))
say("  licence     : checked out ONCE at startup (shared Env)")
say("  guard       : external (tools/watch_build.ps1)")
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
        say("  HiGHS summer reference: 3.01945e6")
    end
catch e
    say("could not read solution status: $e")
end
