import pandas as pd,sqlite3
d=pd.ExcelFile(r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx").parse("ind_process_routes_co2_emission")
s=d[d["Industry"].astype(str).str.contains(r"\(LN",regex=True,na=False)]
print(s[["Industry","to_node","unit","2030","2040","2050"]].to_string())
c=pd.ExcelFile(r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx").parse("ind_process_routes_co2_capture")
s2=c[c["Industry"].astype(str).str.contains(r"\(LN",regex=True,na=False)]
print("\ncapture rows:"); print(s2.to_string()[:500])
m=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.hcco2.sqlite",uri=True)
for n,v in m.execute("""SELECT e.name,cast(pv.value as text) FROM parameter_value pv
  JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
  JOIN entity e ON e.id=pv.entity_id
  WHERE pd.name='flow_ratio_equality_coefficient' AND e.name LIKE '(LN+EL)O_BEC1%'"""):
    print("  DB:",n[:74],"=",v[:10])
m.close()
