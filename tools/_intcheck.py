from spinedb_api import DatabaseMapping
url = "sqlite:///checkpoints/Final_SpineOpt_Model.tiny.sqlite"
ints = ("units_invested_available_int","connections_invested_available_int",
        "storages_invested_available_int","units_on_int","is_active",
        "unit_availability_factor_int")
with DatabaseMapping(url) as db:
    hits = {}
    for pv in db.get_parameter_value_items():
        n = pv["parameter_definition_name"]
        if "_int" in n or n in ("units_on_non_anticipativity_size",):
            v = str(pv["parsed_value"])
            hits.setdefault(n, []).append(v)
    if not hits:
        print("no *_int integer-flagging parameters found")
    for k, v in sorted(hits.items()):
        trues = sum(1 for x in v if x.lower() in ("true","1","1.0"))
        print(f"{k:45} {len(v):5} values, {trues} truthy")
