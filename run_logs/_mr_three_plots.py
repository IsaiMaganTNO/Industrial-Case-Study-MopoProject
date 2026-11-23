import pickle, numpy as np, pandas as pd, geopandas as gpd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.colors import TwoSlopeNorm
OUT = "final_runs_pessimistic_ccs\\"
g = gpd.read_file(r"geodata\IC1_NWEU.geojson").dissolve("country").reset_index().to_crs(3035)
cen = {r.country: r.geometry.representative_point() for r in g.itertuples()}
cen["UK"] = gpd.GeoSeries.from_xy([-1.5], [53.0], crs=4326).to_crs(3035).iloc[0]
cen["NO"] = gpd.GeoSeries.from_xy([8.5], [60.0], crs=4326).to_crs(3035).iloc[0]
MR = pickle.load(open(r"run_logs\mr_ccslow_ccu_cap16_dac0.pkl", "rb"))
IC = pickle.load(open(r"run_logs\nb_ccslow_ccu_cap16_dac0.pkl", "rb"))
em = MR["emis"].query("year==2050"); em = em.groupby(em.region.str[:2]).co2.sum() / 1e3
cp = MR["co2pipe"].query("year==2050").assign(o=lambda x: x.origin.str[:2], d=lambda x: x.dest.str[:2])
cp = cp[cp.o != cp.d].groupby(["o", "d"]).co2.sum() / 1e3
st = MR["co2store"].query("year==2050"); st = st.groupby(st.region.str[:2]).co2.sum() / 1e3
print("emis", em.round(1).to_dict()); print("co2 x-border", cp.round(1).to_dict()); print("stored", st.round(1).to_dict())
xb = pickle.load(open(r"run_logs\mr_ccslow_ccu_cap16_dac0_xbbio.pkl", "rb"))["xb"].query("year==2050")
xb = xb.groupby(["car", "o", "d"]).v.sum() / 1e3

def arrow(ax, a, b, val, col, scale, lab=True, off=0):
    p, q = cen[a], cen[b]; dx, dy = q.x - p.x, q.y - p.y; L = np.hypot(dx, dy); nx, ny = -dy / L * off, dx / L * off
    ax.annotate("", xy=(q.x - dx * .12 + nx, q.y - dy * .12 + ny), xytext=(p.x + dx * .12 + nx, p.y + dy * .12 + ny),
                arrowprops=dict(arrowstyle="-|>,head_width=.5,head_length=.8", lw=max(1.2, val * scale), color=col, shrinkA=0, shrinkB=0), zorder=5)
    if lab: ax.text(p.x + dx * .5 + nx * 2.2, p.y + dy * .5 + ny * 2.2, f"{val:.0f}", ha="center", va="center", fontsize=9.5, fontweight="bold", color=col,
                    bbox=dict(fc="white", ec="none", alpha=.8, pad=.6), zorder=6)

def frame(ax):
    ax.set_xlim(2.9e6, 4.45e6); ax.set_ylim(2.85e6, 4.35e6); ax.set_axis_off()

# ---------- A: who emits, who stores ----------
fig = plt.figure(figsize=(13, 8.2)); ax = fig.add_axes([0, .02, .6, .9])
P = lambda lon, lat: gpd.GeoSeries.from_xy([lon], [lat], crs=4326).to_crs(3035).iloc[0]
cap = MR["co2net"].query("year==2050 and role=='captured'"); cap = cap.groupby(cap.region.str[:2]).co2.sum() / 1e3
print("captured", cap.round(1).to_dict())
g.plot(ax=ax, color=g.country.map(lambda c: "#e9ecef" if c in ("NL", "BE") else "#f8f9fa"), edgecolor="#adb5bd", lw=.7)
# capture bubbles (on land) and country labels next to them
CAP = {"NL": (5.9, 52.4), "BE": (4.6, 50.7), "DE": (10.0, 51.3), "DK": (9.3, 56.0), "NO": (9.5, 61.0), "UK": (-1.8, 52.6)}
for c, (lon, lat) in CAP.items():
    p = P(lon, lat); v = cap.get(c, 0)
    ax.scatter(p.x, p.y, s=v * 22, color="#2a9d8f", alpha=.85, edgecolor="white", lw=1.2, zorder=4)
    ax.text(p.x, p.y - np.sqrt(v * 22) * 900 - 2.5e4, f"{c}  captured {v:.0f}", ha="center", va="top", fontsize=9.5, fontweight="bold", zorder=9,
            bbox=dict(boxstyle="round,pad=.25", fc="white", ec="#495057", lw=.5, alpha=.92))
