import sqlite3, json, pandas as pd
M = r"runs\3day_mr_frlu_ccslow_ccu_cap16_dac0\input\Final_SpineOpt_Model.tiny.3day.mr_frlu_ccslow_ccu_cap16_dac0.sqlite"
c = sqlite3.connect(M)
for n in ("elec_DE","elec_UK","elec_FR","elec_LU","elec_NLC1"):
    r = c.execute("""select a.name, pv.type, length(pv.value) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id
      join entity e on e.id=pv.entity_id join alternative a on a.id=pv.alternative_id where e.name=? and pd.name='demand'""", (n,)).fetchall()
    print(n, r)
x = pd.read_excel(r"data\Hydro\IC1_parameters_data.xlsx", sheet_name=None)
for s, d in x.items(): print("hydro", s, d.shape, "FR" in d.astype(str).values, "LU" in d.astype(str).values)
