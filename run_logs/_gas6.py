import sqlite3
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
def cap(u):
    r=c.execute("select pv.value from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id "
      "join entity e on e.id=pv.entity_id where e.name=? and pd.name=\"investment_count_fix_cumulative\"",(u,)).fetchone()
    return float(bytes(r[0]).decode()) if r else None
regs=[f"BEC{i}" for i in range(1,9)]+[f"NLC{i}" for i in range(1,10)]
print(f"{'region':7s} {'LNG-term':>10s} {'gas-extr':>10s}")
tl=tg=0
for r in regs:
    l=cap(f"LNG-terminal_{r}"); g=cap(f"gas-extraction_{r}")
    tl+=l or 0; tg+=g or 0
    print(f"{r:7s} {str(l):>10s} {str(g):>10s}")
print(f"{'TOTAL':7s} {tl:10.4f} {tg:10.4f}   -> {(tl+tg)*8760/1000:.1f} TWh/yr max")
