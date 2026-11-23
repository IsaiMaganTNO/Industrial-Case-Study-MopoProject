p=r"tools\make_slides.py"; t=open(p,encoding="utf-8-sig").read()
def cut(t,key):
    i=t.find(key); i=t.rfind("\n",0,i)+1
    j=t.find("section=",i); j=t.find("\n",j)+1
    return t[:i]+t[j:]
t=cut(t,'plot_slide(pdf, "CO2: NL+BE become a CO2 exporter"')
i=t.find('        text_slide(pdf, "Caveats and next steps"'); j=t.find('section="Wrap-up")',i); j=t.find("\n",j)+1
assert i>0 and j>i; t=t[:i]+t[j:]
# sharper images: embed at high dpi, no resampling blur
t=t.replace('ax.imshow(mpimg.imread(path)); ax.axis("off")','ax.imshow(mpimg.imread(path), interpolation="lanczos"); ax.axis("off")')
t=t.replace('plt.rcParams.update({"font.family": "DejaVu Sans"})','plt.rcParams.update({"font.family": "DejaVu Sans", "savefig.dpi": 300, "image.resample": True})')
# industry slide: full-width image, notes in caption
a=t.find('        plot_slide(pdf, "Industry: from bio and electric to gas + CCS"'); b=t.find("\n",t.find("section=",a))+1
t=t[:a]+'''        fig = frame("Industry: from bio and electric to gas + CCS", "Ammonia: biomass -> gas + CCS  |  Steel: molten oxide -> gas DRI + CCS  |  Access to storage abroad makes capture the least-cost option", S)
        img(fig, rf"{CMP}\\C03_industry_routes.png", [.01, .14, .98, .7])
        caption(fig, "Route shares per sector. Each panel: left three bars Standalone (2030/40/50), right three bars Interconnected.")
        pdf.savefig(fig); plt.close(fig)
'''+t[b:]
open(p,"w",encoding="utf-8").write(t)
for k in ["CO2 exporter","Caveats","C03_industry"]: print(k, t.count(k))
