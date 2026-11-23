import re, glob, os
for f in sorted(glob.glob(r"final_runs_pessimistic_ccs\*\*_solve.out")):
    t = open(f, encoding="utf8", errors="ignore").read(); L = t.splitlines()
    print("=====", os.path.basename(f))
    pats = r"^\[\d\d:\d\d:\d\d\]|^\d+\.\d+ seconds|^Creating|^Adding constraints|^Setting objective|^Optimize a model|^Model fingerprint|^Presolved|^Presolve time|^Barrier solved|^Crossover|^Solved in|^Optimal objective|^Thread count|^Gurobi Optimizer|^Barrier statistics|^ *Dense cols|^ *AA' NZ|^ *Factor NZ|^ *Factor Ops|^Ordering time|^Iteration +Objective|^Root relaxation|^Variable types|^ *\d+ continuous|^Coefficient statistics|^ *Matrix range|^Elapsed|^Solving|^Total|^\s*Objective|^Status|^Wall|^\S+ \S+ solved|^Model status|^Peak|GiB|^ *Concurrent|^Ran |^Solution|^Optimal"
    for l in L:
        if re.search(pats, l) and "variable_" not in l and "constraint_" not in l: print("  ", l.strip()[:150])
