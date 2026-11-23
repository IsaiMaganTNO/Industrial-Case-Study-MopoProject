import pandas as pd,sqlite3
d=pd.ExcelFile(r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx").parse("ind_process_routes_co2_emission")
m=sqlite3.connect("file:%s?mode=ro"%r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.retireall.hcco2.sqlite",uri=True)
# compare sheet value vs DB value for units ALREADY route-based, across BOTH unit conventions
tests=[("CEM2-(Afm)_BEC6","cement_BEC6","CEM2-(Afm)"),
       ("CEM2-(Afm)MEA_BEC6","cement_BEC6","CEM2-(Afm)MEA"),
       ("(NG)DRI-EAF_BEC4","steel-primary_BEC4","(NG)DRI-EAF"),
       ("REF-SMR-MEA_BEC2","HC_BEC2","REF-SMR-MEA")]
print("%-22s %-10s %10s %10s %s"%("unit","sheetunit","sheet","db","match"))
for u,outnode,fam in tests:
    r=d[d["Industry"].astype(str)==fam]
    sv=float(r.iloc[0]["2050"]); su=r.iloc[0]["unit"]
    q=m.execute("""SELECT cast(pv.value as text) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id
      WHERE pd.name='flow_ratio_equality_coefficient' AND e.name=?""",
      ("%s__atmosphere__%s__%s"%(u,u,outnode),)).fetchone()
    db=float(q[0]) if q else float("nan")
    print("%-22s %-10s %10.4f %10.4f %s"%(u[:22],su,sv,db,"YES" if abs(sv-db)<1e-6 else "NO"))
m.close()
