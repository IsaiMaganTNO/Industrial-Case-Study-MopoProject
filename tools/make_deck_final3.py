r"""Condensed outward-facing deck: three final pessimistic-CCS runs.
  IC1 (NL+BE, 17 zones) | Country-level (NL+BE, 1 node/country) | Mixed resolution (NL+BE 17 zones + DE/DK/NO/UK)
All indicators split NL / BE. No internal fix/patch wording.
Usage: python tools/make_deck_final3.py <out.pdf>
"""
import os, sys, pickle, re, textwrap
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
sys.path.insert(0, "tools"); import make_slides_pess as M; import plot_run_summary as S
RUN = {"IC1": "nb_ccslow_ccu_cap16_dac0", "CTRY": "nb_ctry_ccslow_ccu_cap16_dac0", "MR": "mr_ccslow_ccu_cap16_dac0"}
D = {k: pickle.load(open(rf"run_logs\{v}_NLBE.pkl", "rb")) for k, v in RUN.items()}
F = {k: pickle.load(open(rf"run_logs\{v}.pkl", "rb")) for k, v in RUN.items()}
X = {k: pd.read_pickle(rf"run_logs\{v}_xbbio.pkl") for k, v in RUN.items()}
K = ["IC1", "CTRY", "MR"]; YRS = [2030, 2040, 2050]; CN = ["NL", "BE"]
SH = {"IC1": "Baseline", "CTRY": "Lower resolution", "MR": "With neighbours"}
SUB = {"IC1": "NL+BE, 17 zones", "CTRY": "NL+BE, 1 node per country", "MR": "NL+BE 17 zones + DE, DK, NO, UK"}
COL = {"IC1": "#9aa3ad", "CTRY": "#1d3557", "MR": "#e76f51"}
NAVY, ACC, GREY = M.NAVY, M.ACC, M.GREY
M.TMP = r"run_logs\_slide_tmp_final3"; os.makedirs(M.TMP, exist_ok=True); save, style = M.save, M.style
RL = {"((COEL)MeOH)O-MEA": "Methanol-to-olefins (CO2 from electrolysis route)", "(MeOH)O-MEA": "Methanol-to-olefins", "(H2)DRI-EAF": "Hydrogen DRI-EAF",
      "(NG)-CC_gco": "Gas furnace + capture", "CEM2-(BMW)Oxy-MEA": "Biomass oxy-fuel + capture", "LC3-(Afm)Oxy-CaL": "Oxy-fuel + capture (CaL)",
      "LC3-(Afm)Oxy-MEA": "Oxy-fuel + capture", "(NG)NH3-MVR-MEA-DEA": "Gas SMR + capture", "(LN)O-MEA": "Steam cracker + capture",
      "(NG)DRI-EAF-MEA": "Gas DRI-EAF + capture", "(H2)NH3": "Green hydrogen"}
def rlab(t): return RL.get(t, S.route_label(t))
PAL = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd", "#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf", "#393b79", "#ad494a"]

def cc(df):
    r = df.region.astype(str).str[:2]
    off = df.tech.astype(str).str.extract(r"_NS(NL|BE)")[0] if "tech" in df.columns else None
    return r.where(df.region.notna(), off) if off is not None else r
def sel(k, key, y=2050):
    x = D[k][key]; x = x[x.year == y]; return x.assign(cn=cc(x))
def sup(k, q, y=2050):
    s = sel(k, "supply", y); s = s[s.energy > 0]; s = s[q(s)]; return {c: s[s.cn == c].energy.sum() / 1e3 for c in CN}
def fleet(k, pat, y=2050):
    f = sel(k, "fleet", y); f = f[f.tech.str.contains(pat, regex=True)]; return {c: f[f.cn == c].units.sum() for c in CN}
def tot(d): return sum(d.values())

# ---------- generic NL/BE stacked bar: one bar per run, NL dark, BE light
def nlbe_bars(ax, vals, title, fmt="{:.0f}"):
    for j, k in enumerate(K):
        b = 0
        for c, a in [("NL", 1.0), ("BE", .45)]:
            v = vals[k][c]; ax.bar(j, v, .62, bottom=b, color=COL[k], alpha=a, edgecolor="white")
            if v > .06 * max(1e-9, max(tot(vals[x]) for x in K)): ax.text(j, b + v / 2, f"{c}\n{fmt.format(v)}", ha="center", va="center", fontsize=8, color="white" if c == "NL" else "#222")
            b += v
        ax.text(j, b, fmt.format(b), ha="center", va="bottom", fontsize=9.5, fontweight="bold")
    ax.set_xticks(range(3), [SH[k].replace(" ", "\n", 1) for k in K], fontsize=8.5); ax.set_title(title, fontsize=11.5, fontweight="bold"); style(ax)
    ax.set_ylim(0, max(max(tot(vals[k]) for k in K), 1e-9) * 1.18)
def panel(name, items, ncol=3, h=4.4):
    n = len(items); nr = int(np.ceil(n / ncol)); fig, axes = plt.subplots(nr, ncol, figsize=(4.7 * ncol, h * nr))
    for ax, (t, fn, *fmt) in zip(np.atleast_1d(axes).flat, items): nlbe_bars(ax, {k: fn(k) for k in K}, t, *(fmt or []))
    for ax in list(np.atleast_1d(axes).flat)[n:]: ax.axis("off")
    fig.tight_layout(); return save(fig, name)

