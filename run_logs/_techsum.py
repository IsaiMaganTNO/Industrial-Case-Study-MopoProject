import re, io, os, sqlite3
R = [
 ("A","NL+BE regional clusters", r"final_runs_pessimistic_ccs\1_IC1_NLBE_17zones\3day_nb_ccslow_ccu_cap16_dac0_solve.out", r"final_runs_pessimistic_ccs\1_IC1_NLBE_17zones\output\Investment_Results.3day_nb_ccslow_ccu_cap16_dac0.sqlite"),
 ("A","NL+BE country level", r"final_runs_pessimistic_ccs\2_CountryLevel_NLBE\3day_nb_ctry_ccslow_ccu_cap16_dac0_solve.out", r"final_runs_pessimistic_ccs\2_CountryLevel_NLBE\output\Investment_Results.3day_nb_ctry_ccslow_ccu_cap16_dac0.sqlite"),
 ("A/B","Mixed resolution", r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\3day_mr_ccslow_ccu_cap16_dac0_solve.out", r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\output\Investment_Results.3day_mr_ccslow_ccu_cap16_dac0.sqlite"),
 ("B","National CO2 caps", r"final_runs_pessimistic_ccs\5_MixedRes_CountryCO2caps_emitter_credit\solve log\ctryco2B_mr_ccslow_ccu_cap16_dac0_solve.out", r"final_runs_pessimistic_ccs\5_MixedRes_CountryCO2caps_emitter_credit\output\Investment_Results.ctryco2B_mr_ccslow_ccu_cap16_dac0.sqlite"),
 ("B","10 repr. days", r"runs\rp10_mr_noblend\10day_noblend_mr_ccslow_ccu_cap16_dac0_solve.out", r"runs\rp10_mr_noblend\output\Investment_Results.10day_noblend_mr_ccslow_ccu_cap16_dac0.sqlite"),
 ("B","Optimistic CCS", r"final_runs_pessimistic_ccs\6_MixedRes_OptimisticCCS\solve log\mr_ccsopt_ccu_dac0_solve.out", r"final_runs_pessimistic_ccs\6_MixedRes_OptimisticCCS\output\Investment_Results.mr_ccsopt_ccu_dac0.sqlite"),
 ("B","With FR + LU", r"xpress_server_v4\solve_xpress.log", r"xpress_server_v4\Investment_Results.3day_mr_frlu_ccslow_ccu_cap16_dac0.v4.xpress.sqlite"),
]
def el(s):
    m=re.search(r"elapsed time: (.*?)(?:,? \d+ milliseconds|$)",s); t=m.group(1) if m else ""
    h=sum(int(n)*{"day":86400,"hour":3600,"minute":60,"second":1}[u.rstrip("s")] for n,u in re.findall(r"(\d+) (days?|hours?|minutes?|seconds?)",t)); return h
def hm(s): return f"{s//3600}h {s%3600//60:02d}m" if s else "n/a"
rows=[]
for g,n,log,db in R:
    raw=open(log,"rb").read(); t=raw.decode("utf-16") if raw[:2]==b"\xff\xfe" else raw.decode("utf-8","ignore"); d={"g":g,"n":n}
    d["solver"]="Xpress 9.7" if "FICO Xpress" in t else ("Gurobi "+re.search(r"Gurobi Optimizer version ([\d.]+)",t).group(1) if "Gurobi Optimizer" in t else ("HiGHS" if "HiGHS" in t else "?"))
    m=re.search(r"Optimize a model with (\d+) rows, (\d+) columns and (\d+) nonzeros",t) or re.search(r"Original problem has:\s*(\d+) rows\s+(\d+) cols\s+(\d+) elements",t)
    d["rows"],d["cols"],d["nz"]=m.groups() if m else ("","","")
    m=re.search(r"Presolved: (\d+) rows, (\d+) columns",t) or re.search(r"Presolved problem has:\s*(\d+) rows\s+(\d+) cols",t)
    d["prows"],d["pcols"]=m.groups() if m else ("","")
    b=[l for l in t.splitlines() if l.startswith("Build complete")]; d["build"]=el(b[-1]) if b else 0
    s=[l for l in t.splitlines() if l.startswith("Solve complete")]; d["solve"]=el(s[-1]) if s else 0
    e=[l for l in t.splitlines() if l.startswith("Execution complete")]; d["total"]=el(e[-1]) if e else 0
    m=re.search(r"Barrier solved model in (\d+) iterations and ([\d.]+) seconds",t); d["bar"]=f"{m.group(1)} it / {float(m.group(2))/60:.0f} min" if m else ""
    m=re.search(r"Crossover time: ([\d.]+) seconds",t); d["xo"]=f"{float(m.group(1))/60:.0f} min" if m else ""
    m=re.findall(r"RAM at end\s*:\s*([\d.]+) GB",t); d["ram"]=m[-1] if m else ""
    m=re.findall(r"termination\s*:\s*(\w+)",t); d["term"]=m[-1] if m else ("OPTIMAL" if "Optimal" in t else "?")
    m=re.findall(r"(?:Optimal objective\s+|Final objective\s*:\s*)([\d.e+]+)",t); d["obj"]=float(m[-1]) if m else None
    c=sqlite3.connect(db)
    def val(p):
        r=c.execute("select pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id where pd.name=?",(p,)).fetchall(); return len(r)
    d["dbobj"]=None
    try:
        import json
        r=c.execute("select pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id where pd.name='total_costs'").fetchall()
        tot=0
        for (v,) in r:
            v=json.loads(v); dd=v.get("data",v)
            tot+=sum(x[1] if isinstance(x,list) else x for x in (dd if isinstance(dd,list) else dd.values()))
        d["dbobj"]=tot
    except Exception as ex: d["dbobj"]=str(ex)[:30]
    m=re.search(r"Execution started at (\S+)",t) or re.search(r"Build started at (\S+)",t); d["date"]=m.group(1)[:10] if m else ""
    rows.append(d)
for d in rows: print({k:(hm(v) if k in("build","solve","total") else v) for k,v in d.items()})
import pickle; pickle.dump(rows,open("run_logs/_techsum.pkl","wb"))
