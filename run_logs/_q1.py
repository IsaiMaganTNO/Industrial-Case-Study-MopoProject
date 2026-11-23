from spinedb_api import DatabaseMapping
import collections
p=r"runs\3day_nb_ccslow\input\Final_SpineOpt_Model.tiny.3day.nb_ccslow.sqlite"
with DatabaseMapping("sqlite:///"+p) as db:
  io=collections.defaultdict(list)
  for c in ("unit__from_node","unit__to_node"):
    for e in db.get_entity_items(entity_class_name=c):
      b=e["entity_byname"]; u,n=(b[0],b[1]) if not b[0].startswith(("CO2","CH4","H2","elec","heat","HC","MeOH","bio","atmos")) else (b[1],b[0])
      io[u].append(("IN " if c=="unit__from_node" else "OUT ")+n)
  for k in sorted(io):
    if k.endswith("NLC1") or k.endswith("NL") or "LNG" in k or "extraction" in k or "LH2" in k:
      if any(s in k for s in ["methanation","FT","MeOH","gas-boiler","bio-boiler","LH2","LNG","extraction","REF-SMR","SMR","CCGT","DAC","PEM","bio-","(BM)NH3","(NG)NH3","CO2-inj","MOE","DRI","heatpump","e-boiler","electric"]):
        print(k, sorted(io[k]))
