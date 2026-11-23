import re
s=open("tools/make_deck_final3.py",encoding="utf8").read()
old_st=s[s.index('        st = F[k]["co2store"]; st = st[st.year == 2050].groupby(["reservoir", "region"])'):s.index('        if k == "MR": ax.set_xlim')]
new_st='''        for r, v in c.items():
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
        for reg, v in (st0.groupby("region").co2.sum() / 1e3).items():
            pass
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
            bal = f"Captured {cap_t:.1f} Mt (NL+BE {c[[i for i in c.index if str(i)[:2] in CN]].sum():.1f})\\nStored {st_t:.1f} Mt (NL {st0[st0.region.astype(str).str[:2]=='NL'].co2.sum()/1e3:.1f}, abroad {st_t - st0[st0.region.astype(str).str[:2]=='NL'].co2.sum()/1e3:.1f})"
        else:
            bal = f"Captured {cap_t:.1f} Mt\\n= stored {st_t:.1f} + reused in methanol {u_t:.1f}"
        ax.text(.02, .02, bal, transform=ax.transAxes, fontsize=9, va="bottom", bbox=dict(boxstyle="round", fc="white", ec="#9aa3ad"), zorder=7)
'''
s=s.replace(old_st,new_st)
s=s.replace('''plt.Line2D([], [], color="#d62828", lw=3)]
    fig.legend(h, ["CO2 captured (area ~ Mt)", "CO2 injected into storage (Mt)", "CO2 pipeline flow (Mt)"], loc="lower center", ncol=3''',
 '''plt.Line2D([], [], color="#d62828", lw=3), plt.scatter([], [], s=150, marker="D", color=ACC)]
    fig.legend(h, ["CO2 captured (Mt)", "CO2 stored per site (Mt)", "CO2 pipeline flow (Mt)", "CO2 reused in methanol (Mt)"], loc="lower center", ncol=4''')
open("tools/make_deck_final3.py","w",encoding="utf8").write(s); print("ok", "pass" in s)
