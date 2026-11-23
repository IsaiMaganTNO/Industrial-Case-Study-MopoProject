import glob
for f in glob.glob(r"data\Gas\*")+glob.glob(r"data\**\*LNG*",recursive=True)+glob.glob(r"data\**\*extract*",recursive=True):
    print(f)
