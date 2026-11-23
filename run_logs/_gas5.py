import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
def cap(u):
    r=c.execute("select pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id "
      "join entity e on e.id=pv.entity_id where e.name=? and pd.name=\"investment_count_fix_cumulative\"",(u,)).fetchone()
    return float(bytes(r[0]).decode()) if r else 0.0
print(f"{'region':8s} {'LNG GW':>8s} {'extr GW':>8s} {'GW*8760':>12s}  observed2050")
obs={"BEC1":30523.3,"NLC3":46430.6,"NLC6":46430.6,"NLC9":46430.6,"BEC5":30523.3}
for reg in ["BEC1","BEC5","NLC3","NLC6","NLC9"]:
    l=cap(f"LNG-terminal_{reg}"); g=cap(f"gas-extraction_{reg}")
    print(f"{reg:8s} {l:8.4f} {g:8.4f} {(l+g)*8760:12.1f}  {obs[reg]:12.1f}")
