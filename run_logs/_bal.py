import pickle, pandas as pd
B=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
n=B["co2net"]; cp=B["co2pipe"]
for y in ["2040","2050"]:
    cap=n[(n["role"].astype(str)=="captured")&(n["year"].astype(str).str.startswith(y))].copy()
    cap["ctry"]=cap["region"].astype(str).str[:2]
    be_cap=cap[cap["ctry"]=="BE"]["co2"].sum()
    # BE consumption of CO2 (e-fuels etc)
    use=n[(n["role"].astype(str)!="captured")&(n["year"].astype(str).str.startswith(y))].copy()
    use["ctry"]=use["region"].astype(str).str[:2]
    be_use=use[(use["ctry"]=="BE")&(~use["tech"].astype(str).str.contains("injection",case=False,na=False))]["co2"].sum()
    c=cp[cp["year"].astype(str).str.startswith(y)].copy()
    c["o"]=c["origin"].astype(str).str[:2]; c["d"]=c["dest"].astype(str).str.replace("CO2_","",regex=False).str[:2]
    exp=c[(c["o"]=="BE")&(c["d"]=="NL")]["co2"].sum()
    imp=c[(c["o"]=="NL")&(c["d"]=="BE")]["co2"].sum()
    print(f"{y}: BE captured={be_cap:12,.1f}  BE other-use={be_use:11,.1f}  BE->NL={exp:11,.1f}  NL->BE={imp:9,.1f}")
    print(f"      net BE export - (captured + imported - used) = {exp - (be_cap + imp + be_use):,.1f}")
