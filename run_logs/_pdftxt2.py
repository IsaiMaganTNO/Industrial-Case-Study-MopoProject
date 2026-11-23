import pymupdf
d=pymupdf.open(r"reports\resolution_IC1_vs_country_final.pdf")
for i,p in enumerate(d):
    t=p.get_text()
    if "Hydrogen supply" in t or "Where captured CO2" in t: print("--- p",i+1); print(t[:700])
