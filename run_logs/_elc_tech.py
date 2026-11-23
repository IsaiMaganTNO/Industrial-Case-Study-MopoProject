import sys; sys.path.insert(0,"tools")
import make_report_2050 as R
F=R.F
for k in F.D:
    s=F.sel(k,"supply",2050); s=s[(s.carrier=="electricity")&(s.energy>0)&s.cn.isin(["NL","BE"])]
    print(k, s.groupby(["tech","cn"]).energy.sum().div(1e3).round(1).loc[lambda x:x>0.5].to_dict())
