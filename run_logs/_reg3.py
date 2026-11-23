import yaml
c = yaml.safe_load(open("data-pipelines/europe/userconfig.yaml", "rb"))
p = c.get("pipelines", {})
print("%-26s %-16s %s" % ("pipeline", "target_res", "status"))
for k, v in p.items():
    if isinstance(v, dict):
        print("%-26s %-16s %s" % (k, v.get("target_resolution"), v.get("status")))
print()
print("countries:", c.get("countries"))
