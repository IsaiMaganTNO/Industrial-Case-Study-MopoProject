import pickle, os, numpy as np, pandas as pd, geopandas as gpd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
OUT = "final_runs_pessimistic_ccs\\"
def save(fig, name):
    tmp = OUT + "_tmp_" + name; fig.savefig(tmp, dpi=200, bbox_inches="tight"); plt.close(fig); os.replace(tmp, OUT + name); print("saved", name)
IC = pickle.load(open(r"run_logs\nb_ccslow_ccu_cap16_dac0_NLBE.pkl", "rb"))["supply"].query("year==2050")
MR = pickle.load(open(r"run_logs\mr_ccslow_ccu_cap16_dac0_NLBE.pkl", "rb"))["supply"].query("year==2050")
RUNS = [("NL+BE alone", IC), ("With neighbours", MR)]
z = gpd.read_file(r"geodata\IC1_NWEU.geojson"); z = z[z.country.isin(["NL", "BE"])].to_crs(3035)
zc = z.set_index("id").geometry.representative_point()

# ---------- 1. building heat mix ----------
HC = {"ground-heatpump": ("Ground heat pump", "#1d6f65"), "air-heatpump": ("Air heat pump", "#2a9d8f"),
      "bio-boiler": ("Biomass boiler", "#6a994e"), "gas-boiler": ("Gas boiler", "#6c757d"), "electric-heating": ("Electric heating", "#e9c46a")}
fig, ax = plt.subplots(figsize=(8, 4.2))
for i, (lab, d) in enumerate(RUNS):
    h = d[d.carrier == "heat"].groupby("tech").energy.sum() / 1e3; left = 0
    print("heat", lab, h.round(1)[h > .1].to_dict())
    for t, (n, c) in HC.items():
        v = h.get(t, 0)
        if v < .5: continue
        ax.barh(i, v, .6, left=left, color=c, edgecolor="white", label=n if i == 0 or t not in IC[IC.carrier == "heat"].tech.unique() else None)
        if v >= 8: ax.text(left + v / 2, i, f"{v:.0f}", ha="center", va="center", color="white", fontsize=10.5, fontweight="bold")
        left += v
    ax.text(left + 2, i, f"{left:.0f} TWh", va="center", fontsize=10)
ax.set_yticks([0, 1], [r[0] for r in RUNS], fontsize=11); ax.invert_yaxis(); ax.set_xlabel("Building heat supply, NL+BE 2050 (TWh)")
for s in ("top", "right"): ax.spines[s].set_visible(False)
ax.legend(loc="upper center", bbox_to_anchor=(.5, -.22), ncol=3, frameon=False, fontsize=9.5)
ax.set_title("With neighbours, biomass boilers replace most heat pumps", fontsize=12.5, fontweight="bold", loc="left")
save(fig, "IC1_vs_neighbours_building_heat_2050.png")

# ---------- 2. electrolysis per zone ----------
fig, axs = plt.subplots(1, 2, figsize=(11, 6.6))
for ax, (lab, d) in zip(axs, RUNS):
    z.plot(ax=ax, color="#f1f3f5", edgecolor="#adb5bd", lw=.6)
    e = d[(d.carrier == "hydrogen") & (d.category == "electrolysis")].groupby("region").energy.sum() / 1e3
    print("ely", lab, e.round(1).to_dict())
    for r, v in e.items():
        if v < .5: continue
        p = zc[r]; ax.scatter(p.x, p.y, s=v * 14, color="#2a9d8f", alpha=.85, edgecolor="white", lw=1.2, zorder=4)
        ax.annotate(f"{v:.0f}", (p.x, p.y), xytext=(0, np.sqrt(v * 14) / 2 + 5), textcoords="offset points", ha="center", fontsize=10.5, fontweight="bold", color="#1d6f65")
    ax.set_title(f"{lab}\nElectrolysis {e.sum():.0f} TWh H2", fontsize=12, fontweight="bold"); ax.set_axis_off()
    ax.set_xlim(z.total_bounds[0] - 2e4, z.total_bounds[2] + 2e4); ax.set_ylim(z.total_bounds[1] - 2e4, z.total_bounds[3] + 4e4)
fig.suptitle("Where hydrogen is produced: with neighbours, NL+BE build far less electrolysis (2050, TWh H2)", fontsize=13, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, .94)); save(fig, "IC1_vs_neighbours_electrolysis_map_2050.png")

# ---------- 3. cross-border energy trade (no CO2) ----------
g = gpd.read_file(r"geodata\IC1_NWEU.geojson").dissolve("country").reset_index().to_crs(3035)
cen = {r.country: r.geometry.representative_point() for r in g.itertuples()}
P = lambda lon, lat: gpd.GeoSeries.from_xy([lon], [lat], crs=4326).to_crs(3035).iloc[0]
cen["UK"] = P(-1.5, 53.0); cen["NO"] = P(8.5, 60.0)
xb = pickle.load(open(r"run_logs\mr_ccslow_ccu_cap16_dac0_xbbio.pkl", "rb"))["xb"].query("year==2050")
xb = xb.groupby(["car", "o", "d"]).v.sum() / 1e3
C6 = ["NL", "BE", "DE", "DK", "NO", "UK"]
CARS = [("elec", "Electricity", "#e9a23b", .06), ("H2", "Hydrogen", "#2a9d8f", .08), ("CH4", "Methane (gas)", "#e76f51", .03)]
fig, axs = plt.subplots(1, 3, figsize=(15, 6.2))
for ax, (car, t, col, sc) in zip(axs, CARS):
    g.plot(ax=ax, color=g.country.map(lambda c: "#dee2e6" if c in ("NL", "BE") else "#f8f9fa"), edgecolor="#adb5bd", lw=.6)
    net = {}
    for (o, d), v in xb.get(car, pd.Series(dtype=float)).items():
        if o in C6 and d in C6 and ("NL" in (o, d) or "BE" in (o, d)):
            k = tuple(sorted((o, d))); net[k] = net.get(k, 0) + (v if (o, d) == k else -v)
    print(car, {k: round(v, 1) for k, v in net.items()})
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
    for c in C6: ax.text(cen[c].x, cen[c].y, c, ha="center", va="center", fontsize=10, fontweight="bold", color="#343a40", zorder=8,
                         bbox=dict(boxstyle="round,pad=.2", fc="white", ec="#adb5bd", lw=.5))
    ax.set_title(f"{t}\nNL+BE net export {out:.0f} TWh", fontsize=12.5, fontweight="bold")
    ax.set_xlim(2.9e6, 4.45e6); ax.set_ylim(2.85e6, 4.35e6); ax.set_axis_off()
fig.suptitle("With neighbours, NL+BE export energy: a gas transit hub, plus power and hydrogen (net flows 2050, TWh)", fontsize=13.5, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, .93)); save(fig, "MR_energy_trade_2050.png")
