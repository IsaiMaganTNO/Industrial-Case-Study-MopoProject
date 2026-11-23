import glob, os, sys; sys.path.insert(0,"tools"); import postprocess as P
import inspect; print(inspect.getsource(P.to_milestone)); print(inspect.getsource(P.load_weights)[:1500])
w = P.load_weights(glob.glob(r"final_runs_pessimistic_ccs\1_IC1_NLBE_17zones\input\*.sqlite")[0]); print(w)
