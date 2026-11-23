import pickle
A=pickle.load(open(r"run_logs\nb_v2_NLBE.pkl","rb")); B=pickle.load(open(r"run_logs\nb_ctry_NLBE.pkl","rb"))
for n,d in (("SA",A),("CL",B)):
  f=d["fleet"][d["fleet"].year==2050]; s=d["supply"][d["supply"].year==2050]
  print(n,"nuc",round(f[f.tech.str.contains("^nuclear")].units.sum(),2),"PEM",round(f[f.tech.str.contains("^PEM")].units.sum(),2),"bat",round(f[f.tech.str.contains("^battery")].units.sum(),2),
   "el",round(s[s.carrier=="electricity"].energy.sum()/1e3),"h2",round(s[s.carrier=="hydrogen"].energy.sum()/1e3,1),"pem",round(s[(s.carrier=="hydrogen")&s.tech.str.contains("^PEM")].energy.sum()/1e3,1))
