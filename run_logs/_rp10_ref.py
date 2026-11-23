import pickle, sqlite3, glob, pandas as pd
hc = pickle.load(open(r"run_logs\_hc_supply_all.pkl", "rb"))
for k in ("MR", "S2"):
    t = pd.Series({key: v for key, v in hc[k].items() if v > 1}).groupby(level=[0, 1, 2]).sum()
    print("==", k, "HC supply by tech/country/year (TWh)"); print(t.unstack(2).round(0).fillna(0).to_string())
# are NL/BE refinery units present in both inputs?
for n, db in [("MR", glob.glob(r"final_runs_pessimistic_ccs\3_*\input\*.sqlite")[0]), ("RP10", glob.glob(r"runs\rp10_mr_noblend\*.sqlite")[0])]:
    c = sqlite3.connect(db)
    u = [r[0] for r in c.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='unit' and e.name like 'REF%' and (e.name like '%NLC%' or e.name like '%BEC%')")]
    print(n, db.split("\\")[-1], "NL/BE REF units:", len(u), sorted(u)[:8])
