import os,re,collections
from spinedb_api import DatabaseMapping, from_database
p=r"runs\3day_nb_v2\input\Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite"
I=re.compile(r"^((?:BE|NL))C\d_(\w+?)_((?:BE|NL))C\d$")
intra=set()
with DatabaseMapping("sqlite:///"+os.path.abspath(p)) as db:
    for e in db.get_entity_items(entity_class_name="connection"):
        m=I.match(e["name"])
        if m and m.group(1)==m.group(3): intra.add(e["name"])
    print("intra-country connections",len(intra), collections.Counter(I.match(c).group(2) for c in intra))
    pv=collections.defaultdict(list)
    for v in db.get_parameter_value_items():
        bn=v["entity_byname"]
        if bn and bn[0] in intra:
            val=from_database(v["value"],v["type"]); x=getattr(val,"values",val)
            try: x=[float(a) for a in x][:3] if hasattr(x,"__len__") and not isinstance(x,str) else x
            except Exception: pass
            pv[(v["entity_class_name"],v["parameter_definition_name"],v["alternative_name"])].append(x)
    for k,vs in sorted(pv.items()):
        s=collections.Counter(str(x) for x in vs).most_common(3)
        print(k,len(vs),s)
    rc=collections.Counter(e["entity_class_name"] for e in db.get_entity_items() if e["entity_byname"] and e["entity_byname"][0] in intra)
    print(rc)