# storage triangles at sea
STO = {"NL": (4.4, 53.9), "DK": (7.8, 57.4), "NO": (5.0, 59.6), "UK": (1.3, 55.3)}
for c, v in st.items():
    p = P(*STO[c]); ax.scatter(p.x, p.y, s=v * 9, marker="v", color="#212529", alpha=.8, zorder=6)
    ax.text(p.x + np.sqrt(v * 9) * 700 + 2e4, p.y, f"stored {v:.0f}", ha="left", va="center", fontsize=9, color="#212529", zorder=8,
            bbox=dict(boxstyle="round,pad=.2", fc="white", ec="none", alpha=.85))
# CO2 transport arrows with explicit start/end points so arrowheads do not stack
ROUTE = {("NL", "UK"): ((4.3, 52.3), (1.8, 54.6)), ("BE", "UK"): ((3.0, 51.3), (1.0, 52.4)), ("DE", "UK"): ((7.4, 53.9), (2.2, 55.5)),
         ("DE", "NO"): ((8.6, 54.6), (5.6, 59.0)), ("BE", "NL"): ((4.4, 51.2), (4.6, 51.7)), ("NL", "BE"): ((5.6, 51.5), (5.3, 51.1))}
for (a, b), v in cp.items():
    if v <= 1: continue
    (x0, y0), (x1, y1) = ROUTE[(a, b)]; p, q = P(x0, y0), P(x1, y1)
    ax.annotate("", xy=(q.x, q.y), xytext=(p.x, p.y), zorder=5,
                arrowprops=dict(arrowstyle="-|>,head_width=.45,head_length=.7", lw=max(1.3, v * .13), color="#6c3483", shrinkA=0, shrinkB=0,
                                connectionstyle="arc3,rad=.12"))
    m = ((p.x + q.x) / 2, (p.y + q.y) / 2)
    ax.text(*m, f"{v:.0f}", ha="center", va="center", fontsize=9.5, fontweight="bold", color="#6c3483", zorder=7,
            bbox=dict(boxstyle="round,pad=.2", fc="white", ec="#6c3483", lw=.5, alpha=.9))
frame(ax)
from matplotlib.lines import Line2D
H = [Line2D([], [], marker="o", ls="", color="#2a9d8f", ms=10, label="CO2 captured (Mt)"),
     Line2D([], [], marker="v", ls="", color="#212529", ms=10, label="CO2 stored (Mt)"),
     Line2D([], [], color="#6c3483", lw=3, label="CO2 transported across borders (Mt)")]
ax.legend(handles=H, loc="upper left", frameon=True, fontsize=9.5, framealpha=.9)
ia = fig.add_axes([.72, .3, .25, .45])
cats = ["CO2\ncaptured", "Stored\nin NL", "Stored\nabroad"]
alone = [31.9, 16, 0]; nb = [cap["NL"] + cap["BE"], 16, cp.loc[("NL", "UK")] + cp.loc[("BE", "UK")]]
y = np.arange(len(cats)); ia.barh(y - .2, alone, .38, color="#adb5bd", label="NL+BE alone"); ia.barh(y + .2, nb, .38, color="#6c3483", label="With neighbours")
for i, (a, b) in enumerate(zip(alone, nb)):
    ia.text(a + 1, i - .2, f"{a:.0f}", va="center", fontsize=9); ia.text(b + 1, i + .2, f"{b:.0f}", va="center", fontsize=9, fontweight="bold")
ia.set_yticks(y, cats, fontsize=9.5); ia.invert_yaxis(); ia.set_xlabel("Mt CO2, NL+BE 2050", fontsize=9); ia.legend(fontsize=8.5, frameon=False, loc="lower right")
for s in ("top", "right"): ia.spines[s].set_visible(False)
fig.suptitle("With neighbours, NL+BE capture more CO2 and ship it to UK storage (2050)", fontsize=13.5, fontweight="bold", y=.99)
# layout check: report overlapping text boxes and map content spilling into the inset
fig.canvas.draw(); R = fig.canvas.get_renderer()
T = [(t.get_text().replace("\n", " "), t.get_window_extent(R)) for t in ax.texts if t.get_text()]
for i in range(len(T)):
    for j in range(i + 1, len(T)):
        if T[i][1].overlaps(T[j][1]): print("OVERLAP:", T[i][0], "|", T[j][0])
ib = ia.get_tightbbox(R); mb = ax.get_window_extent(R)
print("map axes x1 =", round(mb.x1), " inset x0 =", round(ib.x0), "->", "OK" if mb.x1 < ib.x0 else "OVERLAP map/inset")
for t, b in T:
    if b.x1 > ib.x0 and b.y1 > ib.y0 and b.y0 < ib.y1: print("TEXT INTO INSET:", t)
    if not mb.contains(b.x0, b.y0) or not mb.contains(b.x1, b.y1): print("TEXT OUTSIDE MAP:", t)
import os
tmp = OUT + "_tmp_co2map.png"; fig.savefig(tmp, dpi=200, bbox_inches="tight"); plt.close(fig)
os.replace(tmp, OUT + "IC1_vs_neighbours_CO2_map_2050.png")

