import os,re,collections
from spinedb_api import DatabaseMapping
p=r"runs\3day_nb_v2\input\Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite"
Z=re.compile(r"(BE|NL)C\d")
ents=collections.Counter(); intra=collections.Counter(); pv=collections.Counter(); types=collections.Counter()
with DatabaseMapping("sqlite:///"+os.path.abspath(p)) as db:
    for e in db.get_entity_items():
        n="|".join(e["entity_byname"]); zs=set(m.group(0)[:2]+"x" for m in re.finditer(r"(BE|NL)C\d",n)); zz=set(re.findall(r"(?:BE|NL)C\d",n))
        if zz:
            ents[e["entity_class_name"]]+=1
            if len(zz)>1 and len(set(z[:2] for z in zz))==1: intra[e["entity_class_name"]]+=1
    for v in db.get_parameter_value_items():
        n="|".join(v["entity_byname"])
        if Z.search(n):
            pv[(v["entity_class_name"],v["parameter_definition_name"])]+=1; types[v["type"]]+=1
print("zonal entities by class:",dict(ents.most_common(20)))
print("intra-country (zone-to-zone) entities:",dict(intra))
print("value types:",dict(types))
print("distinct zonal (class,param):",len(pv))
for k,c in pv.most_common(45): print(" ",k,c)
