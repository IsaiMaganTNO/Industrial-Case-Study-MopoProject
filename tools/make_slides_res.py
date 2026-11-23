r"""Resolution deck (final pessimistic-CCS runs: CCU leak closed, DAC off, NL storage 16 Mt/yr).
IC1 (17 zones) vs Country-level (1 node/country).  Usage: python tools/make_slides_res.py <out.pdf>
Inputs: run_logs/<run>{,_NLBE}.pkl, plots in runs/3day_nb_ctry_ccslow_ccu_cap16_dac0/plots/cmp_vs_ic1
"""
import os, sys, pickle
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
sys.path.insert(0, "tools"); import make_slides_pess as M
RUN = {"IC1": "nb_ccslow_ccu_cap16_dac0", "CTRY": "nb_ctry_ccslow_ccu_cap16_dac0"}
OLD = {"IC1": "nb_ccslow", "CTRY": "nb_ctry_ccslow"}
M.D = {k: pickle.load(open(rf"run_logs\{v}_NLBE.pkl", "rb")) for k, v in RUN.items()}
M.FULL = {k: pickle.load(open(rf"run_logs\{v}.pkl", "rb")) for k, v in RUN.items()}
OF = {k: pickle.load(open(rf"run_logs\{v}.pkl", "rb"))["obj"].sum() for k, v in OLD.items()}
M.LAB.update({"IC1": "IC1\n(NL+BE, 17 zones)", "CTRY": "Country-level\n(NL+BE, 1 node/country)"})
M.TMP = r"run_logs\_slide_tmp_res"; os.makedirs(M.TMP, exist_ok=True)
CMP = r"runs\3day_nb_ctry_ccslow_ccu_cap16_dac0\plots\cmp_vs_ic1"
D, K, COL, LAB, style, save = M.D, ["IC1", "CTRY"], M.COL, M.LAB, M.style, M.save
sup, fl, obj = M.sup, M.fl, M.obj
YRS = [2030, 2040, 2050]
SH = {"IC1": "IC1", "CTRY": "Country"}
M.PAL6 = ["#1d3557", "#e76f51", "#2a9d8f", "#e9c46a", "#8338ec", "#6c757d", "#d62828", "#90be6d"]
def flt(k, pat, y=2050):
    f = D[k]["fleet"]; f = f[f.year == y]; return f[f.tech.str.contains(pat, regex=True)].units.sum()
def cap(k, y=2050): return D[k]["co2net"].query("year==@y and role=='captured'").co2.sum() / 1e3
def used(k, y=2050):
    c = D[k]["co2net"].query("year==@y and role=='used / injected'"); return c[~c.tech.str.startswith("CO2-injection")].co2.sum() / 1e3
def prod(k, sector, pat, y=2050):
    p = D[k]["prod"]; p = p[(p.year == y) & (p.sector == sector)]; return p[p.tech.str.contains(pat, regex=True)].output.sum() / 1e3
def share(k, sector, pat, y=2050):
    p = D[k]["prod"]; p = p[(p.year == y) & (p.sector == sector)]; return 100 * p[p.tech.str.contains(pat, regex=True)].output.sum() / max(p.output.sum(), 1e-9)

def fig_obj():
    a, b = M.FULL["IC1"]["obj"] / 1e3, M.FULL["CTRY"]["obj"] / 1e3; d = (b - a)
    d = d[d.abs() > .05].sort_values()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5), gridspec_kw={"width_ratios": [1, 1.6]})
    v = [obj("IC1") / 1e6, obj("CTRY") / 1e6]; ax1.bar([0, 1], v, color=[COL[k] for k in K], width=.6)
    for i, x in enumerate(v): ax1.text(i, x + .03, f"{x:.3f} M", ha="center", fontsize=12, fontweight="bold")
    ax1.set_xticks([0, 1], [LAB[k] for k in K]); ax1.set_ylim(0, max(v) * 1.15); ax1.set_title("Total objective (whole model)"); style(ax1)
    ax2.barh(range(len(d)), d.values, color=[M.ACC if x < 0 else "#2a9d8f" for x in d.values])
    for i, x in enumerate(d.values): ax2.text(x + (2 if x >= 0 else -2), i, f"{x:+.1f} k", va="center", ha="left" if x >= 0 else "right", fontsize=10)
    ax2.set_yticks(range(len(d)), [s.replace("_", " ") for s in d.index]); ax2.axvline(0, color="#555", lw=.8)
    ax2.set_title("Country-level minus IC1, by cost component (k)"); ax2.grid(axis="x", color="#e3e7ec")
    for s in ["top", "right"]: ax2.spines[s].set_visible(False)
    lo = min(d.min(), 0); ax2.set_xlim(lo * 1.35, max(d.max(), 0) * 1.35 + 10)
    fig.tight_layout(); return save(fig, "obj")

