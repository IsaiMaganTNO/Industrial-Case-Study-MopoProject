be_lng=3.4844*8; nl_lng=3.9829*9; nl_ext=1.3174*9
H=8760
print("Current ceilings at 100% LF (TWh/yr):")
print(f"  BE LNG {be_lng*H/1000:7.1f}   NL LNG {nl_lng*H/1000:7.1f}   NL extr {nl_ext*H/1000:7.1f}")
print()
print("Option A - availability_factor on LNG + extraction decline")
print(f"{'af_LNG':>7s} {'BE':>8s} {'NL LNG':>8s} {'extr2050':>9s} {'TOTAL50':>9s}  vs model 662.1")
for af in [0.75,0.65,0.60,0.55,0.50]:
    for extr in [0.0]:
        be=be_lng*H*af/1000; nl=nl_lng*H*af/1000; ex=nl_ext*H*extr/1000
        print(f"{af:7.2f} {be:8.1f} {nl:8.1f} {ex:9.1f} {be+nl+ex:9.1f}")
print()
print("Reference inland demand: BE ~180, NL ~320 today; 2050 decarbonised should be WELL below.")
print()
print("Option A at af=0.55 + extraction 0:")
be=be_lng*H*0.55/1000; nl=nl_lng*H*0.55/1000
print(f"   BE {be:.1f} TWh ({be/180:.2f}x today), NL {nl:.1f} TWh ({nl/320:.2f}x today), total {be+nl:.1f}")
