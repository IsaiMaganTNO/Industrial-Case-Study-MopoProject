import sqlite3,glob,json
A=glob.glob(r"final_runs_pessimistic_ccs\3_*\input\*.sqlite")[0]; B=r"runs\3day_mr_frlu_v4\input\Final_SpineOpt_Model.tiny.3day.mr_frlu_ccslow_ccu_cap16_dac0.v4.sqlite"
q="""select e.name,pd.name,cast(pv.value as text) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity e on e.id=pv.entity_id join alternative a on a.id=pv.alternative_id where (e.name in ('biofuels','synfuels') and pd.name='investment_count_total_max_cumulative') or (e.name='atmosphere' and pd.name='storage_investment_count_max_cumulative') or (e.name like 'representative_period_%' and pd.name in ('block_start','block_end')) or (e.name='operations_y2050' and pd.name='representative_blocks_by_period')"""
ra={r[:2]:r[2] for r in sqlite3.connect(A).execute(q)}; rb={r[:2]:r[2] for r in sqlite3.connect(B).execute(q)}
for k in sorted(ra):
  va,vb=ra[k],rb.get(k)
  if k[1] in ("block_start","block_end"): print(k, "same" if va==vb else (va,vb)); continue
  if k[1]=="representative_blocks_by_period":
    da=json.loads(va)["data"][0][1]["data"]; db=json.loads(vb)["data"][0][1]["data"]
    print(k,"n",len(da),len(db),"assign same:",da==db, da[:8], db[:8]); continue
  da=json.loads(va)["data"]; db=json.loads(vb)["data"]
  print(k,{t[:4]:round(db[t]/da[t],3) if da[t] else (da[t],db[t]) for t in da})
