import os,re,collections
from spinedb_api import DatabaseMapping
with DatabaseMapping("sqlite:///"+os.path.abspath(r"checkpoints\Investment_Results.3day_mr_fix.sqlite")) as db:
    s=set()
    for v in db.get_parameter_value_items(entity_class_name="report__connection__node__direction__stochastic_scenario", parameter_definition_name="connection_flow"):
        c=v["entity_byname"][1]
        if re.search(r"CH4|CO2|elec|H2",c) and not re.search(r"bus|truck|car",c): s.add(c)
cs=sorted(s); print(len(cs))
x=[c for c in cs if len(set(re.findall(r"(NL|BE|DE|DK|NO|UK)",c)))>1]
print(len(x)); print("\n".join(x[:150]))
