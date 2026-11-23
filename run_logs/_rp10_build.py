import os, shutil, subprocess, sys, pandas as pd
EU = r"EU_case\Pan-European-Framework-Energy-System-Planning\src\_clustering\results"
W = r"runs\rp10_mr"; R = os.path.join(W, "results"); os.makedirs(R, exist_ok=True)
for f in ["representative_periods.csv", "weights_wy2009.csv"]: shutil.copy(os.path.join(EU, f), R)
w = pd.read_csv(os.path.join(R, "weights_wy2009.csv"))
print("periods", w.period.nunique(), "reps", w.rep_period.nunique(), "row sums ok:", (w.groupby("period").weight.sum() - 1).abs().max() < 1e-3)
print("rep weights (days):", w.groupby("rep_period").weight.sum().round(1).to_dict())
src = r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\Final_SpineOpt_Model.tiny.3day.mr_ccslow_ccu_cap16_dac0.sqlite"
dst = os.path.abspath(os.path.join(W, "Final_SpineOpt_Model.tiny.10day.mr_ccslow_ccu_cap16_dac0.sqlite")); shutil.copy(src, dst)
script = os.path.abspath(r"Pan-European-Framework-Energy-System-Planning\src\_clustering\clustering_output.py")
r = subprocess.run([sys.executable, script, "sqlite:///" + dst], cwd=W, capture_output=True, text=True)
print(r.stdout[-1500:], r.stderr[-1500:])
