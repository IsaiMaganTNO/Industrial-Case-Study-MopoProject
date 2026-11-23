import pandas as pd
d = pd.read_pickle(r"run_logs\_cong_IC1.pkl"); d = d[d.car=="elec"].copy()
d["nmax"] = pd.to_numeric(d.nmax, errors="coerce")
d = d[d.conn.str.split("_").str[0].str.match(r"(NL|BE)C") & d.conn.str.split("_").str[2].str.match(r"(NL|BE)C")]
d["atmax"] = (d.n2050 >= d.nmax - 1e-6)
print(len(d), "at max build:", d.atmax.sum(), " full>=90% & at max:", ((d.sat>=.9)&d.atmax).sum(), " full>=90% & NOT at max:", ((d.sat>=.9)&~d.atmax).sum())
print(d[d.sat>=.9][["conn","n2050","nmax","sat"]].round(2).to_string())
