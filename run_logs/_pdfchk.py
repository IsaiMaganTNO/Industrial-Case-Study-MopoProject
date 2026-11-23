import pymupdf
doc=pymupdf.open(r"runs\3day_nb_ctry\SLIDES_Standalone_vs_CountryLevel.pdf")
for i,p in enumerate(doc):
  t=p.get_text()
  # crude overflow check: text blocks extending beyond page or overlapping footer
  bl=[b for b in p.get_text("blocks") if b[3]>p.rect.height*0.97 and "Industrial Case" not in b[4] and not b[4].strip().isdigit()]
  print(i+1, t.split("\n")[0][:70], "| low blocks:",len(bl))
