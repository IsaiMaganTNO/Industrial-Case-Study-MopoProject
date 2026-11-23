# =============================================================================
# Export a SpineOpt model to a solver-neutral MPS file (for solving on another PC)
#
#   julia --project=jenv -t 4 tools\xpress_export\export_mps.jl <db.sqlite> <outdir>
#
# Writes:
#   <outdir>\model.mps.gz        -> goes in the zip (columns x1..xN, rows r1..rM)
#   <outdir>\varnames.txt     -> STAYS HERE; maps xI to the SpineOpt variable name
#   <outdir>\export_info.txt     -> sizes, objective sense, timestamp
#
# Names are replaced by short generic ones because SpineOpt names contain
# spaces/commas, which break MPS parsers. The mapping is used by import_solution.jl.
# =============================================================================
using SpineOpt, Dates, Printf
const JuMP = SpineOpt.JuMP
const MOI  = JuMP.MOI
say(msg) = (println("[", Dates.format(now(), "HH:MM:SS"), "] ", msg); flush(stdout))
db, outdir = ARGS[1], ARGS[2]
mkpath(outdir)
url_in = "sqlite:///" * replace(abspath(db), "\\" => "/")
say("building model from $url_in (optimize=false)")
m = run_spineopt(url_in, nothing; log_level=3, optimize=false, use_model_names=true)
vars = JuMP.all_variables(m)
nv = length(vars)
names = JuMP.name.(vars)
ndup = nv - length(Set(names))
say("variables: $nv  (duplicate names: $ndup)")
ndup == 0 || error("duplicate variable names - name-based import would be ambiguous")
open(joinpath(outdir, "varnames.txt"), "w") do io
    for (i, n) in enumerate(names)
        println(io, "x", i, "\t", n)
    end
end
say("renaming variables/constraints to generic names")
for (i, v) in enumerate(vars)
    JuMP.set_name(v, "x$i")
end
j = 0
for (F, S) in JuMP.list_of_constraint_types(m)
    F == JuMP.VariableRef && continue          # bounds are not rows
    for c in JuMP.all_constraints(m, F, S)
        global j += 1
        JuMP.set_name(c, "r$j")
    end
end
say("rows: $j")
sense = JuMP.objective_sense(m)
f = joinpath(outdir, "model.mps.gz")
say("writing $f")
JuMP.write_to_file(m, f; format=MOI.FileFormats.FORMAT_MPS, print_objsense=true)
open(joinpath(outdir, "export_info.txt"), "w") do io
    println(io, "source_db   = ", abspath(db))
    println(io, "exported    = ", now())
    println(io, "columns     = ", nv)
    println(io, "rows        = ", j)
    println(io, "sense       = ", sense)
    println(io, "integers    = ", count(JuMP.is_integer, vars) + count(JuMP.is_binary, vars))
    println(io, "mps_bytes   = ", filesize(f))
end
say(@sprintf("DONE  model.mps.gz = %.1f MB", filesize(f) / 2^20))

