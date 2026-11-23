import os,re,collections
from spinedb_api import DatabaseMapping
p=r"runs\3day_nb_v2\input\Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite"
Z=re.compile(r"(?:BE|NL)C\d")
with DatabaseMapping("sqlite:///"+os.path.abspath(p)) as db:
    nodes=[e["name"] for e in db.get_entity_items(entity_class_name="node") if Z.search(e["name"])]
    pat=collections.Counter(Z.sub("<Z>",n) for n in nodes)
    print("node patterns",len(pat)); print(sorted(pat.items(),key=lambda x:-x[1])[:60])
    conns=[e["name"] for e in db.get_entity_items(entity_class_name="connection") if Z.search(e["name"])]
    print("conn patterns",collections.Counter(re.sub(r"(?:BE|NL)C\d","<Z>",re.sub(r"_(?:BE|NL)C\d$","_<Z>",c)) for c in conns).most_common(25))
    print("node groups:",[e["name"] for e in db.get_entity_items(entity_class_name="node") if "group" in e["name"]][:10])
    ug=[ (e["entity_class_name"],e["entity_byname"]) for e in db.get_entity_items() if e["entity_class_name"] in ("user_constraint","investment_group")][:8]; print(ug)
    cls=collections.Counter(e["entity_class_name"] for e in db.get_entity_items() if any(Z.search(x) for x in e["entity_byname"]) and e["entity_class_name"].startswith("node__") or e["entity_class_name"] in("node__node",))
    print(cls)
    print("all classes:",sorted(set(c["name"] for c in db.get_entity_class_items())))
