import pickle
for k,v in {"MR":"mr_ccslow_ccu_cap16_dac0","S4":"frlu_mr_ccslow_ccu_cap16_dac0"}.items():
    f=pickle.load(open(rf"run_logs\{v}_NLBE.pkl","rb"))["fleet"]
    q=f[f.tech.str.startswith("nuclear")]
    print(k, q.groupby(["year", q.tech.str.contains("existing")]).units.sum().round(2).to_dict())