# ---------- figures
def f_energy():
    return panel("energy", [
        ("Offshore wind (TWh)", lambda k: sup(k, lambda s: s.category == "wind offshore")),
        ("Nuclear (TWh)", lambda k: sup(k, lambda s: s.tech.str.startswith("nuclear"))),
        ("Solar + onshore wind (TWh)", lambda k: sup(k, lambda s: s.category.isin(["solar PV", "wind onshore"]))),
        ("Hydrogen from electrolysis (TWh)", lambda k: sup(k, lambda s: (s.carrier == "hydrogen") & (s.category == "electrolysis"))),
        ("Hydrogen imported as LH2 (TWh)", lambda k: sup(k, lambda s: s.tech == "LH2-terminal")),
        ("Hydrogen turbines (TWh el.)", lambda k: sup(k, lambda s: s.tech.str.startswith("CCGT-H2")))])
def f_gas():
    return panel("gas", [
        ("Fossil gas landed as LNG (TWh)", lambda k: sup(k, lambda s: s.tech == "LNG-terminal")),
        ("Biomethane (TWh)", lambda k: sup(k, lambda s: (s.carrier == "methane") & s.tech.str.startswith("bio"))),
        ("Synthetic methane (TWh)", lambda k: sup(k, lambda s: s.tech.str.startswith("methanation")))], h=4.6)
def gas_use(k):
    s = sel(k, "supply"); s = s[(s.carrier == "methane") & (s.energy > 0)]; x = X[k]["xb"].query("year==2050 and car=='CH4'")
    sup_ = s.energy.sum() / 1e3; im = x[~x.o.isin(CN) & x.d.isin(CN)].v.sum() / 1e3; ex = x[x.o.isin(CN) & ~x.d.isin(CN)].v.sum() / 1e3
    return sup_, im, ex, sup_ + im - ex
def f_gasbal():
    fig, ax = plt.subplots(figsize=(12, 5)); w = .2
    parts = [("Gas supplied in NL+BE (LNG + biomethane)", 0, "#6c757d"), ("Pipeline import", 1, "#adb5bd"), ("Pipeline export", 2, "#e9c46a"), ("Gas used in NL+BE", 3, "#d62828")]
    for j, k in enumerate(K):
        v = gas_use(k)
        for i, (l, idx, c) in enumerate(parts):
            ax.bar(j + (i - 1.5) * w, v[idx], w, color=c, label=l if j == 0 else None); ax.text(j + (i - 1.5) * w, v[idx] + 5, f"{v[idx]:.0f}", ha="center", fontsize=9)
    ax.set_xticks(range(3), [f"{SH[k]}\n({SUB[k]})" for k in K], fontsize=9.5); ax.set_ylabel("TWh in 2050"); ax.legend(frameon=False, ncol=2); style(ax)
    return save(fig, "gasbal")
HEAT = [("Ground heat pump", r"^ground-heatpump"), ("Air heat pump", r"^air-heatpump(?!-cool)"), ("Electric resistance", r"^electric-heating"),
        ("Gas boiler", r"^gas-boiler"), ("Biomass boiler", r"^bio-boiler"), ("Oil/coal boiler", r"^(oil|coal)-boiler")]
HCOL = ["#1d3557", "#457b9d", "#a8dadc", "#6c757d", "#6a994e", "#3d3d3d"]
def f_heat():
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    for ax, c in zip(axes, CN):
        for j, k in enumerate(K):
            s = sel(k, "supply"); s = s[(s.carrier == "heat") & (s.energy > 0) & (s.cn == c)]; b = 0
            for i, (l, p) in enumerate(HEAT):
                v = s[s.tech.str.contains(p, regex=True)].energy.sum() / 1e3  # noqa
                ax.bar(j, v, .6, bottom=b, color=HCOL[i], label=l if j == 0 and c == "NL" else None, edgecolor="white")
                if v > 4: ax.text(j, b + v / 2, f"{v:.0f}", ha="center", va="center", color="white", fontsize=9)
                b += v
        ax.set_xticks(range(3), [SH[k] for k in K]); ax.set_title(c, fontsize=13, fontweight="bold"); style(ax)
    axes[0].set_ylabel("Building heat supply 2050 (TWh)"); fig.legend(loc="lower center", ncol=6, frameon=False, bbox_to_anchor=(.5, -.05))
    fig.tight_layout(); return save(fig, "heat")
def f_routes(secs, name):
    fig, axes = plt.subplots(1, len(secs), figsize=(5 * len(secs), 5.2))
    labs = sorted({rlab(t) for k in K for t in D[k]["prod"].query("sector in @secs").tech})
    col = {l: PAL[i % len(PAL)] for i, l in enumerate(labs)}
    for ax, sec in zip(axes, secs):
        cols = []; used = set()
        for k in K:
            p = sel(k, "prod"); p = p[p.sector == sec].assign(r=lambda z: z.tech.map(rlab))
            for c in CN: cols.append((f"{SH[k].split()[0]}\n{c}", p[p.cn == c].groupby("r").output.sum() / 1e3))
        xs = [0, 1, 2.6, 3.6, 5.2, 6.2]
        for xi, (lab, ser) in zip(xs, cols):
            b = 0
            for r, v in ser.items():
                if v < .01: continue
                ax.bar(xi, v, .85, bottom=b, color=col[r], edgecolor="white"); used.add(r)
                if v > .25: ax.text(xi, b + v / 2, f"{v:.1f}", ha="center", va="center", fontsize=8, color="white")
                b += v
        ax.set_xticks(xs, [c[0] for c in cols], fontsize=8.5); ax.set_title(sec.capitalize(), fontsize=12, fontweight="bold"); style(ax)
        ax.legend([plt.Rectangle((0, 0), 1, 1, color=col[r]) for r in sorted(used)], sorted(used), frameon=False, fontsize=8.5, loc="upper center", bbox_to_anchor=(.5, -.12), ncol=1)
    axes[0].set_ylabel("Production 2050 (Mt)"); fig.tight_layout(); return save(fig, name)
