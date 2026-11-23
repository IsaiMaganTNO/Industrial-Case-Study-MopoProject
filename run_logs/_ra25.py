import geopandas as gpd, pandas as pd
geo = gpd.read_file(r"geodata/IC1_NWEU.geojson")[["id","geometry"]].rename(columns={"id":"region"})
pp = pd.read_csv(r"data/Energy_Conversion/powerplants.csv", low_memory=False).dropna(subset=["lat","lon"])
pts = gpd.GeoDataFrame(pp, geometry=gpd.points_from_xy(pp.lon, pp.lat), crs="EPSG:4326")
j = gpd.sjoin(pts, geo, how="inner", predicate="within")
print("plants with coords:", len(pts), "| assigned:", len(j))
agg = j.groupby("region").agg(n=("region","size"), cap_GW=("Capacity", lambda s: s.sum()/1000))
agg = agg.sort_values("cap_GW", ascending=False)
print(agg.round(1).to_string())
print("\nTOTAL assigned GW: %.1f" % agg.cap_GW.sum())
new = [i for i in ["DE","DK","NO","UK"] if i in agg.index]
print("new-country GW: %.1f  (%.0f%% of total)" % (
    agg.loc[new].cap_GW.sum(), 100*agg.loc[new].cap_GW.sum()/agg.cap_GW.sum()))
print("BE+NL GW: %.1f" % agg.drop(index=new).cap_GW.sum())
print("\nfueltype mix in new countries (GW):")
t = j[j.region.isin(new)].groupby(["region","Fueltype"]).Capacity.sum().div(1000).round(1)
print(t[t > 0.5].to_string())
