r"""Slide deck (PDF, 16:9): Standalone (NL+BE, 17 zones) vs Country-level (NL+BE, 1 node per country).
Usage: python tools/make_slides_ctry.py <out.pdf>"""
import os, sys, re, pickle, textwrap
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.image as mpimg
sys.path.insert(0, "tools"); import plot_run_summary as S
NAVY, ACC, GREY = "#1d3557", "#e76f51", "#5c6770"
CSA, CCL = "#9aa3ad", NAVY
P = r"runs\3day_nb_ctry\plots"; SA_D = P + r"\summary_named_standalone"; CL_D = P + r"\summary_named_countrylevel"; CMP = P + r"\compare_standalone"
TMP = r"run_logs\_slide_tmp_ctry"; os.makedirs(TMP, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "savefig.dpi": 300, "image.resample": True})
W, H = 13.333, 7.5; page = [0]
A = pickle.load(open(r"run_logs\nb_v2_NLBE.pkl", "rb")); B = pickle.load(open(r"run_logs\nb_ctry_NLBE.pkl", "rb"))
BAL = pickle.load(open(r"run_logs\_bal_sa_cl.pkl", "rb"))
INTRA = re.compile(r"^((BE|NL)C\d+)_(\w+)_((BE|NL)C\d+)$")

def frame(title, subtitle=None, section=None):
    fig = plt.figure(figsize=(W, H)); page[0] += 1
    fig.patches.append(plt.Rectangle((0, .9), 1, .1, transform=fig.transFigure, color=NAVY))
    fig.patches.append(plt.Rectangle((0, .895), 1, .005, transform=fig.transFigure, color=ACC))
    fig.text(.035, .945, title, color="white", fontsize=22, fontweight="bold", va="center")
    if section: fig.text(.965, .945, section, color="#a8dadc", fontsize=11, va="center", ha="right")
    if subtitle: fig.text(.035, .86, subtitle, color=GREY, fontsize=12.5, style="italic", va="center")
    fig.text(.965, .02, f"{page[0]}", color=GREY, fontsize=9, ha="right")
    fig.text(.035, .02, "Industrial Case Study (MOPO) - SpineOpt investment runs - Zonal (17 zones) vs Country-level resolution", color="#9aa3ad", fontsize=8)
    return fig
def img(fig, path, rect):
    ax = fig.add_axes(rect); ax.imshow(mpimg.imread(path), interpolation="lanczos"); ax.axis("off"); return ax
def bullets(fig, items, x, y, w=40, fs=12.5, gap=.012):
    for it in items:
        bold = it.startswith("!"); it = it.lstrip("!"); txt = textwrap.fill(it, w); n = txt.count("\n") + 1
        fig.text(x, y, "\u25A0", color=ACC, fontsize=fs * .7, va="top")
        fig.text(x + .018, y, txt, fontsize=fs, va="top", color=NAVY if bold else "#222", fontweight="bold" if bold else "normal", linespacing=1.3)
        y -= n * fs * 1.3 / 72 / H + gap
    return y
def caption(fig, text):
    fig.patches.append(plt.Rectangle((.035, .055), .93, .075, transform=fig.transFigure, color="#f1f4f8"))
    fig.patches.append(plt.Rectangle((.035, .055), .004, .075, transform=fig.transFigure, color=ACC))
    fig.text(.05, .0925, textwrap.fill(text, 165), fontsize=11, va="center", color="#222", linespacing=1.35)
def plot_slide(pdf, title, path, notes, sub=None, cap=None, section=None, imgw=.62):
    fig = frame(title, sub, section)
    img(fig, path, [.02, .15 if cap else .06, imgw, .68 if cap else .77])
    bullets(fig, notes, .035 + imgw + .01, .8, w=int(34 * (1 - imgw) / .38))
    if cap: caption(fig, cap)
    pdf.savefig(fig); plt.close(fig)
def wide_slide(pdf, title, path, cap, sub=None, section=None):
    fig = frame(title, sub, section); img(fig, path, [.01, .14, .98, .7]); caption(fig, cap); pdf.savefig(fig); plt.close(fig)
def two_slide(pdf, title, p1, p2, l1, l2, cap, sub=None, section=None):
    fig = frame(title, sub, section)
    for p, l, x in [(p1, l1, .02), (p2, l2, .51)]:
        fig.text(x + .235, .825, l, ha="center", fontsize=13, fontweight="bold", color=NAVY); img(fig, p, [x, .15, .47, .66])
    caption(fig, cap); pdf.savefig(fig); plt.close(fig)
