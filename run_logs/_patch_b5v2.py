import io
p="tools/make_report_figs.py"; s=io.open(p,encoding="utf-8").read()
fn='''
def industry_v2(K, yr, name, ncol=3):
    """Original B5 layout (sectors as rows, one panel per run) wrapped into rows of ncol panels."""
    import matplotlib.pyplot as plt, pandas as pd, os, math
    F = R.F; SECS = R.SECS; rows = []; nr = math.ceil(len(K) / ncol)
    fig, axes = plt.subplots(nr, ncol, figsize=(3.6 * ncol + 1.5, (0.6 + .32 * len(SECS)) * nr + .8), sharey=True, squeeze=False)
    for i, ax in enumerate(axes.flat):
        if i >= len(K): ax.axis("off"); continue
        k = K[i]; p = R.D[k]["prod"]; p = p.assign(cat=p.apply(F.dcat, axis=1)); ticks = []
        for y, sec in enumerate(SECS):
            q = p[(p.sector == sec) & (p.year == yr)]; t = q.output.sum()
            sh = q.groupby("cat").output.sum() / t * 100 if t > 0 else pd.Series(dtype=float); left = 0
            for l, c in F.DCAT:
                v = sh.get(l, 0); ax.barh(-y, v, .85, left=left, color=c, edgecolor="white", lw=.3); left += v
                rows.append(dict(run=k, sector=sec, year=yr, route_type=l, share_pct=v, output_kt=t * v / 100))
            if t <= 0: ax.text(1, -y, "no production in NL+BE", va="center", fontsize=6.5, color="#888")
            ticks.append((-y, sec))
        ax.set_yticks([t[0] for t in ticks], [t[1] for t in ticks], fontsize=7.5); ax.tick_params(axis="y", labelleft=(i % ncol == 0))
        ax.set_xlim(0, 100); ax.set_xlabel("% of NL+BE production", fontsize=8)
        ax.set_title(R.SH[k], fontsize=11, fontweight="bold"); [ax.spines[sp].set_visible(False) for sp in ("top", "right")]
    h = [plt.Rectangle((0, 0), 1, 1, color=c) for _, c in F.DCAT]; L = [l for l, _ in F.DCAT]
    if len(K) < nr * ncol:
        axes.flat[len(K)].legend(h, L, loc="center", frameon=False, fontsize=9)
        fig.tight_layout()
    else:
        fig.legend(h, L, loc="lower center", ncol=3, frameon=False, fontsize=9); fig.tight_layout(rect=(0, .06, 1, 1))
    pd.DataFrame(rows).to_csv(os.path.join(R.DAT, name + ".csv"), index=False)
    return R.sv(fig, name)
'''
s=s.replace('\nif __name__ == "__main__":', fn+'\nif __name__ == "__main__":',1)
s=s.replace('    industry_vertical(SETS["B"][0], 2050, "B5_industry_routes_vertical")','    industry_vertical(SETS["B"][0], 2050, "B5_industry_routes_vertical")\n    industry_v2(SETS["B"][0], 2050, "B5_industry_routes_vertical_v2")',1)
io.open(p,"w",encoding="utf-8",newline="\n").write(s)
