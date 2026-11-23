import pickle
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
R={"IC1":"nb_ccslow_ccu_cap16_dac0","CTRY":"nb_ctry_ccslow_ccu_cap16_dac0"}
D={k:pickle.load(open(rf"run_logs\{v}_NLBE.pkl","rb")) for k,v in R.items()}
LAB={"MOE":"Molten oxide electrolysis","(H2)DRI-EAF":"Hydrogen direct reduction","(NG)DRI-EAF-MEA":"Gas direct reduction + CO2 capture",
     "(LN)O-MEA":"Naphtha cracker + CO2 capture","(MeOH)O-MEA":"Methanol from captured CO2","((COEL)MeOH)O-MEA":"Methanol from captured CO2"}
COL={"Molten oxide electrolysis":"#f4a261","Hydrogen direct reduction":"#2a9d8f","Gas direct reduction + CO2 capture":"#457b9d",
     "Naphtha cracker + CO2 capture":"#6c757d","Methanol from captured CO2":"#e76f51"}
fig,axes=plt.subplots(2,1,figsize=(6.5,10))
for ax,(sec,t) in zip(axes,[("steel (primary)","Primary steel"),("olefins","Plastics (olefins)")]):
    for j,k in enumerate(R):
        p=D[k]["prod"].query("year==2050 and sector==@sec"); s=p.groupby(p.tech.map(lambda x:LAB.get(x,x))).output.sum(); s=s/s.sum()*100; b=0
        for l,c in COL.items():
            v=s.get(l,0)
            if v<.1: continue
            ax.bar(j,v,.55,bottom=b,color=c,edgecolor="white",label=l)
            ax.text(j,b+v/2,f"{v:.0f}%",ha="center",va="center",color="white",fontsize=11,fontweight="bold"); b+=v
    ax.set_xticks([0,1],["Zonal\n(17 zones)","Country-level\n(1 node per country)"],fontsize=10.5); ax.set_ylim(0,100)
    ax.set_title(t,fontsize=13,fontweight="bold"); ax.set_ylabel("Share of production 2050 (%)")
    for sp in ("top","right"): ax.spines[sp].set_visible(False)
    h,l=ax.get_legend_handles_labels(); d=dict(zip(l,h)); ax.legend(d.values(),d.keys(),frameon=False,loc="center left",bbox_to_anchor=(1.0,.5),fontsize=9.5)
fig.tight_layout(); out=r"final_runs_pessimistic_ccs\IC1_vs_country_routes_2050_vertical.png"; fig.savefig(out,dpi=200,bbox_inches="tight"); print(out)

