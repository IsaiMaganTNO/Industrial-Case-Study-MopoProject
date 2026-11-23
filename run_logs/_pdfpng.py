import pymupdf
d=pymupdf.open(r"reports\resolution_IC1_vs_country_final.pdf")
for i,p in enumerate(d): p.get_pixmap(dpi=55).save(rf"run_logs\_slide_tmp_res\p{i+1:02d}.png")
print(len(d))