def f_co2sector():
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharex=True)
    srcs = sorted({s for k in K for s in D[k]["co2net"].query("role=='captured' and year==2050").source})
    for ax, k in zip(axes, K):
        c = sel(k, "co2net"); c = c[c.role == "captured"]
        p = c.pivot_table(index="source", columns="cn", values="co2", aggfunc="sum").reindex(index=srcs, columns=CN).fillna(0) / 1e3
        y = np.arange(len(p)); left = np.zeros(len(p))
        for cn, a in [("NL", 1.0), ("BE", .45)]: ax.barh(y, p[cn], left=left, color=COL[k], alpha=a, label=cn, edgecolor="white"); left += p[cn].values
        for i, v in enumerate(left):
            if v > .05: ax.text(v + .3, i, f"{v:.1f}", va="center", fontsize=9)
        ax.set_yticks(y, [s.replace("refinery (SMR+CC, internal H2)", "refinery hydrogen (SMR)").replace("chemicals / e-fuels", "chemicals (olefins, methanol)") for s in p.index] if k == "IC1" else [""] * len(y))
        ax.set_title(f"{SH[k]} - {left.sum():.0f} Mt", fontsize=12, fontweight="bold"); ax.grid(axis="x", color="#e3e7ec")
        for s_ in ["top", "right"]: ax.spines[s_].set_visible(False)
        ax.legend(frameon=False, loc="lower right"); ax.set_xlabel("Mt CO2 captured, 2050")
    fig.tight_layout(); return save(fig, "co2sector")
def co2dest(k):
    st = D[k]["co2store"].query("year==2050").co2.sum() / 1e3
    c = D[k]["co2net"].query("year==2050 and role=='used / injected'"); u = c[~c.tech.str.startswith("CO2-injection")].co2.sum() / 1e3
    p = F[k]["co2pipe"]; p = p[p.year == 2050]; nb = lambda s: s.str[:2].isin(CN)
    ex = (p[nb(p.origin) & ~nb(p.dest)].co2.sum() - p[~nb(p.origin) & nb(p.dest)].co2.sum()) / 1e3 if len(p) else 0
    em = D[k]["emis"].query("year==2050").co2.sum() / 1e3
    return st, u, ex, em
def f_co2dest():
    fig, ax = plt.subplots(figsize=(12, 5.2))
    for j, k in enumerate(K):
        st, u, ex, em = co2dest(k); b = 0
        for v, l, c in [(st, "Stored under the North Sea (NL)", "#2a9d8f"), (u, "Used in methanol for plastics", ACC), (ex, "Exported for storage abroad", "#457b9d")]:
            ax.bar(j - .17, v, .32, bottom=b, color=c, label=l if j == 0 else None)
            if v > .8: ax.text(j - .17, b + v / 2, f"{v:.1f}", ha="center", va="center", color="white", fontsize=10, fontweight="bold")
            b += v
        ax.bar(j + .17, em, .32, color="#6c757d", label="Net emissions of NL+BE" if j == 0 else None); ax.text(j + .17, em + .8, f"{em:.1f}", ha="center", fontsize=10)
    ax.set_xticks(range(3), [f"{SH[k]}\n({SUB[k]})" for k in K], fontsize=9.5); ax.set_ylabel("Mt CO2 in 2050"); ax.legend(frameon=False, loc="upper left"); style(ax)
    return save(fig, "co2dest")
RF = [("Electrolysers", r"^PEM"), ("Methanol synthesis", r"^\(H2\)MeOH"), ("Methanation", r"^methanation"), ("Biogas upgrading", r"^bio-diges"), ("Green ammonia", r"^\(H2\)NH3")]
def f_renew():
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    for ax, c in zip(axes, CN):
        for j, k in enumerate(K):
            b = 0
            for i, (l, p) in enumerate(RF):
                v = fleet(k, p)[c]; ax.bar(j, v, .6, bottom=b, color=PAL[i], label=l if j == 0 and c == "NL" else None, edgecolor="white")
                if v > .7: ax.text(j, b + v / 2, f"{v:.1f}", ha="center", va="center", color="white", fontsize=9)
                b += v
            ax.text(j, b + .3, f"{b:.1f}", ha="center", fontsize=10, fontweight="bold")
        ax.set_xticks(range(3), [SH[k] for k in K]); ax.set_title(c, fontsize=13, fontweight="bold"); style(ax)
    axes[0].set_ylabel("Installed capacity 2050 (GW)"); fig.legend(loc="lower center", ncol=5, frameon=False, bbox_to_anchor=(.5, -.05)); fig.tight_layout(); return save(fig, "renew")
