r"""Slide decks (PDF, 16:9) for the PESSIMISTIC CCS runs (low_CO2 caps + high-cost CO2 tariffs).
Usage: python tools/make_slides_pess.py {ctry|mr|combined} <out.pdf>
  ctry     : IC1 (NL+BE 17 zones) vs Country-level (NL+BE 2 nodes)
  mr       : IC1 vs Mixed resolution (NL+BE IC1 + DE/DK/NO/UK as 1 node each), DAC fixed
  combined : IC1 baseline vs change in resolution vs change in scope
"""
import os, sys, glob, pickle, textwrap
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.image as mpimg
sys.path.insert(0, "tools"); import plot_run_summary as S
NAVY, ACC, GREY = "#1d3557", "#e76f51", "#5c6770"
RUN = {"IC1": "nb_ccslow", "CTRY": "nb_ctry_ccslow", "MR": "mr_ccslow_dac0"}
LAB = {"IC1": "IC1 baseline\n(NL+BE, 17 zones)", "CTRY": "Resolution change\n(NL+BE, 1 node/country)", "MR": "Scope change\n(+DE/DK/NO/UK)"}
SHORT = {"IC1": "IC1", "CTRY": "Country-level", "MR": "Mixed resolution"}
COL = {"IC1": "#9aa3ad", "CTRY": NAVY, "MR": ACC}
CMP = {"CTRY": r"runs\3day_nb_ctry_ccslow\plots\cmp_vs_ic1_pess", "MR": r"runs\3day_mr_ccslow_dac0\plots\cmp_vs_ic1_pess"}
D = {k: pickle.load(open(rf"run_logs\{v}_NLBE.pkl", "rb")) for k, v in RUN.items()}
FULL = {k: pickle.load(open(rf"run_logs\{v}.pkl", "rb")) for k, v in RUN.items()}
TMP = r"run_logs\_slide_tmp_pess"; os.makedirs(TMP, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "savefig.dpi": 300, "image.resample": True})
W, H = 13.333, 7.5; page = [0]; FOOT = [""]

def frame(title, subtitle=None, section=None):
    fig = plt.figure(figsize=(W, H)); page[0] += 1
    fig.patches.append(plt.Rectangle((0, .9), 1, .1, transform=fig.transFigure, color=NAVY))
    fig.patches.append(plt.Rectangle((0, .895), 1, .005, transform=fig.transFigure, color=ACC))
    fig.text(.035, .945, title, color="white", fontsize=22, fontweight="bold", va="center")
    if section: fig.text(.965, .945, section, color="#a8dadc", fontsize=11, va="center", ha="right")
    if subtitle: fig.text(.035, .86, subtitle, color=GREY, fontsize=12.5, style="italic", va="center")
    fig.text(.965, .02, f"{page[0]}", color=GREY, fontsize=9, ha="right")
    fig.text(.035, .02, FOOT[0], color="#9aa3ad", fontsize=8)
    return fig
def img(fig, path, rect):
    ax = fig.add_axes(rect); ax.imshow(mpimg.imread(path), interpolation="lanczos"); ax.axis("off")
def bullets(fig, items, x, y, w=40, fs=12.5, gap=.012):
    for it in items:
        bold = it.startswith("!"); it = it.lstrip("!"); txt = textwrap.fill(it, w); n = txt.count("\n") + 1
        fig.text(x, y, "\u25A0", color=ACC, fontsize=fs * .7, va="top")
        fig.text(x + .018, y, txt, fontsize=fs, va="top", color=NAVY if bold else "#222", fontweight="bold" if bold else "normal", linespacing=1.3)
        y -= n * fs * 1.3 / 72 / H + gap
def caption(fig, text):
    fig.patches.append(plt.Rectangle((.035, .055), .93, .075, transform=fig.transFigure, color="#f1f4f8"))
    fig.patches.append(plt.Rectangle((.035, .055), .004, .075, transform=fig.transFigure, color=ACC))
    fig.text(.05, .0925, textwrap.fill(text, 165), fontsize=11, va="center", color="#222", linespacing=1.35)
