import os,re,collections,sqlite3
p=r"runs\3day_nb_v2\input\Final_SpineOpt_Model.tiny.3day.nb_v2.sqlite"
c=sqlite3.connect(p)
print(c.execute("select name, default_value is not null, default_type from parameter_definition where name in ('capacity_per_connection','connection_flow_cost','fix_ratio_out_in_connection_flow','investment_count_max_cumulative','connection_investment_cost','connection_availability_factor','connection_type')").fetchall())
from spinedb_api import DatabaseMapping
I=re.compile(r"^((BE|NL)C\d)_(\w+?)_((BE|NL)C\d)$")
with DatabaseMapping("sqlite:///"+os.path.abspath(p)) as db:
    G=collections.defaultdict(lambda: collections.defaultdict(set))
    for e in db.get_entity_items(entity_class_name="connection__node__node"):
        cn,n1,n2=e["element_name_list"]; m=I.match(cn)
        if not m or m.group(2)!=m.group(5): continue
        # node__node: flow goes from n2 to n1
        G[(m.group(2),m.group(3))][n2].add(n1)
    for k,adj in sorted(G.items()):
        ns=set(adj)|{y for v in adj.values() for y in v}
        def reach(s):
            seen={s};st=[s]
            while st:
                x=st.pop()
                for y in adj.get(x,()):
                    if y not in seen: seen.add(y);st.append(y)
            return seen
        ok=all(reach(n)==ns for n in ns)
        print(k,len(ns),"strongly connected" if ok else "NOT strongly connected")
