import json
a = json.load(open("run_logs/fp_pre.json"))
b = json.load(open("run_logs/fp_post_imp.json"))
print("%-22s %-28s %-28s %s" % ("store", "entity pre->post", "pval pre->post", "mtime changed"))
for n in a:
    x, y = a[n], b[n]
    ch = x.get("mtime") != y.get("mtime")
    de = "%s -> %s" % (x.get("entity"), y.get("entity"))
    dv = "%s -> %s" % (x.get("parameter_value"), y.get("parameter_value"))
    flag = ""
    if x.get("entity") != y.get("entity") or x.get("parameter_value") != y.get("parameter_value"):
        flag = "  <== COUNTS CHANGED"
    print("%-22s %-28s %-28s %-5s%s" % (n[:22], de, dv, ch, flag))
