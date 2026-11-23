import os,re,collections
from spinedb_api import DatabaseMapping
dbs={"mr":r"checkpoints\Final_SpineOpt_Model.tiny.3day.mr_fix.sqlite","nb":r"runs\3day_nb_v2\input\Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite"}
for k,p in dbs.items():
    with DatabaseMapping("sqlite:///"+os.path.abspath(p)) as db:
        c=collections.Counter()
        for e in db.get_entity_items():
            n="|".join(e["entity_byname"])
            if re.search(r"(NL|BE)C\d",n) and re.search(r"bus-|truck-|car-|heat|transport",n,re.I):
                c[(e["entity_class_name"],re.sub(r"_(NL|BE)C\d.*","",e["entity_byname"][0]))]+=1
        print("=====",k,sum(c.values()))
        for x,v in sorted(c.items())[:40]: print(" ",x,v)
