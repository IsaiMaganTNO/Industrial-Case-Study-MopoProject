import pandas as pd, glob, os
for p in glob.glob(r"data\**\*.xlsx",recursive=True)+glob.glob(r"data\**\*.csv",recursive=True):
    if any(k in os.path.basename(p).lower() for k in ("gas","pipe","transmission","network","grid")):
        print(p)
