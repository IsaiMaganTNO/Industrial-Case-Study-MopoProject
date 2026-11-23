import pandas as pd
# define_polygons: on_level is the target_resolution, e.g. "IC1".
# region_data[on_level] is the sheet named by that level.
xl = pd.ExcelFile("data-pipelines/europe/_ines-builder/region_transformation.xlsx")
d = xl.parse("IC1")
print("IC1 sheet shape:", d.shape, list(d.columns))
print("countries present:", sorted(d.country.astype(str).unique()))
for c in ["BE","NL","DE","DK","NO","UK","FR"]:
    ids = d[d.country == c].id.tolist()
    print("  %-3s n=%2d  %s" % (c, len(ids), ids[:10]))
