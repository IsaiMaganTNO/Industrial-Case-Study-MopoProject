using SpineOpt, SpineInterface, HiGHS, JuMP, TulipaClustering, TulipaIO, DataFrames, CSV, DuckDB, Distances, PyCall

println("julia imports OK")
println("PyCall python  = ", PyCall.python)
println("PyCall libpython = ", PyCall.libpython)
