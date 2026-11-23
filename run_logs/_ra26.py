import os
for d in ["data/Rdemand","data/VRE","data/Buildings","data/Gas","data/Electricity_Transmission"]:
    if not os.path.isdir(d): print("MISSING", d); continue
    print("==", d)
    for root,_,fs in os.walk(d):
        for f in sorted(fs)[:6]:
            print("   ", os.path.relpath(os.path.join(root,f), d), os.path.getsize(os.path.join(root,f)))
        break
