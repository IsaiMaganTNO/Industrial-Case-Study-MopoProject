import re,pickle,sqlite3,sys
from collections import Counter
from spinedb_api import DatabaseMapping,from_database
N=r"checkpoints\Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite"
NB=re.compile(r"(BE|NL)C\d|NS(NL|BE)\d")
def rd(p):
  E=set();V={}
  with DatabaseMapping("sqlite:///"+p.replace("\\","/")) as m:
    for e in m.get_entity_items(): E.add((e["entity_class_name"],tuple(e["entity_byname"])))
    for v in m.get_parameter_value_items(): V[(v["entity_class_name"],tuple(v["entity_byname"]),v["parameter_definition_name"],v["alternative_name"])]=(v["type"],bytes(v["value"]) if v["value"] is not None else None)
  return E,V
EN,VN=rd(N)
EA,EB=pickle.load(open(r"run_logs\_red_ents.pkl","rb")); VA,VB=pickle.load(open(r"run_logs\_red_vals.pkl","rb"))
ok=True
def chk(name,cond,info=""):
  global ok; ok&=bool(cond); print(("PASS " if cond else "FAIL ")+name,info)
# C1 entity set == old model, except known data-driven entities
extra=EN-EA; miss=EA-EN
chk("C1 no old entity missing except known", all(k[0] in("unit_flow__unit_flow","node__to_unit") for k in miss), f"missing {len(miss)} {Counter(k[0] for k in miss)}")
print("   extra vs old",len(extra),Counter(re.sub(r"(BE|NL)C\d","XX",k[1][0]).split("__")[0] for k in extra).most_common(12))
# C2 no foreign country full entities
bad=[k for k in EN if re.search(r"(?<![A-Za-z0-9])(DE|DK|NO|UK|AT|CH|CZ|IE|PL|SE|FI)(?![A-Za-z0-9])|(?:NS|AS|AT|BS)(DE|DK|NO|UK)","__".join(k[1])) and k not in EA]
chk("C2 no non-stub foreign entities", not bad, str(bad[:5]))
# C3 every NL+BE param identical to mr_fix
d=[k for k in VN if NB.search("__".join(k[1])) and VN[k]!=VB.get(k)]
d2=[k for k in VB if NB.search("__".join(k[1])) and (k[0],k[1]) in EN and k not in VN]
chk("C3 NL+BE params == mixedres", not d and not d2, f"diff {len(d)} missing {len(d2)} {d[:3]} {d2[:3]}")
# C4 non-regional params == old model
d=[k for k in set(VN)|set(VA) if not NB.search("__".join(k[1])) and (k[0],k[1]) in EN and VN.get(k)!=VA.get(k)]
chk("C4 stubs/global/temporal params == old NL+BE model", not d, f"{len(d)} {d[:4]}")
# C5 guard
con=sqlite3.connect(N)
g=con.execute("""select count(*), sum(cast(pv.value as real)) from parameter_value pv join parameter_definition pd on pd.id=pv.parameter_definition_id join entity_class ec on ec.id=pv.entity_class_id where pd.name='investment_count_initial_cumulative' and ec.name='connection'""").fetchone()
print("   guard raw",g)
print("   integrity",con.execute("pragma integrity_check").fetchone()[0], "fk",con.execute("pragma foreign_key_check").fetchall()[:3])
print("ALL", "PASS" if ok else "FAIL")
