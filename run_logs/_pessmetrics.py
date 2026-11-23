import pickle, sys, pandas as pd
sys.path.insert(0,"tools"); import plot_run_summary as S
pd.set_option("display.width",250); pd.set_option("display.max_rows",400); pd.set_option("display.max_columns",20)
R=["nb_ccslow","nb_ctry_ccslow","mr_ccslow_dac0"]
D={r:pickle.load(open(rf"run_logs\{r}_NLBE.pkl" if r!="nb_v2x" else "","rb")) for r in R}
X={r:pd.read_pickle(rf"run_logs\{r}_xbbio.pkl") for r in R}
rows={}
for r,d in D.items():
  m={}
  for y in (2030,2040,2050):
    e=d["emis"].query("year==@y"); m[("CO2 net NLBE Mt",y)]=e.co2.sum()/1e3
    m[("CO2 stored NLBE Mt",y)]=d["co2store"].query("year==@y").co2.sum()/1e3
    s=d["supply"].query("year==@y and energy>0")
    for (c,cat),v in s.groupby(["carrier","category"]).energy.sum().items():
      if y==2050: m[(f"TWh {c}: {cat}",y)]=v/1e3
    cn=d["co2net"].query("year==@y and role=='captured'")
    for src,v in cn.groupby("source").co2.sum().items():
      if y==2050: m[(f"CO2 captured: {src} Mt",y)]=v/1e3
    xb=X[r]["xb"].query("year==@y")
    out=xb[xb.o.isin(["NL","BE"])&~xb.d.isin(["NL","BE"])].groupby("car").v.sum()
    inn=xb[xb.d.isin(["NL","BE"])&~xb.o.isin(["NL","BE"])].groupby("car").v.sum()
    for c in ("CO2","elec","H2","CH4"):
      m[(f"XB net export {c} (k units)",y)]=(out.get(c,0)-inn.get(c,0))/1e3
  f=d["fleet"].query("year==2050"); f=f[f.region.astype(str).str.match(r"^(NL|BE)")]
  g=f.groupby(f.tech.str.replace(r"_(NS|BS|AT|AS)\w+$","",regex=True).str.replace(r"battery-storage.*","battery-storage",regex=True)).units.sum()
  for t in ["PEM","nuclear-3","methanation","REF-SMR","REF-SMR-MEA","SMR+CC","gas-boiler","bio-boiler","air-heatpump","ground-heatpump","CCGT","CCGT+CC","CCGT-H2","battery-storage","wind-off-FO-SP370-HH155","wind-off-FB-SP370-HH155","solar-PV-no-tracking","wind-on-SP277-HH100","DAC"]:
    m[(f"fleet2050 {t}",2050)]=g.get(t,0)
  p=d["prod"].query("year==2050"); p=p.assign(rt=p.tech.map(S.route_label))
  sh=p.groupby(["sector","rt"]).output.sum(); sh=sh/sh.groupby(level=0).transform("sum")*100
  for (sec,rt),v in sh.items():
    if v>=3: m[(f"route% {sec}: {rt}",2050)]=v
  rows[r]=pd.Series(m)
T=pd.DataFrame(rows).fillna(0); T.index=[f"{a} [{b}]" for a,b in T.index]
T.round(2).to_csv(r"run_logs\ccs_metrics_pess_NLBE.csv"); print(T.round(1).to_string())