def f_bio():
    def bio(k):
        b = X[k]["bio"].query("year==2050"); return {c: b[b.c == c].v.sum() / 1e3 for c in CN}
    def biouse(k, pat):
        b = X[k]["bio"].query("year==2050"); b = b[b.unit.str.contains(pat, regex=True)]; return {c: b[b.c == c].v.sum() / 1e3 for c in CN}
    return panel("bio", [("Biomass used, total (TWh)", bio), ("...of which for biogas (TWh)", lambda k: biouse(k, r"^bio-diges")),
                         ("...of which for heat (TWh)", lambda k: biouse(k, r"boiler")), ("...of which for power (TWh)", lambda k: biouse(k, r"^bioST|^bio-CHP|^bioCCGT"))], ncol=4)
def f_trade():
    cars = [("elec", "Electricity (TWh)"), ("CH4", "Methane (TWh)"), ("H2", "Hydrogen (TWh)"), ("CO2", "CO2 (Mt)")]
    fig, axes = plt.subplots(1, 4, figsize=(16, 5))
    for ax, (car, t) in zip(axes, cars):
        for j, k in enumerate(K):
            x = X[k]["xb"].query("year==2050 and car==@car")
            im = x[~x.o.isin(CN) & x.d.isin(CN)].v.sum() / 1e3; ex = x[x.o.isin(CN) & ~x.d.isin(CN)].v.sum() / 1e3
            ax.bar(j - .17, im, .32, color="#457b9d", label="Import" if j == 0 else None); ax.bar(j + .17, -ex, .32, color=ACC, label="Export" if j == 0 else None)
            ax.text(j, max(im, 0) + 3, f"net {im - ex:+.0f}", ha="center", fontsize=9, fontweight="bold")
        ax.axhline(0, color="#555", lw=.8); ax.set_xticks(range(3), [SH[k].replace(" ", "\n", 1) for k in K], fontsize=8.5); ax.set_title(t, fontsize=12, fontweight="bold"); style(ax)
    axes[0].legend(frameon=False); fig.tight_layout(); return save(fig, "trade")
def f_co2map():
    import geopandas as gpd
    g = gpd.read_file(r"geodata\IC1_NWEU.geojson"); off = gpd.read_file(r"geodata\offshore.geojson")
    cen = {r.id: (r.geometry.representative_point().x, r.geometry.representative_point().y) for r in g.itertuples()}
    oc = {r.id: (r.geometry.representative_point().x, r.geometry.representative_point().y) for r in off.itertuples()}
    gc = g.assign(c=g.id.str[:2]).dissolve("c")
    ccen = {c: (geo.representative_point().x, geo.representative_point().y) for c, geo in gc.geometry.items()}
    def pt(r):
        if r in cen: return cen[r]
        if r[:2] in ("NL", "BE") and r[:2] in ccen: return ccen[r[:2]]
        return ccen.get(r[:2])
    fig, axes = plt.subplots(1, 3, figsize=(18, 7.2))
    for ax, k in zip(axes, K):
        g.plot(ax=ax, color="#eef1f4", edgecolor="#c5ccd3", lw=.4)
        g[g.id.str[:2].isin(CN)].plot(ax=ax, color="#dde6ef", edgecolor="#9aa3ad", lw=.5)
        c = F[k]["co2net"]; c = c[(c.year == 2050) & (c.role == "captured")].groupby("region").co2.sum() / 1e3
        if k == "CTRY":  # one node per country: show capture at country centroid
            c = c.groupby(c.index.astype(str).str[:2]).sum()
        for r, v in c.items():
            p = pt(str(r))
            if p and v > .1: ax.scatter(*p, s=v * 45, color="#6c757d", alpha=.55, edgecolor="white", zorder=3)
        pp = F[k]["co2pipe"]; pp = pp[pp.year == 2050].groupby(["origin", "dest"]).co2.sum() / 1e3
        for (o, d), v in pp.items():
            po, pd_ = pt(o), pt(d)
            if v < .2 or po is None or pd_ is None or po == pd_: continue
            ax.annotate("", xy=pd_, xytext=po, arrowprops=dict(arrowstyle="-|>", color="#d62828", lw=.8 + 6 * min(v, 50) / 50, alpha=.85, mutation_scale=13, shrinkA=4, shrinkB=4), zorder=4)
            ax.text((po[0] + pd_[0]) / 2, (po[1] + pd_[1]) / 2, f"{v:.0f}" if v >= 1 else f"{v:.1f}", fontsize=7.5, ha="center", va="center",
                    bbox=dict(boxstyle="round,pad=.12", fc="white", ec="none", alpha=.85), zorder=5)
        for r, v in c.items():
            p = pt(str(r))
            if p and v >= .5: ax.text(p[0], p[1], f"{v:.1f}", fontsize=7, ha="center", va="center", color="#222", zorder=6)
        u = F[k]["co2net"]; u = u[(u.year == 2050) & (u.role == "used / injected") & ~u.tech.str.startswith("CO2-injection")]
        u = u.groupby(u.region.astype(str).str[:2] if k == "CTRY" else "region").co2.sum() / 1e3
        for r, v in u.items():
            p = pt(str(r))
            if p and v > .1:
                ax.scatter(p[0] + .25, p[1] - .2, s=v * 45, marker="D", color=ACC, alpha=.75, edgecolor="white", zorder=3)
                ax.text(p[0] + .25, p[1] - .2, f"{v:.1f}", fontsize=7, ha="center", va="center", color="white", fontweight="bold", zorder=6)
        st0 = F[k]["co2store"]; st0 = st0[st0.year == 2050]
        st = st0.groupby("reservoir").co2.sum() / 1e3
        for res, v in st.items():
            sid = res.replace("CO2-storage-", "")
            if sid not in oc or v < .1: continue
            ax.scatter(*oc[sid], s=v * 45, marker="s", color="#2a9d8f", alpha=.8, edgecolor="white", zorder=3)
            ax.text(oc[sid][0], oc[sid][1] - .55, f"{v:.1f}", fontsize=7.5, ha="center", color="#2a9d8f", fontweight="bold")
        for (res, reg), v in (st0.groupby(["reservoir", "region"]).co2.sum() / 1e3).items():
            sid = res.replace("CO2-storage-", ""); src = pt(str(reg))
            if sid in oc and src and v >= .1: ax.plot([src[0], oc[sid][0]], [src[1], oc[sid][1]], color="#2a9d8f", lw=1, ls=":", zorder=2)
        cap_t = c.sum(); st_t = st.sum(); u_t = u.sum()
        if k == "MR":
            bal = f"Captured {cap_t:.1f} Mt (NL+BE {c[[i for i in c.index if str(i)[:2] in CN]].sum():.1f})\nStored {st_t:.1f} Mt (NL {st0[st0.region.astype(str).str[:2]=='NL'].co2.sum()/1e3:.1f}, abroad {st_t - st0[st0.region.astype(str).str[:2]=='NL'].co2.sum()/1e3:.1f})"
        else:
            bal = f"Captured {cap_t:.1f} Mt\n= stored {st_t:.1f} + reused in methanol {u_t:.1f}"
        ax.text(.02, .02, bal, transform=ax.transAxes, fontsize=9, va="bottom", bbox=dict(boxstyle="round", fc="white", ec="#9aa3ad"), zorder=7)
        if k == "MR": ax.set_xlim(-8, 16); ax.set_ylim(49, 63)
        else: ax.set_xlim(1.5, 8); ax.set_ylim(49.4, 55.3)
        ax.set_axis_off(); ax.set_title(f"{SH[k]}\n({SUB[k]})", fontsize=12, fontweight="bold")
    h = [plt.scatter([], [], s=200, color="#6c757d", alpha=.55), plt.scatter([], [], s=200, marker="s", color="#2a9d8f"),
         plt.Line2D([], [], color="#d62828", lw=3), plt.scatter([], [], s=150, marker="D", color=ACC)]
    fig.legend(h, ["CO2 captured (Mt)", "CO2 stored per site (Mt)", "CO2 pipeline flow (Mt)", "CO2 reused in methanol (Mt)"], loc="lower center", ncol=4, frameon=False, fontsize=11)
    fig.tight_layout(rect=(0, .06, 1, 1)); return save(fig, "co2map")
