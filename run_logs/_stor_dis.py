import sys; sys.path.insert(0,"tools"); import make_report_figs as M
F=M.F
for k in ["IC1","CTRY","MR","RP10"]:
    for c in ["NL","BE"]:
        s=F.sel(k,"supply",2050); s=s[(s.carrier=="electricity")&(s.energy>0)&(s.cn==c)]
        hit=sum((q(s)) for _,q,_ in M.ELC).astype(bool)
        rest=s[~hit].groupby("tech").energy.sum().div(1e3).round(1); rest=rest[rest>0.1]
        u=M.R.U; ch=u[(u.run==k)&(u.year==2050)&(u.cn==c)&(u.carrier=="electricity")&(u.cat=="Storage charging")].twh.sum()
        print(k,c,"charge",round(ch,1),"| not shown:",dict(rest))
