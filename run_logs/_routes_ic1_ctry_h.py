import pickle, os
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
R = {"IC1": "nb_ccslow_ccu_cap16_dac0", "CTRY": "nb_ctry_ccslow_ccu_cap16_dac0"}
D = {k: pickle.load(open(rf"run_logs\{v}_NLBE.pkl", "rb")) for k, v in R.items()}
CAT = {"MOE": "Electricity", "(EL)-CC_gco": "Electricity", "(H2)DRI-EAF": "Green hydrogen", "(H2)-CC_gco": "Green hydrogen",
       "(NG)DRI-EAF-MEA": "Fossil + CO2 capture", "(LN)O-MEA": "Fossil + CO2 capture",
       "(MeOH)O-MEA": "Methanol from captured CO2", "((COEL)MeOH)O-MEA": "Methanol from captured CO2",
       "(LN)O": "Fossil, no capture", "(NG)_gco": "Fossil, no capture"}
COL = {"Electricity": "#f4a261", "Green hydrogen": "#2a9d8f", "Methanol from captured CO2": "#e76f51",
       "Fossil + CO2 capture": "#6c757d", "Fossil, no capture": "#343a40"}
LAB = {"IC1": "17 zones", "CTRY": "Country level"}
def make(secs, out, title):
    fig, axes = plt.subplots(len(secs), 1, figsize=(6.2, 2.6 * len(secs) + 1.6), sharex=True)
    for ax, (sec, yr, t) in zip(axes, secs):
        for i, k in enumerate(["IC1", "CTRY"]):
            p = D[k]["prod"].query("year==@yr and sector==@sec")
            unk = [x for x in p.tech.unique() if x not in CAT and p[p.tech == x].output.sum() > 0]
            if unk: print("unmapped", sec, unk)
            s = p.groupby(p.tech.map(lambda x: CAT.get(x, "Other"))).output.sum(); s = s / s.sum() * 100
            print(sec, yr, k, s.round(1)[s > .5].to_dict())
            left = 0
            for c, col in COL.items():
                v = s.get(c, 0)
                if v < .5: continue
                ax.barh(i, v, .62, left=left, color=col, edgecolor="white", label=c)
                if v >= 9: ax.text(left + v / 2, i, f"{v:.0f}%", ha="center", va="center", color="white", fontsize=10, fontweight="bold")
                left += v
        ax.set_yticks([0, 1], [LAB["IC1"], LAB["CTRY"]], fontsize=10); ax.invert_yaxis()
        ax.set_title(t, fontsize=12, fontweight="bold", loc="left"); ax.set_xlim(0, 100)
        for sp in ("top", "right"): ax.spines[sp].set_visible(False)
    axes[-1].set_xlabel("Share of production in NL+BE (%)", fontsize=10)
    h, l = [], []
    for ax in axes:
        for hh, ll in zip(*ax.get_legend_handles_labels()):
            if ll not in l: h.append(hh); l.append(ll)
    order = [x for x in COL if x in l]; h = [h[l.index(x)] for x in order]
    fig.legend(h, order, loc="lower center", ncol=2, frameon=False, fontsize=9.5, bbox_to_anchor=(.5, 0))
    fig.suptitle(title, fontsize=12.5, fontweight="bold")
    fig.tight_layout(rect=(0, .1 if len(secs) < 3 else .08, 1, 1))
    tmp = r"final_runs_pessimistic_ccs\_tmp_" + out; fig.savefig(tmp, dpi=200); plt.close(fig)
    os.replace(tmp, r"final_runs_pessimistic_ccs" + "\\" + out); print("saved", out)
make([("steel (primary)", 2050, "Primary steel (2050)"), ("olefins", 2050, "Plastics (olefins) (2050)")],
     "IC1_vs_country_industry_routes_2050_h.png", "At country level, industry relies less on\nhydrogen and methanol from captured CO2")
make([("steel (primary)", 2050, "Primary steel (2050)"), ("olefins", 2050, "Plastics (olefins) (2050)"), ("glass (container)", 2040, "Container glass (2040)")],
     "IC1_vs_country_industry_routes_3sectors_h.png", "At country level, industry relies less on\nhydrogen and methanol from captured CO2")
