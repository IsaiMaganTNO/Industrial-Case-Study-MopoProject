import pickle
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
R = {"IC1": "nb_ccslow_ccu_cap16_dac0", "MR": "mr_ccslow_ccu_cap16_dac0"}
D = {k: pickle.load(open(rf"run_logs\{v}_NLBE.pkl", "rb")) for k, v in R.items()}
CAT = {"MOE": "Electricity", "(H2)DRI-EAF": "Green hydrogen", "(H2)NH3": "Green hydrogen",
       "(NG)DRI-EAF-MEA": "Fossil + CO2 capture", "(NG)NH3-MVR-MEA-DEA": "Fossil + CO2 capture", "(LN)O-MEA": "Fossil + CO2 capture",
       "LC3-(Afm)Oxy-CaL": "Alternative fuels + CO2 capture", "LC3-(Afm)Oxy-MEA": "Alternative fuels + CO2 capture",
       "(MeOH)O-MEA": "Methanol from captured CO2", "((COEL)MeOH)O-MEA": "Methanol from captured CO2",
       "CEM2-(BMW)Oxy-MEA": "Biomass + CO2 capture"}
COL = {"Electricity": "#f4a261", "Green hydrogen": "#2a9d8f", "Methanol from captured CO2": "#e76f51",
       "Biomass + CO2 capture": "#6a994e", "Alternative fuels + CO2 capture": "#a98467", "Fossil + CO2 capture": "#6c757d"}
SECS = [("steel (primary)", "Primary steel"), ("ammonia", "Ammonia"), ("olefins", "Plastics (olefins)"), ("cement", "Cement")]
fig, axes = plt.subplots(len(SECS), 1, figsize=(6.2, 10), sharex=True)
for ax, (sec, t) in zip(axes, SECS):
    for i, k in enumerate(["IC1", "MR"]):
        p = D[k]["prod"].query("year==2050 and sector==@sec")
        s = p.groupby(p.tech.map(lambda x: CAT.get(x, "Other"))).output.sum(); s = s / s.sum() * 100
        unk = [x for x in p.tech.unique() if x not in CAT]
        if unk: print("unmapped", sec, unk)
        left = 0
        for c, col in COL.items():
            v = s.get(c, 0)
            if v < .5: continue
            ax.barh(i, v, .62, left=left, color=col, edgecolor="white", label=c)
            if v >= 9: ax.text(left + v / 2, i, f"{v:.0f}%", ha="center", va="center", color="white", fontsize=10, fontweight="bold")
            left += v
    ax.set_yticks([0, 1], ["NL+BE alone", "With neighbours"], fontsize=10); ax.invert_yaxis()
    ax.set_title(t, fontsize=12, fontweight="bold", loc="left"); ax.set_xlim(0, 100)
    for sp in ("top", "right"): ax.spines[sp].set_visible(False)
axes[-1].set_xlabel("Share of 2050 production in NL+BE (%)", fontsize=10)
h, l = [], []
for ax in axes:
    for hh, ll in zip(*ax.get_legend_handles_labels()):
        if ll not in l: h.append(hh); l.append(ll)
order = [x for x in COL if x in l]; h = [h[l.index(x)] for x in order]
fig.legend(h, order, loc="lower center", ncol=2, frameon=False, fontsize=9.5, bbox_to_anchor=(.5, 0))
fig.suptitle("With CO2 storage abroad, industry shifts\nfrom electricity and hydrogen to carbon capture", fontsize=12.5, fontweight="bold")
fig.tight_layout(rect=(0, .07, 1, 1)); out = r"final_runs_pessimistic_ccs\IC1_vs_neighbours_industry_routes_2050.png"
fig.savefig(out, dpi=200); print(out)

