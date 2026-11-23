import pandas as pd
d = pd.read_excel("data-pipelines/europe/_ines-builder/region_transformation.xlsx",
                  sheet_name="PECD2_PECD1")
sub = d[d.target.isin(["DE", "DK", "NO", "UK"])]
print("%-4s %6s %10s %10s" % ("ctry", "n", "sum_cap", "sum_pot"))
for c, g in sub.groupby("target"):
    print("%-4s %6d %10.4f %10.4f" % (c, len(g), g.capacity.sum(), g.potential.sum()))
print()
print("area unique:", sorted(sub.area.unique()))
print("population unique:", sorted(sub.population.unique()))
print()
print("=> area/population are constant 1.0 -> NOT usable as weights.")
print("=> capacity and potential both sum to 1.0 per country -> usable.")
