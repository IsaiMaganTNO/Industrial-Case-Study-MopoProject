# ratios are OUTPUT cement per unit INPUT fuel -> invert for intensity
rows={
 "CEM2-(Afm)":   dict(capex=2791.4,fom=0.0290,atm=0.535,cap=0.0,  elec=12.489,waste=1.465),
 "CEM2-(Afm)MEA":dict(capex=2959.3,fom=0.0290,atm=0.129,cap=0.516,elec=5.969, waste=0.935),
 "LC3-(Afm)MEA": dict(capex=3024.3,fom=0.0307,atm=0.098,cap=0.391,elec=6.721, waste=1.156),
}
print("%-15s %7s %7s %7s %7s %7s"%("route","elec/t","waste/t","emit","capt","gross"))
for k,v in rows.items():
    e=1/v["elec"]; w=1/v["waste"]
    print("%-15s %7.4f %7.4f %7.3f %7.3f %7.3f"%(k[:15],e,w,v["atm"],v["cap"],v["atm"]+v["cap"]))
print()
base=rows["CEM2-(Afm)"]; mea=rows["CEM2-(Afm)MEA"]
d_elec=1/mea["elec"]-1/base["elec"]
d_waste=1/mea["waste"]-1/base["waste"]
d_capex=mea["capex"]-base["capex"]
d_abated=base["atm"]-mea["atm"]
print("MEA vs unabated, per t cement:")
print("  extra elec   : %+.4f MWh/t  (%.2fx)"%(d_elec,(1/mea["elec"])/(1/base["elec"])))
print("  extra waste  : %+.4f MWh/t"%d_waste)
print("  extra capex  : %+.1f (%.1f%%)"%(d_capex,100*d_capex/base["capex"]))
print("  CO2 abated   : %.3f t/t cement"%d_abated)
for ep in (0.03,0.05,0.08):
    print("   elec @%.2f/MWh -> elec cost alone = %.1f EUR per t CO2 abated"
          %(ep,(d_elec*ep*1000)/d_abated))
