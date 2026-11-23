import hashlib, os
B=r"verification\Data - IC1 and PECD1"
def md5(p):
    return hashlib.md5(open(p,"rb").read()).hexdigest()
pairs=[
 ("Gas/Gas_Sectors_Dataset.xlsx","data/Gas/Gas_Sectors_Dataset.xlsx"),
 ("Gas/Gas_Sectors_Dataset.xlsx","data/Gas/Gas_Sectors_Dataset_IC1_placeholder.xlsx"),
 ("CO2_network(direct_link_ines_builder)/CO2_data_IC1_low_cost.xlsx","data-pipelines/europe/_ines-builder/CO2_data_IC1.xlsx"),
 ("CO2_network(direct_link_ines_builder)/CO2_data_IC1_high_cost.xlsx","data-pipelines/europe/_ines-builder/CO2_data_IC1.xlsx"),
 ("Industry/technology_catalogue_ind_nuts0_nuts3_update.xlsx","data/Industry/technology_catalogue_ind_nuts0_nuts3.xlsx"),
]
for a,b in pairs:
    pa=os.path.join(B,*a.split("/")); pb=b.replace("/",os.sep)
    ok=os.path.exists(pa) and os.path.exists(pb)
    if not ok:
        print(f"  MISSING: {a if not os.path.exists(pa) else b}"); continue
    ha,hb=md5(pa),md5(pb)
    sa,sb=os.path.getsize(pa)/1024,os.path.getsize(pb)/1024
    print(f"  {'IDENTICAL' if ha==hb else 'DIFFERENT'}  {os.path.basename(a)[:44]:46} {sa:8.1f}KB vs {sb:8.1f}KB  {os.path.basename(b)[:38]}")
