import json, os, hashlib
for p in [r"data/Energy_Conversion/config.json",
          r"backups/data-pre-mixedres/Energy_Conversion/config.json"]:
    print("==", p, os.path.exists(p))
    if os.path.exists(p):
        print("   md5", hashlib.md5(open(p,"rb").read()).hexdigest()[:12], os.path.getsize(p))
        print("   geolevel:", json.load(open(p)).get("geolevel"))
