import geopandas as gpd, json, os
src = r"verification/IC_NWEU.geojson"
dst = r"geodata/IC1_NWEU.geojson"
areas = {"DE": 357105.079912, "DK": 42585.056921, "NO": 323025.002853, "UK": 244480.713358}
g = gpd.read_file(src)
assert len(g) == 21, len(g)
# normalise the level typo: UK carries IC_NWEU, the other 20 carry IC1_NWEU
assert set(g["level"]) == {"IC1_NWEU", "IC_NWEU"}, set(g["level"])
g["level"] = "IC1"
# fill the null area_km2 on the four country features from the PECD1 sheet
for cid, a in areas.items():
    m = g["id"] == cid
    assert m.sum() == 1 and g.loc[m, "area_km2"].isna().all()
    g.loc[m, "area_km2"] = a
assert g["area_km2"].notna().all()
# drop the two bookkeeping columns the active file does not have
g = g.drop(columns=[c for c in ("layer", "path") if c in g.columns])
g.to_file(dst, driver="GeoJSON")
print("written", dst, os.path.getsize(dst))
h = gpd.read_file(dst)
print("feat", len(h), "levels", set(h["level"]), "cols", list(h.columns))
print("crs", h.crs, "| nulls in area_km2:", int(h["area_km2"].isna().sum()))
print(h[["id","country","area_km2","per_km2"]].to_string())
