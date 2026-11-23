import sys; sys.path.insert(0,"tools")
import make_report_2050 as R
F=R.F
for k in F.D:
  for y in (2030,2040,2050):
    s=F.sel(k,"supply",y); s=s[(s.carrier=="electricity")&(s.energy>0)&s.cn.isin(["NL","BE"])&s.tech.str.contains("CCGT|OCGT|gas|CC",case=False)]
    g=s.groupby("tech").energy.sum().div(1e3).round(1); g=g[g>0.1]
    if len(g): print(k,y,g.to_dict())
