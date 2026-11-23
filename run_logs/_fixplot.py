import re
p=r"tools\plot_mixedres_compare.py"; s=open(p,encoding="utf8").read()
fn='''
# --- plot-specific supply labels (postprocess.classify is industry-oriented: any "+CC" tech is
#     "industry: CCS-equipped", and nuclear/hydro/storage/LNG land in "other"). Relabel by tech+carrier.
def supply_label(tech, carrier):
    l = str(tech).lower()
    if "ccgt+cc" in l:                         return "gas power + CCS (CCGT+CC)"
    if "ccgt-h2" in l:                         return "hydrogen turbine (CCGT-H2)"
    if "ccgt" in l or "ocgt" in l:             return "gas power, unabated"
    if "nuclear" in l:                         return "nuclear"
    if "hydro" in l or l.startswith("ror") or "ph-discharge" in l: return "hydro (incl. pumped)"
    if "battery" in l:                         return "battery discharge"
    if "-dr" in l:                             return "EV/transport flexibility (discharge)"
    if "scpc" in l:                            return "coal power"
    if "oil-eng" in l:                         return "oil engines"
    if "waste" in l:                           return "waste incineration"
    if l.startswith("biost"):                  return "biomass power"
    if "solar" in l:                           return "solar PV"
    if "wind-off" in l:                        return "wind offshore"
    if "wind-on" in l:                         return "wind onshore"
    if "lng-terminal" in l:                    return "LNG import"
    if "gas-extraction" in l:                  return "domestic gas extraction"
    if "bio-diges-up+cc" in l:                 return "biomethane + CCS"
    if "bio-diges" in l:                       return "biomethane"
    if "methanation" in l:                     return "synthetic methane"
    if "lh2-terminal" in l:                    return "liquid H2 import"
    if "smr+cc" in l:                          return "blue H2 (SMR+CCS)"
    if "smr" in l:                             return "grey H2 (SMR)"
    if any(k in l for k in ("pem", "aec", "soec")): return "electrolysis"
    if "heatpump" in l:                        return "heat pumps"
    if "electric-heating" in l:                return "electric resistance heating"
    if "gas-boiler" in l:                      return "gas boilers"
    if "bio-boiler" in l:                      return "biomass boilers"
    if "oil-boiler" in l:                      return "oil boilers"
    if "coal-boiler" in l:                     return "coal boilers"
    return "other: " + re.sub(r"_.*$", "", str(tech))
for _d in (M, V):
    _s = _d["supply"]
    _s["category"] = [supply_label(t, c) for t, c in zip(_s.tech, _s.carrier)]
    _s["region"] = _s["region"].astype(object).where(_s["region"].notna(), "offshore")
'''
s=s.replace('G = gpd.read_file', fn+'G = gpd.read_file',1)
s=s.replace('def ctry(r):\n    r = str(r); return','def ctry(r):\n    r = str(r)\n    if r in ("nan","None",""): return "offshore"\n    return',1)
s=s.replace('"NL+BE electricity generation 2050 (TWh)"','"NL+BE onshore electricity generation 2050 (TWh; offshore wind not region-assigned)"')
s=s.replace('"NL+BE direct CO2 emissions 2050 (Mt)"','"NL+BE gross direct CO2 2050 (Mt; incl. gas CO2 booked at LNG terminals)"')
s=s.replace('f"NL+BE {car} supply"','f"NL+BE gross {car} supply (incl. storage discharge)"')
s=s.replace('x.set_ylabel("TWh")','x.set_ylabel("TWh/yr")')
s=s.replace('"units (mixed - vre15), all vintages"','"unit count (mixed - vre15), summed over vintages\\n(units differ by tech: GW for power, plant units for industry)"')
s=s.replace('f"Mixed-res {car} supply by country, 2050"','f"Mixed-res gross {car} supply by country, 2050 (offshore = wind farms not assigned to a country)"')
s=s.replace('f"Direct CO2 emissions {y} (Mt; gas CO2 booked at extraction/LNG gate)"','f"Gross direct CO2 {y} (Mt) - fossil gas CO2 booked where gas is EXTRACTED/IMPORTED\\n(NO high because exported gas is counted in NO)"')
s=s.replace('f"Electricity generation {y} (TWh, excl. offshore)"','f"Onshore electricity generation {y} (TWh; offshore wind excluded)"')
s=s.replace('"objective (thousands)"','"objective value (model cost units, x1000)"')
s=s.replace('ax.set_title("Objective breakdown")','ax.set_title("Objective breakdown (note: mixed run covers 6 countries, vre15 only NL+BE)")')
open(p,"w",encoding="utf8").write(s)
