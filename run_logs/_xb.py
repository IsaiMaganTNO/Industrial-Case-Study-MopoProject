import pickle, pandas as pd
pd.set_option("display.width",108)
A=pickle.load(open(r"run_logs\routeemis.pkl","rb"))
B=pickle.load(open(r"run_logs\co2bidir.pkl","rb"))
def xb(D,y):
    cp=D["co2pipe"]
    cp=cp[cp["year"].astype(str).str.startswith(y)].copy()
    cp["o"]=cp["origin"].astype(str).str[:2]
    cp["d"]=cp["dest"].astype(str).str.replace("CO2_","",regex=False).str[:2]
    return cp
for y in ["2030","2040","2050"]:
    print(f"===== {y}  cross-border CO2 (ktCO2)")
    for tag,D in [("BASELINE",A),("BIDIR   ",B)]:
        cp=xb(D,y)
        be2nl=cp[(cp["o"]=="BE")&(cp["d"]=="NL")]["co2"].sum()
        nl2be=cp[(cp["o"]=="NL")&(cp["d"]=="BE")]["co2"].sum()
        tot  =cp["co2"].sum()
        act  =(cp["co2"].abs()>1e-6).sum()
        print(f"  {tag}: BE->NL={be2nl:12,.1f}   NL->BE={nl2be:10,.1f}   all_pipe_flow={tot:12,.1f}  active_edges={act}")
    print()
