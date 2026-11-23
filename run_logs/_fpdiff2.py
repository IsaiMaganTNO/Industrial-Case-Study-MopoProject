import json
pre = json.load(open("run_logs/fp_pre.json"))
post = json.load(open("run_logs/fp_post_build.json"))
print("%-22s %16s %16s %7s" % ("store", "entity pre>post", "pval pre>post", "drift"))
drift = []
for k in pre:
    a, b = pre[k], post.get(k)
    if b is None:
        continue
    de = b["entity"] - a["entity"]
    dv = b["parameter_value"] - a["parameter_value"]
    flag = "" if (de == 0 and dv == 0) else "  <<< DRIFT"
    if flag:
        drift.append((k, de, dv))
    print("%-22s %7d>%-8d %7d>%-8d %s" % (k, a["entity"], b["entity"],
          a["parameter_value"], b["parameter_value"], flag))
print()
print("STORES WITH DRIFT:", len(drift))
for k, de, dv in drift:
    print("   %-20s entity %+d  pval %+d" % (k, de, dv))