def text_slide(pdf, title, blocks, section=None, sub=None):
    fig = frame(title, sub, section); xs = [.05, .52] if len(blocks) > 1 else [.05]
    for x, (head, items) in zip(xs, blocks):
        fig.text(x, .8, head, fontsize=16, fontweight="bold", color=ACC)
        bullets(fig, items, x, .74, w=48 if len(blocks) > 1 else 95, fs=13.5, gap=.02)
    pdf.savefig(fig); plt.close(fig)
def style(ax):
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.grid(axis="y", color="#e3e7ec"); ax.set_axisbelow(True)
def save(fig, name):
    f = os.path.join(TMP, name + ".png"); fig.savefig(f, dpi=200, bbox_inches="tight"); plt.close(fig); return f

# ---------------- custom figures
def fig_intra_flows():
    d = BAL["SA"]; m = d.obj.str.match(INTRA)
    x = d[m & (d.dir == "to_node")].copy()
    x = x[x.obj.map(lambda o: INTRA.match(o).group(2) == INTRA.match(o).group(5))]
    lab = {"elec": "Electricity (TWh)", "H2": "Hydrogen (TWh)", "CH4": "Methane (TWh)", "HC": "Heat carrier (TWh)", "CO2": "CO2 (Mt)", "bio": "Biomass (TWh)"}
    p = (x.groupby(["car", "year"]).v.sum() / 1e3).unstack().reindex(["elec", "H2", "CO2", "bio"])
    fig, ax = plt.subplots(figsize=(10, 5.2)); xx = np.arange(len(p)); w = .26
    for j, (y, c) in enumerate(zip([2030, 2040, 2050], ["#a8dadc", "#457b9d", NAVY])):
        ax.bar(xx + (j - 1) * w, p[y], w, color=c, label=str(y))
        for i, v in enumerate(p[y]): ax.text(i + (j - 1) * w, v + 8, f"{v:.0f}", ha="center", fontsize=8.5)
    ax.set_xticks(xx, [lab[k] for k in p.index]); ax.set_ylabel("Flow between zones of the same country")
    ax.set_title("Standalone: energy moved between zones inside NL and BE", fontweight="bold"); ax.legend(frameon=False); style(ax)
    return save(fig, "intra_flows")
def fig_nuclear_zone():
    # country totals per year (zone labels are not meaningful in the Country-level run)
    def f(d):
        x = d["fleet"][d["fleet"].tech.str.startswith("nuclear")]
        return x.assign(c=x.region.str[:2]).groupby(["c", "year"]).units.sum().unstack().reindex(index=["NL", "BE"], columns=[2030, 2040, 2050]).fillna(0)
    fa, fb = f(A), f(B)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5.2), sharey=True)
    for ax, c in zip(axes, ["BE", "NL"]):
        xx = np.arange(3); w = .38
        for j, (df, nm, col) in enumerate([(fa, "Standalone", CSA), (fb, "Country-level", CCL)]):
            ax.bar(xx + (j - .5) * w, df.loc[c].values, w, color=col, label=nm)
            for i, v in enumerate(df.loc[c].values): ax.text(i + (j - .5) * w, v + .1, f"{v:.1f}", ha="center", fontsize=9)
        ax.set_xticks(xx, [2030, 2040, 2050]); ax.set_title({"BE": "Belgium", "NL": "Netherlands"}[c], fontweight="bold"); style(ax)
    axes[0].set_ylabel("Nuclear capacity (GW)"); axes[0].legend(frameon=False)
    return save(fig, "nuclear_zone")
