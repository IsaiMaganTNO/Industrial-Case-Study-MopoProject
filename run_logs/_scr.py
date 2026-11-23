import csv
rows=list(csv.DictReader(open(r"run_logs\retire_screen_7day.csv")))
print("cols:",rows[0].keys())
blocked=[r for r in rows if "BLOCK" in str(r).upper()]
print("blocked:",len(blocked))
for r in blocked: print("   ",{k:v for k,v in r.items() if v}) 
