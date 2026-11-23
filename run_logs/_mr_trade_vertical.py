import pickle, os, pandas as pd, geopandas as gpd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
OUT = "final_runs_pessimistic_ccs\\"
g = gpd.read_file(r"geodata\IC1_NWEU.geojson").dissolve("country").reset_index().to_crs(3035)
cen = {r.country: r.geometry.representative_point() for r in g.itertuples()}
P = lambda lon, lat: gpd.GeoSeries.from_xy([lon], [lat], crs=4326).to_crs(3035).iloc[0]
cen["UK"] = P(-1.5, 53.0); cen["NO"] = P(8.5, 60.0)
xb = pickle.load(open(r"run_logs\mr_ccslow_ccu_cap16_dac0_xbbio.pkl", "rb"))["xb"].query("year==2050")
xb = xb.groupby(["car", "o", "d"]).v.sum() / 1e3
C6 = ["NL", "BE", "DE", "DK", "NO", "UK"]
CARS = [("elec", "Electricity", "#e9a23b", .06), ("H2", "Hydrogen", "#2a9d8f", .08), ("CH4", "Methane (gas)", "#e76f51", .03)]
fig, axs = plt.subplots(3, 1, figsize=(6.2, 16))
for ax, (car, t, col, sc) in zip(axs, CARS):
    g.plot(ax=ax, color=g.country.map(lambda c: "#dee2e6" if c in ("NL", "BE") else "#f8f9fa"), edgecolor="#adb5bd", lw=.6)
    net = {}
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
    for c in C6: ax.text(cen[c].x, cen[c].y, c, ha="center", va="center", fontsize=10, fontweight="bold", color="#343a40", zorder=8,
                         bbox=dict(boxstyle="round,pad=.2", fc="white", ec="#adb5bd", lw=.5))
    ax.set_title(f"{t}: NL+BE net export {out:.0f} TWh", fontsize=12.5, fontweight="bold")
    ax.set_xlim(2.9e6, 4.45e6); ax.set_ylim(2.85e6, 4.35e6); ax.set_axis_off()
    print(car, round(out, 1))
fig.suptitle("With neighbours, NL+BE export energy:\na gas transit hub, plus power and hydrogen\n(net flows 2050, TWh)", fontsize=13, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, .95))
tmp = OUT + "_tmp_trade_v.png"; fig.savefig(tmp, dpi=200, bbox_inches="tight"); plt.close(fig)
os.replace(tmp, OUT + "MR_energy_trade_2050_vertical.png"); print("saved")
