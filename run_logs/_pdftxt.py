import pymupdf
d=pymupdf.open(r"reports\resolution_IC1_vs_country_final.pdf")
for i in [2,3,4,11]: print(f"--- p{i+1}"); print(d[i].get_text()[:1800])
