import pickle
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
R = {"NL+BE alone": "nb_ccslow_ccu_cap16_dac0", "With neighbours": "mr_ccslow_ccu_cap16_dac0"}
CN = ["NL", "BE"]
SL = {"refinery (SMR+CC, internal H2)": "Refinery hydrogen", "chemicals / e-fuels": "Steam crackers (plastics)", "plastics": "Plastics (gas-based)",
      "bioenergy (BECCS)": "Biogas upgrading", "cement": "Cement", "steel": "Steel", "ammonia": "Ammonia", "glass": "Glass"}
SC = {"Refinery hydrogen": "#264653", "Steam crackers (plastics)": "#2a9d8f", "Plastics (gas-based)": "#8ab17d", "Biogas upgrading": "#6a994e",
      "Cement": "#e9c46a", "Steel": "#f4a261", "Ammonia": "#e76f51", "Glass": "#adb5bd"}
DC = {"Stored in NL (North Sea)": "#1d3557", "Reused in methanol for plastics": "#9d4edd", "Exported to UK for storage": "#457b9d"}
fig, axes = plt.subplots(1, 2, figsize=(12, 6.5), sharey=True)
for ax, (t, run) in zip(axes, R.items()):
    D = pickle.load(open(rf"run_logs\{run}_NLBE.pkl", "rb")); F = pickle.load(open(rf"run_logs\{run}.pkl", "rb"))
    c = D["co2net"].query("year==2050")
    src = (c[c.role == "captured"].groupby(c.source.map(lambda s: SL.get(s, s))).co2.sum() / 1e3).sort_values(ascending=False)
    small = src[src < 1.5]; src = src[src >= 1.5]
    if small.sum() > 0: src["Other (glass, steel, ...)" if t == "NL+BE alone" else "Other"] = small.sum()
    st = D["co2store"].query("year==2050").co2.sum() / 1e3
    re_ = c[(c.role == "used / injected") & ~c.tech.str.startswith("CO2-injection")].co2.sum() / 1e3
    p = F["co2pipe"].query("year==2050"); nb = lambda z: z.str[:2].isin(CN)
    ex = (p[nb(p.origin) & ~nb(p.dest)].co2.sum() - p[~nb(p.origin) & nb(p.dest)].co2.sum()) / 1e3
    dst = {k: v for k, v in zip(DC, [st, re_, ex]) if v > .1}
    print(t, src.round(1).to_dict(), {k: round(v, 1) for k, v in dst.items()}, "src", round(src.sum(), 1), "dst", round(sum(dst.values()), 1))
    W, XL, XR = .32, 0, 1.6; tot = src.sum()
    b = 0
    for k, v in src.items():
        col = SC.get(k, "#ced4da")
        ax.bar(XL, v, W, bottom=b, color=col, edgecolor="white", lw=1)
        ax.text(XL - W / 2 - .05, b + v / 2, f"{k}  {v:.0f}" if v >= 1 else f"{k}  {v:.1f}", ha="right", va="center", fontsize=9.5)
        b += v
    b = 0; bl = 0
    for k, v in dst.items():
        ax.bar(XR, v, W, bottom=b, color=DC[k], edgecolor="white", lw=1)
        ax.text(XR + W / 2 + .05, b + v / 2, f"{k}\n{v:.0f} Mt", ha="left", va="center", fontsize=9.5, color=DC[k], fontweight="bold")
        ax.add_patch(Polygon([(XL + W / 2, bl), (XR - W / 2, b), (XR - W / 2, b + v), (XL + W / 2, bl + v)], color=DC[k], alpha=.18, lw=0))
        b += v; bl += v
    ax.text(XL, tot + 1.2, f"Captured\n{tot:.0f} Mt", ha="center", va="bottom", fontsize=11, fontweight="bold")
    ax.set_title(t, fontsize=13, fontweight="bold", pad=34); ax.set_xlim(-1.9, 3.3); ax.axis("off")
fig.suptitle("Where CO2 is captured and where it goes (NL+BE, 2050)", fontsize=14, fontweight="bold")
fig.tight_layout(); out = r"final_runs_pessimistic_ccs\CO2_capture_to_destination_2050.png"; fig.savefig(out, dpi=200); print(out)
