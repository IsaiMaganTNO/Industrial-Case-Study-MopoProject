import io
p="tools/make_report_figs.py"; s=io.open(p,encoding="utf-8").read()
fn='''
def industry_vertical(K, yr, name):
    """One small panel per sector (stacked vertically), one horizontal bar per run."""
    import matplotlib.pyplot as plt, pandas as pd, os
    F = R.F; SECS = R.SECS; rows = []
    fig, axes = plt.subplots(len(SECS), 1, figsize=(16/2.54, (0.42*len(K)+0.45)*len(SECS)/2.54*2.2), sharex=True)
    for ax, sec in zip(axes, SECS):
        for j, k in enumerate(K):
            p = R.D[k]["prod"]; p = p.assign(cat=p.apply(F.dcat, axis=1))
            q = p[(p.sector == sec) & (p.year == yr)]; t = q.output.sum()
            sh = q.groupby("cat").output.sum() / t * 100 if t > 0 else pd.Series(dtype=float); left = 0
            for l, c in F.DCAT:
                v = sh.get(l, 0); ax.barh(-j, v, .8, left=left, color=c, edgecolor="white", lw=.3); left += v
                rows.append(dict(run=k, sector=sec, year=yr, route_type=l, share_pct=v, output_kt=t * v / 100))
            if t <= 0: ax.text(1, -j, "no production in NL+BE", va="center", fontsize=6.5, color="#888")
        ax.set_yticks([-j for j in range(len(K))], [R.SH[k] for k in K], fontsize=7)
        ax.set_xlim(0, 100); ax.set_ylim(-len(K) + .45, .55)
        ax.set_title(sec[0].upper() + sec[1:], fontsize=8.5, fontweight="bold", loc="left", pad=2)
        for sp in ("top", "right"): ax.spines[sp].set_visible(False)
        ax.tick_params(axis="x", labelsize=7)
    axes[-1].set_xlabel("% of NL+BE production", fontsize=8)
    fig.legend([plt.Rectangle((0, 0), 1, 1, color=c) for _, c in F.DCAT], [l for l, _ in F.DCAT],
               loc="lower center", ncol=2, frameon=False, fontsize=7.5)
    fig.tight_layout(rect=(0, .045, 1, 1), h_pad=.6)
    pd.DataFrame(rows).to_csv(os.path.join(R.DAT, name + ".csv"), index=False)
    return R.sv(fig, name)
'''
s=s.replace('\nif __name__ == "__main__":', fn+'\nif __name__ == "__main__":',1)
s=s.replace('        stackfig(K, yrs, it_h2use, "Hydrogen consumption (TWh/yr)", f"{g}4_hydrogen_consumption_vertical", vertical=True)',
 '        stackfig(K, yrs, it_h2use, "Hydrogen consumption (TWh/yr)", f"{g}4_hydrogen_consumption_vertical", vertical=True)\n    industry_vertical(SETS["B"][0], 2050, "B5_industry_routes_vertical")',1)
io.open(p,"w",encoding="utf-8",newline="\n").write(s)
