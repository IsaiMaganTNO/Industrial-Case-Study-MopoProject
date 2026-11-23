import re,pickle
from collections import Counter
A,B=pickle.load(open(r"run_logs\_red_ents.pkl","rb"))
NB=re.compile(r"(BE|NL)C\d")
ca={e[1][0] for e in A if e[0]=="connection"}; cb={e[1][0] for e in B if e[0]=="connection"}
xa={c for c in ca if NB.search(c) and not re.fullmatch(r"(?:BE|NL)C\d_\w+_(?:BE|NL)C\d",c)}
xb={c for c in cb if NB.search(c) and not re.fullmatch(r"(?:BE|NL)C\d_\w+_(?:BE|NL)C\d",c)}
print("cross-border conns nn",len(xa),"mr",len(xb),"common",len(xa&xb))
print("nn only",sorted(xa-xb));print("mr only",sorted(xb-xa))
print("conns not touching NB in nn",sorted(c for c in ca if not NB.search(c))[:20])
na={e[1][0] for e in A if e[0]=="node"}; nb_={e[1][0] for e in B if e[0]=="node"}
stub=sorted(n for n in na if re.search(r"_(DE|DK|NO|UK)$",n));print("nn stub nodes",stub)
print("stubs missing in mr",[n for n in stub if n not in nb_])
print("nn units non-NB",sorted({e[1][0] for e in A if e[0]=="unit" and not NB.search(e[1][0])})[:30])
