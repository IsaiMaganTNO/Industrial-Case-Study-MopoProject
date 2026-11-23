be_lng=669.0; nl_lng=860.3; nl_ext=284.547945; nl_bio=8.518997
print("NATIONAL totals from Gas_Sectors_Dataset.xlsx (GWh/d) and annual at 100% LF:")
for n,v in [("BE LNG",be_lng),("NL LNG",nl_lng),("NL extraction",nl_ext),("NL biomethane",nl_bio)]:
    print(f"  {n:16s} {v:10.3f} GWh/d = {v*365/1000:7.1f} TWh/yr")
tot=(be_lng+nl_lng+nl_ext)*365/1000
print(f"  {'fossil total':16s} {'':10s}   {tot:7.1f} TWh/yr")
print()
print("Model 2050 methane supply = 662.1 TWh  -> ratio to national ceiling =",round(662.062/tot,4))
print()
print("So NO replication error. Model total == national total. RETRACTED.")