def fig_zone(pat, title, name, unit="GW"):
    fig, ax = plt.subplots(figsize=(13, 4.8)); regs = sorted(set(D["IC1"]["fleet"].region.dropna()) | set(D["CTRY"]["fleet"].region.dropna()))
    regs = [r for r in regs if str(r)[:2] in ("NL", "BE")]; xx = np.arange(len(regs)); w = .4
    for j, k in enumerate(K):
        f = D[k]["fleet"].query("year==2050"); f = f[f.tech.str.contains(pat, regex=True)].groupby("region").units.sum()
        ax.bar(xx + (j - .5) * w, [f.get(r, 0) for r in regs], w, color=COL[k], label=LAB[k].replace("\n", " "))
    ax.set_xticks(xx, regs, fontsize=9.5); ax.set_ylabel(f"{title}, 2050 ({unit})"); ax.legend(frameon=False); style(ax)
    return save(fig, name)

def fig_co2zone():
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    regs = ["NLC1", "NLC2", "NLC5", "NLC6", "NLC7", "NLC9", "BEC1", "BEC4", "BEC6", "BEC7"]; xx = np.arange(len(regs))
    for ax, k in zip(axes, K):
        c = D[k]["co2net"].query("year==2050"); c = c.assign(kind=np.where(c.role == "captured", "Captured",
                np.where(c.tech.str.startswith("CO2-injection"), "Injected to storage", "Used (methanol/olefins)")))
        p = c.pivot_table(index="region", columns="kind", values="co2", aggfunc="sum").reindex(regs).fillna(0) / 1e3
        for i, (kind, col) in enumerate([("Captured", "#5c6770"), ("Injected to storage", "#2a9d8f"), ("Used (methanol/olefins)", M.ACC)]):
            ax.bar(xx + (i - 1) * .27, p.get(kind, 0 * xx), .27, color=col, label=kind)
        ax.set_xticks(xx, regs, fontsize=9.5); ax.set_title(LAB[k].replace("\n", " ")); style(ax)
    axes[0].set_ylabel("Mt CO2, 2050"); axes[0].legend(frameon=False); fig.tight_layout(); return save(fig, "co2zone")

def fig_time():
    R = [("Electrolytic H2 (TWh)", lambda k, y: sup(k, "hydrogen", "electrolysis", y)),
         ("Offshore wind (TWh)", lambda k, y: sup(k, "electricity", "wind offshore", y)),
         ("Nuclear (GW)", lambda k, y: flt(k, r"^nuclear", y)),
         ("CO2 captured (Mt)", lambda k, y: cap(k, y)),
         ("CO2 used in methanol (Mt)", lambda k, y: used(k, y)),
         ("Steel via MOE (%)", lambda k, y: share(k, "steel (primary)", r"^MOE", y))]
    fig, axes = plt.subplots(2, 3, figsize=(14, 6.5))
    for ax, (t, f) in zip(axes.flat, R):
        for k in K: ax.plot(YRS, [f(k, y) for y in YRS], "-o", color=COL[k], lw=2.5, label=LAB[k].replace("\n", " "))
        ax.set_title(t, fontsize=11.5); ax.set_xticks(YRS); style(ax); ax.set_ylim(bottom=0)
    axes[0, 0].legend(frameon=False, fontsize=9); fig.tight_layout(); return save(fig, "time")

def fig_routes():
    R = [("Steel: molten-oxide\nelectrolysis", "steel (primary)", r"^MOE"), ("Steel: H2-DRI", "steel (primary)", r"^\(H2\)DRI"),
         ("Steel: gas DRI\n+ CCS", "steel (primary)", r"DRI-EAF-MEA"), ("Olefins: naphtha\n+ CCS", "olefins", r"^\(LN\)O-MEA"),
         ("Olefins: via\nmethanol", "olefins", r"MeOH\)O"), ("Glass: H2 share", "glass (container)", r"^\(H2\)")]
    fig, ax = plt.subplots(figsize=(13, 5)); xx = np.arange(len(R)); w = .38
    for j, k in enumerate(K):
        v = [share(k, s, p) for _, s, p in R]; ax.bar(xx + (j - .5) * w, v, w, color=COL[k], label=LAB[k].replace("\n", " "))
        for i, x in enumerate(v): ax.text(i + (j - .5) * w, x + 1.5, f"{x:.0f}%", ha="center", fontsize=9.5)
    ax.set_xticks(xx, [r for r, _, _ in R], fontsize=10); ax.set_ylabel("Share of sector output, NL+BE 2050 (%)"); ax.set_ylim(0, 115)
    ax.legend(frameon=False, loc="upper right"); style(ax); return save(fig, "routes")

def fig_cap():
    Mx = [("PEM", r"^PEM"), ("Methanol\nsynthesis", r"^\(H2\)MeOH"), ("Nuclear", r"^nuclear"), ("H2 turbines", r"^CCGT-H2"),
          ("Ground HP", r"^ground-heatpump"), ("Air HP", r"^air-heatpump"), ("Batteries", r"^battery"), ("Biogas\nupgrading", r"^bio-diges")]
    fig, ax = plt.subplots(figsize=(13, 5)); xx = np.arange(len(Mx)); w = .38
    for j, k in enumerate(K):
        v = [flt(k, p) for _, p in Mx]; ax.bar(xx + (j - .5) * w, v, w, color=COL[k], label=LAB[k].replace("\n", " "))
        for i, x in enumerate(v): ax.text(i + (j - .5) * w, x + .4, f"{x:.1f}", ha="center", fontsize=9)
    ax.set_xticks(xx, [m for m, _ in Mx]); ax.set_ylabel("Capacity in NL+BE, 2050 (GW)"); ax.legend(frameon=False); style(ax)
    return save(fig, "cap")

