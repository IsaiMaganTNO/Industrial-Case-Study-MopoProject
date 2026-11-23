import sys,pickle
sys.path.insert(0,"tools")
import postprocess as PP
md=r"checkpoints\Final_SpineOpt_Model.tiny.3day.routeemis.sqlite"
rs=r"checkpoints\Investment_Results.3day_routeemis.sqlite"
w=PP.load_weights(md)
print("wmap days:",len(w) if w else None)
d=PP.load(rs,wmap=w)
pickle.dump(d,open(r"run_logs\routeemis.pkl","wb"))
print("keys:",sorted(d.keys()))
print("objective:",d.get("objective"))
