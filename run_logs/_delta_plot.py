import pickle
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
R={"IC1":"nb_ccslow_ccu_cap16_dac0","CTRY":"nb_ctry_ccslow_ccu_cap16_dac0"}
D={k:pickle.load(open(rf"run_logs\{v}_NLBE.pkl","rb")) for k,v in R.items()}
def sup(k,f):
    s=D[k]["supply"]; s=s[(s.year==2050)&(s.energy>0)]; return s[f(s)].energy.sum()/1e3
items=[("Hydrogen from electrolysis",lambda s:(s.carrier=="hydrogen")&(s.tech=="PEM")),
       ("Nuclear",lambda s:(s.carrier=="electricity")&s.tech.str.startswith("nuclear")),
       ("Offshore wind",lambda s:(s.carrier=="electricity")&s.tech.str.startswith("wind-off")),
       ("Solar + onshore wind",lambda s:(s.carrier=="electricity")&s.tech.str.match(r"solar|wind-on")),
       ("Ground-source heat pumps",lambda s:(s.carrier=="heat")&s.tech.str.startswith("ground-heatpump")),
       ("Air-source heat pumps",lambda s:(s.carrier=="heat")&s.tech.str.match(r"air-heatpump(?!-cool)")),
       ("Hydrogen imports (liquid)",lambda s:s.tech=="LH2-terminal"),
       ("Fossil gas (LNG)",lambda s:s.tech=="LNG-terminal")]
rows=[(l,sup("IC1",f),sup("CTRY",f)) for l,f in items]
for r in rows: print(r[0],round(r[1],1),round(r[2],1),round(r[2]-r[1],1))
fig,ax=plt.subplots(figsize=(10,5.5))
for i,(l,a,b) in enumerate(rows[::-1]):
    d=b-a; ax.barh(i,d,color="#2a9d8f" if d>0 else "#e76f51")
    ax.text(d+(1.5 if d>=0 else -1.5),i,f"{d:+.0f}  ({a:.0f}  {b:.0f})",va="center",ha="left" if d>=0 else "right",fontsize=10)
ax.set_yticks(range(len(rows)),[r[0] for r in rows[::-1]],fontsize=11); ax.axvline(0,color="#333",lw=.8)
ax.set_xlim(-95,75); ax.set_xlabel("Change in 2050 (TWh/yr): country-level minus zonal",fontsize=11)
ax.set_title("What changes when NL and BE are modelled as one node per country (2050)",fontsize=12.5,fontweight="bold")
for s in ("top","right"): ax.spines[s].set_visible(False)
ax.grid(axis="x",color="#e3e7ec"); ax.set_axisbelow(True)
fig.tight_layout(); out=r"final_runs_pessimistic_ccs\IC1_vs_Country_delta_2050.png"; fig.savefig(out,dpi=200); print(out)
