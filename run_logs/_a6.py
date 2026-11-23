import pickle, pandas as pd
pd.set_option("display.width",95); pd.set_option("display.max_rows",300)
d = pickle.load(open("run_logs/retireall.pkl","rb"))
prod = d["prod"]
print("cols:", list(prod.columns))
print("fuels:", sorted(prod.fuel.dropna().unique())[:60])
print()
h2 = prod[prod.fuel.astype(str).str.contains("h2|hydrog",case=False,na=False)]
print("== H2-consuming techs (prod.output) ==")
print(h2.groupby(["tech","year"]).output.sum().unstack().round(1).to_string())
