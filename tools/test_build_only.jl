# =============================================================================
# Structure-only test: can SpineOpt BUILD a model from a DB containing
# programmatically-inserted unit_flow__unit_flow entities?
#
# We do NOT solve. Building is where a malformed entity would blow up:
# run_spineopt reads the DB, resolves the `unit_flow` superclass indirection
# and generates constraints. If our hand-written rows were wrong, this is
# where it surfaces - in seconds instead of an hour.
#
# RUN AS:
#   julia --project=jenv tools\test_build_only.jl <model.sqlite>
# =============================================================================

using SpineOpt
using Dates

const JuMP = SpineOpt.JuMP
using Gurobi

const DB = "sqlite:///" * replace(abspath(ARGS[1]), "\\" => "/")

println("=== SpineOpt build-only test ===")
println("db = ", DB)
flush(stdout)

# The DB carries `time_limit` as an Int, which the solver rejects (it wants a
# Float). That is a PRE-EXISTING model setting, nothing to do with the rows
# under test, so we override the solver here rather than touch the DB.
const SOLVER = JuMP.optimizer_with_attributes(
    Gurobi.Optimizer,
    "TimeLimit" => 600.0,
    "OutputFlag" => 0,
)

t0 = now()
try
    # Build the optimisation model without optimising it.
    m = run_spineopt(DB; optimize=false, log_level=1, mip_solver=SOLVER, lp_solver=SOLVER)
    println("BUILD OK  (", round(Dates.value(now() - t0) / 1000, digits=1), " s)")

    # Confirm the inserted flow is actually present as a variable.
    probe = 0
    for k in keys(m.ext[:spineopt].variables[:unit_flow])
        if occursin("oil-eng_NLC1", string(k)) && occursin("atmosphere", string(k))
            probe += 1
            probe <= 3 && println("  var: ", k)
        end
    end
    println("unit_flow vars matching oil-eng_NLC1 -> atmosphere: ", probe)
    println(probe > 0 ? "PASS - inserted row produced a decision variable" :
                        "FAIL - row ignored by SpineOpt")
catch e
    println("BUILD FAILED after ", round(Dates.value(now() - t0) / 1000, digits=1), " s")
    showerror(stdout, e, catch_backtrace())
    println()
    exit(1)
end
