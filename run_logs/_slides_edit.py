p=r"tools\make_slides.py"; t=open(p,encoding="utf-8-sig").read()
R=[
(r'NB = r"runs\3day_nb_v2\plots\summary"; MR = r"runs\3day_mr_fix\plots"; CMP = MR + r"\compare_nb_v2"',
 r'MR = r"runs\3day_mr_fix\plots"; NB = MR + r"\summary_named_standalone"; IC = MR + r"\summary_named_interconnected"; CMP = MR + r"\compare_named"'),
('"Industrial Case Study (MOPO) - SpineOpt 3-day representative runs - NL+BE IC1 vs mixed resolution"','"Industrial Case Study (MOPO) - SpineOpt investment runs - Standalone vs Interconnected"'),
('("Net CO2, booked at import (Mt)", "0", "+106")','("Net CO2 of NL+BE (Mt)", "0", "+106")'),
('("LNG imports (TWh)", "99", "558"), ',''),
('hdr = ["Indicator (NL+BE, 2050)", "nb_v2\\nNL+BE alone", "mr_fix\\n6 countries"]','hdr = ["Indicator (NL+BE, 2050)", "Standalone\\nNL+BE alone", "Interconnected\\n6 countries"]'),
('"nb_v2: NL+BE at IC1 resolution (17 zones)     vs     mr_fix: NL+BE IC1 + DE, DK, NO, UK at country level"','"Standalone: NL+BE in 17 zones     vs     Interconnected: NL+BE + DE, DK, NO, UK"'),
('("nb_v2 - NL+BE alone", ["NL (9) and BE (8) IC1 zones; neighbours are fixed border stubs",','("Standalone - NL+BE alone", ["NL (9) and BE (8) zones; neighbouring countries as fixed boundary conditions",'),
('"Objective 3.64 M, 85 min, optimal, no penalties"]),','"Solved to optimality"]),'),
('("mr_fix - mixed resolution", ["Same NL+BE data, plus DE, DK, NO, UK as single nodes, fully optimised",','("Interconnected - 6 countries", ["Same NL+BE data, plus DE, DK, NO, UK (one node each), fully optimised",'),
('"Objective 7.07 M, 142 min, optimal, no penalties"])],','"Solved to optimality"])],'),
('sub="Identical assumptions: scenario \'baseline_blended_representative_periods\', nuclear caps, no DAC")','sub="Identical assumptions for NL+BE in both runs - only the system boundary differs")'),
('''            "LNG terminals in NL+BE run at full capacity (558 TWh) - part of this gas transits to Germany, France and the UK",\n''',''),
('"All 16 CO2 storage sites inject at round, constant volumes - storage availability is the key lever for the outcome"','"CO2 storage availability abroad is the key lever for the outcome"'),
('"nb_v2: electricity grows to 500 TWh"','"Standalone: electricity grows to 500 TWh"'),
('"nb_v2: industry routes"','"Standalone: industry routes"'),
('"nb_v2: CO2 balance reaches net zero"','"Standalone: CO2 balance reaches net zero"'),
('"mr_fix: six countries share one CO2 budget"','"Interconnected: six countries share one CO2 budget"'),
('"mr_fix: CO2 storage is used everywhere"','"Interconnected: CO2 storage is used everywhere"'),
('"Round, constant volumes suggest all sites are at their caps"','"Storage is used in all five countries"'),
('"mr_fix: industry routes, all six countries"','"Interconnected: industry routes, all six countries"'),
(r'rf"{MR}\summary_6country\05_industry_routes.png"',r'rf"{IC}\05_industry_routes.png"'),
('"mr_fix: cross-border flows in 2050"','"Interconnected: cross-border flows in 2050"'),
('cap="Net CO2 per country (emissions minus geological storage). Emissions of imported gas are booked at the import terminal / extraction site.")','cap="Net CO2 per country (emissions minus geological storage).")'),
('"CO2 flows from NL+BE to UK, NO and DK storage; gas from NO and through NL+BE to Germany. nb_v2 (for reference) has fixed border stubs only."','"CO2 flows from NL+BE to UK, NO and DK storage; gas flows from Norway and through NL+BE to Germany."'),
('"Run 1: nb_v2 (NL+BE alone)"','"Run 1: Standalone"'),
('"Run 2: mr_fix (6 countries)"','"Run 2: Interconnected"'),
('"Cheap foreign storage makes capture the least-cost option"','"Access to storage abroad makes capture the least-cost option"'),
('"NL storage full in both runs"','"NL storage sites used fully in both runs"'),
('"Nuclear is phased out in BE and NL"','"No nuclear in BE and NL by 2050"'),
('"Less electrification because CCS replaces it"','"Less electrification: capture replaces it"'),
('"Biomass is freed up as ammonia moves to gas + CCS"','"Belgium uses far more biomass in 2050"'),
('"Emissions of imported gas are booked at import, not at use",\n                         ',''),
('"Results hinge on CO2 storage volumes abroad; all storage sites inject at round, constant volumes",','"Results hinge on CO2 storage volumes abroad",'),
]
for a,b in R:
    n=t.count(a)
    if n!=1: print("MISS" if n==0 else f"x{n}", a[:70]); continue
    t=t.replace(a,b)
# drop gas and accounting slides
import re
for key in ['"Gas: NL+BE as a transit hub"','"Who is responsible for the emissions?"']:
    i=t.find("        plot_slide(pdf, "+key); j=t.find("        plot_slide(pdf,",i+10)
    assert i>0 and j>i, key; t=t[:i]+t[j:]
t=t.replace("left nb_v2, right mr_fix","left Standalone, right Interconnected").replace("left three bars nb_v2 (2030/40/50), right three bars mr_fix","left three bars Standalone (2030/40/50), right three bars Interconnected").replace("difference mr_fix minus nb_v2","difference Interconnected minus Standalone").replace("less in mr_fix","less in Interconnected")
t=t.replace('"No nuclear in NL+BE by 2050 in mr_fix (nb_v2: 9 GW)"','"No nuclear in NL+BE by 2050 (Standalone: 9 GW)"')
open(p,"w",encoding="utf-8").write(t)
left=[l for l in t.splitlines() if re.search(r"nb_v2|mr_fix",l) and "runs\\" not in l and "run_logs" not in l and "mr_fix.pkl" not in l]
print("remaining tag lines:"); print("\n".join(left))
