import sqlite3, re, json, collections
def grab(p):
    c=sqlite3.connect("file:%s?mode=ro"%p.replace("\\","/"),uri=True)
    q="""SELECT pd.name,e.name,a.name,pv.value FROM parameter_value pv
         JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
         JOIN entity e ON e.id=pv.entity_id JOIN alternative a ON a.id=pv.alternative_id"""
    d={(x[0],x[1],x[2]):x[3] for x in c.execute(q)}
    c.close(); return d
old=grab(r"backups\spinetoolbox-items-pre-mixedres\items\ines_db\ines_db.sqlite")
new=grab(r".spinetoolbox\items\ines_db\ines_db.sqlite")
ic1=re.compile(r"(BEC\d|NLC\d)(_|$)")
diff=[k for k in (set(old)&set(new)) if ic1.search(k[1]) and old[k]!=new[k]]
# classify by technology prefix
GAS=("SMR","PEM","AEC","SOEC","gas-pyrolysis","methanation","bio-diges","bio-gasif","DAC","harber-bosch")
g=[k for k in diff if k[1].startswith(GAS)]
v=[k for k in diff if k[1].startswith(("wind-","solar-"))]
o=[k for k in diff if k not in g and k not in v]
print("differing BE/NL values: %d  -> gas-tech %d | VRE %d | other %d"%(len(diff),len(g),len(v),len(o)))
print("\nOTHER (non-gas, non-VRE) by parameter:",collections.Counter(k[0] for k in o).most_common())
for k in o[:12]: print("   %-26s %s"%(k[0],k[1]))
print("\nexample gas delta:")
for k in g[:3]:
    print("   ",k[1],k[0]); print("      old",old[k][:90]); print("      new",new[k][:90])
