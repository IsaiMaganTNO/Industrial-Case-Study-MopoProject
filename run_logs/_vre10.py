import pandas as pd, collections
def summarise(path, label):
    xl = pd.ExcelFile(path)
    print("===", label)
    print("  sheets:", xl.sheet_names[:6])
    for s in xl.sheet_names[:3]:
        d = xl.parse(s)
        idx = d.iloc[:, 0].astype(str)
        ic1 = sum(1 for x in idx if x.startswith(("BEC", "NLC")))
        pre = collections.Counter(x[:2] for x in idx if not x.startswith(("BEC", "NLC")))
        tgt = {k: pre.get(k, 0) for k in ["DE", "DK", "NO", "UK"]}
        print("  [%s] shape=%s cols=%s" % (s, d.shape, list(d.columns)[:5]))
        print("      rows=%d IC1=%d target=%s" % (len(idx), ic1, tgt))
        print("      sample idx:", list(idx[:8]))

summarise("data/VRE/VRE_greenfield_installation_potentials/potential_wind-on.xlsx",
          "potential_wind-on")
summarise("data/VRE/VRE_installed_capacities_2020_and_2025/capacity_wind-on-existing.xlsx",
          "capacity_wind-on-existing")
