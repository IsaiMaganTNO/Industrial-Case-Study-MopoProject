import pandas as pd
R=pd.concat([pd.read_csv(rf"final_runs_pessimistic_ccs\report_2050\1_industry_routes_{g}_2050.csv") for g in "AB"]).drop_duplicates()
R=R[R.share_pct>0.5]; R["s"]=R.route_type.str.split().str[0]+":"+R.share_pct.round(0).astype(int).astype(str)
print(R.groupby(["sector","run"]).s.apply(" ".join).unstack()[["IC1","CTRY","MR","NATCAP","RP10","CCSOPT"]].to_string())
C=pd.concat([pd.read_csv(rf"final_runs_pessimistic_ccs\report_2050\5_co2_capture_dest_{g}_2050.csv") for g in "AB"]).drop_duplicates()
print(C[C.kind=="captured"].pivot_table(index="item",columns="run",values="mt",aggfunc="sum").round(1).fillna(0).to_string())
