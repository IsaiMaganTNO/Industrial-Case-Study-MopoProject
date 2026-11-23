import pandas as pd
for n in ["electricity_supply_mix","hydrogen_supply_mix","co2_system"]:
    a=pd.read_csv(r"reports_v2_biocap365\Investment_Results.3day_biocap365_%s.csv"%n,index_col=0)
    b=pd.read_csv(r"reports_v2_retireall\Investment_Results.3day_retireall_%s.csv"%n,index_col=0)
    print("===",n)
    print("--- biocap365"); print(a.round(1).to_string())
    print("--- retireall"); print(b.round(1).to_string()); print()
