import sys; sys.path.insert(0,"tools"); import make_report_figs as M, pandas as pd
pd.set_option("display.width",250,"display.max_rows",300,"display.max_columns",30)
D="results_2050_analysis/data/"
for f in ["A1_electricity_generation","B1_electricity_generation","A3_electricity_consumption","B3_electricity_consumption","A2_hydrogen_supply","B2_hydrogen_supply","A4_hydrogen_consumption","B4_hydrogen_consumption"]:
    d=pd.read_csv(D+f+".csv"); d=d[d.year==2050]
    p=d.pivot_table(index="item",columns=["label","country"],values="twh",aggfunc="sum").round(1)
    p=p[p.abs().sum(axis=1)>0.05]; print("=====",f); print(p.to_string()); print("TOTAL", p.sum().round(0).to_dict())
X=M.F.X
for k in ["MR","CCSOPT","FRLU","IC1"]:
    x=X[k]["xb"]; x=x[(x.year==2050)&(x.car=="H2")]
    x=x.assign(o2=x.o.str[:2],d2=x.d.str[:2]); x=x[(x.o2!=x.d2)]
    print("== H2 xb",k); print((x.groupby(["o2","d2"]).v.sum()/1e3).round(1).loc[lambda s:s>0.1].to_string())