def plot_slide(pdf, title, path, notes, sub=None, cap=None, section=None, imgw=.62):
    fig = frame(title, sub, section); img(fig, path, [.02, .15 if cap else .06, imgw, .68 if cap else .77])
    bullets(fig, notes, .035 + imgw + .01, .8, w=int(34 * (1 - imgw) / .38))
    if cap: caption(fig, cap)
    pdf.savefig(fig); plt.close(fig)
def wide_slide(pdf, title, path, cap, sub=None, section=None):
    fig = frame(title, sub, section); img(fig, path, [.01, .14, .98, .7]); caption(fig, cap); pdf.savefig(fig); plt.close(fig)
def text_slide(pdf, title, blocks, section=None, sub=None):
    fig = frame(title, sub, section); xs = [.05, .52] if len(blocks) > 1 else [.05]
    for x, (head, items) in zip(xs, blocks):
        fig.text(x, .8, head, fontsize=16, fontweight="bold", color=ACC)
        bullets(fig, items, x, .74, w=48 if len(blocks) > 1 else 95, fs=13.5, gap=.02)
    pdf.savefig(fig); plt.close(fig)
def title_slide(pdf, t, sub, line):
    fig = plt.figure(figsize=(W, H)); page[0] += 1
    fig.patches.append(plt.Rectangle((0, 0), 1, 1, transform=fig.transFigure, color=NAVY))
    fig.patches.append(plt.Rectangle((.06, .43), .2, .008, transform=fig.transFigure, color=ACC))
    fig.text(.06, .62, t, color="white", fontsize=30, fontweight="bold", va="center", linespacing=1.25)
    fig.text(.06, .36, sub, color="#a8dadc", fontsize=14); fig.text(.06, .3, line, color="white", fontsize=13)
    fig.text(.06, .1, "MOPO Industrial Case Study  |  October 2026", color="#9aa3ad", fontsize=11)
    pdf.savefig(fig); plt.close(fig)
def style(ax):
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.grid(axis="y", color="#e3e7ec"); ax.set_axisbelow(True)
def save(fig, name):
    f = os.path.join(TMP, name + ".png"); fig.savefig(f, dpi=200, bbox_inches="tight"); plt.close(fig); return f

# ---------------- metrics (NL+BE, 2050)
def sup(k, c, cat=None, y=2050):
    s = D[k]["supply"]; s = s[(s.carrier == c) & (s.year == y) & (s.energy > 0)]
    if cat: s = s[s.category == cat]
    return s.energy.sum() / 1e3
def fl(k, pat, y=2050):
    f = D[k]["fleet"]; f = f[(f.year == y) & f.region.astype(str).str.match(r"^(NL|BE)")]; return f[f.tech.str.contains(pat)].units.sum()
def stored(k, y=2050): return D[k]["co2store"].query("year==@y").co2.sum() / 1e3
def netco2(k, y=2050): return D[k]["emis"].query("year==@y").co2.sum() / 1e3
def co2exp(k, y=2050):
    p = FULL[k]["co2pipe"]; p = p[p.year == y]; o, d = p.origin.str[:2], p.dest.str[:2]
    nb = lambda s: s.isin(["NL", "BE"])
    return (p[nb(o) & ~nb(d)].co2.sum() - p[~nb(o) & nb(d)].co2.sum()) / 1e3
def obj(k): return FULL[k]["obj"].sum()
def route_share(k, sector, pat):
    p = D[k]["prod"]; p = p[(p.year == 2050) & (p.sector == sector)]
    return 100 * p[p.tech.str.contains(pat, regex=True)].output.sum() / max(p.output.sum(), 1e-9)

