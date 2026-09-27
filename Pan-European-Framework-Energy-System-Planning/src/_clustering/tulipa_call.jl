using TulipaClustering
using TulipaIO
using DataFrames
using DuckDB
using Distances
using CSV

println("WARNING: Check whether there are extreme periods from the loop with the operational assessments")

# --- Temporal resolution -----------------------------------------------------
# EU reference case: 5 representatives x 24 timesteps (5 representative days).
# IC1 is reduced further for FEASIBILITY TESTING ONLY. The question right now is
# whether the model can solve at all, not whether the answer is defensible.
#
# number_of_timesteps is the period DURATION in hours. Below 24 the periods are
# no longer whole days, which degrades intra-day storage cycling and anything
# depending on a diurnal profile (solar above all). A 4-hour period cannot
# represent a day/night cycle; a 1-hour period is a SINGLE timestep, so there is
# no intra-period dynamics whatsoever and storage is degenerate by construction.
#
# This was only tunable after clustering_output.py stopped hardcoding 24 for the
# block boundaries and the representative_blocks_by_period map; it now derives
# the duration from the weights file instead.
#
# RESTORE to number_of_timesteps = 24 (and ideally >= 5 representatives)
# before any result is reported, compared against the EU case, or published.
number_of_representatives = 2
number_of_timesteps = 1   # was 24 (a full day). Smallest possible feasibility test.

function get_data(input_folder,year)
  dir = joinpath(input_folder, "profiles")
  con = DBInterface.connect(DuckDB.DB)
  TulipaIO.create_tbl(con, joinpath(dir, string("profiles","_",year,".csv")); name = "profiles")
  return DBInterface.execute(con, "SELECT * FROM profiles") |> DataFrame
end

input_folder = joinpath(@__DIR__, "")
rp_df = DataFrame()
for alternative in ["wy2009"]
    println("--------",alternative,"--------")

    println("Importing Data")
    clustering_data = get_data(input_folder,string(alternative))
    println("Splitting Periods")
    split_into_periods!(clustering_data; period_duration = number_of_timesteps)

    initial_path = string("results/initial_representative_periods_",alternative,".csv")
    if isfile(initial_path)
        initial_df = DataFrame(CSV.File(initial_path))
        new_number_of_representatives = length(unique(initial_df.period))
        @info "File Uploaded" initial_path size=size(initial_df)
        println("Finding Representative Periods with Extremes")
        clustering_result = find_representative_periods(
            clustering_data,
            new_number_of_representatives;
            initial_representatives = initial_df,
            drop_incomplete_last_period = false,
            method = :convex_hull, # k_means, k_medoids, convex_hull, convex_hull_with_null, conical_hull
            distance = Euclidean(), #Any distance from Distances.jl e.g., SqEuclidean(), or CosineDist()
            # init = :kmcen,
        )
    else
        @warn "File doest not exist in that directory" initial_path
        println("Finding Representative Periods with no Extremes")
        clustering_result = find_representative_periods(
            clustering_data,
            number_of_representatives;
            drop_incomplete_last_period = false,
            method = :convex_hull, # k_means, k_medoids, convex_hull, convex_hull_with_null, conical_hull
            distance = Euclidean(), #Any distance from Distances.jl e.g., SqEuclidean(), or CosineDist()
            # init = :kmcen,
        )
        println("Saving Representative Periods ",alternative, clustering_result.auxiliary_data.medoids)
        #medoids = clustering_result.auxiliary_data.medoids
        rp_df[!,alternative] = clustering_result.auxiliary_data.medoids
        CSV.write(string("results/representative_periods.csv"),rp_df);
    end

    println("Calculating Weights")
    TulipaClustering.fit_rep_period_weights!(
      clustering_result;
      weight_type = :convex, # :dirac, :convex, :conical_bounded
      niters = 1000,
      learning_rate = 1e-3
    )

    println("Writting Results")
    weights = TulipaClustering.weight_matrix_to_df(clustering_result.weight_matrix)
    CSV.write(string("results/weights","_",alternative,".csv"),weights)
    
end
