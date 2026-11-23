import pandas as pd,re,sqlite3,collections
f=r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx"
d=pd.ExcelFile(f).parse("ind_process_routes_co2_emission")
d["Industry"]=d["Industry"].astype(str)
m=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite",uri=True)
CO2={"coal","CH4","HC","crude","waste"}
mode=collections.defaultdict(lambda:{"fuel":set(),"route":False})
for (n,) in m.execute("""SELECT e.name FROM entity e JOIN entity_class ec ON ec.id=e.class_id
  JOIN parameter_value pv ON pv.entity_id=e.id
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  WHERE ec.name='unit_flow__unit_flow' AND pd.name='flow_ratio_equality_coefficient'
    AND e.name LIKE '%__atmosphere__%'"""):
    p=n.split("__")
    k=re.sub(r'_(NL|BE)C\d+$','',p[2])
    if k in CO2: mode[p[0]]["fuel"].add(k)
    else: mode[p[0]]["route"]=True
pure=[u for u,v in mode.items() if v["fuel"] and not v["route"]]
fams=sorted(set(re.sub(r'_(NL|BE)C\d+$','',u) for u in pure))
src=set(d["Industry"])
print("%-50s %10s %s"%("fuel-based family","in source?","2050 factor"))
hits=0
for fam in fams:
    row=d[d["Industry"]==fam]
    if len(row):
        hits+=1
        print("%-50s %10s %.4f"%(fam[:50],"YES",row.iloc[0]["2050"]))
    else:
        print("%-50s %10s"%(fam[:50],"no"))
print("\n%d of %d families have route data"%(hits,len(fams)))
m.close()
