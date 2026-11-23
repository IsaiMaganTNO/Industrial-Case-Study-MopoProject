import pandas as pd, os, re
B=r"verification\Data - IC1 and PECD1"
T={"NO","DE","DK","UK"}
def chk(tag,have):
    have=set(str(x).strip() for x in have)
    miss=sorted(T-have)
    print(f"  {tag[:46]:48} {'OK  ' if not miss else 'MISS'} present={sorted(T&have)} missing={miss}")

print("=== demand / buildings / transport ===")
d=pd.read_csv(os.path.join(B,"Rdemand","other_electricity_demand.csv"),sep=";",nrows=2)
chk("Rdemand hourly elec",d.columns)
d=pd.read_csv(os.path.join(B,"Buildings","scenario_total_yearly_demands_GWh.csv"),sep=";",nrows=2)
chk("Buildings yearly demand",d.columns)
d=pd.read_csv(os.path.join(B,"Buildings","simplified_capacities_with_decommissioning_MW.csv"),sep=";",nrows=2)
chk("Buildings capacities",d.columns)
d=pd.read_csv(os.path.join(B,"Buildings","peak_to_yearly_demand_ratios_MW_GWh.csv"),sep=";",nrows=2)
chk("Buildings peak ratios",d.columns)
t=pd.read_csv(os.path.join(B,"Transport","fleets_per_scenario.csv"))
chk("Transport fleets",t["Country code"])

print("\n=== gas ===")
xl=pd.ExcelFile(os.path.join(B,"Gas","Gas_Sectors_Dataset.xlsx"))
for s in ["CH4_Production","CH4_Storage","CH4_Network","H2_Production","H2_Storage","H2_Network"]:
    g=xl.parse(s); allv=pd.concat([g[c].astype(str) for c in g.columns])
    chk("Gas "+s,allv)

print("\n=== hydro (critical for NO) ===")
xh=pd.ExcelFile(os.path.join(B,"Hydro","EU_parameters_data_20260215_version1.xlsx"))
for s in xh.sheet_names:
    h=xh.parse(s); allv=pd.concat([h[c].astype(str) for c in h.columns])
    chk("Hydro "+s,allv)

print("\n=== biomass / industry / powerplants ===")
bm=pd.read_csv(os.path.join(B,"Biomass","db_biomass_ener_mopo.csv"),usecols=["nuts0"])
chk("Biomass nuts0",bm.nuts0)
xi=pd.ExcelFile(os.path.join(B,"Industry","technology_catalogue_ind_nuts0_nuts3_update.xlsx"))
for s in ["ind_production_2018_nuts0","ind_production_30_50_nuts0"]:
    i=xi.parse(s); allv=pd.concat([i[c].astype(str) for c in i.columns])
    chk("Industry "+s,allv)
NAMES={"Germany":"DE","Denmark":"DK","Norway":"NO","United Kingdom":"UK"}
pp=pd.read_csv(os.path.join(B,"Energy_Conversion","powerplants.csv"),usecols=["Country"])
chk("Powerplants",[NAMES.get(c,c) for c in pp.Country.astype(str).unique()])

print("\n=== networks ===")
et=pd.read_csv(os.path.join(B,"Electricity_Transmission","Electricity_Transmission.csv"))
chk("Elec transmission nodes",pd.concat([et.From_node,et.To_node]))
cg=pd.read_csv(os.path.join(B,"Cargo","cargo_network.csv"),sep=";")
chk("Cargo network",pd.concat([cg["from"],cg["to"]]) if "from" in cg.columns else [])
