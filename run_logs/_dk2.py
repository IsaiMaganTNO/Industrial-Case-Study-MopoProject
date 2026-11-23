import pandas as pd
for f in [r"EU_case\data\Gas\CCS_storage_scenarios_mopo.xlsx", r"data\CO2_network\CO2_data_IC1_high_cost.xlsx", r"EU_case\data-pipelines\europe\_ines-builder\CO2_data.xlsx"]:
    for sh,df in pd.read_excel(f,sheet_name=None).items():
        m=df.astype(str).apply(lambda col: col.str.contains(r"\bDK\b|Denmark|storage-DK",regex=True)).any(axis=1)
        print("==",f,sh,df.shape, list(df.columns)[:12]); 
        if m.any(): print(df[m].head(12).to_string(max_colwidth=40))
