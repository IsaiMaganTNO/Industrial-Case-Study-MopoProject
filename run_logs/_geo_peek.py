import geopandas as gpd, pickle
g = gpd.read_file(r"geodata\IC1_NWEU.geojson"); print(g.columns.tolist()); print(g.iloc[:, :3].to_string()[:1500]); print(g.crs)
for k in ["nb_ccslow_ccu_cap16_dac0", "nb_ctry_ccslow_ccu_cap16_dac0"]:
    s = pickle.load(open(rf"run_logs\{k}_NLBE.pkl", "rb"))["supply"].query("year==2050 and carrier=='hydrogen' and category=='electrolysis'")
    print(k, (s.groupby("region").energy.sum()/1e3).round(1).to_dict())
