"""Group 1 retirement run -- comparison figures."""
import csv, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

T = r"reports_3day_group1\tables"
F = r"reports_3day_group1\figures"
YRS = ["2030", "2041", "2050"]

def load(fn):
    with open(os.path.join(T, fn), encoding="utf-8") as f:
        return list(csv.DictReader(f))

# --- Fig 1: patched techs retiring + replacements
fleet = load("fleet_by_tech_base_vs_group1.csv")
RET = ["BF-BOF", "(NG)PE", "(NG)PEA"]
REP = ["(NG)DRI-EAF-MEA", "(H2)PE", "(NG)PE-MEA", "(H2)PEA", "(NG)PEA-MEA", "(EL)PEA"]
d = {r["tech"]: r for r in fleet}
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
x = np.arange(len(YRS))
for t in RET:
    if t in d:
        ax[0].plot(x, [float(d[t][f"{y}_group1"]) for y in YRS], "o-", label=t, lw=2)
        ax[0].plot(x, [float(d[t][f"{y}_base"]) for y in YRS], "o--", alpha=.35, color=ax[0].lines[-1].get_color())
ax[0].set_title("Retiring fleet (solid=Group 1, dashed=baseline)")
for t in REP:
    if t in d:
        ax[1].plot(x, [float(d[t][f"{y}_group1"]) for y in YRS], "o-", label=t, lw=2)
ax[1].set_title("Replacement fleet (Group 1)")
for a in ax:
    a.set_xticks(x); a.set_xticklabels(YRS); a.set_ylabel("units_invested_available")
    a.legend(fontsize=7); a.grid(alpha=.3)
fig.suptitle("Group 1 forced retirement: 26 units (BF-BOF, (NG)PE, (NG)PEA)")
fig.tight_layout(); fig.savefig(os.path.join(F, "fig1_fleet_retirement.png"), dpi=150); plt.close(fig)

# --- Fig 2: objective components
obj = load("objective_components.csv")
obj = [r for r in obj if abs(float(r["delta"])) > 1 and r["component"] != "total_costs"]
fig, ax = plt.subplots(figsize=(9, 4.5))
names = [r["component"].replace("objective_", "") for r in obj]
vals = [float(r["delta"]) for r in obj]
cols = ["#c0392b" if v > 0 else "#27ae60" for v in vals]
ax.barh(names, vals, color=cols)
ax.axvline(0, color="k", lw=.8)
ax.set_xlabel("cost delta (Group 1 - baseline)")
ax.set_title("Cost impact: +810,628 total (penalties = 0.00)")
ax.grid(alpha=.3, axis="x"); fig.tight_layout()
fig.savefig(os.path.join(F, "fig2_cost_components.png"), dpi=150); plt.close(fig)

# --- Fig 3: CO2 balance
co2 = load("co2_balance.csv")
fig, ax = plt.subplots(figsize=(9, 4.5))
w = 0.35
for i, (pre, lbl, c) in enumerate([("base", "baseline", "#7f8c8d"), ("group1", "Group 1", "#2980b9")]):
    ax.bar(x + (i - .5) * w, [float(r[f"{pre}_gross"]) for r in co2], w, label=f"{lbl} gross", color=c)
    ax.bar(x + (i - .5) * w, [-float(r[f"{pre}_captured"]) for r in co2], w, label=f"{lbl} captured", color=c, alpha=.45)
ax.axhline(0, color="k", lw=.8)
ax.set_xticks(x); ax.set_xticklabels(YRS); ax.set_ylabel("CO2 (model units)")
ax.set_title("CO2: net is identical (cap binds in both); Group 1 handles 45% less carbon in 2050")
ax.legend(fontsize=8); ax.grid(alpha=.3, axis="y")
fig.tight_layout(); fig.savefig(os.path.join(F, "fig3_co2_balance.png"), dpi=150); plt.close(fig)

# --- Fig 4: carrier shifts 2050
car = load("carrier_flows.csv")
WATCH = ["coal", "fossil-CH4", "CH4", "bio", "elec", "crude"]
sel = [r for r in car if r["carrier"] in WATCH and r["direction"] == "from_node"]
fig, ax = plt.subplots(figsize=(9, 4.5))
names = [r["carrier"] for r in sel]
base = [float(r["2050_base"]) for r in sel]
g1 = [float(r["2050_group1"]) for r in sel]
pct = [(b and (gg - b) / b * 100) for b, gg in zip(base, g1)]
ax.barh(names, pct, color=["#c0392b" if p > 0 else "#27ae60" for p in pct])
ax.axvline(0, color="k", lw=.8)
ax.set_xlabel("% change in 2050 consumption (Group 1 vs baseline)")
ax.set_title("Energy carrier shift: coal -91%, electricity +21%")
ax.grid(alpha=.3, axis="x"); fig.tight_layout()
fig.savefig(os.path.join(F, "fig4_carrier_shift.png"), dpi=150); plt.close(fig)

# --- Fig 5: steel handover
steel = load("steel_production.csv")
fig, ax = plt.subplots(1, 2, figsize=(12, 4.5))
for i, node in enumerate(["steel-primary_NLC5", "steel-primary_BEC4"]):
    sel = [r for r in steel if r["node"] == node and r["run"] == "group1"]
    bot = np.zeros(len(YRS))
    for r in sel:
        v = np.array([float(r[y]) for y in YRS])
        if v.sum() <= 0: continue
        ax[i].bar(x, v, .5, bottom=bot, label=r["unit"])
        bot += v
    ax[i].set_xticks(x); ax[i].set_xticklabels(YRS)
    ax[i].set_title(node); ax[i].legend(fontsize=7); ax[i].grid(alpha=.3, axis="y")
    ax[i].set_ylabel("production")
fig.suptitle("Steel: demand fully met throughout as BF-BOF retires")
fig.tight_layout(); fig.savefig(os.path.join(F, "fig5_steel_handover.png"), dpi=150); plt.close(fig)
print("figures written to", F)
