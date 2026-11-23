import os, shutil, collections, pandas as pd
import spinedb_api as api
from spinedb_api import DatabaseMapping, from_database
SRC = r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\Final_SpineOpt_Model.tiny.3day.mr_ccslow_ccu_cap16_dac0.sqlite"
W = r"runs\rp10_mr_noblend"; os.makedirs(W, exist_ok=True)
DST = os.path.abspath(os.path.join(W, "Final_SpineOpt_Model.tiny.10day_noblend.mr_ccslow_ccu_cap16_dac0.sqlite")); shutil.copy(SRC, DST)
EU = r"EU_case\Pan-European-Framework-Energy-System-Planning\src\_clustering\results"
days = pd.read_csv(os.path.join(EU, "representative_periods.csv"))["wy2009"].tolist()           # rep k -> day-of-year
wts = pd.read_csv(os.path.join(EU, "weights_wy2009.csv")).groupby("rep_period").weight.sum()     # rep k -> days represented
assert len(days) == 10 and abs(wts.sum() - 365) < 1e-6
YRS = {"2030": "2030", "2040": "2041", "2050": "2050"}
def pv(m, cls, par, alt, byname, val):
    v, t = api.to_database(val); _, e = m.add_parameter_value_item(entity_class_name=cls, entity_byname=byname, parameter_definition_name=par, alternative_name=alt, value=v, type=t)
    if e: raise RuntimeError(e)
with DatabaseMapping("sqlite:///" + DST) as m:
    # template: node links + cyclic_condition values of block 1 per year (identical across blocks)
    tmpl = {}
    for y in YRS:
        b = f"representative_period_{y}_1"
        nodes = [e["entity_byname"][0] for e in m.get_entity_items(entity_class_name="node__temporal_block") if e["entity_byname"][1] == b]
        vals = [(v["entity_byname"][0], v["alternative_name"], from_database(v["value"], v["type"])) for v in m.get_parameter_value_items(entity_class_name="node__temporal_block") if v["entity_byname"][1] == b]
        tmpl[y] = (nodes, vals)
    keep = {(p, a) for p, a in [(v["parameter_definition_name"], v["alternative_name"]) for v in m.get_parameter_value_items(entity_class_name="temporal_block") if v["entity_name"] == "representative_period_2050_1"]}
    print("block params in 3-day:", sorted(keep))
    for e in list(m.get_entity_items(entity_class_name="temporal_block")):
        if e["name"].startswith("representative_period_"): m.remove_item("entity", e["id"])
    m.commit_session("remove 3-day rep blocks")
    for yi, (y, cy) in enumerate(YRS.items()):
        y0 = pd.Timestamp(f"{cy}-01-01")
        for k in range(1, 11):
            n = f"representative_period_{y}_{k}"; d = days[k - 1]
            _, e = m.add_entity_item(entity_class_name="temporal_block", name=n); assert not e, e
            _, e = m.add_entity_group_item(entity_class_name="temporal_block", group_name="all_rps", member_name=n); assert not e, e
            pv(m, "temporal_block", "resolution", "Base", (n,), api.Duration("1h"))
            pv(m, "temporal_block", "representative_block_index", "wy2009", (n,), float(yi * 10 + k))
            pv(m, "temporal_block", "weight", "wy2009", (n,), float(wts[k]))
            pv(m, "temporal_block", "block_start", "wy2009", (n,), api.DateTime(y0 + pd.Timedelta(days=d - 1)))
            pv(m, "temporal_block", "block_end", "wy2009", (n,), api.DateTime(y0 + pd.Timedelta(days=d)))
            nodes, vals = tmpl[y]
            for nd in nodes:
                _, e = m.add_entity_item(entity_class_name="node__temporal_block", entity_byname=(nd, n)); assert not e, e
            for nd, alt, val in vals: pv(m, "node__temporal_block", "cyclic_condition", alt, (nd, n), val)
        # single-row map as in the 3-day setup: every block weighted by days/365, zero for other years
        row = [float(wts[k] / 365) if yy == y else 0.0 for yy in YRS for k in range(1, 11)]
        mp = api.Map([api.DateTime(y0)], [api.Array(row)], index_name="t")
        m.add_update_item("parameter_value", entity_class_name="temporal_block", entity_byname=(f"operations_y{y}",), parameter_definition_name="representative_blocks_by_period",
                          alternative_name="wy2009", **dict(zip(("value", "type"), api.to_database(mp))))
    m.commit_session("10 rep days, non-blended, same structure as 3-day")
print("built", DST)
