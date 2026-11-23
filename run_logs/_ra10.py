import os, hashlib
for p in [r"data-pipelines/europe/region_transformation.xlsx",
          r"data-pipelines/europe/_ines-builder/region_transformation.xlsx",
          r"data-pipelines/europe/region_transformation_IC1.xlsx",
          r"data-pipelines/europe/_industry-aidres/region_transformation_IC1.xlsx"]:
    if os.path.exists(p):
        print(hashlib.md5(open(p,"rb").read()).hexdigest()[:12], os.path.getsize(p), p)
    else:
        print("MISSING", p)
