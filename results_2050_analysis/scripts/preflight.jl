# Preflight: load the input DB (data only - no model build, no solver) and check
# that the scenario filter selects the intended alternatives.
# usage: julia preflight.jl <db_url> [nofilter]   -> exit 0 = pass, 2 = fail
using SpineInterface, SpineOpt, Dates
const FILTERS = Dict("tool" => "object_activity_control", "scenario" => "baseline_blended_representative_periods")
url = ARGS[1]; usefilter = !(length(ARGS) > 1 && ARGS[2] == "nofilter")
say(m) = (println("[$(Dates.format(now(), "HH:MM:SS"))] $m"); flush(stdout))
say("preflight on $url  (filter: $(usefilter ? FILTERS["scenario"] : "NONE"))")
usefilter ? using_spinedb(url, SpineOpt; filters=FILTERS) : using_spinedb(url, SpineOpt)
fails = String[]
chk(c, msg) = (c ? say("  ok   $msg") : (say("  FAIL $msg"); push!(fails, msg)))
pv(p; kw...) = try p(; kw..., _strict=false) catch e; "ERR $(sprint(showerror, e))" end
t50 = DateTime(2050)
# 1. CO2 storage: low_CO2 (0.03699) not medium/high (0.05753)
x = pv(SpineOpt.storage_investment_count_fix_cumulative; node=node(Symbol("CO2-storage-NSNL012")), t=t50)
chk(x isa Number && isapprox(x, 0.036986301369863014; rtol=1e-9), "CO2 storage NSNL012 2050 = low_CO2 0.036986 (got $x)")
# 2. flex: GA_flex0 (0.0) not GA_flex20 (0.0003)
x = pv(SpineOpt.storage_investment_count_fix_cumulative; node=node(Symbol("bus-DR_BEC2")), t=t50)
chk(x isa Number && x == 0.0, "bus-DR_BEC2 2050 = GA_flex0 0.0 (got $x)")
# 3. no limited_nuclear-3 group cap
x = pv(SpineOpt.investment_count_total_max_cumulative; investment_group=investment_group(Symbol("nuclear-3")), t=t50)
chk(x === nothing, "no nuclear-3 group cap (got $x)")
# 4. no limited_fossil-CH4 cap
x = pv(SpineOpt.storage_state_max; node=node(Symbol("fossil-CH4")), t=t50)
chk(x === nothing || x == 0, "no fossil-CH4 storage cap (got $x)")
# 5. NL/BE existing fleet as in MR baseline
for u in ("nuclear-3-existing_BEC1", "SCPC-existing_NLC1", "CCGT-existing_NLC3", "bioST-existing_NLC8")
    chk(unit(Symbol(u)) !== nothing, "existing unit present: $u")
end
chk(unit(Symbol("oil-eng-existing_BEC5")) === nothing, "v3-only unit absent: oil-eng-existing_BEC5")
# 6. FR and LU present
chk(node(Symbol("elec_FR")) !== nothing && node(Symbol("elec_LU")) !== nothing, "elec_FR and elec_LU present")
if isempty(fails); say("PREFLIGHT PASSED"); exit(0); else say("PREFLIGHT FAILED ($(length(fails)))"); exit(2); end

