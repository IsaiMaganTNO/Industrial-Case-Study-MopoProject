import pickle, re
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
D = pickle.load(open(r"run_logs\nb_ccslow_ccu_cap16_dac0_NLBE.pkl", "rb"))
s = D["supply"]; s = s[(s.year == 2050) & (s.carrier == "electricity") & (s.energy > 0)]
def grp(t):
    if t.startswith("wind-off"): return "Offshore wind"
    if t.startswith("wind-on"): return "Onshore wind"
    if t.startswith("solar"): return "Solar PV"
    if t.startswith("nuclear"): return "Nuclear"
    if t.startswith("CCGT-H2"): return "Hydrogen turbines"
    if t.startswith("battery"): return "Battery discharge"
    if t.startswith("RoR"): return "Hydro (run-of-river)"
    return "Other"
def cn(r):
    reg = str(r.region) if r.region is not None and str(r.region) != "None" else ""
    if reg[:2] in ("NL", "BE"): return reg[:2]
    m = re.search(r"_NS(NL|BE)", r.tech) or re.search(r"_(NL|BE)C", r.tech); return m.group(1) if m else "?"
s = s.assign(g=s.tech.map(grp), c=s.apply(cn, axis=1))
print(s[s.c == "?"].tech.unique())
p = s.pivot_table(index="c", columns="g", values="energy", aggfunc="sum").fillna(0) / 1e3
p.loc["NL+BE"] = p.sum()
p = p.reindex(["NL", "BE", "NL+BE"])
ORD = [("Offshore wind", "#1d3557"), ("Onshore wind", "#457b9d"), ("Solar PV", "#f4a261"), ("Nuclear", "#9d4edd"),
       ("Hydrogen turbines", "#2a9d8f"), ("Hydro (run-of-river)", "#8ecae6"), ("Battery discharge", "#adb5bd"), ("Other", "#6c757d")]
ORD = [(g, c) for g, c in ORD if g in p.columns and p[g].sum() > 0]
print(p.round(1).to_string())
fig, ax = plt.subplots(figsize=(9, 6))
for j, r in enumerate(p.index):
    b = 0
    for g, c in ORD:
        v = p.loc[r, g]
        ax.bar(j, v, .6, bottom=b, color=c, edgecolor="white", label=g if j == 0 else None)
        if v > 15: ax.text(j, b + v / 2, f"{v:.0f}", ha="center", va="center", color="white", fontsize=10, fontweight="bold")
        b += v
    ax.text(j, b + 6, f"{b:.0f} TWh", ha="center", fontsize=11, fontweight="bold")
ax.set_xticks(range(len(p)), ["Netherlands", "Belgium", "NL + BE"], fontsize=11)
ax.set_ylabel("Electricity supply 2050 (TWh/yr)", fontsize=11); ax.set_ylim(0, p.sum(axis=1).max() * 1.1)
ax.set_title("Annual electricity supply by technology, 2050", fontsize=13, fontweight="bold")
for sp in ("top", "right"): ax.spines[sp].set_visible(False)
ax.grid(axis="y", color="#e3e7ec"); ax.set_axisbelow(True)
h, l = ax.get_legend_handles_labels(); ax.legend(h[::-1], l[::-1], frameon=False, loc="upper left", bbox_to_anchor=(1.01, 1), fontsize=10)
fig.tight_layout(); out = r"final_runs_pessimistic_ccs\IC1_electricity_supply_2050.png"; fig.savefig(out, dpi=200); print(out)