def f_emis():
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=True)
    for ax, k in zip(axes, K):
        e = F[k]["emis"]; e = e.assign(c=e.region.astype(str).str[:2]); p = e.groupby(["year", "c"]).co2.sum().unstack().reindex(YRS).fillna(0) / 1e3
        cs = [c for c in ["NL", "BE", "DE", "DK", "NO", "UK"] if c in p.columns]
        colors = {"NL": COL[k], "BE": COL[k], "DE": "#6c757d", "DK": "#adb5bd", "NO": "#2a9d8f", "UK": "#457b9d"}
        alpha = {"NL": 1, "BE": .45}
        xs = np.arange(3); w = .8 / len(cs)
        for i, c in enumerate(cs):
            ax.bar(xs + (i - (len(cs) - 1) / 2) * w, p[c], w, color=colors[c], alpha=alpha.get(c, .9), label=c, edgecolor="white")
        ax.plot(xs, p[cs].sum(axis=1), "k-o", lw=2, label="Total")
        for xi, v in zip(xs, p[cs].sum(axis=1)): ax.text(xi, v + 6, f"{v:.0f}", ha="center", fontsize=9, fontweight="bold")
        ax.axhline(0, color="#555", lw=.8); ax.set_xticks(xs, YRS); ax.set_title(f"{SH[k]}", fontsize=12, fontweight="bold"); style(ax); ax.legend(frameon=False, fontsize=8.5, ncol=2)
    axes[0].set_ylabel("Net CO2 emissions (Mt/yr)"); fig.tight_layout(); return save(fig, "emis")
ELC = [("Offshore wind", lambda s: s.category == "wind offshore", "#1f5f8b"), ("Onshore wind", lambda s: s.category == "wind onshore", "#5fa8d3"),
       ("Solar PV", lambda s: s.category == "solar PV", "#f2b134"), ("Nuclear", lambda s: s.tech.str.startswith("nuclear"), "#7b3294"),
       ("Gas power", lambda s: s.tech.str.match(r"^(CCGT|OCGT)(?!-H2)"), "#8c8c8c"), ("Hydrogen turbines", lambda s: s.tech.str.startswith("CCGT-H2"), "#2a9d8f"),
       ("Biomass power", lambda s: s.tech.str.startswith("bio"), "#6a994e")]
def f_elecmix():
    fig, axes = plt.subplots(1, 2, figsize=(15, 5.2), sharey=True)
    for ax, c in zip(axes, CN):
        xs = []; lab = []
        for j, k in enumerate(K):
            for i, y in enumerate(YRS):
                x = j * 3.6 + i; xs.append(x); lab.append(str(y)[2:])
                s = sel(k, "supply", y); s = s[(s.carrier == "electricity") & (s.energy > 0) & (s.cn == c)]; b = 0
                for n, q, col in ELC:
                    v = s[q(s)].energy.sum() / 1e3; ax.bar(x, v, .85, bottom=b, color=col, label=n if (j, i, c) == (0, 0, "NL") else None, edgecolor="white", lw=.4); b += v
        ax.set_xticks(xs, lab, fontsize=8.5); ax.set_title(c, fontsize=13, fontweight="bold"); style(ax); ax.set_ylim(bottom=0)
    axes[0].set_ylabel("Electricity generation (TWh)"); fig.legend(loc="lower center", ncol=7, frameon=False, bbox_to_anchor=(.5, -.07))
    for ax in axes:
        for j, k in enumerate(K): ax.annotate(SH[k], (j * 3.6 + 1, 0), xytext=(0, -26), textcoords="offset points", ha="center", fontsize=9.5, fontweight="bold", annotation_clip=False)
    fig.tight_layout(); return save(fig, "elecmix")