def fig_kpi_bars(keys, name):
    M = [("Offshore wind\n(TWh)", lambda k: sup(k, "electricity", "wind offshore")),
         ("Electrolytic H2\n(TWh)", lambda k: sup(k, "hydrogen", "electrolysis")),
         ("Methane use\n(TWh)", lambda k: sup(k, "methane")),
         ("Heat pumps\n(TWh heat)", lambda k: sup(k, "heat", "electrification (heat pumps)")),
         ("Bio heat\n(TWh)", lambda k: sup(k, "heat", "bioenergy")),
         ("Gas heat\n(TWh)", lambda k: sup(k, "heat", "unabated fossil"))]
    fig, axes = plt.subplots(1, len(M), figsize=(15, 4.8))
    for ax, (t, f) in zip(axes, M):
        v = [f(k) for k in keys]; ax.bar(range(len(keys)), v, color=[COL[k] for k in keys], width=.7)
        for i, x in enumerate(v): ax.text(i, x + max(v) * .02, f"{x:.0f}", ha="center", fontsize=10)
        ax.set_title(t, fontsize=11.5, fontweight="bold"); ax.set_xticks([]); style(ax); ax.set_ylim(0, max(max(v), 1) * 1.15)
    fig.legend([plt.Rectangle((0, 0), 1, 1, color=COL[k]) for k in keys], [LAB[k].replace("\n", " ") for k in keys], loc="lower center", ncol=len(keys), frameon=False, bbox_to_anchor=(.5, -.06))
    fig.tight_layout(); return save(fig, name)
def fig_cap_bars(keys, name):
    M = [("PEM", "^PEM"), ("Methanation", "^methanation"), ("Nuclear", "^nuclear"), ("Gas boilers", "^gas-boiler"),
         ("Bio-boilers", "^bio-boiler"), ("Heat pumps", "heatpump$"), ("Batteries", "^battery")]
    fig, ax = plt.subplots(figsize=(13, 5)); xx = np.arange(len(M)); w = .8 / len(keys)
    for j, k in enumerate(keys):
        v = [fl(k, p) for _, p in M]; ax.bar(xx + (j - (len(keys) - 1) / 2) * w, v, w, color=COL[k], label=LAB[k].replace("\n", " "))
        for i, x in enumerate(v): ax.text(i + (j - (len(keys) - 1) / 2) * w, x + .4, f"{x:.1f}", ha="center", fontsize=8.5)
    ax.set_xticks(xx, [m for m, _ in M]); ax.set_ylabel("Capacity in NL+BE, 2050 (GW)"); ax.legend(frameon=False); style(ax)
    return save(fig, name)
def fig_co2(keys, name):
    M = [("CO2 stored in NL+BE", stored), ("CO2 exported to other countries", co2exp), ("Net CO2 emitted by NL+BE", netco2)]
    fig, ax = plt.subplots(figsize=(11, 5)); xx = np.arange(len(M)); w = .8 / len(keys)
    for j, k in enumerate(keys):
        v = [f(k) for _, f in M]; ax.bar(xx + (j - (len(keys) - 1) / 2) * w, v, w, color=COL[k], label=LAB[k].replace("\n", " "))
        for i, x in enumerate(v): ax.text(i + (j - (len(keys) - 1) / 2) * w, x + 1, f"{x:.1f}", ha="center", fontsize=9.5)
    ax.set_xticks(xx, [m for m, _ in M]); ax.set_ylabel("Mt CO2 in 2050"); ax.legend(frameon=False); style(ax)
    return save(fig, name)
