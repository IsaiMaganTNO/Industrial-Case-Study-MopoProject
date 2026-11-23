from spinedb_api import DatabaseMapping
db=r"checkpoints\Final_SpineOpt_Model.tiny.3day.gascap.vre15.sqlite"
with DatabaseMapping("sqlite:///"+db) as m:
    # membership: which units belong to which investment_group
    mem={}
    for e in m.get_entity_items(entity_class_name="unit__investment_group"):
        u,g=e["entity_byname"]
        mem.setdefault(g,[]).append(u)
    for g in sorted(mem):
        if "NSBE01" in g or "NSNL033" in g:
            print(f"{g:26} -> {mem[g]}")
    print("\ntotal investment_groups:",len(mem))
    multi={g:v for g,v in mem.items() if len(v)>1}
    print("groups with >1 member:",len(multi))