def fig_h2_chain():
    rows = []
    for k, d in BAL.items():
        x = d[(d.car == "H2") & (d.year == 2050) & (d.kind == "unit")].copy()
        x["g"] = x.obj.str.replace(r"_(BE|NL)C\d+$", "", regex=True)
        sup = x[x.dir == "to_node"].groupby("g").v.sum() / 1e3; use = x[x.dir == "from_node"].groupby("g").v.sum() / 1e3
        rows.append((k, sup, use))
    def grp(s, M):
        out = {}
        for g, v in s.items():
            lab = next((l for l, r in M if re.search(r, g)), "Other")
            out[lab] = out.get(lab, 0) + v
        return pd.Series(out)
    SUP = [("Electrolysis (PEM)", r"^PEM"), ("LH2 import terminal", r"LH2")]
    USE = [("Polyethylene (H2 route)", r"^\(H2\)PEA"), ("Methanation", r"methanation"), ("H2 power plants", r"CCGT-H2"), ("Other industry", r"^\(")]
    lab = {"SA": "Standalone", "CL": "Country-level"}
    fig, axes = plt.subplots(1, 2, figsize=(13, 5.2), sharey=True)
    for ax, (nm, M, idx) in zip(axes, [("Hydrogen produced in NL+BE, 2050", SUP, 1), ("Hydrogen used in NL+BE, 2050", USE, 2)]):
        df = pd.concat({lab[k]: grp(r[idx], M) for k, *_ in [(r[0],) for r in rows] for r in [next(z for z in rows if z[0] == k)]}, axis=1).fillna(0)
        df = df[(df > .5).any(axis=1)]; xx = np.arange(len(df)); w = .38
        for j, (c, col) in enumerate([("Standalone", CSA), ("Country-level", CCL)]):
            ax.bar(xx + (j - .5) * w, df[c], w, color=col, label=c)
            for i, v in enumerate(df[c]): ax.text(i + (j - .5) * w, v + 1, f"{v:.0f}", ha="center", fontsize=9)
        ax.set_xticks(xx, [textwrap.fill(i, 14) for i in df.index]); ax.set_title(nm, fontweight="bold"); style(ax)
    axes[0].set_ylabel("TWh/yr"); axes[0].legend(frameon=False)
    return save(fig, "h2_chain")
def fig_pea():
    rows = {}
    for k, d in BAL.items():
        x = d[(d.year == 2050) & d.obj.str.match(r"^\((EL|H2)\)PEA_") & (d.dir == "from_node") & d.car.isin(["elec", "H2"])]
        rows[k] = x.assign(z=x.obj.str.extract(r"_((BE|NL))C\d+$")[0], r=x.car).groupby(["z", "r"]).v.sum().unstack().reindex(index=["NL", "BE"], columns=["H2", "elec"]).fillna(0) / 1e3
    fig, axes = plt.subplots(1, 2, figsize=(12, 5), sharey=True)
    for ax, c in zip(axes, ["NL", "BE"]):
        df = pd.DataFrame({"Standalone": rows["SA"].loc[c], "Country-level": rows["CL"].loc[c]}).T
        df.plot.bar(stacked=True, ax=ax, color=["#2a9d8f", "#f2b134"], width=.55, legend=False)
        for i, (_, r) in enumerate(df.iterrows()):
            y0 = 0
            for v in r.values:
                if v > 1: ax.text(i, y0 + v / 2, f"{v:.0f}", ha="center", va="center", fontsize=10, color="white", fontweight="bold")
                y0 += v
        ax.set_title({"BE": "Belgium", "NL": "Netherlands"}[c], fontweight="bold"); ax.set_xlabel(""); ax.tick_params(axis="x", rotation=0); style(ax)
    axes[0].set_ylabel("Energy input to polyethylene production 2050 (TWh/yr)")
    axes[1].legend(["Hydrogen route", "Electric route"], frameon=False)
    return save(fig, "pea_route")
def fig_storage_flex():
    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    cav = {}
    for k, d in BAL.items():
        x = d[d.obj.str.startswith("salt-cavern") & (d.dir == "to_node")]; cav[k] = x.groupby("year").v.sum().reindex([2030, 2040, 2050]).fillna(0) / 1e3
    bat = {k: d["fleet"][d["fleet"].tech.str.startswith("battery")].groupby("year").units.sum().reindex([2030, 2040, 2050]).fillna(0) for k, d in (("SA", A), ("CL", B))}
    for ax, data, yl, t in [(axes[0], cav, "H2 withdrawn from salt caverns (TWh/yr)", "Hydrogen salt caverns"), (axes[1], bat, "Battery capacity (GW)", "Batteries")]:
        xx = np.arange(3); w = .38
        for j, (k, nm, c) in enumerate([("SA", "Standalone", CSA), ("CL", "Country-level", CCL)]):
            ax.bar(xx + (j - .5) * w, data[k].values, w, color=c, label=nm)
            for i, v in enumerate(data[k].values): ax.text(i + (j - .5) * w, v * 1.01 + .3, f"{v:.0f}" if v >= 1 else f"{v:.1f}", ha="center", fontsize=9)
        ax.set_xticks(xx, [2030, 2040, 2050]); ax.set_ylabel(yl); ax.set_title(t, fontweight="bold"); style(ax)
    axes[0].legend(frameon=False)
    return save(fig, "storage_flex")
