import pandas as pd, numpy as np
LOW=r"verification\CO2_network(direct_link_ines_builder)\CO2_data_IC1_low_cost.xlsx"
HIGH=r"verification\CO2_network(direct_link_ines_builder)\CO2_data_IC1_high_cost.xlsx"
ACT=r"data-pipelines\europe\_ines-builder\CO2_data_IC1.xlsx"
for t,p in [("ACTIVE",ACT),("LOW",LOW),("HIGH",HIGH)]:
    print(t,"sheets:",pd.ExcelFile(p).sheet_names)
a=pd.ExcelFile(ACT); l=pd.ExcelFile(LOW); h=pd.ExcelFile(HIGH)
for s in a.sheet_names:
    da=a.parse(s)
    if s not in l.sheet_names: print(f"  {s}: not in LOW"); continue
    dl=l.parse(s); dh=h.parse(s) if s in h.sheet_names else None
    num=[c for c in da.columns if pd.api.types.is_numeric_dtype(da[c])]
    same_l = da.shape==dl.shape and all(np.allclose(da[c].fillna(-999),dl[c].fillna(-999)) for c in num if c in dl.columns)
    same_h = dh is not None and da.shape==dh.shape and all(np.allclose(da[c].fillna(-999),dh[c].fillna(-999)) for c in num if c in dh.columns)
    print(f"  {s:28} shape{da.shape} vs LOW{dl.shape}  values==LOW:{same_l}  ==HIGH:{same_h}")
