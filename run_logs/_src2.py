import pandas as pd, sqlite3, collections
p=r"data-pipelines\europe\_ines-builder\CO2_data_IC1.xlsx"
net=pd.ExcelFile(p).parse("network")
print("rows:",len(net),"| modes:",net['mode'].unique())
E=set(zip(net['from'],net['to']))
print("unique directed pairs:",len(E))
rev=[(a,b) for a,b in E if (b,a) in E]
print("pairs that also have the reverse in source:",len(rev))
und=set(frozenset((a,b)) for a,b in E)
print("unique UNDIRECTED pairs:",len(und))
# region set
regs=sorted(set(net['from'])|set(net['to']))
print("\nnodes in source:",regs)
# BE -> NL edges in source
be=[(a,b) for a,b in E if str(a).startswith('BE') and str(b).startswith('NL')]
nl=[(a,b) for a,b in E if str(a).startswith('NL') and str(b).startswith('BE')]
print(f"\nsource BE->NL edges: {len(be)} {sorted(be)}")
print(f"source NL->BE edges: {len(nl)} {sorted(nl)}")
