import pymupdf
doc=pymupdf.open(r"runs\3day_nb_ctry\SLIDES_Standalone_vs_CountryLevel.pdf")
for i,p in enumerate(doc):
  H=p.rect.height; W=p.rect.width
  # bullet text: right column blocks overlapping caption band (y between 0.87H..0.945H)
  bad=[b[4][:40] for b in p.get_text("blocks") if b[1]<0.87*H<b[3] and b[0]>0.5*W]
  if bad: print(i+1,bad)
print("done")
