import pickle, numpy as np, pandas as pd, geopandas as gpd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
g = gpd.read_file(r"geodata\IC1_NWEU.geojson"); g = g[g.country.isin(["NL", "BE"])]
cen = g.set_index("id").geometry.to_crs(3035).centroid.to_crs(4326)
d = pd.read_pickle(r"run_logs\_cong_IC1.pkl"); d = d[d.car == "elec"]
d["a"], d["b"] = d.conn.str.split("_").str[0], d.conn.str.split("_").str[2]
d = d[d.a.isin(cen.index) & d.b.isin(cen.index)]
d["key"] = d.apply(lambda r: tuple(sorted((r.a, r.b))), axis=1)
L = d.groupby("key").agg(sat=("sat", "max"), cap=("capGW", "max")).reset_index()
print("links", len(L), "full >=90% of hours:", (L.sat >= .9).sum())
E = {}
for k, f in (("IC1", "nb_ccslow_ccu_cap16_dac0"), ("CTRY", "nb_ctry_ccslow_ccu_cap16_dac0")):
    s = pickle.load(open(rf"run_logs\{f}_NLBE.pkl", "rb"))["supply"].query("year==2050 and carrier=='hydrogen' and category=='electrolysis'")
    E[k] = s.groupby("region").energy.sum() / 1e3
fig, axes = plt.subplots(1, 2, figsize=(12, 7.2))
cmap = plt.get_cmap("Reds"); norm = plt.Normalize(0, 1)
for ax, k in zip(axes, ["IC1", "CTRY"]):
    if k == "IC1":
        g.plot(ax=ax, color="#f1f3f5", edgecolor="#adb5bd", lw=.6)
        for _, r in L.sort_values("sat").iterrows():
            p, q = cen[r.key[0]], cen[r.key[1]]
            ax.plot([p.x, q.x], [p.y, q.y], color=cmap(norm(.15 + .85 * r.sat)), lw=1 + 1.2 * r.cap, solid_capstyle="round", zorder=2)
        title = "Detailed: 17 zones"
    else:
        g.dissolve("country").plot(ax=ax, color="#f1f3f5", edgecolor="#adb5bd", lw=.8)
        title = "Country level: 1 node per country"
    e = E[k]
    if k == "CTRY":   # one node per country: plot the national total at the country centroid
        tot = e.groupby(e.index.str[:2]).sum()
        pts = g.dissolve("country").geometry.to_crs(3035).centroid.to_crs(4326)
        items = [(pts[c], v, c) for c, v in tot.items()]
    else:
        items = [(cen[z], v, z) for z, v in e.items() if v > .5]
    for pt, v, lab in items:
        ax.scatter(pt.x, pt.y, s=v * 14, color="#2a9d8f", alpha=.85, edgecolor="white", lw=1.2, zorder=4)
        ax.annotate(f"{v:.0f} TWh", (pt.x, pt.y), xytext=(0, np.sqrt(v * 14) / 2 + 6), textcoords="offset points", ha="center", fontsize=10, fontweight="bold", color="#1d6f65", zorder=5)
    ax.set_title(f"{title}\nElectrolysis {e.sum():.0f} TWh H2", fontsize=12, fontweight="bold")
    ax.set_axis_off(); ax.set_aspect(1.5)
sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(0, 100)); sm.set_array([])
cb = fig.colorbar(sm, ax=axes[0], orientation="horizontal", fraction=.04, pad=.02, shrink=.8)
cb.set_label("Power link: share of hours at full capacity (%)", fontsize=9.5)
h = [Line2D([], [], marker="o", ls="", color="#2a9d8f", ms=10, label="Hydrogen from electrolysis (bubble size)"),
     Line2D([], [], color=cmap(.9), lw=3, label="Power link between zones (width = capacity)")]
fig.legend(handles=h, loc="lower center", ncol=2, frameon=False, fontsize=10)
fig.suptitle("Grid limits inside the countries shape where hydrogen is made (2050)", fontsize=14, fontweight="bold")
fig.tight_layout(rect=(0, .05, 1, .95))
out = r"final_runs_pessimistic_ccs\IC1_vs_country_grid_congestion_electrolysis_2050.png"; fig.savefig(out, dpi=200); print(out)
print(L.sort_values("sat", ascending=False).round(2).to_string())
