import json
p=r"EU_case\.spinetoolbox\project.json"
d=json.load(open(p,encoding="utf8"))
items=d.get("items",{})
print("items:",len(items))
for k,v in items.items():
    print(f"  {k:28} {v.get('type')}")
conns=d.get("connections",[])
print("\nconnections:",len(conns))
for c in conns[:30]:
    print("  ",c.get("from"),"->",c.get("to"))
