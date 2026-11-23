import pandas as pd
p=r"data/Rdemand/other_electricity_demand.csv"
d=pd.read_csv(p, parse_dates=True, index_col=0, nrows=50)   # exactly as demand_DB.py does
print("DEFAULT-COMMA PARSE -> ncols:", len(d.columns))
print("   columns:", list(d.columns)[:3])
print("   index[:2]:", list(d.index[:2]))
d2=pd.read_csv(p, sep=";", parse_dates=True, index_col=0, nrows=50)
print("\nSEMICOLON PARSE -> ncols:", len(d2.columns))
print("   columns:", list(d2.columns)[:8])
print("   index[:2]:", list(d2.index[:2]), type(d2.index[0]))
print("   index dtype:", d2.index.dtype)
