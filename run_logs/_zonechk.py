import pymupdf,re
doc=pymupdf.open(r"runs\3day_nb_ctry\SLIDES_Standalone_vs_CountryLevel.pdf")
for i,p in enumerate(doc):
  for b in p.get_text("blocks"):
    s=b[4].replace("\n"," ")
    if "Industrial Case Study (MOPO)" in s: continue
    if re.search(r"zone|(NL|BE)C\d",s): print(i+1,"|",s[:150])
