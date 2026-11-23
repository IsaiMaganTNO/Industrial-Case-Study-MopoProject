import sys, os, glob, collections; sys.path.insert(0, "tools")
from postprocess import load_weights, unpack_flow
from spinedb_api import DatabaseMapping
F="final_runs_pessimistic_ccs"
R={"MR":(rf"{F}\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\*.sqlite", rf"{F}\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\output\*.sqlite"),
   "RP10":(r"runs\rp10_mr_noblend\*.sqlite", r"runs\rp10_mr_noblend\output\*.sqlite")}
def reg(n): return n.split("_")[-1][:2] if "_" in n else "?"
for k,(gi,go) in R.items():
    inp=glob.glob(gi)[0]; w=load_weights(inp); U=collections.Counter(); C=collections.Counter(); nodes=set()
    with DatabaseMapping("sqlite:///"+os.path.abspath(glob.glob(go)[0])) as db:
        for v in db.get_parameter_value_items(entity_class_name="report__unit__node__direction__stochastic_scenario", parameter_definition_name="unit_flow"):
            bn=v["entity_byname"]
            if not bn[2].startswith("HC"): continue
            nodes.add(bn[2]); r=reg(bn[2])
            if r not in ("NL","BE"): continue
            for y,x in unpack_flow(v,w):
                if y==2050: U[(bn[3], bn[1].rsplit("_",1)[0][:28], r)]+=x/1e3
        for v in db.get_parameter_value_items(entity_class_name="report__connection__node__direction__stochastic_scenario", parameter_definition_name="connection_flow"):
            bn=v["entity_byname"]
            if not bn[2].startswith("HC"): continue
            r=reg(bn[2])
            if r not in ("NL","BE"): continue
            for y,x in unpack_flow(v,w):
                if y==2050: C[(bn[3], bn[1], r)]+=x/1e3
    import re
    sup=sum(x for (d,t,r),x in U.items() if d=="to_node"); use=sum(x for (d,t,r),x in U.items() if d=="from_node")
    ext=lambda n: set(re.findall(r"(?:^|_)([A-Z]{2})(?=C?\d|_|$)", n))-{"NL","BE","HC"}
    imp=collections.Counter(); exp=collections.Counter()
    for (d,c,r),x in C.items():
        e=ext(c)
        if not e: continue
        (imp if d=="to_node" else exp)[c]+=x
    print("#####",k,"2050 NL+BE HC: production",round(sup),"use by units",round(use),"import",round(sum(imp.values())),"export",round(sum(exp.values())))
    print("  imports by conn:",{a:round(b) for a,b in imp.most_common(8)}); print("  exports by conn:",{a:round(b) for a,b in exp.most_common(8)})
    print("  top uses:",{t[1]:round(x) for t,x in sorted(U.items(),key=lambda t:-t[1]) if t[0]=="from_node"}.__repr__()[:900])
    continue
    print("=====",k,"HC nodes sample:",sorted(nodes)[:6])
    print("-- unit flows NL/BE 2050 (TWh) [to_node=supply, from_node=use]")
    for kk,x in sorted(U.items(), key=lambda t:-t[1]):
        if x>1: print(" ",kk,round(x,1))
    print("-- connection flows NL/BE HC nodes 2050 (TWh) [to_node=inflow, from_node=outflow]")
    for kk,x in sorted(C.items(), key=lambda t:-t[1]):
        if x>1: print(" ",kk,round(x,1))