def fig_industry_diff():
    rows = []
    for y in [2030, 2040, 2050]:
        f = lambda d, y=y: d["prod"][d["prod"].year == y].assign(r=lambda z: z.tech.map(S.route_label)).groupby(["sector", "r"]).output.sum() / 1e3
        df = pd.concat({"SA": f(A), "CL": f(B)}, axis=1).fillna(0); df["d"] = df.CL - df.SA
        for (s, r), v in df[df.d.abs() > .05].iterrows(): rows.append((y, s, r, v.SA, v.CL, v.d))
    t = pd.DataFrame(rows, columns=["year", "sector", "route", "SA", "CL", "d"])
    tot = {y: A["prod"][A["prod"].year == y].output.sum() / 1e3 for y in [2030, 2040, 2050]}
    fig, ax = plt.subplots(figsize=(11, 5.4))
    lbl = [f"{r.year}  {r.sector}: {r.route}" for r in t.itertuples()]
    ax.barh(range(len(t)), t.d, color=[ACC if v > 0 else "#457b9d" for v in t.d])
    for i, v in enumerate(t.d): ax.text(v + (.02 if v > 0 else -.02), i, f"{v:+.2f}", va="center", ha="left" if v > 0 else "right", fontsize=9)
    ax.set_yticks(range(len(t)), lbl, fontsize=9.5); ax.invert_yaxis(); ax.axvline(0, color="#333", lw=.8)
    ax.set_xlim(-1.2, 1.2); ax.set_xlabel(f"Change in output, Country-level minus Standalone (total industrial output {tot[2050]:.1f} per year)")
    ax.set_title("All industrial route changes larger than 0.05 (everything else is identical)", fontweight="bold")
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    return save(fig, "industry_diff")
def kpi(pdf):
    def sup(d, c, y, pat=None):
        s = d["supply"]; s = s[(s.carrier == c) & (s.year == y)]; s = s[s.tech.str.contains(pat)] if pat else s; return s.energy.sum() / 1e3
    def fl(d, pat): f = d["fleet"][d["fleet"].year == 2050]; return f[f.tech.str.contains(pat)].units.sum()
    o = lambda d, f: f(d)
    rows = [("Total system cost (objective)", "3.644 M", "3.603 M  (-1.1%)"),
            ("Industrial output / route mix", "46.2", "46.2  (near identical)"),
            ("Net CO2 / CO2 stored (Mt)", "0 / 27.2", "0 / 27.2"),
            ("Electricity generation (TWh)", f"{sup(A,'electricity',2050):.0f}", f"{sup(B,'electricity',2050):.0f}"),
            ("Nuclear capacity (GW)", f"{fl(A,'^nuclear'):.1f}", f"{fl(B,'^nuclear'):.1f}"),
            ("Hydrogen supply (TWh)", f"{sup(A,'hydrogen',2050):.0f}", f"{sup(B,'hydrogen',2050):.0f}"),
            ("of which electrolysis (TWh)", f"{sup(A,'hydrogen',2050,'^PEM'):.0f}", f"{sup(B,'hydrogen',2050,'^PEM'):.0f}"),
            ("Electrolysers PEM (GW)", f"{fl(A,'^PEM'):.1f}", f"{fl(B,'^PEM'):.1f}"),
            ("Batteries (GW)", f"{fl(A,'^battery'):.1f}", f"{fl(B,'^battery'):.1f}"),
            ("H2 salt cavern use (TWh)", "66", "0")]
    fig = frame("Key numbers: NL+BE in 2050", "Identical data, scenario, CO2 budget and storage caps - only the spatial resolution differs", "Comparison")
    ax = fig.add_axes([.06, .1, .88, .72]); ax.axis("off")
    t = ax.table(cellText=[list(r) for r in rows], colLabels=["Indicator (NL+BE, 2050)", "Standalone\n17 zones", "Country-level\n1 node per country"], loc="upper center", cellLoc="center", colWidths=[.5, .22, .22])
    t.auto_set_font_size(False); t.set_fontsize(13); t.scale(1, 2.05)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor("#dde3ea")
        if r == 0: cell.set_facecolor(NAVY); cell.get_text().set_color("white"); cell.get_text().set_fontweight("bold")
        elif r % 2: cell.set_facecolor("#f6f8fb")
        if c == 0 and r > 0: cell._loc = "left"
        if c == 2 and r > 0: cell.get_text().set_fontweight("bold"); cell.get_text().set_color(NAVY)
    pdf.savefig(fig); plt.close(fig)

