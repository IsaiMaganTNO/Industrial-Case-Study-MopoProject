import pickle, geopandas as gpd, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
R = {"IC1": ("nb_ccslow_ccu_cap16_dac0", "NL+BE alone (17 zones)"), "MR": ("mr_ccslow_ccu_cap16_dac0", "With neighbours (DE, DK, NO, UK)")}
CN = ["NL", "BE"]
g = gpd.read_file(r"geodata\IC1_NWEU.geojson"); off = gpd.read_file(r"geodata\offshore.geojson")
rp = lambda geo: (geo.representative_point().x, geo.representative_point().y)
cen = {r.id: rp(r.geometry) for r in g.itertuples()}; oc = {r.id: rp(r.geometry) for r in off.itertuples()}
pt = lambda r: cen.get(str(r))
CAP, PIPE, STO = "#457b9d", "#c1121f", "#1b4332"
fig, axes = plt.subplots(1, 2, figsize=(13, 7.5), gridspec_kw={"width_ratios": [1, 1.25]})
for ax, (k, (run, title)) in zip(axes, R.items()):
    F = pickle.load(open(rf"run_logs\{run}.pkl", "rb"))
    pts = []
    g.plot(ax=ax, color="#f1f3f5", edgecolor="white", lw=.6)
    g[g.id.str[:2].isin(CN)].plot(ax=ax, color="#dee2e6", edgecolor="white", lw=.6)
    c = F["co2net"]; c = c[c.year == 2050]
    cap = c[c.role == "captured"].groupby("region").co2.sum() / 1e3
    reuse = c[(c.role == "used / injected") & ~c.tech.str.startswith("CO2-injection")].co2.sum() / 1e3
    for r, v in cap.items():
        p = pt(r)
        if p and v >= .3:
            pts.append(p); ax.scatter(*p, s=v * 30, color=CAP, alpha=.45, edgecolor=CAP, lw=.8, zorder=3)
            if v >= 3: ax.text(p[0], p[1], f"{v:.0f}", ha="center", va="center", fontsize=8, color="#0b2545", fontweight="bold", zorder=6)
    pp = F["co2pipe"]; pp = pp[pp.year == 2050].groupby(["origin", "dest"]).co2.sum() / 1e3
    for (o, d), v in pp.items():
        po, pd_ = pt(o), pt(d)
        if v < .5 or po is None or pd_ is None or po == pd_: continue
        pts += [po, pd_]
        ax.annotate("", xy=pd_, xytext=po, zorder=4, arrowprops=dict(arrowstyle="-|>", color=PIPE, alpha=.8, lw=.6 + 5 * min(v, 50) / 50,
                    mutation_scale=10, shrinkA=6, shrinkB=6, connectionstyle="arc3,rad=.12"))
        if v >= 3:
            ax.text((po[0] + pd_[0]) / 2, (po[1] + pd_[1]) / 2, f"{v:.0f}", fontsize=8, color=PIPE, ha="center", va="center", fontweight="bold",
                    bbox=dict(boxstyle="round,pad=.15", fc="white", ec="none", alpha=.9), zorder=5)
    st0 = F["co2store"]; st0 = st0[st0.year == 2050]
    st = st0.groupby("reservoir").co2.sum() / 1e3
    for res, v in st.items():
        sid = res.replace("CO2-storage-", "")
        if sid in oc and v >= .1:
            pts.append(oc[sid]); ax.scatter(*oc[sid], s=60, marker="v", color=STO, zorder=5)
            ax.text(oc[sid][0] + .25, oc[sid][1], f"{v:.1f}" if v < 10 else f"{v:.0f}", fontsize=8, color=STO, va="center", fontweight="bold", zorder=6)
    nl_st = st0[st0.region.astype(str).str[:2] == "NL"].co2.sum() / 1e3
    capNB = cap[[i for i in cap.index if str(i)[:2] in CN]].sum()
    if k == "IC1":
        bal = f"2050, NL+BE\nCaptured: {capNB:.0f} Mt\n  stored in NL: {nl_st:.0f} Mt\n  reused in methanol: {reuse:.0f} Mt"
    else:
        exp_ = pp[[ (o, d) for (o, d) in pp.index if str(o)[:2] in CN and str(d)[:2] not in CN]].sum()
        bal = f"2050, NL+BE\nCaptured: {capNB:.0f} Mt\n  stored in NL: {nl_st:.0f} Mt\n  exported to UK: {exp_:.0f} Mt\nAll six countries: {cap.sum():.0f} Mt captured"
    xs, ys = zip(*pts); pad = .6
    x0, x1, y0, y1 = min(xs) - pad, max(xs) + pad + .6, min(ys) - pad, max(ys) + pad
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect(1 / np.cos(np.radians((y0 + y1) / 2)))
    ax.text(.5, -.02, bal.replace("\n  ", "  |  ").replace("\n", "  |  ", 1).replace("\n", "\n"), transform=ax.transAxes, fontsize=9.5, va="top", ha="center", bbox=dict(boxstyle="round,pad=.4", fc="white", ec="#adb5bd"), zorder=7)
    ax.set_axis_off(); ax.set_title(title, fontsize=13, fontweight="bold")
h = [Line2D([], [], marker="o", ls="", ms=11, color=CAP, alpha=.45, mec=CAP), Line2D([], [], color=PIPE, lw=2.5),
     Line2D([], [], marker="v", ls="", ms=8, color=STO)]
fig.legend(h, ["CO2 captured (bubble size ~ Mt)", "CO2 pipeline flow (Mt/yr)", "Offshore storage site (Mt/yr)"], loc="lower center", ncol=3, frameon=False, fontsize=10.5)
fig.tight_layout(rect=(0, .07, 1, 1)); out = r"final_runs_pessimistic_ccs\CO2_network_2050_v2.png"; fig.savefig(out, dpi=200); print(out)