def fig_co2split():
    fig, ax = plt.subplots(figsize=(11, 5)); parts = [("Stored (NL, cap 16)", M.stored, "#2a9d8f"), ("Used in methanol -> olefins", used, M.ACC), ("Exported", M.co2exp, "#9aa3ad")]
    for j, k in enumerate(K):
        b = 0
        for lbl, f, col in parts:
            v = f(k); ax.bar(j, v, .55, bottom=b, color=col, label=lbl if j == 0 else None)
            if v > .3: ax.text(j, b + v / 2, f"{v:.1f}", ha="center", va="center", color="white", fontsize=11, fontweight="bold")
            b += v
        ax.text(j, b + .4, f"captured {cap(k):.1f}", ha="center", fontsize=10.5)
    ax.set_xticks([0, 1], [LAB[k] for k in K]); ax.set_ylabel("Mt CO2, NL+BE 2050"); ax.legend(frameon=False, loc="upper right"); style(ax)
    return save(fig, "co2split")

X = {k: pd.read_pickle(rf"run_logs\{v}_xbbio.pkl") for k, v in RUN.items()}
def cc(df):
    r = df.region.astype(str).str[:2]; off = df.tech.astype(str).str.extract(r"_NS(NL|BE)")[0]
    return r.where(df.region.notna(), off)
CN = ["NL", "BE"]; CA = {"NL": 1.0, "BE": .5}

def fig_trade():
    cars = [("elec", "Electricity"), ("CH4", "Methane"), ("H2", "Hydrogen"), ("CO2", "CO2 (Mt)")]
    fig, axes = plt.subplots(1, 4, figsize=(15, 5))
    for ax, (car, t) in zip(axes, cars):
        for j, k in enumerate(K):
            x = X[k]["xb"].query("year==2050 and car==@car"); sc = 1e3
            nb = x.o.isin(CN) & x.d.isin(CN); ex = x[x.o.isin(CN) & ~x.d.isin(CN)].v.sum() / sc
            im = x[~x.o.isin(CN) & x.d.isin(CN)].v.sum() / sc; nlbe = x[nb & (x.o == "NL")].v.sum() / sc; benl = x[nb & (x.o == "BE")].v.sum() / sc
            xs = j * 4 + np.arange(3)
            ax.bar(xs[0], im, color="#457b9d"); ax.bar(xs[1], -ex, color=M.ACC); ax.bar(xs[2], nlbe + benl, color="#9aa3ad")
            for xi, v in zip(xs, [im, -ex, nlbe + benl]): ax.text(xi, v + (2 if v >= 0 else -2), f"{abs(v):.0f}", ha="center", va="bottom" if v >= 0 else "top", fontsize=8.5)
            ax.text(xs[1], ax.get_ylim()[1] if False else max(im, nlbe + benl) * 1.25 + 5, f"{'IC1' if k=='IC1' else 'Country'}\nnet {im-ex:+.0f}", ha="center", fontsize=9, fontweight="bold")
        ax.axhline(0, color="#555", lw=.8); ax.set_xticks([]); ax.set_title(t + (" (TWh)" if car != "CO2" else ""), fontsize=12); style(ax)
    h = [plt.Rectangle((0, 0), 1, 1, color=c) for c in ["#457b9d", M.ACC, "#9aa3ad"]]
    fig.legend(h, ["Import from neighbours", "Export to neighbours", "NL<->BE exchange (both directions)"], loc="lower center", ncol=3, frameon=False, bbox_to_anchor=(.5, -.04))
    fig.tight_layout(); return save(fig, "trade")

def fig_co2sector():
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    for ax, k in zip(axes, K):
        c = D[k]["co2net"].query("year==2050 and role=='captured'"); c = c.assign(cn=cc(c))
        p = c.pivot_table(index="source", columns="cn", values="co2", aggfunc="sum").reindex(columns=CN).fillna(0) / 1e3
        p = p.loc[p.sum(axis=1).sort_values().index]; y = np.arange(len(p)); left = np.zeros(len(p))
        for cn, col in [("NL", M.NAVY), ("BE", "#e9c46a")]:
            ax.barh(y, p[cn], left=left, color=col, label=cn); left += p[cn].values
        for i, v in enumerate(left): ax.text(v + .2, i, f"{v:.1f}", va="center", fontsize=10)
        ax.set_yticks(y, p.index); ax.set_title(LAB[k].replace("\n", " ") + f" - total {left.sum():.1f} Mt"); ax.grid(axis="x", color="#e3e7ec")
        for s in ["top", "right"]: ax.spines[s].set_visible(False)
    axes[0].legend(frameon=False); axes[0].set_xlabel("Mt CO2 captured, 2050"); axes[1].set_xlabel("Mt CO2 captured, 2050")
    fig.tight_layout(); return save(fig, "co2sector")