def fig_routes(keys, name):
    R = [("Steel: molten-oxide\nelectrolysis", "steel (primary)", r"^MOE"), ("Steel: gas DRI\n+ CCS", "steel (primary)", r"DRI-EAF-MEA"),
         ("Ammonia: biomass\ngasification", "ammonia", r"^\(BM\)NH3"), ("Ammonia: gas SMR\n+ CCS", "ammonia", r"^\(NG\)NH3-"),
         ("Glass float:\ngas + CC", "glass (float)", r"^\(NG\)"), ("Cement: biomass\noxy-fuel + CCS", "cement", r"\(BMW\)")]
    fig, ax = plt.subplots(figsize=(13, 5)); xx = np.arange(len(R)); w = .8 / len(keys)
    for j, k in enumerate(keys):
        v = [route_share(k, s, p) for _, s, p in R]; ax.bar(xx + (j - (len(keys) - 1) / 2) * w, v, w, color=COL[k], label=LAB[k].replace("\n", " "))
        for i, x in enumerate(v): ax.text(i + (j - (len(keys) - 1) / 2) * w, x + 1.5, f"{x:.0f}%", ha="center", fontsize=9)
    ax.set_xticks(xx, [r for r, _, _ in R], fontsize=10); ax.set_ylabel("Share of sector output in NL+BE, 2050 (%)"); ax.set_ylim(0, 115); ax.legend(frameon=False, loc="upper right"); style(ax)
    return save(fig, name)

def kpi_table(pdf, keys, sub):
    def r(lbl, f, fmt="{:.0f}"): return [lbl] + [fmt.format(f(k)) for k in keys]
    rows = [["Total system cost (objective, whole model)"] + [f"{obj(k)/1e6:.3f} M" for k in keys],
            r("Net CO2 emitted by NL+BE (Mt)", netco2, "{:.1f}"), r("CO2 stored in NL+BE (Mt)", stored, "{:.1f}"),
            r("CO2 exported (Mt)", co2exp, "{:.1f}"),
            r("Offshore wind (TWh)", lambda k: sup(k, "electricity", "wind offshore")),
            r("Electrolytic H2 (TWh)", lambda k: sup(k, "hydrogen", "electrolysis")),
            r("Methane use (TWh)", lambda k: sup(k, "methane")),
            r("PEM / methanation (GW)", lambda k: f"{fl(k,'^PEM'):.1f} / {fl(k,'^methanation'):.1f}", "{}"),
            r("Nuclear (GW)", lambda k: fl(k, "^nuclear"), "{:.1f}"),
            r("Heat: pumps / bio / gas (TWh)", lambda k: f"{sup(k,'heat','electrification (heat pumps)'):.0f} / {sup(k,'heat','bioenergy'):.0f} / {sup(k,'heat','unabated fossil'):.0f}", "{}")]
    fig = frame("Key numbers: NL+BE in 2050", sub, "Comparison")
    ax = fig.add_axes([.04, .08, .92, .75]); ax.axis("off")
    cw = [.42] + [.56 / len(keys)] * len(keys)
    t = ax.table(cellText=rows, colLabels=["Indicator (NL+BE, 2050)"] + [LAB[k] for k in keys], loc="upper center", cellLoc="center", colWidths=cw)
    t.auto_set_font_size(False); t.set_fontsize(12.5); t.scale(1, 2.0)
    for (rr, c), cell in t.get_celld().items():
        cell.set_edgecolor("#dde3ea")
        if rr == 0: cell.set_facecolor(NAVY); cell.get_text().set_color("white"); cell.get_text().set_fontweight("bold"); cell.set_height(cell.get_height() * 1.5)
        elif rr % 2: cell.set_facecolor("#f6f8fb")
        if c == 0 and rr > 0: cell._loc = "left"
    pdf.savefig(fig); plt.close(fig)

SETUP_IC1 = ["NL (9) + BE (8) zones, each with own electricity, gas, H2, CO2, heat and biomass nodes",
             "Transport between zones limited by line/pipeline capacities (H2 and part of power expandable)",
             "Own CO2 cap for NL+BE: 165 / 37 / 0 Mt (2030/40/50)"]
