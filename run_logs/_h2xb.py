import sys; sys.path.insert(0,"tools")
import make_report_figs as M
F=M.F
for k in ("IC1","CTRY","MR"):
  x=F.X[k]["xb"]; x=x[(x.car=="H2")]
  print("==",k); print(x.groupby(["year","o","d"]).v.sum().div(1e3).round(1).loc[lambda s:s.abs()>0.1].to_string())
