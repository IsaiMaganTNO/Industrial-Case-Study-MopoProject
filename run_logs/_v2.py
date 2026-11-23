import pandas as pd
pd.set_option("display.width",220); pd.set_option("display.max_colwidth",60)
f=r"verification\global_constraints_industry_case_study.xlsx"
for s in ["userconfig.yaml","scenario_config.yaml"]:
    d=pd.read_excel(f,s,header=None)
    print("#"*110); print(s, d.shape)
    print(d.to_string(max_rows=60))
