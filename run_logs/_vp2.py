import pickle
d=pickle.load(open(r"run_logs\gascap.pkl","rb"))
s=d["supply"]; e=s[(s.carrier=="electricity")&(s.year==2050)]
tot=e["energy"].sum()
def en(pat): return e[e.tech.str.startswith(pat)]["energy"].sum()
won=en("wind-on-SP"); sol=en("solar-PV-no"); woff=en("wind-off-FB-SP")
print(f"2050 total electricity supply   {tot:12,.0f} GWh")
print(f"  wind-on  (new)  {won:12,.0f}  cap 48.99 GW -> at 0.15 = 7.35 GW")
print(f"  solar-PV (new)  {sol:12,.0f}  cap 196.02 GW -> at 0.15 = 29.40 GW")
print(f"  wind-off (new)  {woff:12,.0f}")
print()
# implied CF
print("implied CFs from gascap fleet:")
fl=d["fleet"]; fl50=fl[fl.year==2050]
for pre,lab in [("wind-on-SP","wind-on"),("solar-PV-no","solar-PV")]:
    gw=fl50[fl50.tech.str.startswith(pre)]["units"].sum()
    gen=en(pre)
    print(f"  {lab:10s} {gw:7.2f} GW -> {gen:11,.0f} GWh  CF={gen/(gw*8760):.3f}")
print()
# what 0.15 caps would deliver
print("Generation AVAILABLE if capped at 0.15 (same CFs):")
won_gw=7.35; sol_gw=29.40
print(f"  wind-on  {won_gw:6.2f} GW x CF 0.384 x 8760 = {won_gw*0.384*8760:11,.0f} GWh")
print(f"  solar-PV {sol_gw:6.2f} GW x CF 0.141 x 8760 = {sol_gw*0.141*8760:11,.0f} GWh")
lost=won+sol-(won_gw*0.384*8760+sol_gw*0.141*8760)
print(f"  -> onshore generation lost   ~{lost:11,.0f} GWh = {lost/tot:.1%} of 2050 supply")
