s=open("tools/make_deck_final3.py",encoding="utf8").read()
fn='''DCAT = [("Fossil, no capture", "#6c757d"), ("Fossil + carbon capture", "#457b9d"), ("Electricity", "#f4a261"), ("Hydrogen", "#2a9d8f"),
        ("Methanol from captured CO2", "#e76f51"), ("Biomass / scrap / other low-carbon", "#6a994e")]
def dcat(r):
    f = r.fuel
    if f in ("natural gas", "coal", "alt. fuel mix", "generic: EU average mix", "generic: reference route"): return DCAT[1][0] if r.cc else DCAT[0][0]
    if f == "electricity": return DCAT[2][0]
    if f == "hydrogen": return DCAT[3][0]
    if f == "methanol": return DCAT[4][0]
    return DCAT[5][0]
SECS = ["steel (primary)", "steel (secondary)", "olefins", "ammonia", "cement", "glass (container)", "glass (float)", "glass (fibre)", "chlorine", "aluminium", "paper", "pulp"]
def f_decarb():
    fig, axes = plt.subplots(1, 3, figsize=(18, 6.4), sharey=True)
    for ax, k in zip(axes, K):
        p = D[k]["prod"]; p = p.assign(cat=p.apply(dcat, axis=1))
        y = 0; ticks = []
        for sec in SECS:
            for yr in YRS:
                q = p[(p.sector == sec) & (p.year == yr)]; t = q.output.sum()
                if t <= 0: continue
                sh = q.groupby("cat").output.sum() / t * 100; left = 0
                for l, c in DCAT:
                    v = sh.get(l, 0); ax.barh(y, v, .85, left=left, color=c, edgecolor="white", lw=.3); left += v
                ticks.append((y, f"{sec}  {yr}" if yr == 2030 else str(yr))); y -= 1
            y -= .6
        ax.set_yticks([t[0] for t in ticks], [t[1] for t in ticks], fontsize=7); ax.set_xlim(0, 100); ax.set_xlabel("% of production (NL+BE)")
        ax.set_title(f"{SH[k]}\\n({SUB[k]})", fontsize=12, fontweight="bold")
        for s_ in ["top", "right"]: ax.spines[s_].set_visible(False)
    fig.legend([plt.Rectangle((0, 0), 1, 1, color=c) for _, c in DCAT], [l for l, _ in DCAT], loc="lower center", ncol=6, frameon=False, fontsize=10)
    fig.tight_layout(rect=(0, .05, 1, 1)); return save(fig, "decarb")
def f_cost():'''
s=s.replace("def f_cost():",fn,1)
s=s.replace('''        M.plot_slide(pdf, "Steel, plastics and glass by country"''','''        M.plot_slide(pdf, "How each industrial sector decarbonises", f_decarb(), [], section=SEC, imgw=.9,
                     cap="Share of production per sector by route type, 2030 / 2040 / 2050, NL+BE together. Production volumes are fixed; only the technology changes.")
        M.plot_slide(pdf, "Steel, plastics and glass by country"''',1)
open("tools/make_deck_final3.py","w",encoding="utf8").write(s)
