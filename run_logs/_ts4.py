import pickle;N=pickle.load(open(r"run_logs\nodac_nuc.pkl","rb"));s=N["co2store"];print(s.groupby(["reservoir","year"]).co2.agg(["sum","count","max"]))
