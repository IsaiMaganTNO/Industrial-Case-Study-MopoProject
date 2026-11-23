print("=== CO2 BUDGET verdict ===")
ver={2030:99.801+65.628, 2040:22.178+14.584, 2050:0.0}
mod={2030:165400.0/1000, 2040:36800.0/1000, 2050:0.0}
for y in ver:
    r = mod[y]/ver[y] if ver[y] else float("nan")
    print(f"  {y}: verification {ver[y]:8.3f} Mt   model {mod[y]:8.3f} Mt   ratio {r:.4f}")
print()
print("=== fossil-CH4 limited_commodity: Pan-EU vs IC1-specific ===")
paneu={2030:2500000,2040:1000000,2050:500000}
ic1={2030:1102262.019231,2040:440904.807692,2050:220452.403846}
print(f"{'year':6s} {'PanEU GWh':>14s} {'IC1 GWh':>16s} {'IC1 TWh':>10s} {'model uses':>12s}")
for y in paneu:
    print(f"{y:6d} {paneu[y]:14,.0f} {ic1[y]:16,.0f} {ic1[y]/1000:10.1f} {'PanEU (inert)':>12s}")
print()
print("  ratio IC1/PanEU =", round(ic1[2030]/paneu[2030],6), "(= the 0.440905 factor in the sheet)")
print("  Our gascap patch yields 279.1 TWh/yr vs IC1 budget 2050 =", round(ic1[2050]/1000,1),"TWh")
