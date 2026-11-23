import pickle, os, numpy as np, pandas as pd, geopandas as gpd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
OUT = "final_runs_pessimistic_ccs\\"
g = gpd.read_file(r"geodata\IC1_NWEU.geojson").dissolve("country").reset_index().to_crs(3035)
cen = {r.country: r.geometry.representative_point() for r in g.itertuples()}
P = lambda lon, lat: gpd.GeoSeries.from_xy([lon], [lat], crs=4326).to_crs(3035).iloc[0]
cen["UK"] = P(-1.5, 53.0); cen["NO"] = P(8.5, 60.0)
xb = pickle.load(open(r"run_logs\mr_ccslow_ccu_cap16_dac0_xbbio.pkl", "rb"))["xb"].query("year==2050")
xb = xb.groupby(["car", "o", "d"]).v.sum() / 1e3
bio = pickle.load(open(r"run_logs\mr_ccslow_ccu_cap16_dac0_xbbio.pkl", "rb"))["bio"].query("year==2050")
bio = bio.groupby("c").v.sum() / 1e3
C6 = ["NL", "BE", "DE", "DK", "NO", "UK"]

def base(ax):
    g.plot(ax=ax, color=g.country.map(lambda c: "#dee2e6" if c in ("NL", "BE") else "#f8f9fa"), edgecolor="#adb5bd", lw=.6)
    ax.set_xlim(2.9e6, 4.45e6); ax.set_ylim(2.85e6, 4.35e6); ax.set_axis_off()

def labels(ax, below=0):
    for c in C6: ax.text(cen[c].x, cen[c].y - below, c, ha="center", va="center", fontsize=10, fontweight="bold", color="#343a40", zorder=8,
                         bbox=dict(boxstyle="round,pad=.2", fc="white", ec="#adb5bd", lw=.5))

def trade(ax, car, t, col, sc):
    base(ax); net = {}
    for (o, d), v in xb.get(car, pd.Series(dtype=float)).items():
        if o in C6 and d in C6 and ("NL" in (o, d) or "BE" in (o, d)):
            k = tuple(sorted((o, d))); net[k] = net.get(k, 0) + (v if (o, d) == k else -v)
    out = 0
    for (a, b), v in net.items():
        if abs(v) < 1: continue
        s, d_ = (a, b) if v > 0 else (b, a); v = abs(v)
        if s in ("NL", "BE") and d_ not in ("NL", "BE"): out += v
        if d_ in ("NL", "BE") and s not in ("NL", "BE"): out -= v
        p, q = cen[s], cen[d_]; dx, dy = q.x - p.x, q.y - p.y
        ax.annotate("", xy=(q.x - dx * .15, q.y - dy * .15), xytext=(p.x + dx * .15, p.y + dy * .15), zorder=5,
                    arrowprops=dict(arrowstyle="-|>,head_width=.45,head_length=.7", lw=max(1.3, v * sc), color=col, shrinkA=0, shrinkB=0, connectionstyle="arc3,rad=.1"))
        ax.text(p.x + dx * .5, p.y + dy * .5, f"{v:.0f}", ha="center", va="center", fontsize=10, fontweight="bold", color=col, zorder=7,
                bbox=dict(boxstyle="round,pad=.2", fc="white", ec=col, lw=.5))
    labels(ax); ax.set_title(f"{t}\nNL+BE net export {out:.0f} TWh", fontsize=12.5, fontweight="bold"); print(car, round(out, 1))

def save(fig, name):
    tmp = OUT + "_tmp_" + name; fig.savefig(tmp, dpi=200, bbox_inches="tight"); plt.close(fig); os.replace(tmp, OUT + name); print("saved", name)

# option 1: electricity + hydrogen
fig, axs = plt.subplots(1, 2, figsize=(11, 6.4))
trade(axs[0], "elec", "Electricity", "#e9a23b", .06); trade(axs[1], "H2", "Hydrogen", "#2a9d8f", .08)
fig.suptitle("With neighbours, NL+BE export electricity and hydrogen, mainly to Germany (net flows 2050, TWh)", fontsize=13, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, .93)); save(fig, "MR_energy_trade_elec_h2_2050.png")

# option 2: electricity + hydrogen + biomass use per country
fig, axs = plt.subplots(1, 3, figsize=(15.5, 6.4))
trade(axs[0], "elec", "Electricity", "#e9a23b", .06); trade(axs[1], "H2", "Hydrogen", "#2a9d8f", .08)
ax = axs[2]; base(ax)
for c in C6:
    v = bio.get(c, 0); p = cen[c]
    ax.scatter(p.x, p.y, s=v * 6, color="#6a994e", alpha=.8, edgecolor="white", lw=1.2, zorder=4)
    ax.text(p.x, p.y, f"{c}\n{v:.0f}", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#343a40", zorder=8,
            bbox=dict(boxstyle="round,pad=.2", fc="white", ec="#adb5bd", lw=.5, alpha=.9))
nlbe = bio.get("NL", 0) + bio.get("BE", 0)
ax.set_title(f"Biomass use\nNL+BE {nlbe:.0f} TWh (alone: 43 TWh)", fontsize=12.5, fontweight="bold")
print("bio", bio.round(1).to_dict())
fig.suptitle("With neighbours (2050, TWh): NL+BE export electricity and hydrogen and use more biomass", fontsize=13.5, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, .93)); save(fig, "MR_energy_trade_elec_h2_biomass_2050.png")
