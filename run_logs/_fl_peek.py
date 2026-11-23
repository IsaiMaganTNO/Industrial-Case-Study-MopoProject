import pickle
d = pickle.load(open(r"run_logs\_flows2050_IC1.pkl","rb"))
print(d.kind.unique(), d.node.unique()[:40], d.cn.unique(), len(d))
