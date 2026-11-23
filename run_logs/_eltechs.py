import sys; sys.path.insert(0,"tools")
import make_report_2050 as R
F=R.F; t={}
for k in F.D:
  for y in (2030,2040,2050):
    s=F.sel(k,"supply",y); s=s[(s.carrier=="electricity")&(s.energy>0)&s.cn.isin(["NL","BE"])]
    for n,v in s.groupby("tech").energy.sum().items():
      if v>100 and not n.startswith(("wind","solar","battery","nuclear")): t.setdefault(n,set()).add(f"{k}{str(y)[2:]}")
for n in sorted(t): print(n, sorted(t[n]))
