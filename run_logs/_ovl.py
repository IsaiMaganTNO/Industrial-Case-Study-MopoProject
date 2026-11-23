import pymupdf
d=pymupdf.open(r"runs\3day_mr_fix\SLIDES_Standalone_vs_Interconnected.pdf")
for i,p in enumerate(d):
    H=p.rect.height; W=p.rect.width
    for b in p.get_text("blocks"):
        x0,y0,x1,y1,t=b[:5]
        if x1>W-5 or (y1>H*0.87 and y0<H*0.87 and "MOPO" not in t): print(i+1,"OVER",round(y0/H,2),round(y1/H,2),round(x1/W,2),t[:60].replace("\n"," "))
print("pages",len(d))
