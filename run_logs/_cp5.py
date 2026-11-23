import os,re,collections
from spinedb_api import DatabaseMapping
p=r"runs\3day_nb_v2\input\Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite"
I=re.compile(r"^((BE|NL)C\d)_(\w+?)_((BE|NL)C\d)$")
with DatabaseMapping("sqlite:///"+os.path.abspath(p)) as db:
    intra={e["name"] for e in db.get_entity_items(entity_class_name="connection") if (m:=I.match(e["name"])) and m.group(2)==m.group(5)}
    c=collections.Counter(e["entity_class_name"] for e in db.get_entity_items() if any(x in intra for x in e["element_name_list"] or ()))
    print(c)
