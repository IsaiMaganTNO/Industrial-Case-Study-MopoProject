# DAC cost per tonne CO2, from its own parameters
def crf(r,n): return r*(1+r)**n/((1+r)**n-1)
capex=2993.2523; fom=0.0097935; r=0.10
# DAC ratios: CO2 <- CH4 = 0.785 ; CO2 <- elec = 4.923
# i.e. per 1 unit CO2 output it needs 1/0.785 CH4 and 1/4.923 elec
ch4_per_t = 1/0.785
el_per_t  = 1/4.923
gas=0.018; 
# elec: use marginal CCGT total from previous calc
el_price=0.04725
C=crf(r,25)
for CF in (0.6,0.9):
    hours=8760*CF
    inv=capex*C/hours
    fo =fom*1000/hours
    fuel=ch4_per_t*gas
    elec=el_per_t*el_price
    # the CH4 burned by DAC itself carries upstream CO2 0.200/MWh
    co2_from_gas=ch4_per_t*0.200
    net = 1.0 - co2_from_gas
    tot=inv+fo+fuel+elec
    print(f"CF={CF}: cost/unit-CO2 = {tot:.5f}  gross 1.0 t, gas-CO2 {co2_from_gas:.4f} t, NET {net:.4f} t")
    print(f"         => per NET tonne = {tot/net:.5f}  (x1000 = {tot/net*1000:.1f} EUR/t)")
print()
print("compare: CCGT+CC abatement breakeven was 80.64 EUR/t")