RF = [("Electrolysers (PEM)", r"^PEM"), ("Methanol synthesis", r"^\(H2\)MeOH"), ("Methanation", r"^methanation"),
      ("Biogas upgrading", r"^bio-diges"), ("Green ammonia (H2)", r"^\(H2\)NH3"), ("Bio-ammonia", r"^\(BM\)NH3")]
def fig_renewfuel():
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    for ax, k in zip(axes, K):
        f = D[k]["fleet"]; f = f.assign(cn=cc(f)); xs = np.arange(3); w = .38
        for j, cn in enumerate(CN):
            bot = np.zeros(3)
            for i, (l, p) in enumerate(RF):
                v = np.array([f[(f.year == y) & (f.cn == cn) & f.tech.str.contains(p, regex=True)].units.sum() for y in YRS])
                ax.bar(xs + (j - .5) * w, v, w, bottom=bot, color=M.PAL6[i], label=l if j == 0 else None, edgecolor="white", lw=.5); bot += v
            for xi, b in zip(xs, bot): ax.text(xi + (j - .5) * w, b + .3, f"{cn}\n{b:.1f}", ha="center", fontsize=8)
        ax.set_xticks(xs, YRS); ax.set_title(LAB[k].replace("\n", " ")); style(ax)
    axes[0].set_ylabel("Installed capacity (GW)"); axes[1].legend(frameon=False, loc="upper left", fontsize=9)
    fig.tight_layout(); return save(fig, "renewfuel")

def fig_bio():
    fig, ax = plt.subplots(figsize=(11, 5)); xs = np.arange(3); w = .2
    for j, (k, cn) in enumerate([(k, cn) for k in K for cn in CN]):
        b = X[k]["bio"]; v = [b[(b.year == y) & (b.c == cn)].v.sum() / 1e3 for y in YRS]
        ax.bar(xs + (j - 1.5) * w, v, w, color=COL[k], alpha=CA[cn], label=f"{SH[k]} - {cn}", edgecolor="white")
        for xi, x in zip(xs, v): ax.text(xi + (j - 1.5) * w, x + .5, f"{x:.0f}", ha="center", fontsize=8.5)
    ax.set_xticks(xs, YRS); ax.set_ylabel("Biomass used (TWh)"); ax.legend(frameon=False, ncol=2); style(ax); return save(fig, "bio")

def fig_country_kpi():
    R = [("Offshore wind\n(TWh)", lambda d: d["supply"].query("carrier=='electricity' and category=='wind offshore'")),
         ("Electrolytic H2\n(TWh)", lambda d: d["supply"].query("carrier=='hydrogen' and category=='electrolysis'")),
         ("Nuclear\n(TWh)", lambda d: d["supply"][d["supply"].tech.str.startswith("nuclear")]),
         ("Heat pumps\n(TWh heat)", lambda d: d["supply"].query("carrier=='heat' and category=='electrification (heat pumps)'")),
         ("LNG imports\n(TWh)", lambda d: d["supply"].query("tech=='LNG-terminal'")),
         ("Biomethane\n(TWh)", lambda d: d["supply"][(d["supply"].carrier == "methane") & d["supply"].tech.str.startswith("bio")])]
    fig, axes = plt.subplots(1, len(R), figsize=(15, 4.8))
    for ax, (t, fn) in zip(axes, R):
        for j, k in enumerate(K):
            s = fn(D[k]); s = s[(s.year == 2050) & (s.energy > 0)]; s = s.assign(cn=cc(s)); bot = 0
            for cn in CN:
                v = s[s.cn == cn].energy.sum() / 1e3; ax.bar(j, v, .6, bottom=bot, color=COL[k], alpha=CA[cn], edgecolor="white")
                if v > 2: ax.text(j, bot + v / 2, f"{cn}\n{v:.0f}", ha="center", va="center", fontsize=8, color="white" if cn == "NL" else "#222")
                bot += v
        ax.set_title(t, fontsize=11, fontweight="bold"); ax.set_xticks([0, 1], ["IC1", "Country"]); style(ax)
    fig.tight_layout(); return save(fig, "ctrykpi")

def fig_steel_ctry():
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)
    for ax, sec in zip(axes, ["steel (primary)", "olefins", "glass (container)"]):
        rows = {}
        for k in K:
            p = D[k]["prod"].query("year==2050 and sector==@sec"); p = p.assign(cn=cc(p), r=p.tech.map(M.S.route_label))
            for cn in CN: rows[f"{SH[k]}\n{cn}"] = p[p.cn == cn].groupby("r").output.sum() / 1e3
        t = pd.DataFrame(rows).fillna(0).T; bot = np.zeros(len(t))
        for i, r in enumerate(t.columns):
            ax.bar(range(len(t)), t[r], .65, bottom=bot, color=M.PAL6[i % len(M.PAL6)], label=r, edgecolor="white")
            for xi, (v, b) in enumerate(zip(t[r], bot)):
                if v > .3: ax.text(xi, b + v / 2, f"{v:.1f}", ha="center", va="center", fontsize=8.5, color="white")
            bot += t[r].values
        ax.set_xticks(range(len(t)), t.index, fontsize=9.5); ax.set_title(sec.capitalize()); ax.legend(frameon=False, fontsize=8.5, loc="upper right"); style(ax)
    axes[0].set_ylabel("Production 2050 (Mt)"); fig.tight_layout(); return save(fig, "steelctry")

