import sqlite3, re, collections, json
M = r"checkpoints\frlu\Final_SpineOpt_Model.tiny.3day.mr_frlu_ccslow_ccu_cap16_dac0.v3.sqlite"
c = sqlite3.connect(M)
units = [n for (n,) in c.execute("select e.name from entity e join entity_class ec on ec.id=e.class_id where ec.name='unit'")]
def tech(cc): return {n[:-len(cc)-1] for n in units if n.endswith("_"+cc)}
ref = [tech(x) for x in ("DE","DK","NO","UK")]
common = {t for t in set().union(*ref) if sum(t in r for r in ref) >= 3}
print("FR missing unit techs:", sorted(common - tech("FR")))
print("FR existing units:", sorted(t for t in tech("FR") if "existing" in t))
for cc in ("DE","FR","LU"):
    n = c.execute("""select count(*) from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id
      where e.name=? and pd.name='demand'""", (f"elec_{cc}",)).fetchone()[0]
    b = c.execute("select count(*) from parameter_value pv join entity e on e.id=pv.entity_id where e.name=?", (f"biomass-stock_{cc}",)).fetchone()[0]
    print(f"{cc}: elec demand rows {n}, biomass-stock params {b}")
for e, p, t in c.execute("""select e.name, pd.name, substr(cast(pv.value as text),1,120) from parameter_value pv join entity e on e.id=pv.entity_id
  join parameter_definition pd on pd.id=pv.parameter_definition_id where e.name in ('nuclear-3-existing_FR','CCGT-existing_FR')
  and pd.name in ('initial_units_invested_available','existing_units','number_of_units','capacity_per_unit','investment_count_max_cumulative')"""):
    print(" ", e, p, t)
