import pandas as pd
pd.set_option("display.width",200)
base=r"data-pipelines\europe\_ines-builder\CO2_data_IC1.xlsx"
lo=r"verification\CO2_network(direct_link_ines_builder)\CO2_data_IC1_low_cost.xlsx"
hi=r"verification\CO2_network(direct_link_ines_builder)\CO2_data_IC1_high_cost.xlsx"
for lbl,f in [("CURRENT",base),("LOW",lo),("HIGH",hi)]:
    n=pd.read_excel(f,"network"); s=pd.read_excel(f,"storage"); ns=pd.read_excel(f,"network_to_storage")
    print(f"--- {lbl}")
    print(f"    network tariff: min {n.tariff.min():.5f} max {n.tariff.max():.5f} mean {n.tariff.mean():.5f}")
    print(f"    net_to_storage tariff: min {ns.tariff.min():.5f} max {ns.tariff.max():.5f} mean {ns.tariff.mean():.5f}")
    for col in ["low","medium","high"]:
        if col in s.columns:
            print(f"    storage[{col}]: min {s[col].min():.4f} max {s[col].max():.4f} mean {s[col].mean():.4f}")
