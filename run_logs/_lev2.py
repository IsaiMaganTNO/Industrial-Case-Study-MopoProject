import sqlite3, json
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite")
# atmosphere cap - the known-good /365 precedent
for e in ["atmosphere","fossil-CH4"]:
    for p,v,a in c.execute("""select pd.name,pv.value,al.name from parameter_value pv
      join parameter_definition pd on pd.id=pv.parameter_definition_id
      join entity en on en.id=pv.entity_id join alternative al on al.id=pv.alternative_id
      where en.name=? and pd.name in ('storage_state_max','balance_type','storage_longterm_active')""",(e,)):
        print(f"{e:12s} [{a:19s}] {p:26s} {bytes(v).decode()[:130]}")
    print()
print("INTERPRETATION:")
print(" atmosphere cap was already divided by 365 (per TIME_REPRESENTATION.md S7).")
print(" fossil-CH4 budget 2.5e6/1e6/5e5 is NOT divided -> would be ~365x too LOOSE")
print(" if it behaves as a long-term stock the same way.")
print()
print(" 500000 GWh / 365 = ", 500000/365, "GWh effective annual if /365 applied")
