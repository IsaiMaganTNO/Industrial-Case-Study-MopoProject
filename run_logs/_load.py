import sys, pickle
sys.path.insert(0,"tools")
import postprocess as PP
MODEL=r"checkpoints\Final_SpineOpt_Model.tiny.3day.co2bidir.sqlite"
RES  =r"checkpoints\Investment_Results.3day_co2bidir.sqlite"
w=PP.load_weights(MODEL)
d=PP.load(RES, wmap=w)
with open(r"run_logs\co2bidir.pkl","wb") as f: pickle.dump(d,f)
print("frames:",list(d.keys()))
print("\nobjective:")
print(d["obj"].to_string()[:1200])
