import yaml
cfg=yaml.safe_load(open(r"data-pipelines\europe\userconfig.yaml",encoding="utf-8"))
t=cfg["technology"]
for k in sorted(t):
    if "wood" in k: print(repr(k),t[k])
