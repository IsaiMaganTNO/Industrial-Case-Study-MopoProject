import sys,pickle;sys.path.insert(0,"tools");import plot_run_summary as R,pandas as pd
d=pickle.load(open(r"runs\3day_nn_fix\logs\nn_fix.pkl","rb"))
s=d["supply"];s=s[(s.carrier=="electricity")&(s.energy>0)];s=s[s.region.isna()|s.region.astype(str).str.match(R.NB)]
print((s.assign(g=s.tech.map(lambda t:R.group(t,R.ELEC))).groupby(["g","year"]).energy.sum().unstack()/1e3).round(1).to_string())
f=d["fleet"];f=f[f.region.isna()|f.region.astype(str).str.match(R.NB)]
f=f[f.tech.str.match(r"^(nuclear|wind|solar|CCGT|OCGT|bio|battery)",case=False)|f.tech.str.contains("-H2")]
print(f.assign(g=f.tech.map(lambda t:R.group(t,R.ELEC))).groupby(["g","year"]).units.sum().unstack().round(1).to_string())
print(sorted(f.tech[f.tech.str.match("^bio",case=False)].unique())[:15])
