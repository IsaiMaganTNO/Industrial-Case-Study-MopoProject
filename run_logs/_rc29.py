import os,hashlib
a=r"backups\data-pre-mixedres"; b=r"data"
def h(p):
    m=hashlib.md5()
    with open(p,"rb") as f:
        for c in iter(lambda:f.read(1<<20),b""): m.update(c)
    return m.hexdigest()
for root,_,fs in os.walk(a):
    for f in fs:
        pa=os.path.join(root,f); pb=pa.replace(a,b,1)
        if not os.path.exists(pb): print("MISSING",pb); continue
        if os.path.getsize(pa)!=os.path.getsize(pb) or h(pa)!=h(pb):
            print("DIFF  %10d -> %10d  %s"%(os.path.getsize(pa),os.path.getsize(pb),pb))
