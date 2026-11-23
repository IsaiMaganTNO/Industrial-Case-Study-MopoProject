import sys; sys.path.insert(0,"tools"); import make_report_figs as M
F=M.F; import collections; tot=collections.Counter()
for k in ["IC1","CTRY","MR","NATCAP","RP10","CCSOPT","FRLU"]:
  for y in [2030,2040,2050]:
    for c in ["NL","BE"]:
        s=F.sel(k,"supply",y); s=s[(s.carrier=="electricity")&(s.energy>0)&(s.cn==c)]
        hit=sum((q(s)) for _,q,_ in M.ELC).astype(bool)
        for t,v in s[~hit].groupby(s.tech.str.replace(r"_[A-Z]{2}C?\d*.*$","",regex=True)).energy.sum().items(): tot[t]+=v/1e3
print({k:round(v,1) for k,v in tot.items()})
u=M.R.U; print(u[u.carrier=="electricity"].cat.unique()); print(u[(u.tech.str.contains("storage"))].groupby(["carrier","cat"]).twh.sum())
