using SpineOpt
const JuMP = SpineOpt.JuMP
const HiGHS = SpineOpt.HiGHS
@eval SpineOpt _compute_and_print_conflict!(m) = @info "IIS disabled"
solver = JuMP.optimizer_with_attributes(HiGHS.Optimizer,
    HiGHS.ComputeInfeasibilityCertificate() => false, "presolve" => "on", "threads" => 8)
m = run_spineopt(ARGS...; mip_solver=solver, lp_solver=solver, optimize=false, log_level=0)
jm = m isa JuMP.Model ? m : m.ext[:spineopt].model
nint = count(v -> JuMP.is_integer(v), JuMP.all_variables(jm))
nbin = count(v -> JuMP.is_binary(v),  JuMP.all_variables(jm))
println("TOTAL VARIABLES : ", JuMP.num_variables(jm))
println("INTEGER         : ", nint)
println("BINARY          : ", nbin)
println("PROBLEM TYPE    : ", (nint+nbin) == 0 ? "LP (continuous)" : "MIP")
