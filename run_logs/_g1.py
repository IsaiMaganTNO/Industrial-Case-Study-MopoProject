import pickle
for tag in ["co2bidir", "vre15"]:
    d = pickle.load(open("run_logs/%s.pkl" % tag, "rb"))
    print("===", tag, type(d))
    if isinstance(d, dict):
        for k, v in d.items():
            try:
                print("  ", k, type(v).__name__, getattr(v, "shape", ""),
                      list(v.columns) if hasattr(v, "columns") else "")
            except Exception as e:
                print("  ", k, "ERR", e)
    break
