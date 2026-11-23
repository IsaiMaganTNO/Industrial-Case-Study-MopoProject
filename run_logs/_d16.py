import hashlib, os, glob
def md5(p): return hashlib.md5(open(p,"rb").read()).hexdigest()
cands=glob.glob(r"verification\**\CO2_data_IC1*.xlsx",recursive=True)+[r"data-pipelines\europe\_ines-builder\CO2_data_IC1.xlsx"]
for p in cands:
    print(f"  {md5(p)[:12]}  {os.path.getsize(p)/1024:8.1f}KB  {p}")
