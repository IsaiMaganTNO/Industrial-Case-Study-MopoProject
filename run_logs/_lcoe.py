# crude annuitised LCOE at 2050 capex, r=0.05
r=0.05
tech={
 "wind-off-FO":(2855.1,30,0.5209,0.3378,0.003899543378995434),
 "wind-off-FB":(1920.5,30,0.5209,0.3378,0.003899543378995434),
 "wind-on"    :( 933.9,30,0.3584,0.2691,0.0021728310502283103),
 "solar-PV"   :( 269.5,40,0.1422,0.1608,0.001030593607305936),
 "nuclear-3"  :(6948.2,60,0.90  ,0.90  ,0.010232749659380331),
 "CCGT+CC"    :(1438.8,30,0.90  ,0.90  ,0.004379621382095512),
}
print(f"{'tech':12s} {'annuity':>9s} {'LCOE@annualCF':>14s} {'LCOE@sampledCF':>15s} {'penalty':>8s}")
for k,(cap,L,cfa,cfs,fom) in tech.items():
    a=cap*r/(1-(1+r)**-L)
    tot=a+fom*cap*8760/8760*1000*0  # fom is fraction-ish; ignore scale, show capex-only
    la=a/(cfa*8760)*1000; ls=a/(cfs*8760)*1000
    print(f"{k:12s} {a:9.1f} {la:14.2f} {ls:15.2f} {ls/la-1:+7.1%}")
