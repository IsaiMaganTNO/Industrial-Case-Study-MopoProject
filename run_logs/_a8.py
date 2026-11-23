import pickle, pandas as pd, re, csv
pd.set_option("display.width",95); pd.set_option("display.max_rows",400)
d = pickle.load(open("run_logs/retireall.pkl","rb"))
fl = d["fleet"]
rows=list(csv.DictReader(open("run_logs/retire_screen.csv")))
fams=sorted({re.sub(r"_(BE|NL)C\d+$","",r["node"]) for r in rows})
print("families in screen:", len(fams))
print(fams)
print()
# which units were patched (RETIRE-SAFE) and what replaced them
tech_of=lambda u: re.sub(r"_(BE|NL)C\d+$","",u)
safe=sorted({tech_of(r["unit"]) for r in rows if r["verdict"]=="RETIRE-SAFE"})
print("patched techs:", len(safe))
for t in safe:
    sub=fl[fl.tech==t]
    s=sub.groupby("year").units.sum()
    print(f"  {t:52s} {dict(s.round(3))}")
