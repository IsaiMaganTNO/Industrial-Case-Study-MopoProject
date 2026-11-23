import pandas as pd,os,glob
def head(p,n=1):
    with open(p,encoding="utf-8",errors="replace") as f: return f.readline()[:200]
print("== heat: scenario_total_yearly_demands_GWh.csv")
p=r"data\Buildings\scenario_total_yearly_demands_GWh.csv"
print("  hdr:",head(p))
print("\n== heat demand-timeseries dir")
fs=sorted(glob.glob(r"data\Buildings\demand-timeseries\*"))
print("  n files",len(fs)); print("  ",[os.path.basename(f) for f in fs[:8]])
if fs: print("  hdr of first:",head(fs[0]))
print("\n== transport fleet.csv")
print("  hdr:",head(r"data\Transport\fleet.csv"))
fs=sorted(glob.glob(r"data\Transport\road\*"))
print("  road files",len(fs),[os.path.basename(f) for f in fs[:6]])
print("\n== industry catalogue")
x=pd.ExcelFile(r"data\Industry\technology_catalogue_ind_nuts0_nuts3.xlsx")
print("  sheets:",x.sheet_names[:10])
print("\n== hydro IC1_parameters_data.xlsx")
x=pd.ExcelFile(r"data\Hydro\IC1_parameters_data.xlsx")
print("  sheets:",x.sheet_names)
