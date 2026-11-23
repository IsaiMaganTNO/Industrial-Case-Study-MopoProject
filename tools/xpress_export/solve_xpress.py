"""
Solve model.mps.gz with FICO Xpress and write solution.csv  (no Spine/Julia needed)

Setup on the Xpress PC (once):
    pip install xpress          # uses your existing Xpress licence (XPRESS / XPAUTH_PATH env var)
Run:
    python solve_xpress.py                  # default: barrier + crossover
    python solve_xpress.py --method dual    # dual simplex instead
    python solve_xpress.py --threads 16 --timelimit 172800
Bring back:  solution.csv  and  solve_status.txt   (and solve_xpress.log if anything failed)
"""
import argparse, gzip, os, shutil, sys, time

ap = argparse.ArgumentParser()
ap.add_argument("--mps", default="model.mps.gz")
ap.add_argument("--method", choices=["barrier", "dual", "primal"], default="barrier")
ap.add_argument("--threads", type=int, default=0, help="0 = Xpress default (all cores)")
ap.add_argument("--timelimit", type=int, default=172800, help="seconds (default 48 h)")
a = ap.parse_args()

import xpress as xp
here = os.path.dirname(os.path.abspath(__file__))
os.chdir(here)

# Uncompress (Xpress reads plain MPS most reliably).
mps = a.mps
if mps.endswith(".gz"):
    plain = mps[:-3]
    if not os.path.exists(plain):
        print("uncompressing", mps, "...", flush=True)
        with gzip.open(mps, "rb") as fi, open(plain, "wb") as fo:
            shutil.copyfileobj(fi, fo, 64 << 20)
    mps = plain

p = xp.problem()
p.setlogfile("solve_xpress.log")
p.setControl("outputlog", 1)
p.read(mps)
ncol = p.attributes.cols; nrow = p.attributes.rows
print(f"read {mps}: {nrow} rows x {ncol} cols", flush=True)

p.setControl("timelimit", a.timelimit)
if a.threads: p.setControl("threads", a.threads)
p.setControl("defaultalg", {"dual": 2, "primal": 3, "barrier": 4}[a.method])
p.setControl("crossover", 1)          # need a basic (vertex) solution like simplex gives

t0 = time.time()
flag = {"dual": "d", "primal": "p", "barrier": "b"}[a.method]
p.lpoptimize(flag)
dt = time.time() - t0

st = p.attributes.lpstatus            # 1 = optimal
obj = p.attributes.lpobjval
print(f"lpstatus={st} objective={obj:.10g} time={dt:.0f}s", flush=True)
with open("solve_status.txt", "w") as f:
    f.write(f"lpstatus={st}  (1=optimal, 2=infeasible, 4=unfinished, 5=unbounded)\n")
    f.write(f"objective={obj!r}\nseconds={dt:.0f}\nmethod={a.method}\nrows={nrow}\ncols={ncol}\n")
    f.write(f"xpress_version={xp.getversion()}\n")

if st != 1:
    print("NOT OPTIMAL - solution not written. Send back solve_status.txt and solve_xpress.log")
    sys.exit(1)

x = p.getSolution()
names = p.getnamelist(2, 0, ncol - 1)
with open("solution.csv", "w", newline="") as f:
    f.write("name,value\n")
    for n, v in zip(names, x):
        f.write(f"{n},{v!r}\n")
print("wrote solution.csv  ->  send it back together with solve_status.txt")

