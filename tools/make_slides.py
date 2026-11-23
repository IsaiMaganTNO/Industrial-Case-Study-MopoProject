r"""Slide deck (PDF, 16:9) comparing 3day_nb_v2 and 3day_mr_fix.
Usage: python tools/make_slides.py <out.pdf>"""
import os, sys, pickle, textwrap
import numpy as np, pandas as pd
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.image as mpimg
NAVY, ACC, GREY = "#1d3557", "#e76f51", "#5c6770"
MR = r"runs\3day_mr_fix\plots"; NB = MR + r"\summary_named_standalone"; IC = MR + r"\summary_named_interconnected"; CMP = MR + r"\compare_named"
TMP = r"run_logs\_slide_tmp"; os.makedirs(TMP, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans", "savefig.dpi": 300, "image.resample": True})
W, H = 13.333, 7.5
page = [0]

def frame(title, subtitle=None, section=None):
    fig = plt.figure(figsize=(W, H)); page[0] += 1
    fig.patches.append(plt.Rectangle((0, .9), 1, .1, transform=fig.transFigure, color=NAVY))
    fig.patches.append(plt.Rectangle((0, .895), 1, .005, transform=fig.transFigure, color=ACC))
    fig.text(.035, .945, title, color="white", fontsize=22, fontweight="bold", va="center")
    if section: fig.text(.965, .945, section, color="#a8dadc", fontsize=11, va="center", ha="right")
    if subtitle: fig.text(.035, .86, subtitle, color=GREY, fontsize=12.5, style="italic", va="center")
    fig.text(.965, .02, f"{page[0]}", color=GREY, fontsize=9, ha="right")
    fig.text(.035, .02, "Industrial Case Study (MOPO) - SpineOpt investment runs - Standalone vs Interconnected", color="#9aa3ad", fontsize=8)
    return fig

def img(fig, path, rect):
    ax = fig.add_axes(rect); ax.imshow(mpimg.imread(path), interpolation="lanczos"); ax.axis("off")
    # keep aspect, centred
    return ax

def bullets(fig, items, x, y, w=40, fs=12.5, gap=.012):
    for it in items:
        bold = it.startswith("!"); it = it.lstrip("!")
        txt = textwrap.fill(it, w)
        n = txt.count("\n") + 1
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

def two_slide(pdf, title, p1, p2, l1, l2, cap, sub=None, section=None):
    fig = frame(title, sub, section)
    for p, l, x in [(p1, l1, .02), (p2, l2, .51)]:
        fig.text(x + .235, .825, l, ha="center", fontsize=13, fontweight="bold", color=NAVY)
        img(fig, p, [x, .15, .47, .66])
    caption(fig, cap); pdf.savefig(fig); plt.close(fig)

# ---------- extra figures from caches ----------
M = pickle.load(open(r"run_logs\mr_fix.pkl", "rb"))
def cty(df):
    r = df.region.astype(str).str.extract(r"^([A-Z]{2})")[0]
    off = df.tech.astype(str).str.extract(r"_(?:NS|AS|AT|BS)([A-Z]{2})")[0]
    return r.where(df.region.notna(), off)
def fig_country_emis():
    e = M["emis"].copy(); e["c"] = cty(e)
    p = e.groupby(["c", "year"]).co2.sum().unstack()[[2030, 2040, 2050]].reindex(["NL", "BE", "DE", "DK", "NO", "UK"]) / 1e3
    fig, ax = plt.subplots(figsize=(10, 5.4)); x = np.arange(6); w = .26
    for j, (y, c) in enumerate(zip([2030, 2040, 2050], ["#a8dadc", "#457b9d", NAVY])):
        ax.bar(x + (j - 1) * w, p[y], w, color=c, label=str(y))
        for i, v in enumerate(p[y]): ax.text(i + (j - 1) * w, v + (4 if v >= 0 else -12), f"{v:.0f}", ha="center", fontsize=8.5)
    ax.axhline(0, color="#333", lw=.8); ax.set_xticks(x, p.index, fontsize=12); ax.set_ylabel("Net CO2 (Mt/yr)")
    tot = p.sum(); ax.set_title(f"Net CO2 per country - system total {tot[2030]:.0f} / {tot[2040]:.0f} / {tot[2050]:.0f} Mt", fontweight="bold")
    for s in ["top", "right"]: ax.spines[s].set_visible(False)
    ax.legend(frameon=False); ax.grid(axis="y", color="#e3e7ec"); ax.set_axisbelow(True)
    f = os.path.join(TMP, "country_emis.png"); fig.savefig(f, dpi=200, bbox_inches="tight"); plt.close(fig); return f
def fig_storage_sites():
    s = M["co2store"]; s = s[s.year == 2050].groupby("reservoir").co2.sum().sort_values() / 1e3
    s.index = [i.replace("CO2-storage-", "") for i in s.index]
    c = [{"NL": "#e76f51", "DK": "#2a9d8f", "DE": "#f2b134", "NO": "#457b9d", "UK": NAVY}.get(next((k for k in ["NL", "DK", "DE", "NO", "UK"] if k in i), ""), "#999") for i in s.index]
    fig, ax = plt.subplots(figsize=(10, 6)); ax.barh(s.index, s.values, color=c)
    for i, v in enumerate(s.values): ax.text(v + .5, i, f"{v:.1f}", va="center", fontsize=9)
    ax.set_xlabel("CO2 injected 2050 (Mt/yr)"); ax.set_title(f"CO2 storage by site, 2050 - total {s.sum():.0f} Mt/yr", fontweight="bold")
    for s_ in ["top", "right"]: ax.spines[s_].set_visible(False)
    h = [plt.Rectangle((0, 0), 1, 1, color=v) for v in ["#e76f51", "#2a9d8f", "#f2b134", "#457b9d", NAVY]]
    ax.legend(h, ["NL", "DK", "DE", "NO", "UK"], frameon=False, loc="lower right")
    f = os.path.join(TMP, "storage_sites.png"); fig.savefig(f, dpi=200, bbox_inches="tight"); plt.close(fig); return f
def fig_kpi_table(pdf):
    rows = [("Electricity generation (TWh)", "502", "437"), ("Offshore wind (GW)", "61", "34"), ("Nuclear (GW)", "9.1", "0"),
            ("Electrolysers PEM (GW)", "12.0", "2.8"), ("SMR hydrogen (GW)", "108", "77"), ("Gas boilers (GW)", "17.6", "33.3"),
            ("CO2 captured (Mt)", "34", "216"), ("CO2 stored in NL (Mt)", "27.2", "27.2"),
            ("CO2 exported (Mt)", "0", "185"), ("Net CO2 of NL+BE (Mt)", "0", "+106")]
    fig = frame("Key numbers: NL+BE in 2050", "Same NL+BE data in both runs - only the system boundary differs", "Comparison")
    ax = fig.add_axes([.06, .1, .88, .72]); ax.axis("off")
    hdr = ["Indicator (NL+BE, 2050)", "Standalone\nNL+BE alone", "Interconnected\n6 countries"]
    t = ax.table(cellText=[list(r) for r in rows], colLabels=hdr, loc="upper center", cellLoc="center", colWidths=[.5, .22, .22])
    t.auto_set_font_size(False); t.set_fontsize(13); t.scale(1, 2.05)
    for (r, c), cell in t.get_celld().items():
        cell.set_edgecolor("#dde3ea")
        if r == 0: cell.set_facecolor(NAVY); cell.get_text().set_color("white"); cell.get_text().set_fontweight("bold")
        elif r % 2: cell.set_facecolor("#f6f8fb")
        if c == 0 and r > 0: cell.get_text().set_ha("left"); cell._loc = "left"
        if c == 2 and r > 0: cell.get_text().set_fontweight("bold"); cell.get_text().set_color(NAVY)
    pdf.savefig(fig); plt.close(fig)

def text_slide(pdf, title, blocks, section=None, sub=None):
    fig = frame(title, sub, section)
    xs = [.05, .52] if len(blocks) > 1 else [.05]
    for x, (head, items) in zip(xs, blocks):
        fig.text(x, .8, head, fontsize=16, fontweight="bold", color=ACC)
        bullets(fig, items, x, .74, w=48 if len(blocks) > 1 else 95, fs=13.5, gap=.02)
    pdf.savefig(fig); plt.close(fig)

def main(out):
    ce, ss = fig_country_emis(), fig_storage_sites()
    with PdfPages(out) as pdf:
        # title
        fig = plt.figure(figsize=(W, H)); page[0] += 1
        fig.patches.append(plt.Rectangle((0, 0), 1, 1, transform=fig.transFigure, color=NAVY))
        fig.patches.append(plt.Rectangle((.06, .43), .2, .008, transform=fig.transFigure, color=ACC))
        fig.text(.06, .62, "Decarbonising NL+BE industry:\nwhat changes when neighbours join?", color="white", fontsize=32, fontweight="bold", va="center", linespacing=1.25)
        fig.text(.06, .36, "SpineOpt investment runs 2030 / 2040 / 2050  -  3 representative days per year  -  Gurobi", color="#a8dadc", fontsize=14)
        fig.text(.06, .3, "Standalone: NL+BE in 17 zones     vs     Interconnected: NL+BE + DE, DK, NO, UK", color="white", fontsize=13)
        fig.text(.06, .1, "MOPO Industrial Case Study  |  October 2026", color="#9aa3ad", fontsize=11)
        pdf.savefig(fig); plt.close(fig)

        text_slide(pdf, "Set-up of the two runs", [
            ("Standalone - NL+BE alone", ["NL (9) and BE (8) zones; neighbouring countries as fixed boundary conditions",
                                    "Own CO2 cap: net zero in 2050 for NL+BE alone",
                                    "Only NL storage sites available (NSNL012 21 Mt, NSNL031 6.2 Mt)",
                                    "Solved to optimality"]),
            ("Interconnected - 6 countries", ["Same NL+BE data, plus DE, DK, NO, UK (one node each), fully optimised",
                                           "ONE shared CO2 budget for 6 countries (net zero in 2050 in total)",
                                           "16 storage sites (UK, NO, DK, DE, NL); CO2 pipelines between countries",
                                           "Solved to optimality"])],
            section="Introduction", sub="Identical assumptions for NL+BE in both runs - only the system boundary differs")

        text_slide(pdf, "Main messages", [("", [
            "!Industry fully decarbonises by 2050 in both runs and in all six countries - but via different routes",
            "!Alone, NL+BE must go net-zero domestically: more offshore wind (61 GW), nuclear (9 GW), electrolysis (12 GW), bio-ammonia and molten-oxide steel",
            "!Together, cheap CCS dominates: NL+BE keep gas-based routes with capture and export 185 Mt CO2/yr to UK, NO and DK storage",
            "NL+BE are no longer net zero themselves (+106 Mt in 2050); the system as a whole is - other countries' storage compensates",
            "CO2 storage availability abroad is the key lever for the outcome"])],
            section="Summary")

        fig_kpi_table(pdf)

        # ---- baseline nb_v2
        plot_slide(pdf, "Standalone: electricity grows to 500 TWh", rf"{NB}\01_electricity_generation.png",
                   ["Demand roughly doubles from 2030 to 2050 (electrification of heat and industry)", "Offshore wind becomes the backbone", "Nuclear 9 GW in 2050 (BE 6, NL 3)"],
                   section="Run 1: Standalone", cap="Annual electricity generation in NL+BE by technology; totals above the bars.")
        plot_slide(pdf, "Standalone: industry routes", rf"{NB}\05_industry_routes.png",
                   ["Ammonia 80% via biomass gasification", "Primary steel: molten-oxide electrolysis 57% / gas DRI + CCS 43%", "Cement and olefins 100% with capture from 2040"],
                   section="Run 1: Standalone", imgw=.68, cap="Share of production per sector and route. Grey = unabated, blue = CCS, yellow = electric, green = bio.")
        plot_slide(pdf, "Standalone: CO2 balance reaches net zero", rf"{NB}\07_co2_balance.png",
                   ["Emissions 165 -> 37 -> 0 Mt", "Both NL storage sites full from 2040 (27.2 Mt/yr)", "Limited storage forces non-CCS routes"],
                   section="Run 1: Standalone", cap="Gross emissions by source (positive) and geological storage (negative); red diamond = net NL+BE emissions.")

        # ---- mr_fix system
        plot_slide(pdf, "Interconnected: six countries share one CO2 budget", ce,
                   ["System total meets the budget: 795 -> 255 -> 0 Mt", "UK and DK become net negative (storage hosts)", "NL+BE and NO remain net emitters", "No direct air capture needed"],
                   section="Run 2: Interconnected", cap="Net CO2 per country (emissions minus geological storage).")
        plot_slide(pdf, "Interconnected: CO2 storage is used everywhere", ss,
                   ["356 Mt/yr injected in 2050 across 16 sites", "Danish onshore site at its 25.5 Mt/yr cap", "Storage is used in all five countries"],
                   section="Run 2: Interconnected", cap="CO2 injected per storage site in 2050, coloured by host country.")
        plot_slide(pdf, "Interconnected: industry routes, all six countries", rf"{IC}\05_industry_routes.png",
                   ["No unabated reference routes remain in 2050", "Gas-based routes with capture everywhere: ammonia, steel (DRI-EAF), olefins, cement"],
                   section="Run 2: Interconnected", imgw=.68, cap="Share of production per sector and route, summed over the six countries.")
        fig = frame("Interconnected: cross-border flows in 2050", "Net flows between countries; arrow width proportional to volume", "Run 2: Interconnected")
        img(fig, rf"{CMP}\C07_flow_map_2050_mr_fix.png", [.02, .16, .96, .66])
        caption(fig, "CO2 flows from NL+BE to UK, NO and DK storage; gas flows from Norway and through NL+BE to Germany.")
        pdf.savefig(fig); plt.close(fig)

        # ---- comparison
        S = "What changes for NL+BE"
        plot_slide(pdf, "Electricity: less generation, no nuclear", rf"{CMP}\C01_electricity_mix.png",
                   ["2050: 437 vs 502 TWh", "Offshore wind 34 vs 61 GW", "No nuclear in BE and NL by 2050", "Less electrification: capture replaces it"],
                   section=S, cap="NL+BE electricity generation by technology; left Standalone, right Interconnected.")
        plot_slide(pdf, "Capacity: where the investments shift", rf"{CMP}\C02_capacity_delta.png",
                   ["Fewer offshore wind farms, PEM and nuclear", "More gas boilers kept", "SMR stays the main hydrogen source"],
                   section=S, cap="Left: installed capacity in 2050. Right: difference Interconnected minus Standalone per milestone year (negative = less in Interconnected).")
        fig = frame("Industry: from bio and electric to gas + CCS", "Ammonia: biomass -> gas + CCS  |  Steel: molten oxide -> gas DRI + CCS  |  Access to storage abroad makes capture the least-cost option", S)
        img(fig, rf"{CMP}\C03_industry_routes.png", [.01, .14, .98, .7])
        caption(fig, "Route shares per sector. Each panel: left three bars Standalone (2030/40/50), right three bars Interconnected.")
        pdf.savefig(fig); plt.close(fig)
        plot_slide(pdf, "Hydrogen: electrolysis largely disappears", rf"{CMP}\C06_hydrogen_supply.png",
                   ["PEM 64 -> 9 TWh in 2050", "Liquid H2 imports similar", "SMR with capture remains the workhorse"],
                   section=S, cap="Hydrogen supply in NL+BE by source.")
        plot_slide(pdf, "Nuclear and biomass", rf"{CMP}\C10_nuclear_biomass.png",
                   ["No nuclear in NL+BE by 2050 (Standalone: 9 GW)", "Biomass use 2050: BE 158 vs 4 TWh, NL 51 vs 40 TWh", "Belgium uses far more biomass in 2050"],
                   section=S, cap="Left: nuclear capacity per country. Right: biomass consumed per country.")
        plot_slide(pdf, "Costs of NL+BE assets", rf"{CMP}\C08_cost_breakdown_nlbe.png",
                   ["Industry dominates both runs", "Savings on nuclear, offshore wind and PEM", "Extra spending on CCS-related assets"],
                   section=S, cap="Investment (solid) and fixed O&M (light) of assets located in NL+BE, summed over the milestone years. Not the full objective.")

    print("wrote", out, page[0], "pages")

if __name__ == "__main__":
    main(sys.argv[1])