def main(out):
    fi, fn, fh, fp, fs, fd = fig_intra_flows(), fig_nuclear_zone(), fig_h2_chain(), fig_pea(), fig_storage_flex(), fig_industry_diff()
    with PdfPages(out) as pdf:
        fig = plt.figure(figsize=(W, H)); page[0] += 1
        fig.patches.append(plt.Rectangle((0, 0), 1, 1, transform=fig.transFigure, color=NAVY))
        fig.patches.append(plt.Rectangle((.06, .43), .2, .008, transform=fig.transFigure, color=ACC))
        fig.text(.06, .62, "Decarbonising NL+BE industry:\ndoes spatial resolution matter?", color="white", fontsize=32, fontweight="bold", va="center", linespacing=1.25)
        fig.text(.06, .36, "SpineOpt investment runs 2030 / 2040 / 2050  -  3 representative days per year  -  Gurobi", color="#a8dadc", fontsize=14)
        fig.text(.06, .3, "Standalone: NL+BE in 17 zones     vs     Country-level: NL+BE as one node per country", color="white", fontsize=13)
        fig.text(.06, .1, "MOPO Industrial Case Study  |  October 2026", color="#9aa3ad", fontsize=11)
        pdf.savefig(fig); plt.close(fig)
        text_slide(pdf, "Set-up of the two runs", [
            ("Standalone - 17 zones", ["NL (9) and BE (8) zones, each with its own electricity, gas, hydrogen, CO2, heat-carrier and biomass node",
                                       "Transport between zones limited by line and pipeline capacities (expandable at a cost)",
                                       "Own CO2 cap: net zero in 2050; NL storage only (27.2 Mt/yr)"]),
            ("Country-level - 2 nodes", ["Same data. Zone networks merged into one node per country and carrier",
                                         "No transport limits inside a country; links between NL, BE and neighbours unchanged",
                                         "Same CO2 cap, storage caps and scenario. Plants, demand and resources unchanged and summed per country"])],
            section="Introduction", sub="A controlled experiment: the only difference is the spatial resolution of the networks")
        text_slide(pdf, "Main messages", [("", [
            "!Industrial decarbonisation is robust to spatial resolution: same output, same CCS shares, only small route shifts (<1 of 46)",
            "!The energy system around industry does change: removing grid limits inside a country moves the cheapest route for some plants",
            "Dutch polyethylene production switches from hydrogen to electricity -> hydrogen demand and electrolysis fall sharply (PEM 64 -> 26 TWh)",
            "Without electrolysis to buffer, salt caverns are no longer used; batteries partly take over",
            "No new nuclear in NL (3.1 -> 0 GW in 2050); Belgium unchanged at 6.0 GW. Total cost 1.1% lower",
            "Country-level models leave out network limits inside a country, so they understate grid costs and overstate how freely energy can move"])], section="Summary")
        kpi(pdf)
        S_ = "Why results differ"
        plot_slide(pdf, "The zonal network is heavily used", fi,
                   ["2050: 733 TWh electricity and 108 TWh hydrogen move between zones in the Standalone run",
                    "120 of 158 links within a country run at their peak at least 20% of the time", "Six Dutch power links are expanded",
                    "!In the Country-level run all of this is free and unlimited"],
                   section=S_, cap="Annual flows over links between zones of the same country (Standalone). These links do not exist in the Country-level run.")
        plot_slide(pdf, "Polyethylene: from hydrogen to electricity", fp,
                   ["Standalone: the main Dutch plant runs on hydrogen, because grid limits restrict power to its location",
                    "With one national electricity node, the electric route becomes cheaper",
                    "NL 2050: hydrogen 16 -> 0 TWh, electricity 24 -> 38 TWh", "BE 2050: hydrogen 42 -> 33 TWh, electricity 6 -> 14 TWh"],
                   section=S_, cap="Energy input to polyethylene production per country, 2050.")
        plot_slide(pdf, "Hydrogen: one chain reaction", fh,
                   ["Less H2 for polyethylene (-25) and methanation (-13)", "Electrolysis falls 64 -> 26 TWh",
                    "LH2 imports unchanged (42.5 TWh): the remaining supply"],
                   section=S_, cap="Hydrogen produced and used in NL+BE in 2050, per technology group.")
        plot_slide(pdf, "Flexibility: caverns out, batteries in", fs,
                   ["Standalone: caverns buffer wind-driven electrolysis (66 TWh cycled)", "Country-level: small electrolysis, caverns retired in 2030",
                    "Battery capacity roughly doubles"],
                   section=S_, cap="Left: hydrogen withdrawn from salt caverns. Right: battery capacity in NL+BE.")
        plot_slide(pdf, "Nuclear: none in the Netherlands", fn,
                   ["Belgium: same nuclear in 2050 (6.0 GW)", "Netherlands: 3.1 GW in Standalone, none in Country-level",
                    "!Likely cause: with grid limits between zones, local generation is worth more; at country level, offshore wind can reach all demand"],
                   section=S_, cap="Nuclear capacity per country (existing plus new).")
        S2 = "Results side by side"
        plot_slide(pdf, "Electricity generation", rf"{CMP}\C01_electricity_mix.png",
                   ["2050: 502 vs 474 TWh", "Lower electrolysis demand outweighs more electric polyethylene and heat pumps", "Offshore wind total about the same"],
                   section=S2, cap="NL+BE electricity generation by technology; left Standalone, right Country-level.")
        plot_slide(pdf, "Capacity: where investments shift", rf"{CMP}\C02_capacity_delta.png",
                   ["Less nuclear and PEM", "More batteries and heat pumps", "Other technologies nearly identical"],
                   section=S2, cap="Left: installed capacity 2050. Right: difference Country-level minus Standalone per milestone year.")
        plot_slide(pdf, "Hydrogen supply over time", rf"{CMP}\C06_hydrogen_supply.png",
                   ["2030-2040 nearly equal", "Divergence in 2050 when electrolysis scales up in the Standalone run"],
                   section=S2, cap="Hydrogen supply in NL+BE by source.")
        two_slide(pdf, "Heat supply", rf"{SA_D}\04_heat_supply.png", rf"{CL_D}\04_heat_supply.png", "Standalone", "Country-level",
                  "Country-level 2050: more heat pumps, no bio-boilers, fewer gas boilers. The freed biomass goes to ammonia production.", section=S2)
        S3 = "Industry"
        wide_slide(pdf, "Industrial routes: practically the same", rf"{CMP}\C03_industry_routes.png",
                   "Route shares per sector. Each panel: left three bars Standalone (2030/40/50), right three bars Country-level.",
                   sub="Same sectors decarbonise with the same technologies; differences are hard to see at this scale", section=S3)
        plot_slide(pdf, "Industry: the few differences", fd,
                   ["Glass: some H2 furnaces replaced by electric (cheap national power)", "Ammonia: more biomass gasification, less SMR+CCS (biomass freed from heating)",
                    "Cement 2030: CCS one decade later in part; same from 2040"],
                   section=S3, imgw=.64, cap="All route changes larger than 0.05 (output units). The 2050 total output is 46.2 in both runs.")
        plot_slide(pdf, "CO2: same balance in both runs", rf"{CMP}\C04_co2_balance_2050.png",
                   ["Net zero in 2050 in both", "Storage cap (27.2 Mt/yr) binding in both", "Capture sources shift slightly between ammonia and hydrogen"],
                   section=S3, cap="NL+BE CO2 balance in 2050.")
        plot_slide(pdf, "Costs of NL+BE assets", rf"{CMP}\C08_cost_breakdown_nlbe.png",
                   ["Total cost -1.1%", "Savings mainly nuclear and PEM", "Industry costs identical"],
                   section=S3, cap="Investment and fixed O&M of assets located in NL+BE, summed over the milestone years. Not the full objective.")
        text_slide(pdf, "Conclusions", [
            ("What the resolution changes", ["Grid limits inside a country drive where and how hydrogen and electricity are supplied",
                                             "Country-level runs leave out internal grid limits, so they understate infrastructure needs",
                                             "Differences add up to ~1% of system cost"]),
            ("What it does not change", ["Industrial decarbonisation pathway and CCS shares",
                                         "CO2 balance and storage use", "Wind, solar and LH2 import totals"])],
            section="Conclusions", sub="For industry-focused questions, country resolution gives the same answer; for network and siting questions, zones are needed")
    print("wrote", out, page[0], "pages")
if __name__ == "__main__":
    main(sys.argv[1])