DCAT = [("Fossil, no capture", "#6c757d"), ("Fossil + carbon capture", "#457b9d"), ("Electricity", "#f4a261"), ("Hydrogen", "#2a9d8f"),
        ("Methanol from captured CO2", "#e76f51"), ("Biomass / scrap / other low-carbon", "#6a994e")]
def dcat(r):
    f = r.fuel
    if f in ("natural gas", "coal", "alt. fuel mix", "generic: EU average mix", "generic: reference route"): return DCAT[1][0] if r.cc else DCAT[0][0]
    if f == "electricity": return DCAT[2][0]
    if f == "hydrogen": return DCAT[3][0]
    if f == "methanol": return DCAT[4][0]
    return DCAT[5][0]
SECS = ["steel (primary)", "steel (secondary)", "olefins", "ammonia", "cement", "glass (container)", "glass (float)", "glass (fibre)", "chlorine", "aluminium", "paper", "pulp"]
def f_decarb():
    fig, axes = plt.subplots(1, 3, figsize=(18, 6.4), sharey=True)
    for ax, k in zip(axes, K):
        p = D[k]["prod"]; p = p.assign(cat=p.apply(dcat, axis=1))
        y = 0; ticks = []
        for sec in SECS:
            for yr in YRS:
                q = p[(p.sector == sec) & (p.year == yr)]; t = q.output.sum()
                if t <= 0: continue
                sh = q.groupby("cat").output.sum() / t * 100; left = 0
                for l, c in DCAT:
                    v = sh.get(l, 0); ax.barh(y, v, .85, left=left, color=c, edgecolor="white", lw=.3); left += v
                ticks.append((y, f"{sec}  {yr}" if yr == 2030 else str(yr))); y -= 1
            y -= .6
        ax.set_yticks([t[0] for t in ticks], [t[1] for t in ticks], fontsize=7); ax.set_xlim(0, 100); ax.set_xlabel("% of production (NL+BE)")
        ax.set_title(f"{SH[k]}\n({SUB[k]})", fontsize=12, fontweight="bold")
        for s_ in ["top", "right"]: ax.spines[s_].set_visible(False)
    fig.legend([plt.Rectangle((0, 0), 1, 1, color=c) for _, c in DCAT], [l for l, _ in DCAT], loc="lower center", ncol=6, frameon=False, fontsize=10)
    fig.tight_layout(rect=(0, .05, 1, 1)); return save(fig, "decarb")
def f_cost():
    def c(k):
        o = F[k]["obj"]; return o.sum() / 1e6
    fig, ax = plt.subplots(figsize=(7, 5)); v = [c(k) for k in ["IC1", "CTRY"]]
    ax.bar([0, 1], v, .55, color=[COL["IC1"], COL["CTRY"]])
    for i, x in enumerate(v): ax.text(i, x * 1.01, f"{x:.2f}", ha="center", fontsize=12, fontweight="bold")
    ax.set_xticks([0, 1], ["Baseline\n(17 zones)", "Lower resolution\n(1 node per country)"]); ax.set_ylabel("Total system cost 2030-2050 (model units)"); style(ax)
    ax.set_ylim(0, max(v) * 1.15); return save(fig, "cost")

