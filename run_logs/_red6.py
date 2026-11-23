import re,pickle
from collections import Counter,defaultdict
from spinedb_api import from_database
A,B=pickle.load(open(r"run_logs\_red_vals.pkl","rb"))
EA,EB=pickle.load(open(r"run_logs\_red_ents.pkl","rb"))
NB=re.compile(r"(BE|NL)C\d")
xb=[e for e in EA&EB if e[0].startswith("connection") and NB.search("__".join(e[1])) and re.search(r"(?<![A-Za-z])(DE|DK|NO|UK|FR|LU)(?![a-z])","__".join(e[1]))]
d=Counter()
ex=[]
for k in set(A)|set(B):
  if (k[0],k[1]) in set(xb) and A.get(k)!=B.get(k): d[(k[2],k[3],"A" if k in A else "-","B" if k in B else "-")]+=1; ex.append(k)
print("cross-border param diffs",d)
for k in ex[:6]:
  a=A.get(k);b=B.get(k)
  f=lambda t: from_database(t[1],t[0]) if t else None
  x,y=f(a),f(b);print(k,getattr(x,"values",x) if x is not None else None,"|",getattr(y,"values",y) if y is not None else None)
f=lambda t: from_database(t[1],t[0])
for k in A:
  if k[0] in("investment_group","temporal_block") and A[k]!=B.get(k) and k[2] in("investment_count_total_max_cumulative","representative_blocks_by_period"):
    x,y=f(A[k]),f(B[k]);print(k,getattr(x,"values",x),"|",getattr(y,"values",y))
# AT etc stubs connectivity
st=[e for e in EB if e[0]=="connection__from_node" and re.search(r"_(AT|CH|CZ|IE|PL|SE|FI)$",e[1][1])]
print("new stub conns",Counter(re.sub(r"\d","",e[1][0]) for e in st).most_common(12))
