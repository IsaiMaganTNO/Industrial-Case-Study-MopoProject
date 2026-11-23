import pickle, pandas as pd, re
pd.set_option("display.width",250); pd.set_option("display.max_rows",300)
d=pickle.load(open(r"run_logs\nb_ccslow_ccu_cap16_dac0_NLBE.pkl","rb"))
s=d["supply"]
print("== heat/cool techs"); print((s[s.carrier.isin(["heat","cooling"])].groupby(["carrier","category","tech","year"]).energy.sum()/1e3).round(1).unstack().to_string())
f=d["fleet"]; print("== fleet techs with furnace/boiler/heat/kiln/el"); print(sorted(f[f.tech.str.contains("furn|boil|heat|kiln|e-|electr|resist",case=False)].tech.unique()))
print("== 'other' category fleet techs"); print(sorted(f[f.category=="other"].tech.str.replace(r"_(BE|NL)C\d.*$","",regex=True).unique()))
