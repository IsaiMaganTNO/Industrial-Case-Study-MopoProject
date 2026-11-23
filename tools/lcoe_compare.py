"""LCOE comparison: bioST vs VRE, using the model's own parameters.

Annualised capex via CRF at the model discount rate, divided by annual output
at the capacity factor the SOLVER sees (3 representative days) and at the TRUE
annual CF, to separate genuine economics from sampling bias.
"""
import sqlite3, json, datetime, collections

DB=r"reports_3day_group1\INPUT_Final_SpineOpt_Model.tiny.3day.group1.sqlite"
c=sqlite3.connect(DB)

def pv(ent,par,alt=1):
    q="""SELECT pv.value FROM parameter_value pv JOIN entity e ON e.id=pv.entity_id
         JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
         WHERE e.name=? AND pd.name=? AND pv.alternative_id=?"""
    r=c.execute(q,(ent,par,alt)).fetchone()
    if not r: return None
    v=r[0].decode() if isinstance(r[0],bytes) else r[0]
    try: return json.loads(v)
    except Exception: return v

# discount rate
dr=None
for r in c.execute("""SELECT pv.value FROM parameter_value pv
     JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
     WHERE pd.name LIKE '%discount%' LIMIT 1"""):
    v=r[0].decode() if isinstance(r[0],bytes) else r[0]
    try: dr=float(json.loads(v).get("data",v))
    except Exception:
        try: dr=float(v)
        except Exception: pass
if dr is None: dr=0.05
print(f"discount rate = {dr}")

START=datetime.datetime(2018,1,1)
DAYS=[datetime.date(2018,5,14),datetime.date(2018,9,10),datetime.date(2018,12,24)]
idx=set()
for d0 in DAYS:
    h0=int((datetime.datetime(d0.year,d0.month,d0.day)-START).total_seconds()//3600)
    idx.update(range(h0,h0+24))

def cf(tech_prefix):
    q="""SELECT e.name, pv.value FROM parameter_value pv
         JOIN entity e ON e.id=pv.entity_id
         JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
         WHERE pd.name='availability_factor' AND pv.alternative_id=
           (SELECT id FROM alternative WHERE name='wy2008')"""
    tot=cnt=st=sc=0.0
    for n,v in c.execute(q):
        if not n.startswith(tech_prefix): continue
        v=v.decode() if isinstance(v,bytes) else v
        for i,x in enumerate(json.loads(v)["data"]):
            x=float(x); tot+=x; cnt+=1
            if i in idx: st+=x; sc+=1
    return (tot/cnt if cnt else None, st/sc if sc else None)

CRF=lambda r,n: r*(1+r)**n/((1+r)**n-1)

TECHS=[
 ("bioST",                   "bioST_NLC6",                     None,  0.90),
 ("wind-on-SP277-HH100",     "wind-on-SP277-HH100_NLC6",       "wind-on-SP277-HH100", None),
 ("wind-off-FB-SP370-HH155", "wind-off-FB-SP370-HH155_NSNL011","wind-off-FB-SP370-HH155", None),
 ("solar-PV-no-tracking",    "solar-PV-no-tracking_NLC6",      "solar-PV-no-tracking", None),
]
BIO_FUEL=0.0111   # connection_flow_cost biomass-stock -> bio, NLC-range
BIO_EFF=0.35      # steam-cycle electrical efficiency assumption

print(f"\n{'tech':26s}{'capex50':>9s}{'life':>6s}{'CRF':>7s}{'CFann':>7s}{'CF3d':>7s}"
      f"{'LCOEann':>9s}{'LCOE3d':>9s}")
for label,ent,prefix,fixed_cf in TECHS:
    ic=pv(ent,"unit_investment_cost"); fom=pv(ent,"fom_cost") or 0.0
    life=pv(ent,"lifetime_economic")
    yrs=int(str(life.get("data") if isinstance(life,dict) else life).rstrip("Y"))
    capex=float(ic["data"]["2050-01-01T00:00:00"])
    crf=CRF(dr,yrs)
    if fixed_cf: cfa=cfs=fixed_cf
    else: cfa,cfs=cf(prefix)
    fomf=float(fom)
    def lcoe(cfv):
        hours=8760*cfv
        ann_capex=capex*crf
        fuel=(BIO_FUEL/BIO_EFF) if label=="bioST" else 0.0
        return (ann_capex+fomf*8760)/hours + fuel
    print(f"{label:26s}{capex:9,.0f}{yrs:6d}{crf:7.4f}{cfa:7.3f}{cfs:7.3f}"
          f"{lcoe(cfa):9.4f}{lcoe(cfs):9.4f}")
print("\nbioST fuel component = {:.4f} (= {} / {} efficiency)".format(BIO_FUEL/BIO_EFF,BIO_FUEL,BIO_EFF))