# ---------- deck
def main(out):
    M.FOOT[0] = "MOPO Industrial Case Study - SpineOpt - NL+BE decarbonisation with limited CO2 storage"
    v = {k: {} for k in K}
    for k in K:
        st, u, ex, em = co2dest(k); v[k].update(st=st, u=u, ex=ex, em=em, cap=D[k]["co2net"].query("year==2050 and role=='captured'").co2.sum() / 1e3,
            ely=tot(sup(k, lambda s: (s.carrier == "hydrogen") & (s.category == "electrolysis"))), ow=tot(sup(k, lambda s: s.category == "wind offshore")),
            nuc=tot(fleet(k, r"^nuclear")), hp=tot(sup(k, lambda s: (s.carrier == "heat") & (s.category == "electrification (heat pumps)"))),
            bioh=tot(sup(k, lambda s: (s.carrier == "heat") & s.tech.str.startswith("bio"))), gasuse=gas_use(k)[3])
    dC = 100 * (F["CTRY"]["obj"].sum() / F["IC1"]["obj"].sum() - 1)
    with PdfPages(out) as pdf:
        M.title_slide(pdf, "Decarbonising Dutch and Belgian industry\nwith limited CO2 storage",
                      "SpineOpt investment model, 2030 / 2040 / 2050  -  how much do spatial detail and neighbouring countries matter?",
                      "Baseline: NL+BE in 17 zones   |   Lower resolution: 1 node per country   |   With neighbours: + DE, DK, NO, UK")
        M.text_slide(pdf, "Three model set-ups", [
            ("What differs", ["!Baseline: NL and BE split into 17 zones with limited transport between zones",
                              "!Lower resolution: same data, NL and BE each one node (no internal bottlenecks)",
                              "!With neighbours: baseline + Germany, Denmark, Norway and the UK, linked by electricity, gas, hydrogen and CO2 networks; one shared climate target"]),
            ("What is the same", ["Net-zero CO2 in 2050 (NL+BE, or all six countries together)", "Limited CO2 storage: 2.5 / 10.5 / 16 Mt per year in NL (2030/40/50), none in BE",
                                  "High CO2 transport and injection costs", "No direct air capture", "Same technologies, costs, demands and weather (3 representative days per year)"])],
            section="Introduction")
        M.text_slide(pdf, "Key messages", [("", [
            f"!Spatial detail matters moderately: one node per country lowers total cost by {abs(dC):.0f}% and needs less electrolysis ({v['IC1']['ely']:.0f} -> {v['CTRY']['ely']:.0f} TWh) and nuclear ({v['IC1']['nuc']:.0f} -> {v['CTRY']['nuc']:.0f} GW), because bottlenecks between zones disappear",
            "!Neighbours matter much more: with a shared target, NL+BE keep more gas-based industry with carbon capture and export CO2 for storage abroad",
            f"With neighbours, NL+BE export {v['MR']['ex']:.0f} Mt CO2/yr and emit {v['MR']['em']:.0f} Mt net in 2050; this is offset by negative emissions in other countries",
            f"Alone, NL+BE must reuse captured CO2 in methanol for plastics ({v['IC1']['u']:.0f} Mt) because storage is limited",
            f"Buildings: heat pumps when alone ({v['IC1']['hp']:.0f} TWh); imported biomass boilers with neighbours ({v['MR']['bioh']:.0f} TWh)",
            "Industry routes for cement, ammonia and glass hardly depend on resolution; steel and plastics do"])], section="Summary")
        M.plot_slide(pdf, "CO2 emissions over time", f_emis(), ["NL+BE alone: net zero in 2050 in both resolutions", "With neighbours: one shared target for six countries",
                     "NL and BE stay positive in 2050; Norway, the UK and Denmark become net negative (biomass with capture and storage)"],
                     section="Summary", imgw=.7, cap="Net CO2 emissions per country (Mt/yr). Dark = NL, light = BE.")
        SEC = "Energy"
        M.plot_slide(pdf, "Electricity and hydrogen", f_energy(), [f"Offshore wind {v['IC1']['ow']:.0f} / {v['CTRY']['ow']:.0f} / {v['MR']['ow']:.0f} TWh", "Nearly all offshore wind and electrolysis are in NL",
                     "Nuclear: spread over NL and BE in the baseline, only BE at lower resolution", "With neighbours: far less electrolysis; LH2 imports the same in all set-ups"],
                     section=SEC, imgw=.68, cap="2050. Dark = NL, light = BE. Bars: Baseline, Lower resolution, With neighbours.")
        M.plot_slide(pdf, "Electricity generation over time", f_elecmix(), ["Offshore wind grows to the main source in NL", "BE relies on nuclear, offshore wind and imports",
                     "With neighbours: less offshore wind in NL, more imports", "Hydrogen turbines provide back-up"], section=SEC, imgw=.7, cap="Electricity generation per country, 2030 / 2040 / 2050 (TWh).")
        M.plot_slide(pdf, "Gas supply: fossil vs renewable", f_gas(), ["All fossil gas arrives as LNG (no domestic production by 2050)", "Biomethane only when NL+BE are alone", "No synthetic methane in any set-up",
                     "With neighbours, much more LNG is landed - most flows on to the neighbouring countries"], section=SEC, imgw=.68, cap="Methane supplied in NL and BE in 2050 (TWh). Dark = NL, light = BE.")
        M.plot_slide(pdf, "Gas: landed vs used", f_gasbal(), [f"Gas used in NL+BE: {v['IC1']['gasuse']:.0f} / {v['CTRY']['gasuse']:.0f} / {v['MR']['gasuse']:.0f} TWh",
                     "Large transit flows: NL and BE are gas gateways for their neighbours", "Landed gas is not the same as gas used"], section=SEC, imgw=.66,
                     cap="2050. Gas used = supplied + pipeline imports - pipeline exports.")
        M.plot_slide(pdf, "Building heat", f_heat(), ["Heat pumps here are building heat pumps only (air and ground source)", "Industrial electric furnaces are part of the industry routes, not of building heat",
                     "Alone: heat pumps only (ground-source in the baseline, more air-source at lower resolution)", "With neighbours: biomass boilers (imported biomass)"], section=SEC, imgw=.66, cap="Building space heating and hot water, 2050 (TWh).")
        M.plot_slide(pdf, "Biomass use per country", f_bio(), ["Alone: biomass goes to biogas", "With neighbours: biomass for building heat (NL and BE) and for power (BE)"], section=SEC, imgw=.7,
                     cap="Primary biomass used in NL and BE in 2050 (TWh). Dark = NL, light = BE.")
        M.plot_slide(pdf, "Trade with neighbouring countries", f_trade(), ["Gross imports and exports are large", "Alone (NL+BE only): imports and exports balance for every carrier",
                     "With neighbours: NL+BE become net exporters of CO2, gas, electricity and hydrogen"], section=SEC, imgw=.7,
                     cap="2050. Imports positive, exports negative. Flows between NL and BE are not included.")
        SEC = "Industry and CO2"
        M.wide_slide(pdf, "How each industrial sector decarbonises", f_decarb(), section=SEC,
                     cap="Share of production per sector by route type, 2030 / 2040 / 2050, NL+BE together. Production volumes are the same in all years; only the technology changes.")
        M.plot_slide(pdf, "Steel, plastics and glass by country", f_routes(["steel (primary)", "olefins", "glass (container)"], "routes1"),
                     ["Steel: electrolysis when NL+BE are alone (BE adds hydrogen and gas + capture in the baseline); gas + capture in both countries with neighbours", "Plastics (olefins): naphtha + capture, or methanol from captured CO2",
                      "Glass: electric and hydrogen furnaces"], section=SEC, imgw=.7, cap="Production per route in 2050 (Mt). Columns: NL and BE for each set-up.")
        M.plot_slide(pdf, "Cement and ammonia by country", f_routes(["cement", "ammonia"], "routes2"), ["Cement: oxy-fuel with carbon capture in every set-up", "Ammonia: green hydrogen when alone; gas + capture with neighbours"],
                     section=SEC, imgw=.62, cap="Production per route in 2050 (Mt).")
        M.text_slide(pdf, "CO2 captured per sector: what is behind it", [
            ("NL+BE alone (2050)", ["Baseline 32 Mt / lower resolution 27 Mt captured",
                "Refinery hydrogen (gas reforming with capture, NL): 15 Mt in both - the largest source",
                "Steam crackers for plastics with capture: 6-9 Mt",
                "Biogas upgrading with capture (NL, baseline only): 6.5 Mt - negative emissions",
                "Cement oxy-fuel with capture: 2.5 Mt (mostly BE)",
                "Steel gas DRI with capture (BE, baseline only): 1 Mt",
                "Most other sectors switch to electricity or hydrogen and have nothing to capture"]),
            ("With neighbours (2050, NL+BE)", ["51 Mt captured - storage abroad makes capture cheaper than switching fuel",
                "Refinery hydrogen: 14 Mt",
                "Steam crackers: 11 Mt; gas-based plastics with capture: 7 Mt",
                "Steel gas DRI with capture: 7 Mt (NL 4.1, BE 3.1)",
                "Ammonia from gas with capture: 6 Mt (NL 4.5, BE 1.8)",
                "Cement oxy-fuel with capture (incl. biomass): 4.5 Mt",
                "Glass: below 0.3 Mt in all set-ups"])], section=SEC)
        M.plot_slide(pdf, "CO2 captured per sector", f_co2sector(), ["Refinery hydrogen (SMR with capture, NL) is the largest single source", "With neighbours, much more CO2 is captured: gas-based industry with capture stays",
                     "BE captures mostly in cement and chemicals"], section=SEC, imgw=.7, cap="CO2 captured in 2050 (Mt). Dark = NL, light = BE.")
        fig = M.frame("CO2 network in 2050", "Where CO2 is captured, how it moves and where it is stored", SEC); M.img(fig, f_co2map(), [.02, .14, .96, .72])
        M.caption(fig, "Grey circles: CO2 captured per zone. Red arrows: CO2 pipeline flows (Mt/yr). Green squares: CO2 stored per storage site. Orange diamonds: CO2 reused in methanol. Box: 2050 balance. Lower resolution has no pipelines inside a country.")
        pdf.savefig(fig); plt.close(fig)
        M.plot_slide(pdf, "Where captured CO2 goes", f_co2dest(), ["NL storage is full in all set-ups (16 Mt)", "Alone: the rest is reused in methanol for plastics",
                     "With neighbours: the rest is shipped to storage in the UK", "Net NL+BE emissions only above zero when neighbours compensate"], section=SEC, imgw=.64,
                     cap="2050. CO2 in plastics is assumed to stay bound in the product.")
        M.plot_slide(pdf, "Renewable fuel investments", f_renew(), ["Electrolysers and methanol synthesis are all in NL", "Largest in the baseline: zone bottlenecks push CO2 reuse near the source",
                     "Small with neighbours: hydrogen and CO2 storage available abroad"], section=SEC, imgw=.66, cap="Installed capacity in 2050 (GW).")
        M.plot_slide(pdf, "Cost of resolution", f_cost(), [f"One node per country is {abs(dC):.1f}% cheaper", "Mainly less investment in electrolysers, methanol plants, nuclear and heat pumps",
                     "With neighbours the cost covers six countries and is not comparable"], section="Summary", imgw=.5, cap="Total discounted system cost, NL+BE only set-ups.")
        M.text_slide(pdf, "Conclusions", [
            ("Lower spatial resolution", ["Same overall pathway", f"{abs(dC):.0f}% cheaper; smaller hydrogen and methanol chain", "Hides zone bottlenecks for CO2 and hydrogen", "Good for screening, not for siting"]),
            ("Including neighbours", ["Changes the pathway itself", "CO2 export replaces domestic CO2 reuse", "More gas-based industry with capture", "Biomass heat instead of heat pumps",
                                      "Results for NL+BE alone depend strongly on the system boundary"])], section="Conclusions")
        M.text_slide(pdf, "Limitations", [("", ["Three representative days per year; seasonal storage is simplified", "CO2 storage limits are assumptions, not measured capacities",
            "CO2 in plastics is counted as permanently bound", "Neighbouring countries are modelled as one node each", "Costs are model units, useful for comparisons only"])], section="Conclusions")
    print("wrote", out, M.page[0], "pages")
if __name__ == "__main__": main(sys.argv[1])





