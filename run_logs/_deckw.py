import sys,os
sys.path.insert(0,"presentation"); sys.path.insert(0,"analysis_v2")
import sqlite3, pandas as pd
import model as M, spine_io as sio
res=r"..\checkpoints\Investment_Results.3day_vre15.sqlite"
inp=r"..\checkpoints\Final_SpineOpt_Model.tiny.3day.gascap.vre15.sqlite"
rc=sio.connect(res); ic=sio.connect(inp)
y2m,rw=M.milestones(ic)
print("rep weights:",rw)
print("annual weight:",M.annual_weight(rw,y2m))
