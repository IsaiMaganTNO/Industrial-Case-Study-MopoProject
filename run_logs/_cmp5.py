import pickle,re
from collections import Counter
A,B,ex=pickle.load(open(r"run_logs\_cmp_in.pkl","rb"))
SC={"Base","wy2009","medium_bio","current","GA","GA_flex0","high_CO2","flex_buildings","flex_buildings_wy2009_current","flex_industry"}
oa=sorted({(k[0],k[1]) for k in A.keys()-B.keys()}); ob=sorted({(k[0],k[1]) for k in B.keys()-A.keys()})
print("ONLY nn_fix entities",len(oa)); [print("  ",x) for x in oa[:30]]
print("ONLY mr_fix entities",len(ob)); 
c=Counter(re.sub(r"(BE|NL)C\d","XX",x[1]) for x in ob); [print("  ",k,n) for k,n in c.most_common(40)]