def fig_heat():
    fig, ax = plt.subplots(figsize=(12, 5)); techs = [("Ground heat pump", r"^ground-heatpump"), ("Air heat pump", r"^air-heatpump(?!-cool)"),
        ("Electric resistance heating", r"^electric-heating"), ("Gas boiler", r"^gas-boiler"), ("Bio boiler", r"^bio-boiler"), ("Oil/coal boiler", r"^(oil|coal)-boiler")]
    xs = np.arange(3); w = .38
    for j, k in enumerate(K):
        s = D[k]["supply"].query("carrier=='heat' and energy>0"); bot = np.zeros(3)
        for i, (l, p) in enumerate(techs):
            v = np.array([s[(s.year == y) & s.tech.str.contains(p, regex=True)].energy.sum() / 1e3 for y in YRS])
            ax.bar(xs + (j - .5) * w, v, w, bottom=bot, color=M.PAL6[i], label=l if j == 0 else None, edgecolor="white"); bot += v
        for xi in xs: ax.text(xi + (j - .5) * w, bot[xi] + 2, SH[k], ha="center", fontsize=8.5)
    ax.set_xticks(xs, YRS); ax.set_ylabel("Building heat supply (TWh)"); ax.legend(frameon=False, ncol=3, fontsize=9); style(ax); return save(fig, "heat")

def table(pdf):
    def r(l, f, fmt="{:.0f}"):
        a, b = f("IC1"), f("CTRY"); d = b - a; p = f"{100*d/a:+.0f}%" if abs(a) > 1e-6 else "-"
        return [l, fmt.format(a), fmt.format(b), fmt.format(d) if fmt != "{}" else "", p]
    rows = [r("Total system cost (M, whole model)", lambda k: obj(k) / 1e6, "{:.3f}"),
            r("Offshore wind (TWh)", lambda k: sup(k, "electricity", "wind offshore")),
            r("Nuclear generation (TWh)", lambda k: D[k]["supply"].query("year==2050 and tech.str.startswith('nuclear')", engine="python").energy.sum() / 1e3),
            r("Electrolytic H2 (TWh)", lambda k: sup(k, "hydrogen", "electrolysis")),
            r("PEM capacity (GW)", lambda k: flt(k, r"^PEM"), "{:.1f}"),
            r("Methanol synthesis (GW)", lambda k: flt(k, r"^\(H2\)MeOH"), "{:.1f}"),
            r("Nuclear capacity (GW)", lambda k: flt(k, r"^nuclear"), "{:.1f}"),
            r("Heat pumps (TWh heat)", lambda k: sup(k, "heat", "electrification (heat pumps)")),
            r("LNG imports (TWh)", lambda k: D[k]["supply"].query("year==2050 and tech=='LNG-terminal'").energy.sum() / 1e3),
            r("CO2 captured (Mt)", cap, "{:.1f}"), r("CO2 stored (Mt, cap 16)", M.stored, "{:.1f}"),
            r("CO2 used in methanol (Mt)", used, "{:.1f}")]
    fig = M.frame("Key numbers: NL+BE in 2050", "Identical data, scenario and pessimistic CCS - only the spatial resolution differs", "Comparison")
    ax = fig.add_axes([.04, .06, .92, .78]); ax.axis("off")
    t = ax.table(cellText=rows, colLabels=["Indicator (NL+BE, 2050)", "IC1 (17 zones)", "Country-level", "Difference", "%"],
                 loc="upper center", cellLoc="center", colWidths=[.4, .15, .15, .15, .1])
    t.auto_set_font_size(False); t.set_fontsize(12); t.scale(1, 1.75)
    for (rr, c), cell in t.get_celld().items():
        cell.set_edgecolor("#dde3ea")
        if rr == 0: cell.set_facecolor(M.NAVY); cell.get_text().set_color("white"); cell.get_text().set_fontweight("bold")
        elif rr % 2: cell.set_facecolor("#f6f8fb")
        if c == 0 and rr > 0: cell._loc = "left"
    pdf.savefig(fig); plt.close(fig)