PESS = ["!Pessimistic CCS in all runs: low CO2-storage caps (NL 10.5 Mt/yr instead of 27.2)",
        "CO2 pipeline tariffs x6, injection tariffs x1.2-4.7, shipping unchanged",
        "DAC disabled (no existing or new units)"]

def deck_pair(B, out):
    cmp = CMP[B]; keys = ["IC1", B]
    if B == "CTRY":
        FOOT[0] = "Industrial Case Study (MOPO) - SpineOpt - pessimistic CCS - IC1 (17 zones) vs Country-level resolution"
    with PdfPages(out) as pdf:
        if B == "CTRY":
            title_slide(pdf, "Pessimistic CCS in NL+BE:\ndoes spatial resolution matter?", "SpineOpt investment runs 2030 / 2040 / 2050  -  3 representative days per year  -  Gurobi",
                        "IC1: NL+BE in 17 zones     vs     Country-level: NL+BE as one node per country")
            text_slide(pdf, "Set-up of the two runs", [("IC1 - 17 zones", SETUP_IC1 + PESS[:1]),
                ("Country-level - 2 nodes", ["Same data. Zone networks merged into one node per country and carrier",
                                             "No transport limits inside a country; links to neighbours unchanged",
                                             "Same CO2 cap, storage caps, tariffs and scenario"] + PESS[1:])],
                       section="Introduction", sub="A controlled experiment: the only difference is the spatial resolution of the NL+BE networks")
            text_slide(pdf, "Main messages", [("", [
                "!Both runs reach net zero with only 10.5 Mt/yr of storage: captured CO2 is reused in e-fuels/methanation instead",
                "!Country-level needs a smaller hydrogen chain: electrolysis 149 -> 94 TWh, PEM 25 -> 17 GW, methanation 13 -> 8 GW",
                "Heat is decarbonised further at country level: heat pumps 80 -> 116 TWh, gas heat 42 -> 5 TWh",
                "Less nuclear at country level (11 -> 6 GW); offshore wind about the same (~450 TWh)",
                "Industry nearly unchanged: some glass goes fully electric, steel shifts towards molten-oxide electrolysis (57 -> 64%)",
                "Total cost 1.4% lower at country level - the same order as with optimistic CCS (1.1%)"])], section="Summary")
            kpi_table(pdf, keys, "Identical data, scenario and pessimistic CCS - only the spatial resolution differs")
        else:
            FOOT[0] = "Industrial Case Study (MOPO) - SpineOpt - pessimistic CCS - NL+BE alone vs NL+BE with DE/DK/NO/UK (country nodes)"
            title_slide(pdf, "Pessimistic CCS in NL+BE:\ndoes the neighbourhood matter?", "SpineOpt investment runs 2030 / 2040 / 2050  -  3 representative days per year  -  Gurobi",
                        "IC1: NL+BE alone (17 zones)     vs     Mixed resolution: NL+BE zones + DE, DK, NO, UK as one node each")
            text_slide(pdf, "Set-up of the two runs", [("IC1 - NL+BE alone", SETUP_IC1 + PESS[:1]),
                ("Mixed resolution - 6 countries", ["NL+BE identical (17 zones); DE, DK, NO, UK added as one node each",
                                                    "Trade of electricity, gas, H2 and CO2 with the four countries",
                                                    "One shared CO2 cap for 6 countries: 1146 / 255 / 0 Mt",
                                                    "Storage in NO, UK, DK also capped low (DE and some UK sites: 0)"] + PESS[1:])],
                       section="Introduction", sub="Change in spatial scope: NL+BE at the same resolution, but now connected to its neighbours")
            text_slide(pdf, "Main messages", [("", [
                "!Neighbours change NL+BE far more than resolution does: the shared CO2 cap lets NL+BE emit 93 Mt in 2050, compensated elsewhere",
                "!NL+BE keeps gas-based industry with CCS (steel DRI, ammonia SMR, part of glass) and exports 40 Mt CO2 to UK storage",
                "No e-fuel chain: electrolysis 149 -> 29 TWh, PEM 25 -> 8 GW, methanation 13 -> 0 GW, offshore wind 454 -> 249 TWh",
                "Heat moves to biomass from abroad (87 TWh) instead of heat pumps (80 -> 37 TWh)",
                "Nuclear 11.0 -> 8.4 GW",
                "Cost of assets in NL+BE falls; whole-model cost not comparable (6 vs 2 countries)"])], section="Summary")
            kpi_table(pdf, keys, "Same NL+BE data and pessimistic CCS - only the spatial scope differs (whole-model cost covers 6 vs 2 countries)")
        lb = SHORT[B]; SEC = "Results side by side"
        plot_slide(pdf, "Electricity generation", rf"{cmp}\C01_electricity_mix.png",
                   [f"Offshore wind 2050: {sup('IC1','electricity','wind offshore'):.0f} vs {sup(B,'electricity','wind offshore'):.0f} TWh",
                    "Most extra wind in IC1 feeds electrolysis for e-fuels"], section=SEC, cap=f"NL+BE electricity generation by technology; left IC1, right {lb}.")
        plot_slide(pdf, "Capacity: where investments shift", rf"{cmp}\C02_capacity_delta.png",
                   ["Largest shifts: PEM, methanation, heat technologies, nuclear"], section=SEC,
                   cap=f"Left: installed capacity 2050. Right: difference {lb} minus IC1 per milestone year.")
        plot_slide(pdf, "Capacity in NL+BE, 2050", fig_cap_bars(keys, f"cap_{B}"),
                   [f"PEM {fl('IC1','^PEM'):.0f} vs {fl(B,'^PEM'):.0f} GW", f"Methanation {fl('IC1','^methanation'):.0f} vs {fl(B,'^methanation'):.0f} GW",
                    f"Nuclear {fl('IC1','^nuclear'):.1f} vs {fl(B,'^nuclear'):.1f} GW"], section=SEC, imgw=.66, cap="Selected technologies, installed capacity in NL+BE in 2050.")
        plot_slide(pdf, "Hydrogen supply", rf"{cmp}\C06_hydrogen_supply.png",
                   [f"Electrolysis 2050: {sup('IC1','hydrogen','electrolysis'):.0f} vs {sup(B,'hydrogen','electrolysis'):.0f} TWh", "LH2 imports equal (42.5 TWh)"],
                   section=SEC, cap="Hydrogen supply in NL+BE by source.")
        plot_slide(pdf, "Energy carriers in 2050", fig_kpi_bars(keys, f"kpi_{B}"),
                   ["Electrolysis and wind scale together", "Gas use and heat mix show the biggest differences"], section=SEC, imgw=.7,
                   cap="NL+BE totals in 2050.")
        plot_slide(pdf, "Gas supply and transit", rf"{cmp}\C05_gas_supply_transit.png",
                   [f"Methane use 2050: {sup('IC1','methane'):.0f} vs {sup(B,'methane'):.0f} TWh"], section=SEC, cap="Methane supply to NL+BE and transit.")
        S3 = "Industry and CO2"
        wide_slide(pdf, "Industrial routes", rf"{cmp}\C03_industry_routes.png",
                   f"Route shares per sector. Each panel: left three bars IC1 (2030/40/50), right three bars {lb}.", section=S3)
        plot_slide(pdf, "Industry: the routes that change", fig_routes(keys, f"routes_{B}"),
                   (["Steel moves further to molten-oxide electrolysis", "Glass goes fully electric", "Ammonia unchanged (biomass gasification)"] if B == "CTRY"
                    else ["Steel 100% gas DRI + CCS (vs 57% MOE)", "Ammonia 100% gas SMR + CCS (vs 98% biomass)", "Glass partly gas + capture",
                          "Cement partly biomass oxy-fuel (BECCS)"]), section=S3, imgw=.66, cap="Share of sector output in NL+BE in 2050.")
        plot_slide(pdf, "CO2: storage, exports and net emissions", fig_co2(keys, f"co2_{B}"),
                   (["Storage cap of 10.5 Mt binding in both", "Different sites used (NLC6 vs NLC1/NLC5)", "Net zero in both"] if B == "CTRY"
                    else ["NL+BE storage cap binding (10.5 Mt)", f"{co2exp('MR'):.0f} Mt exported to UK storage", f"NL+BE net {netco2('MR'):.0f} Mt; the 6-country total is 0"]),
                   section=S3, imgw=.6, cap="NL+BE CO2 flows in 2050 (Mt).")
        plot_slide(pdf, "CO2 balance 2050", rf"{cmp}\C04_co2_balance_2050.png", ["Sources of captured CO2 and where it goes"], section=S3, cap="NL+BE CO2 balance in 2050.")
        plot_slide(pdf, "Costs of NL+BE assets", rf"{cmp}\C08_cost_breakdown_nlbe.png",
                   (["Savings in nuclear and PEM", "More spent on heat pumps", "Industry costs nearly identical"] if B == "CTRY"
                    else ["Nuclear, offshore wind and PEM roughly halve", "Industry costs nearly identical"]),
                   section=S3, cap="Investment and fixed O&M of assets located in NL+BE, summed over milestone years. Not the full objective.")
        if B == "CTRY":
            text_slide(pdf, "Conclusions", [
                ("What the resolution changes", ["Grid limits inside a country size the hydrogen chain: zonal runs need more electrolysis and methanation",
                                                 "Heat decarbonisation route (heat pumps vs gas) and nuclear siting", "~1.4% of system cost"]),
                ("What it does not change", ["Net zero reached by reusing CO2 instead of storing it", "Industrial routes and CO2 capture",
                                             "Wind, solar and LH2 totals"])],
                section="Conclusions", sub="Under pessimistic CCS, resolution matters for the size of the e-fuel chain, not for the industrial pathway")
        else:
            text_slide(pdf, "Conclusions", [
                ("What the neighbours change", ["Shared CO2 cap: NL+BE emissions offset elsewhere", "CO2 export to UK keeps gas+CCS industry viable",
                                                "No domestic e-fuel chain; half the offshore wind and nuclear", "Heat from imported biomass"]),
                ("Caveats", ["NL+BE net emissions are an accounting view; only the 6-country cap is binding",
                             "Neighbours at country resolution (no internal grid limits)", "3 representative days per year"])],
                section="Conclusions", sub="Under pessimistic CCS, spatial scope changes the industrial pathway itself")
    print("wrote", out, page[0], "pages")