# ---------- B: cross-border energy flows ----------
C6 = ["NL", "BE", "DE", "DK", "NO", "UK"]
CARS = [("elec", "Electricity (TWh)", "#e9c46a", .05), ("H2", "Hydrogen (TWh)", "#2a9d8f", .08), ("CH4", "Methane (TWh)", "#e76f51", .025), ("CO2", "CO2 (Mt)", "#6c3483", .12)]
fig, axs = plt.subplots(2, 2, figsize=(11, 10.5))
for ax, (car, t, col, sc) in zip(axs.flat, CARS):
    g.plot(ax=ax, color=g.country.map(lambda c: "#dee2e6" if c in ("NL", "BE") else "#f1f3f5"), edgecolor="white", lw=.8)
    for c in C6: ax.text(cen[c].x, cen[c].y - 6e4, c, ha="center", fontsize=10, fontweight="bold", color="#495057")
    s = xb.get(car, pd.Series(dtype=float)); net = {}
    for (o, d), v in s.items():
        if o in C6 and d in C6 and ("NL" in (o, d) or "BE" in (o, d)):
            k = tuple(sorted((o, d))); net[k] = net.get(k, 0) + (v if (o, d) == k else -v)
    for (a, b), v in net.items():
        if abs(v) >= 1: arrow(ax, a, b, abs(v), col, sc) if v > 0 else arrow(ax, b, a, abs(v), col, sc)
    ex = sum(v for (a, b), v in net.items() if a in ("BE", "NL") and b not in ("BE", "NL")) - sum(v for (a, b), v in net.items() if b in ("BE", "NL") and a not in ("BE", "NL"))
    ax.set_title(t, fontsize=12.5, fontweight="bold"); frame(ax)
    print(car, {k: round(v, 1) for k, v in net.items()})
fig.suptitle("Net cross-border flows of NL and BE with the modelled neighbours, 2050 (mixed resolution)\nNL+BE become a transit hub for gas and a source of CO2 for storage abroad",
             fontsize=13, fontweight="bold")
fig.tight_layout(rect=(0, 0, 1, .95)); fig.savefig(OUT + "MR_crossborder_flows_2050.png", dpi=200); plt.close(fig)

# ---------- C: butterfly ----------
def sup(D, **q):
    s = D["supply"].query("year==2050"); s = s[s.region.str[:2].isin(["NL", "BE"])]
    for k, v in q.items(): s = s[s[k] == v]
    return s.energy.sum() / 1e3
ICn = pickle.load(open(r"run_logs\nb_ccslow_ccu_cap16_dac0_NLBE.pkl", "rb")); MRn = pickle.load(open(r"run_logs\mr_ccslow_ccu_cap16_dac0_NLBE.pkl", "rb"))
off = lambda D: D["supply"].query("year==2050 and category=='wind offshore'").energy.sum() / 1e3
rows = [("Offshore wind (TWh)", off(ICn), off(MRn)),
        ("Electrolysis H2 (TWh)", sup(IC, carrier="hydrogen", category="electrolysis"), sup(MR, carrier="hydrogen", category="electrolysis")),
        ("Heat pumps, building heat (TWh)", sup(IC, carrier="heat", category="electrification (heat pumps)"), sup(MR, carrier="heat", category="electrification (heat pumps)")),
        ("CO2 captured (Mt)", 31.9, float(cap["NL"] + cap["BE"])), ("CO2 stored abroad (Mt)", 0, float(cp.loc[("NL", "UK")] + cp.loc[("BE", "UK")]))]
print("C", [(r[0], round(r[1], 1), round(r[2], 1)) for r in rows])
fig, ax = plt.subplots(figsize=(9, 5.6)); y = np.arange(len(rows))
for i, (lab, a, b) in enumerate(rows):
    m = max(a, b, 1); ax.barh(i, -a / m, .6, color="#adb5bd"); ax.barh(i, b / m, .6, color="#6c3483")
    ax.text(-a / m - .03, i, f"{a:.0f}", ha="right", va="center", fontsize=10); ax.text(b / m + .03, i, f"{b:.0f}", ha="left", va="center", fontsize=10, fontweight="bold")
ax.set_yticks(y, [r[0] for r in rows], fontsize=10.5); ax.invert_yaxis(); ax.axvline(0, color="black", lw=.8)
ax.set_xlim(-1.35, 1.35); ax.set_xticks([]); [ax.spines[s].set_visible(False) for s in ("top", "right", "bottom")]
ax.text(-.6, -.85, "NL+BE alone", ha="center", fontsize=11.5, fontweight="bold", color="#6c757d")
ax.text(.6, -.85, "With neighbours", ha="center", fontsize=11.5, fontweight="bold", color="#6c3483")
fig.suptitle("NL+BE in 2050: alone vs with neighbours", fontsize=13.5, fontweight="bold")
fig.tight_layout(); fig.savefig(OUT + "IC1_vs_neighbours_butterfly_2050.png", dpi=200); print("done")

