import re
s = open(r"run_logs\_co2map_clean.py", encoding="utf8").read()
# collect plotted points per panel
s = s.replace('    g.plot(ax=ax, color="#f1f3f5"', '    pts = []\n    g.plot(ax=ax, color="#f1f3f5"')
s = s.replace('            ax.scatter(*p, s=v * 30,', '            pts.append(p); ax.scatter(*p, s=v * 30,')
s = s.replace('        if v < .5 or po is None or pd_ is None or po == pd_: continue\n', '        if v < .5 or po is None or pd_ is None or po == pd_: continue\n        pts += [po, pd_]\n')
s = s.replace('            ax.scatter(*oc[sid], s=60,', '            pts.append(oc[sid]); ax.scatter(*oc[sid], s=60,')
# remove fixed limits
s = s.replace('\n        ax.set_xlim(2.3, 7.4); ax.set_ylim(49.4, 54.6)', '')
s = s.replace('\n        ax.set_xlim(-6, 15); ax.set_ylim(49.3, 62.5)', '')
# tight limits + box below map
s = s.replace('    ax.text(.02, .02, bal, transform=ax.transAxes, fontsize=9.5, va="bottom",',
 '''    xs, ys = zip(*pts); pad = .6
    x0, x1, y0, y1 = min(xs) - pad, max(xs) + pad + .6, min(ys) - pad, max(ys) + pad
    ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect(1 / np.cos(np.radians((y0 + y1) / 2)))
    ax.text(.5, -.02, bal.replace("\\n  ", "  |  ").replace("\\n", "  |  ", 1).replace("\\n", "\\n"), transform=ax.transAxes, fontsize=9.5, va="top", ha="center",''')
s = s.replace('fig.tight_layout(rect=(0, .05, 1, 1))', 'fig.tight_layout(rect=(0, .07, 1, 1))')
open(r"run_logs\_co2map_clean.py", "w", encoding="utf8").write(s)
print(s.count("pts"), "set_xlim(2.3" in s)