def main(out):
    M.FOOT[0] = "Industrial Case Study (MOPO) - SpineOpt - pessimistic CCS, CCU leak closed, no DAC, NL storage 16 Mt/yr - IC1 vs Country-level"
    dO = 100 * (obj("CTRY") / obj("IC1") - 1); dOld = 100 * (OF["CTRY"] / OF["IC1"] - 1)
    ic, ct = "IC1", "CTRY"; S1, S2, S3 = "Results side by side", "Why: mechanisms", "Industry and CO2"
    with PdfPages(out) as pdf:
        M.title_slide(pdf, "How much does spatial resolution\nmatter? NL+BE, pessimistic CCS",
                      "SpineOpt investment runs 2030 / 2040 / 2050  -  3 representative days per year  -  Gurobi, both OPTIMAL, zero penalties",
                      "IC1: NL+BE in 17 zones     vs     Country-level: NL+BE as one node per country")
        M.text_slide(pdf, "Set-up of the two runs", [
            ("Identical in both", ["Same technology data, demand, weather and 3 representative days",
                                   "Pessimistic CCS: CO2 pipeline tariffs x6, injection tariffs x1.2-4.7",
                                   "!NL storage 2.5 / 10.5 / 16 Mt/yr (2030/40/50); BE none",
                                   "!Direct air capture disabled; CO2 used in methanation is counted when the methane is burned",
                                   "NL+BE CO2 cap 165 / 37 / 0 Mt"]),
            ("Only difference: spatial resolution", ["IC1: 9 NL + 8 BE zones, each with own power, gas, H2, CO2, heat and biomass nodes",
                                                     "Transport between zones limited by line and pipeline capacities",
                                                     "Country-level: zones merged into one node per country and carrier, no transport limits inside a country",
                                                     "Links to the sea (offshore wind, storage sites) unchanged"])],
            section="Introduction", sub="A controlled experiment: one dimension changed")
        M.text_slide(pdf, "Main messages", [("", [
            f"!Total cost is {abs(dO):.1f}% lower at country level ({obj(ic)/1e6:.3f} -> {obj(ct)/1e6:.3f} M), almost all in investment",
            f"!Same overall pathway: net zero in 2050, the 16 Mt storage cap is binding, both runs still capture about 28-32 Mt CO2, and steel, ammonia, cement and glass mostly follow the same routes",
            f"!Main mechanism: CO2 transport costs between zones. In IC1 the refinery zone NLC2 pays the (x6) pipeline tariff to move CO2 towards storage, so it turns its captured CO2 into methanol on site instead (PEM {flt(ic,'^PEM'):.0f} vs {flt(ct,'^PEM'):.0f} GW, methanol {flt(ic,r'^[(]H2[)]MeOH'):.1f} vs {flt(ct,r'^[(]H2[)]MeOH'):.1f} GW)",
            f"Electrolysis {sup(ic,'hydrogen','electrolysis'):.0f} vs {sup(ct,'hydrogen','electrolysis'):.0f} TWh; offshore wind barely changes ({sup(ic,'electricity','wind offshore'):.0f} vs {sup(ct,'electricity','wind offshore'):.0f} TWh)",
            f"Nuclear {flt(ic,'^nuclear'):.0f} vs {flt(ct,'^nuclear'):.0f} GW: the zonal run spreads nuclear over many zones",
            "Steel: IC1 keeps H2-DRI and gas DRI+CCS next to MOE; country level goes 100% molten-oxide electrolysis",
            f"Robust: the cost gap had the same sign in the earlier runs ({dOld:.1f}%); fixing the CO2 leak made the resolution effect larger, not smaller"])],
            section="Summary")
        table(pdf)
        M.plot_slide(pdf, "System cost", fig_obj(), [f"Total {dO:+.1f}%",
                     f"Unit investment {(M.FULL[ct]['obj']['unit_investment_costs']-M.FULL[ic]['obj']['unit_investment_costs'])/1e3:+.0f} k: less PEM, methanol, nuclear, heat pumps",
                     "Fixed O&M and taxes nearly equal", "Network costs small in both"], section=S1, imgw=.66,
                     cap="Objective function components (whole model, NL+BE plus offshore). Country minus IC1.")
        M.plot_slide(pdf, "Electricity generation", rf"{CMP}\C01_electricity_mix.png",
                     [f"Offshore wind 2050: {sup(ic,'electricity','wind offshore'):.0f} vs {sup(ct,'electricity','wind offshore'):.0f} TWh",
                      "Nuclear output about half at country level", "H2 turbines in both (~13 TWh) as flexible backup"],
                     section=S1, cap="NL+BE electricity generation by technology; left IC1, right Country-level.")
        M.plot_slide(pdf, "Capacity in NL+BE, 2050", fig_cap(),
                     ["Largest gaps: PEM, methanol synthesis, nuclear, ground heat pumps", "Country level uses air heat pumps (cheaper, no siting limits)",
                      "Biogas: with capture in IC1, without at country level"], section=S1, imgw=.66, cap="Installed capacity in NL+BE in 2050 (GW).")
        M.plot_slide(pdf, "Capacity shifts over time", rf"{CMP}\C02_capacity_delta.png", ["Differences appear from 2040 onwards", "2030 nearly identical"],
                     section=S1, cap="Left: installed capacity 2050. Right: Country-level minus IC1 per milestone year.")
        M.plot_slide(pdf, "NL and BE separately, 2050", fig_country_kpi(),
                     ["Dark = NL, light = BE", "Offshore wind and electrolysis are almost all NL", "Nuclear: IC1 splits over NL and BE, country level puts it all in BE",
                      "Biomethane: NL in IC1, split NL/BE at country level"], section=S1, imgw=.7, cap="Selected 2050 totals split by country.")
        M.plot_slide(pdf, "Building heat: what is in 'heat pumps'", fig_heat(),
                     ["'Heat pumps' = air- and ground-source heat pumps only", "Electric resistance heating is a separate, small category (<2 TWh)",
                      "Industrial e-furnaces are NOT in heat: they are industry routes (e.g. electric glass furnace)", "Gas boilers gone by 2050 in both runs"],
                     section=S1, imgw=.64, cap="Building space heat and hot water supply by technology (NL+BE). Cooling not shown.")
        M.plot_slide(pdf, "Hydrogen supply", rf"{CMP}\C06_hydrogen_supply.png",
                     [f"Electrolysis 2050: {sup(ic,'hydrogen','electrolysis'):.0f} vs {sup(ct,'hydrogen','electrolysis'):.0f} TWh",
                      f"2040: {sup(ic,'hydrogen','electrolysis',2040):.0f} vs {sup(ct,'hydrogen','electrolysis',2040):.0f} TWh",
                      "LH2 imports equal (42.5 TWh)", "!No stand-alone SMR+CCS (SMR+CC) built in either run", "Refinery SMR+CC (REF-SMR-MEA) makes H2 inside the refinery for fuels; it is not in this chart but captures ~15 Mt CO2"], section=S1, cap="Hydrogen supply to the H2 network in NL+BE by source. Refinery-internal H2 is not shown.")
        M.plot_slide(pdf, "Gas supply", rf"{CMP}\C05_gas_supply_transit.png",
                     ["LNG imports equal (~46 TWh)", "Biogas 26 TWh in both; IC1 adds capture (BECCS 6.5 Mt)", "No synthetic methane in either run"],
                     section=S1, cap="Methane supply to NL+BE and transit.")
        M.plot_slide(pdf, "Trajectories 2030-2050", fig_time(),
                     ["Paths split in 2040", "Country level builds less electrolysis and more MOE steel in 2040", "Captured CO2 converges by 2050"],
                     section=S1, imgw=.68, cap="NL+BE indicators per milestone year.")
        M.plot_slide(pdf, "Mechanism: moving CO2 between zones costs money", fig_co2zone(),
                     ["!IC1: NLC2 captures 12.9 Mt and uses all of it on site in methanol", "Pipelines NLC2-NLC1/3/5 exist and each zone hop pays the pessimistic (x6) flow tariff (capacity use not yet checked)",
                      "!Country level: no transport cost inside a country, so storage is reached for free", "Methanol then only fills the gap above the storage cap"],
                     section=S2, imgw=.64, cap="Captured, injected and used CO2 per zone in 2050. Country-level results are reported back to zone level only for units, not for flows.")
        M.plot_slide(pdf, "Where electrolysers are built", fig_zone(r"^PEM", "PEM capacity", "zpem"),
                     ["IC1: PEM sits in the refinery zones NLC1/NLC2 to feed methanol", "Country level: capacity spread evenly (no locational value)"],
                     section=S2, imgw=.64, cap="PEM capacity per zone, 2050 (GW). At country level the zone split is not meaningful.")
        M.plot_slide(pdf, "Where nuclear is built", fig_zone(r"^nuclear", "Nuclear capacity", "znuc"),
                     ["IC1: 11 GW spread over many BE and NL zones (likely local supply behind grid limits - not yet checked)", "Country level: 6 GW, all in one place"],
                     section=S2, imgw=.64, cap="New nuclear capacity per zone, 2050 (GW).")
        M.wide_slide(pdf, "Industrial routes", rf"{CMP}\C03_industry_routes.png",
                     "Route shares per sector. Each panel: left three bars IC1 (2030/40/50), right three bars Country-level.", section=S3)
        M.plot_slide(pdf, "Industry: the routes that change", fig_routes(),
                     ["Steel: IC1 mixes MOE, H2-DRI and gas DRI+CCS; country level 100% MOE",
                      f"Olefins via methanol: {share(ic,'olefins','MeOH[)]O'):.0f}% vs {share(ct,'olefins','MeOH[)]O'):.0f}%",
                      "Ammonia (H2), cement (CaL CCS), chlorine, paper: identical"], section=S3, imgw=.66, cap="Share of sector output in NL+BE in 2050.")
        M.plot_slide(pdf, "Industry routes by country, 2050", fig_steel_ctry(),
                     ["Steel: IC1 adds H2-DRI and gas DRI+CCS next to MOE; country level all MOE",
                      "Olefins: methanol is made in NL (NLC1/NLC2) but the methanol-to-olefins plant in IC1 sits mainly in BE (4.0 of 4.6 Mt)", "Glass: same mix in both"], section=S3, imgw=.68, cap="Production per route, split NL / BE, 2050 (Mt).")
        M.plot_slide(pdf, "CO2 captured per sector", fig_co2sector(),
                     ["Refinery SMR+CC is the largest source in both", "IC1 adds BECCS (biogas with capture, NL)", "Steel capture only in IC1 (gas DRI+CCS)"],
                     section=S3, imgw=.68, cap="CO2 captured in 2050 by sector, split NL / BE (Mt).")
        M.plot_slide(pdf, "Renewable fuel investments", fig_renewfuel(),
                     ["Electrolysers and methanol synthesis dominate", "IC1 builds much more of both, almost all in NL", "Methanation is zero in both (CO2 now counted)"],
                     section=S3, imgw=.68, cap="Installed capacity of renewable fuel technologies by country and year (GW).")
        M.plot_slide(pdf, "Biomass use per country", fig_bio(),
                     ["Mostly used for biogas in 2050", "IC1: all in NL; country level: split NL / BE", "Bio boilers phased out by 2050"],
                     section=S3, imgw=.64, cap="Biomass consumed in NL and BE (TWh, primary).")
        M.plot_slide(pdf, "Trade with neighbouring countries, 2050", fig_trade(),
                     ["Neighbours (DE, FR, LU, UK, NO) are outside the optimised area; NL+BE trades with them via the interconnectors", "Imports equal exports for every carrier: no net trade with neighbours in either run",  "Gross flows are large: methane ~210-245 TWh through NL+BE (transit)",
                      "Net figure shown above each run"], section=S3, imgw=.7, cap="Gross imports, exports and NL<->BE exchange in 2050 (TWh; CO2 in Mt).")
        M.plot_slide(pdf, "Where captured CO2 goes", fig_co2split(), ["Stored: 16 Mt in both (cap binding)", "Used: CO2 into methanol for olefins (plastics)", "No CO2 exported (NL+BE only model)", "No methanation, no DAC"], section=S3, imgw=.6, cap="Captured CO2 by destination, NL+BE 2050. Refinery SMR+CC makes H2 used inside the refinery, so it shows in CO2 but not in H2 supply.")
        M.plot_slide(pdf, "CO2 balance 2050", rf"{CMP}\C04_co2_balance_2050.png",
                     [f"Captured {cap(ic):.1f} vs {cap(ct):.1f} Mt", "Stored 16 Mt in both (cap binding)",
                      f"Used in methanol {used(ic):.1f} vs {used(ct):.1f} Mt"], section=S3, cap="NL+BE CO2 balance in 2050.")
        M.plot_slide(pdf, "Costs of NL+BE assets", rf"{CMP}\C08_cost_breakdown_nlbe.png",
                     ["Savings: heat pumps (ground vs air), nuclear, PEM", "Industry costs nearly identical"], section=S3,
                     cap="Investment and fixed O&M of assets in NL+BE, summed over milestone years. Not the full objective.")
        fig = M.frame("Flows in 2050", None, S3)
        for i, (k, n) in enumerate([("IC1", RUN["IC1"]), ("CTRY", RUN["CTRY"])]):
            fig.text(.03 + .48 * i + .235, .85, LAB[k].replace("\n", " "), ha="center", fontsize=13, fontweight="bold", color=M.NAVY)
            M.img(fig, rf"{CMP}\C07_flow_map_2050_{n}.png", [.02 + .48 * i, .15, .47, .68])
        M.caption(fig, "Energy and CO2 flows in 2050. In the country-level run, flows inside a country are not modelled."); pdf.savefig(fig); plt.close(fig)
        M.text_slide(pdf, "Robustness: earlier runs vs final runs", [
            ("Earlier runs (methanation CO2 not counted)", [f"Cost gap {dOld:.1f}%", "Captured CO2 sent to methanation (22.5 / 14.5 Mt)",
                                                         "Same direction: IC1 needs more H2 and more nuclear"]),
            ("Final runs (leak closed, no DAC, 16 Mt)", [f"!Cost gap {dO:.1f}%", "Methanation 0; CO2 goes to methanol for olefins instead",
                                                         "!Resolution effect grows: internal CO2 transport matters more because storage is now the main outlet"])],
            section="Robustness", sub="The direction of the resolution effect does not depend on the CO2 accounting fix")
        M.text_slide(pdf, "Conclusions", [
            ("What resolution changes", [f"System cost by ~{abs(dO):.0f}%", "Size and location of the H2 / methanol chain",
                                         "Nuclear amount and location", "Steel route mix", "Use of CO2 near the source vs moving it to storage"]),
            ("What it does not change", ["Net zero and binding storage cap", "Total CO2 capture of the same order (28-32 Mt)",
                                         "Wind, solar, LH2 and LNG totals", "Ammonia, cement, glass, chlorine routes"])],
            section="Conclusions", sub="Country resolution hides internal CO2 transport costs: it underestimates cost and the need for local CO2 use")
        M.text_slide(pdf, "Caveats", [("", [
            "3 representative days per year; storage and seasonal effects are simplified",
            "CO2 used in methanol for olefins is treated as locked in plastics (end-of-life emissions outside the scope)",
            "NL storage cap raised to 16 Mt/yr in 2050 (from 10.5) - the smallest cap that is feasible without DAC",
            "The main difference comes from zone-to-zone CO2 pipeline tariffs in IC1 (pessimistic x6); with lower tariffs the gap is likely smaller",
            "Country-level results reported per zone (units) are only an allocation, not a location"])], section="Conclusions")
    print("wrote", out, M.page[0], "pages")
if __name__ == "__main__": main(sys.argv[1])







