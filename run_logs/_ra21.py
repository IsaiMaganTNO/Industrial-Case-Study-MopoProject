import geopandas as gpd
a = gpd.read_file(r"geodata/IC1.geojson")
b = gpd.read_file(r"verification/IC_NWEU.geojson")
a = a.set_index("id"); b = b.set_index("id")
print("active ids", len(a), "| nweu ids", len(b))
print("missing from nweu:", sorted(set(a.index) - set(b.index)))
print("extra in nweu   :", sorted(set(b.index) - set(a.index)))
bad = 0
for i in sorted(set(a.index) & set(b.index)):
    ga, gb = a.loc[i, "geometry"], b.loc[i, "geometry"]
    eq = ga.equals(gb)
    sym = ga.symmetric_difference(gb).area
    if not eq or sym > 1e-12:
        bad += 1
        print("  DIFF %-5s equals=%s symdiff_area=%.3e aarea=%.4f barea=%.4f" % (i, eq, sym, ga.area, gb.area))
print("geometry mismatches among shared ids:", bad)
for i in ["DE","DK","NO","UK"]:
    r = b.loc[i]
    print("%-3s level=%-9s country=%-3s area_km2=%s per_km2=%s geom_area_deg2=%.3f" % (
        i, r["level"], r["country"], r["area_km2"], r["per_km2"], r["geometry"].area))