def deck_combined(out):
    FOOT[0] = "Industrial Case Study (MOPO) - SpineOpt - pessimistic CCS - effect of spatial resolution and spatial scope"
    keys = ["IC1", "CTRY", "MR"]
    with PdfPages(out) as pdf:
        title_slide(pdf, "Pessimistic CCS in NL+BE:\nresolution or scope - what matters more?", "SpineOpt investment runs 2030 / 2040 / 2050  -  3 representative days per year  -  Gurobi",
                    "Baseline IC1 (17 zones)   |   Resolution change: 1 node per country   |   Scope change: + DE, DK, NO, UK")
        text_slide(pdf, "Three runs, one question", [
            ("The runs", ["!Baseline: NL+BE alone, 17 zones (IC1)", "!Resolution change: NL+BE alone, 1 node per country",
                          "!Scope change: NL+BE 17 zones + DE, DK, NO, UK as 1 node each, shared CO2 cap"]),
            ("Common to all", PESS + ["Same technology data, demand and 3 representative days"])],
            section="Introduction", sub="Each variant changes one dimension relative to the IC1 baseline")
        text_slide(pdf, "Main messages", [("", [
            "!Scope matters far more than resolution",
            "!Resolution change: same industrial pathway, smaller e-fuel chain (electrolysis 149 -> 94 TWh), more heat pumps, -1.4% cost",
            "!Scope change: different industrial pathway - gas-based industry with CCS, CO2 exported to UK, no methanation, half the offshore wind",
            "Under pessimistic CCS, NL+BE alone must reuse captured CO2 (e-fuels) to reach net zero; with neighbours it can export CO2 and emissions",
            "Heat: heat pumps when alone; imported biomass when connected",
            "Results for NL+BE alone are robust to resolution but not to the system boundary"])], section="Summary")
        kpi_table(pdf, keys, "NL+BE indicators in 2050 for the baseline and both variants")
        SEC = "Narrative"
        plot_slide(pdf, "Energy carriers: resolution vs scope", fig_kpi_bars(keys, "kpi_all"),
                   ["Resolution: smaller H2 chain, more heat pumps, less gas", "Scope: much more gas and bio heat, much less wind and H2"],
                   section=SEC, imgw=.7, cap="NL+BE totals in 2050.")
        plot_slide(pdf, "Capacity: resolution vs scope", fig_cap_bars(keys, "cap_all"),
                   ["PEM and methanation shrink in both, most with neighbours", "Bio-boilers only appear with neighbours", "Nuclear lowest at country level"],
                   section=SEC, imgw=.66, cap="Installed capacity in NL+BE in 2050 (GW).")
        plot_slide(pdf, "Industry: only scope changes the routes", fig_routes(keys, "routes_all"),
                   ["Resolution: small shifts (steel MOE 57 -> 64%)", "Scope: steel and ammonia go fully gas + CCS; glass partly gas + capture"],
                   section=SEC, imgw=.66, cap="Share of sector output in NL+BE in 2050.")
        plot_slide(pdf, "CO2: where does it go?", fig_co2(keys, "co2_all"),
                   ["Baseline and resolution: 10.5 Mt stored, net zero", f"Scope: 10.5 Mt stored + {co2exp('MR'):.0f} Mt exported; NL+BE net {netco2('MR'):.0f} Mt"],
                   section=SEC, imgw=.6, cap="NL+BE CO2 in 2050 (Mt). With neighbours the CO2 cap is shared by 6 countries.")
        fig = frame("Cost of NL+BE assets", "Investment + fixed O&M of assets located in NL+BE, summed over milestone years", SEC)
        for i, (k, p) in enumerate([("CTRY", CMP["CTRY"]), ("MR", CMP["MR"])]):
            fig.text(.03 + .48 * i + .235, .82, f"IC1 vs {SHORT[k]}", ha="center", fontsize=13, fontweight="bold", color=NAVY)
            img(fig, rf"{p}\C08_cost_breakdown_nlbe.png", [.02 + .48 * i, .15, .47, .65])
        caption(fig, "Whole-model objective: IC1 3.829 M, Country-level 3.777 M (-1.4%), Mixed resolution 7.623 M (covers 6 countries; not comparable)."); pdf.savefig(fig); plt.close(fig)
        text_slide(pdf, "Conclusions", [
            ("Spatial resolution", ["Changes the size of the H2/e-fuel chain and the heat route", "Industrial pathway and CO2 balance unchanged", "~1% of cost"]),
            ("Spatial scope", ["Changes the industrial pathway itself", "CO2 export and a shared cap replace domestic CO2 reuse",
                               "Imported biomass replaces heat pumps", "Caveat: NL+BE net emissions are an accounting view"])],
            section="Conclusions", sub="For NL+BE under pessimistic CCS, modelling the neighbours matters more than modelling the zones")
    print("wrote", out, page[0], "pages")

if __name__ == "__main__":
    mode, out = sys.argv[1:3]
    if mode == "combined": deck_combined(out)
    else: deck_pair({"ctry": "CTRY", "mr": "MR"}[mode], out)
