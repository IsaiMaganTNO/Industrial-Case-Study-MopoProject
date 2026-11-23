import geopandas as gpd
g=gpd.read_file(r"geodata\IC1_NWEU.geojson"); print(g.columns.tolist(), len(g)); print(sorted(g.id)[:60])
o=gpd.read_file(r"geodata\offshore.geojson"); print(o.columns.tolist(), len(o)); 
idc=[c for c in o.columns if c!="geometry"][0]; ids=o[idc].astype(str); print([i for i in ids if any(s in i for s in ["NSNL01","NSNL03","NSUK0","NSNOS22","ASNO","ATUK031","NSDKW12","NSBE"])])
