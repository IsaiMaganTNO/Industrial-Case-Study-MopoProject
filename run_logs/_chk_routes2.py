import pandas as pd
R=pd.concat([pd.read_csv(rf"final_runs_pessimistic_ccs\report_2050\1_industry_routes_{g}_2050.csv") for g in "AB"]).drop_duplicates()
ab={"Fossil, no capture":"F","Fossil + carbon capture":"FCC","Electricity":"El","Hydrogen":"H2","Methanol from captured CO2":"MeOH","Biomass / scrap / other low-carbon":"Bio"}
R=R[R.share_pct>0.5]; R["s"]=R.route_type.map(ab)+":"+R.share_pct.round(0).astype(int).astype(str)
print(R.groupby(["sector","run"]).s.apply(" ".join).unstack()[["IC1","CTRY","MR","NATCAP","RP10","CCSOPT"]].to_string())
