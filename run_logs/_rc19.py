import sys, yaml, pandas as pd
sys.path.insert(0,r"data-pipelines/europe/_ines-builder")
import ines_target as it
cfg=yaml.safe_load(open(r"data-pipelines/europe/userconfig.yaml",encoding="utf-8"))
p=r"data-pipelines/europe/_ines-builder/region_transformation.xlsx"
rd={s:pd.read_excel(p,s) for s in pd.ExcelFile(p).sheet_names}
poly=it.define_polygons(cfg,rd,"IC1","OFF3")
on=set(poly["onshore_polygons"])
EXTRA={'AL','AT','BA','BG','CH','CY','CZ','EE','ES','FI','FR','GR','HR','HU','IE','IT','LT','LU','LV','MD','MK','MT','PL','PT','RO','RS','SE','SI','SK','TR','UA'}
print("onshore polygons:",len(on))
print("extras that ARE in polygons (would leak):", sorted(on&EXTRA) or "NONE")
print("-> ines_builder iterates `for target_poly in polygons[...]`, so only these",len(on),"regions are visited.")
