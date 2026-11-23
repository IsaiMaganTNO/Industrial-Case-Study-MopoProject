import pymupdf
d=pymupdf.open(r"runs\3day_mr_fix\SLIDES_nb_v2_vs_mr_fix.pdf")
for i,p in enumerate(d):
    H=p.rect.height; W=p.rect.width
    for b in p.get_text("blocks"):
        x0,y0,x1,y1,t=b[:5]
        if x0>W*0.6 and y1>H*0.80 and y0<H*0.87: print(i+1,"NOTE-LOW",round(y1/H,2),t[:50].replace("\n"," "))
        if y1/H>0.97 and "MOPO" not in t and not t.strip().isdigit(): print(i+1,"BOTTOM",t[:50])
p=d[2]
for b in p.get_text("blocks"): print(round(b[0]/p.rect.width,2),round(b[2]/p.rect.width,2),round(b[1]/p.rect.height,2),b[4][:70].replace("\n","|"))
