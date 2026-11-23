import pickle, geopandas as gpd, numpy as np
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
R = {"IC1": ("nb_ccslow_ccu_cap16_dac0", "NL+BE alone (17 zones)", (2.3, 7.4, 49.4, 54.9)),
     "MR": ("mr_ccslow_ccu_cap16_dac0", "With neighbours (DE, DK, NO, UK)", (-1.5, 10.5, 49.4, 56.8))}
CN = ["NL", "BE"]
g = gpd.read_file(r"geodata\IC1_NWEU.geojson"); off = gpd.read_file(r"geodata\offshore.geojson")
rp = lambda geo: (geo.representative_point().x, geo.representative_point().y)
cen = {r.id: rp(r.geometry) for r in g.itertuples()}; oc = {r.id: rp(r.geometry) for r in off.itertuples()}
CAP, PIPE, STO = "#457b9d", "#c1121f", "#1b4332"
def inside(p, b, m=0): return b[0] + m <= p[0] <= b[1] - m and b[2] + m <= p[1] <= b[3] - m
def clip(po, pd_, b, m=.35):
    t = np.linspace(0, 1, 400); xs = po[0] + (pd_[0] - po[0]) * t; ys = po[1] + (pd_[1] - po[1]) * t
    ok = [inside((x, y), b, m) for x, y in zip(xs, ys)]; i = (ok.index(False) - 1) if False in ok else len(t) - 1
    return (xs[i], ys[i])
fmt = lambda v: f"{v:.1f}" if v < 10 else f"{v:.0f}"
for k, (run, title, B) in R.items():
    F = pickle.load(open(rf"run_logs\{run}.pkl", "rb"))
    fig, ax = plt.subplots(figsize=(7.5, 7.5 * (B[3] - B[2]) / (B[1] - B[0]) / np.cos(np.radians((B[2] + B[3]) / 2)) + .9))
    g.plot(ax=ax, color="#f1f3f5", edgecolor="white", lw=.6)
    g[g.id.str[:2].isin(CN)].plot(ax=ax, color="#dee2e6", edgecolor="white", lw=.6)
    if k == "MR":
        for c_, xy in [("UK", (-1.6, 52.4)), ("DE", (9.3, 51.2))]: ax.text(*xy, c_, fontsize=11, color="#868e96", fontweight="bold", ha="center")
    c = F["co2net"]; c = c[c.year == 2050]
    cap = c[c.role == "captured"].groupby("region").co2.sum() / 1e3
    reuse = c[(c.role == "used / injected") & ~c.tech.str.startswith("CO2-injection")].co2.sum() / 1e3
    outside = []
    for r, v in cap.items():
        p = cen.get(str(r))
        if not p or v < .3: continue
        if not inside(p, B): outside.append(f"{r} captures {fmt(v)}"); continue
        ax.scatter(*p, s=v * (35 if k == "IC1" else 22), color=CAP, alpha=.4, edgecolor=CAP, lw=.8, zorder=3)
    pp = F["co2pipe"]; pp = pp[pp.year == 2050].groupby(["origin", "dest"]).co2.sum() / 1e3
    for (o, d), v in pp.items():
        po, pd_ = cen.get(str(o)), cen.get(str(d))
        if v < .1 or po is None or pd_ is None or po == pd_: continue
        if str(o)[:2] not in CN: outside.append(f"{o} to {d}: {fmt(v)} Mt"); continue
        end = pd_ if inside(pd_, B) else clip(po, pd_, B)
        ax.annotate("", xy=end, xytext=po, zorder=4, arrowprops=dict(arrowstyle="-|>", color=PIPE, alpha=.85, lw=.8 + 5 * min(v, 50) / 50,
                    mutation_scale=11, shrinkA=5, shrinkB=3 if end != pd_ else 5))
        lab = fmt(v) if inside(pd_, B) else f"{fmt(v)} to {d}"
        lp = ((po[0] + end[0]) / 2, (po[1] + end[1]) / 2) if inside(pd_, B) else end
        ax.text(*lp, lab, fontsize=8.5, color=PIPE, ha="center", va="center", fontweight="bold",
                bbox=dict(boxstyle="round,pad=.15", fc="white", ec="none", alpha=.9), zorder=5)
    st0 = F["co2store"]; st0 = st0[st0.year == 2050]; st = st0.groupby("reservoir").co2.sum() / 1e3
    out_st = {}
    for res, v in st.items():
        sid = res.replace("CO2-storage-", ""); p = oc.get(sid)
        if p is None or v < .1: continue
        if not inside(p, B): out_st[sid[2:4]] = out_st.get(sid[2:4], 0) + v; continue
        ax.scatter(*p, s=55, marker="v", color=STO, zorder=5)
        ax.text(p[0] + .18, p[1], fmt(v), fontsize=8.5, color=STO, va="center", fontweight="bold", zorder=6)
    nl_st = st0[st0.region.astype(str).str[:2] == "NL"].co2.sum() / 1e3
    capNB = cap[[i for i in cap.index if str(i)[:2] in CN]].sum()
    if k == "IC1": bal = f"NL+BE 2050: captured {capNB:.0f} Mt = stored in NL {nl_st:.0f} + reused in methanol {reuse:.0f}"
    else:
        ex = pp[[(o, d) for (o, d) in pp.index if str(o)[:2] in CN and str(d)[:2] not in CN]].sum()
        bal = f"NL+BE 2050: captured {capNB:.0f} Mt = stored in NL {nl_st:.0f} + exported to UK {ex:.0f}"
        ns = pp[[(o, d) for (o, d) in pp.index if str(o)[:2] not in CN]]
        bal += "\nNot shown: German CO2 to storage abroad (" + ", ".join(f"{o} to {d} {fmt(v)} Mt" for (o, d), v in ns.items() if v >= .1) + ")"
    ax.set_xlim(B[0], B[1]); ax.set_ylim(B[2], B[3]); ax.set_aspect(1 / np.cos(np.radians((B[2] + B[3]) / 2)))
    ax.set_axis_off(); ax.set_title(title, fontsize=13, fontweight="bold")
    h = [Line2D([], [], marker="o", ls="", ms=10, color=CAP, alpha=.4, mec=CAP), Line2D([], [], color=PIPE, lw=2.5), Line2D([], [], marker="v", ls="", ms=8, color=STO)]
    fig.legend(h, ["CO2 captured (size ~ Mt)", "Pipeline flow (Mt/yr)", "Storage (Mt/yr)"], loc="lower center", ncol=3, frameon=False, fontsize=9.5, bbox_to_anchor=(.5, 0))
    fig.text(.5, .055, bal, ha="center", va="bottom", fontsize=9.5)
    fig.tight_layout(rect=(0, .1, 1, 1)); out = rf"final_runs_pessimistic_ccs\CO2_map_2050_{k}.png"; fig.savefig(out, dpi=200); plt.close(fig)
    print(out, "| capture outside:", outside, "| storage outside:", {a: round(b, 1) for a, b in out_st.items()})



