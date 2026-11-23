import sqlite3,json,collections,sys,os
sys.path.insert(0,"tools")
import postprocess as PP
from spinedb_api import DatabaseMapping
from spinedb_api.parameter_value import from_database
MODEL=r"checkpoints\Final_SpineOpt_Model.tiny.3day.group1.biocap365.sqlite"
RES=r"checkpoints\Investment_Results.3day_biocap365.sqlite"
MS=(2030,2040,2050)
def tsmap(val):
    idx=getattr(val,"indexes",None)
    if idx is None:
        try: return {"const":float(val)}
        except: return {}
    out={}
    for i,x in zip(idx,val.values):
        s=str(i)
        if s[:4].isdigit():
            out[PP.to_milestone(int(s[:4]))]=float(x)
    return out
def pick(d,y):
    if not d: return 0.0
    if "const" in d: return d["const"]
    if y in d: return d[y]
    ks=[k for k in d if isinstance(k,int) and k<=y]
    return d[max(ks)] if ks else 0.0
fom={};cap=collections.defaultdict(float);inv={}
with DatabaseMapping("sqlite:///"+os.path.abspath(MODEL)) as db:
    for v in db.get_parameter_value_items():
        p=v["parameter_definition_name"];cls=v["entity_class_name"]
        val=from_database(v["value"],v["type"])
        if cls=="unit" and p=="fom_cost": fom[v["entity_name"]]=tsmap(val)
        elif cls=="unit__to_node" and p=="capacity_per_unit":
            m=tsmap(val); cap[v["entity_byname"][0]]+= (list(m.values())[0] if m else 0)
        elif cls=="unit" and p=="unit_investment_cost": inv[v["entity_name"]]=tsmap(val)
avail=collections.defaultdict(dict); invd=collections.defaultdict(dict)
with DatabaseMapping("sqlite:///"+os.path.abspath(RES)) as db:
    for v in db.get_parameter_value_items():
        p=v["parameter_definition_name"]
        if p not in("units_invested_available","units_invested"): continue
        u=PP.split_name(v["entity_name"])
        nm=v["entity_name"].replace("default_report__","").replace("__realization","")
        for y,x in tsmap(from_database(v["value"],v["type"])).items():
            (avail if p=="units_invested_available" else invd)[nm][y]=x
FOM=collections.defaultdict(float); INV=collections.defaultdict(float)
for nm,yr in avail.items():
    if nm not in fom: continue
    for y,n in yr.items():
        FOM[nm]+= pick(fom[nm],y)*cap.get(nm,0.0)*n*8760
for nm,yr in invd.items():
    if nm not in inv: continue
    for y,n in yr.items():
        INV[nm]+= pick(inv[nm],y)*n
print("recon FOM total  %18.1f  (objective 2,006,969.49)"%sum(FOM.values()))
print("recon INV total  %18.1f  (objective 1,100,958.67)"%sum(INV.values()))
