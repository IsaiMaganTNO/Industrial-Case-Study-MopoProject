import pandas as pd
# Independent cross-check: biomass-derived OUTPUT from the energy_supply table,
# which is built by a different code path (postprocess.py) from different rows.
for tag,p in [("summer BASE","reports_summer/Investment_Results.summer_energy_supply.csv"),
              ("3rep","reports_3rep_gurobi/Investment_Results.3rep_gurobi_energy_supply.csv")]:
    d = pd.read_csv(p)
    b = d[d.category=="bioenergy"]
    g = b.groupby("year")["energy"].sum()
    print("== {} bioenergy OUTPUT per year (all carriers)".format(tag))
    print(g.to_string(float_format=lambda v:"{:,.1f}".format(v)))
    print()
