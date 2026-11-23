import pymupdf,re
d=pymupdf.open(r"runs\3day_mr_fix\SLIDES_Standalone_vs_Interconnected.pdf")
txt=" ".join(p.get_text() for p in d)
print("pages",len(d))
for w in ["nb_v2","mr_fix","books","booked","LNG","terminal","stub","IC1","penalt"]:
    print(w, len(re.findall(w,txt)))
