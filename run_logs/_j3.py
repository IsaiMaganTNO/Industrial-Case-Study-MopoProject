# Levelised comparison: CCGT vs CCGT+CC, and the implied CO2 shadow price.
# Emissions for gas are booked UPSTREAM at LNG-terminal = 0.200 tCO2 / MWh CH4.
# Neither CCGT nor CCGT+CC carries an atmosphere ratio; CCGT+CC additionally
# CAPTURES 0.18 tCO2 per MWh CH4 input.
gas = 0.018      # EUR/kWh-equivalent, CH4 price 2050 (commodity_data: 18 EUR/MWh)
CF  = 0.60       # assumed; sensitivity below
def crf(r,n): return r*(1+r)**n/((1+r)**n-1)

rows=[]
for name, capex, fom, r, eta, cap_ratio, vom in [
    ("CCGT",     750.16, 0.0025795, 0.07, 0.58,   0.0,  0.00347639),
    ("CCGT+CC", 1438.76, 0.0043796, 0.07, 0.4857, 0.18, 0.01035397),
    ("OCGT",     359.11, 0.0007364, 0.08, 0.41,   0.0,  0.00391093),
]:
    C=crf(r,25)
    hours=8760*CF
    # capex+fom are per unit of capacity; convert to per MWh at CF
    inv_pm = capex*C/hours
    fom_pm = fom*1000/hours
    fuel_in = 1/eta                 # MWh CH4 per MWh elec
    fuel_pm = fuel_in*gas
    co2_up  = fuel_in*0.200         # tCO2 booked upstream on the gas
    co2_cap = fuel_in*cap_ratio     # tCO2 captured by the plant
    co2_net = co2_up-co2_cap
    rows.append((name,inv_pm,fom_pm,fuel_pm,vom,inv_pm+fom_pm+fuel_pm+vom,co2_net,co2_cap))
print(f"{'tech':9s} {'inv':>8s} {'fom':>8s} {'fuel':>8s} {'vom':>8s} {'TOTAL':>9s} {'netCO2':>8s} {'capt':>7s}")
for n,i,f,fu,v,t,c,cp in rows:
    print(f"{n:9s} {i:8.5f} {f:8.5f} {fu:8.5f} {v:8.5f} {t:9.5f} {c:8.4f} {cp:7.4f}")
a=[r for r in rows if r[0]=="CCGT"][0]; b=[r for r in rows if r[0]=="CCGT+CC"][0]
dcost=b[5]-a[5]; dco2=a[6]-b[6]
print()
print(f"CCGT+CC costs {dcost:+.5f} more per MWh and delivers {dco2:.4f} tCO2 less net")
print(f"=> implied breakeven CO2 price = {dcost/dco2*1000:.2f} EUR/tCO2 (x1000 for unit scale)")
