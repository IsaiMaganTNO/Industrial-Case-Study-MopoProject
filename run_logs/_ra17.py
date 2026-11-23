import json
a=json.load(open(r"backups/data-pre-mixedres/Energy_Conversion/config.json"))
b=json.load(open(r"data/Energy_Conversion/config.json"))
for k in sorted(set(a)|set(b)):
    va,vb=a.get(k,"<ABSENT>"),b.get(k,"<ABSENT>")
    if va!=vb: print("DIFF %-20s old=%s  new=%s"%(k,va,vb))
    else: print("same %-20s %s"%(k,str(va)[:50]))
