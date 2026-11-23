import pickle, io, csv
rows=pickle.load(open("run_logs/_techsum.pkl","rb"))
def hm(s): return f"{s//3600}h {s%3600//60:02d}m" if s else "n/a"
def M(x): return f"{int(x)/1e6:.2f}" if x else "n/a"
H=["Group","Run","Solver","Rows (M)","Columns (M)","Non-zeros (M)","Rows after presolve (M)","Columns after presolve (M)","Build time","Solve time","Total run time","Peak RAM (GB)","Termination","Objective (M EUR)","Run date"]
T=[]
for d in rows:
    T.append([d["g"],d["n"],d["solver"],M(d["rows"]),M(d["cols"]),M(d["nz"]),M(d["prows"]),M(d["pcols"]),hm(d["build"]),hm(d["solve"]),hm(d["total"]),d["ram"] or "n/a",d["term"].capitalize(),f"{d['obj']:,.0f}",d["date"]])
with open("results_2050_analysis/data/technical_run_overview.csv","w",newline="",encoding="utf-8") as f: w=csv.writer(f); w.writerow(H); w.writerows(T)
md="# Appendix: technical overview of the model runs\n\n"
md+="| "+" | ".join(H)+" |\n|"+"---|"*len(H)+"\n"+"".join("| "+" | ".join(map(str,r))+" |\n" for r in T)
md+="""
Notes:
- All runs are linear programmes solved to optimality, with an optimality tolerance of 1e-6. The objective is the total discounted system cost over 2030-2060 (three investment years, each representing 10 years, 5% discount rate) for the whole modelled area. The model units are GWh and M EUR, so the objective is in M EUR. Objectives can only be compared between runs with the same geographical scope: the two NL+BE-only runs, and the runs with neighbouring countries. The objective values from the solver logs match the total costs in the output databases.
- Model size is the size of the linear programme passed to the solver, before and after presolve.
- Build time is the time SpineOpt needs to build the optimisation model from the input database. Solve time is the time the solver needs, including writing results. Total run time also includes reading the input data.
- Gurobi runs: Gurobi 13.0.3, barrier method followed by crossover, up to 8 threads, on a local workstation (10 cores, 20 logical processors). Peak RAM is the memory in use at the end of the run.
- With FR + LU: solved with FICO Xpress 9.7 on a separate server (up to 96 threads, 383 GB memory available), because Gurobi was not available. Build and solve times are therefore not directly comparable with the other runs, and the peak RAM was not logged.
- All runs except "10 repr. days" use 3 representative days per investment year. "10 repr. days" uses 10, which makes the model about 3.3 times larger and the run about 15 times longer than the Mixed resolution run.
"""
io.open("results_2050_analysis/APPENDIX_technical_run_overview.md","w",encoding="utf-8",newline="\n").write(md)
print(md)
