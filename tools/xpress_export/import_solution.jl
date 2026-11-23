# =============================================================================
# Import an external (Xpress) solution and write a normal SpineOpt results DB
#
#   julia --project=jenv -t 4 tools\xpress_export\import_solution.jl <db.sqlite> <out.sqlite> <exportdir> <solution.csv>
#
# Rebuilds the SAME model (same DB, same SpineOpt), checks every variable name
# against varnames.txt written at export, fixes all variables to the Xpress
# values, deletes the constraints (so no tolerance can make it "infeasible"),
# and lets HiGHS do a trivial solve. SpineOpt then saves results as usual.
# The objective is recomputed from the fixed values and compared with Xpress.
# Duals/prices are not imported (not in the report outputs anyway).
# =============================================================================
using SpineOpt, Dates, Printf
const JuMP = SpineOpt.JuMP
const MOI  = JuMP.MOI
const HiGHS = SpineOpt.HiGHS
say(msg) = (println("[", Dates.format(now(), "HH:MM:SS"), "] ", msg); flush(stdout))
db, out, expdir, solf = ARGS
url_in  = "sqlite:///" * replace(abspath(db), "\\" => "/")
url_out = "sqlite:///" * replace(abspath(out), "\\" => "/")
const SCENARIO = get(ENV, "IC1_SCENARIO", "ic1_tiny__Run_Model_Planning")
alt = string(SCENARIO, "@", Dates.format(now(), "yyyy-mm-ddTHH:MM:SS"))

readgz(f) = readlines(f)
say("reading mapping and solution")
mapping = [split(l, '\t'; limit=2) for l in readgz(joinpath(expdir, "varnames.txt"))]
sol = Dict{String,Float64}()
for l in readgz(solf)[2:end]
    k, v = split(l, ','; limit=2)
    sol[k] = parse(Float64, v)
end
say("mapping $(length(mapping)) vars, solution $(length(sol)) values")
xp_obj = NaN
st = joinpath(dirname(solf), "solve_status.txt")
if isfile(st)
    for l in readlines(st)
        startswith(l, "objective=") && (global xp_obj = parse(Float64, split(l, "=")[2]))
    end
end

function inject!(m)
    vars = JuMP.all_variables(m)
    length(vars) == length(mapping) || error("variable count $(length(vars)) != exported $(length(mapping)) - not the same model")
    nmiss = 0
    for (i, v) in enumerate(vars)
        gen, nm = mapping[i]
        JuMP.name(v) == nm || error("name mismatch at $i: $(JuMP.name(v)) vs $nm - not the same model")
        val = get(sol, gen, nothing)
        val === nothing && (nmiss += 1; val = 0.0)   # column absent from MPS = unused var, value 0
        JuMP.has_lower_bound(v) && JuMP.delete_lower_bound(v)
        JuMP.has_upper_bound(v) && JuMP.delete_upper_bound(v)
        JuMP.is_integer(v) && JuMP.unset_integer(v)
        JuMP.is_binary(v)  && JuMP.unset_binary(v)
        JuMP.fix(v, val; force=true)
    end
    say("fixed $(length(vars)) variables ($nmiss not in solution -> 0)")
    for (F, S) in JuMP.list_of_constraint_types(m)
        F == JuMP.VariableRef && continue
        JuMP.delete(m, JuMP.all_constraints(m, F, S))
    end
    say("constraints removed; trivial solve follows")
end

solver = JuMP.optimizer_with_attributes(HiGHS.Optimizer, "presolve" => "on", "output_flag" => true)
m = run_spineopt(url_in, url_out; mip_solver=solver, lp_solver=solver, log_level=3, alternative=alt) do m
    SpineOpt.add_event_handler!((m, k) -> inject!(m), m, :window_about_to_solve)
end
jm = m isa JuMP.Model ? m : m.ext[:spineopt].model
say("termination : $(JuMP.termination_status(jm))")
obj = JuMP.objective_value(jm)
say(@sprintf("objective (recomputed) : %.10g", obj))
say(@sprintf("objective (Xpress)     : %.10g   rel.diff %.2e", xp_obj, abs(obj - xp_obj) / max(1, abs(xp_obj))))
say("results in $out  (alternative $alt)")

