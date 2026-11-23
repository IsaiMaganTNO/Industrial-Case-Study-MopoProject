import sqlite3, json, glob, os
R = {
 "A IC1 NL+BE (17 zones)":      r"final_runs_pessimistic_ccs\1_IC1_NLBE_17zones\output\*.sqlite",
 "B Country NL+BE":             r"final_runs_pessimistic_ccs\2_CountryLevel_NLBE\output\*.sqlite",
 "C MixedRes baseline":         r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\output\*.sqlite",
 "D1 Ctry CO2 caps (storage)":  r"final_runs_pessimistic_ccs\4_MixedRes_CountryCO2caps_storagehost_credit\output\*.sqlite",
 "D2 Ctry CO2 caps (emitter)":  r"final_runs_pessimistic_ccs\5_MixedRes_CountryCO2caps_emitter_credit\output\*.sqlite",
 "E Optimistic CCS":            r"final_runs_pessimistic_ccs\6_MixedRes_OptimisticCCS\output\*.sqlite",
 "F 10 rep days":               r"runs\rp10_mr_noblend\output\*.sqlite",
 "G FR+LU (Xpress)":            r"xpress_server\*.sqlite",
}
def tot(c, name):
    s=0;n=0
    for (t,) in c.execute("select cast(pv.value as text) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id where pd.name=?", (name,)):
        d=json.loads(t)["data"]; v=d.values() if isinstance(d,dict) else [y[1] for y in d]
        s+=sum(x for x in v if isinstance(x,(int,float))); n+=1
    return s,n
for k,g in R.items():
    f=glob.glob(g)
    if not f: print(f"{k:30s} MISSING"); continue
    c=sqlite3.connect(f[0])
    alts=[a for (a,) in c.execute("select name from alternative") if "@" in a]
    tc,_=tot(c,"total_costs"); pen,_=tot(c,"objective_objective_penalties")
    nodes=c.execute("select count(*) from entity e join entity_class ec on ec.id=e.class_id where ec.name='node'").fetchone()[0]
    print(f"{k:30s} total={tc:12,.0f} pen={pen:8.3g} nodes={nodes:5d} alts={len(alts)} {os.path.basename(f[0])}")
