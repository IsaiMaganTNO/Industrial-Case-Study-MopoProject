import pandas as pd, matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
d="EU_case_updated_results/baseline_csv/"
df=pd.read_csv("results_2050_analysis/data/EU_baseline_comparison.csv")
df=df[(df.year==2050)&(df.item!="LH2 import terminal")&(df.item!="Net pipeline import")]
c=pd.read_csv(d+"crossborder_flows.csv",index_col=0); nb=["NL","BE"]
def netimp(cm):
    s=c[c.commodity==cm]
    return s[s.target.isin(nb)&~s.source.isin(nb)].y2050.sum()-s[s.source.isin(nb)&~s.target.isin(nb)].y2050.sum()
add=[("EU baseline","EL","NLBE",2050,"Net import",netimp("electricity")),
     ("EU baseline","H2","NLBE",2050,"Net pipeline import",netimp("hydrogen"))]
# our runs: NL+BE net external H2 pipeline trade = imports - exports (intra NL-BE cancels)
D="results_2050_analysis/data/"
a2=pd.read_csv(D+"A2_hydrogen_supply.csv"); a4=pd.read_csv(D+"A4_hydrogen_consumption.csv")
for lab in a2.label.unique():
    i=a2[(a2.label==lab)&(a2.year==2050)&(a2.item=="Net pipeline import")].twh.sum()
    e=a4[(a4.label==lab)&(a4.year==2050)&(a4.item=="Net pipeline export")].twh.sum()
    add.append((lab,"H2","NLBE",2050,"Net pipeline import",i-e))
df=pd.concat([df,pd.DataFrame(add,columns=df.columns)])
df.loc[df.item=="Gas reforming + CCS","item"]="Gas reforming"
runs=["EU baseline","NL+BE country level","NL+BE regional clusters","Mixed resolution"]
lab=["EU case\nbaseline","NL+BE\ncountry\nlevel","NL+BE\nregional\nclusters","Mixed\nresolution"]
col={"Nuclear":"#7b2cbf","Offshore wind":"#03045e","Onshore wind":"#4895ef","Solar PV":"#f9c74f","Gas power":"#c1121f",
 "Hydrogen turbines":"#90be6d","Biomass power":"#6a994e","Other":"#adb5bd","Net import":"#6c757d",
 "Electrolysis":"#2a9d8f","Gas reforming":"#c1121f","Other H2 supply":"#adb5bd","Net pipeline import":"#6c757d"}
fig,axs=plt.subplots(1,2,figsize=(18/2.54,9/2.54))
x=range(len(runs))
for ax,k,yl in [(axs[0],"EL","Electricity supply NL+BE 2050 (TWh)"),(axs[1],"H2","Hydrogen supply NL+BE 2050 (TWh)")]:
    p=df[df.kind==k].pivot_table(index="run",columns="item",values="twh",aggfunc="sum").reindex(runs).fillna(0)
    p=p.loc[:,p.abs().sum()>0.5]; p=p[[c_ for c_ in col if c_ in p]]
    bp=[0.0]*len(runs); bn=[0.0]*len(runs)
    for it in p:
        v=list(p[it]); pos=[max(z,0) for z in v]; neg=[min(z,0) for z in v]
        ax.bar(x,pos,bottom=bp,color=col[it],label=it,width=0.65)
        if any(n<0 for n in neg): ax.bar(x,neg,bottom=bn,color=col[it],width=0.65)
        bp=[a+b for a,b in zip(bp,pos)]; bn=[a+b for a,b in zip(bn,neg)]
    ax.axhline(0,color="k",lw=0.6)
    ax.set_xticks(list(x)); ax.set_xticklabels(lab,fontsize=7); ax.set_ylabel(yl,fontsize=8); ax.tick_params(labelsize=7)
    ax.axvline(0.5,color="k",lw=0.6,ls="--"); ax.spines[["top","right"]].set_visible(False)
    ax.legend(fontsize=6,frameon=False,loc="upper center",bbox_to_anchor=(0.5,-0.36),ncol=(3 if k=="EL" else 2))
    print(k);print(p.round(1))
fig.tight_layout()
for e,kw in [("png",{"dpi":400}),("svg",{})]: fig.savefig(f"results_2050_analysis/figures/C1_EU_comparison_2050.{e}",bbox_inches="tight",**kw)
df.to_csv(D+"C1_EU_comparison_2050.csv",index=False)
