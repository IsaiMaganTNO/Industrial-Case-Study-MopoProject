import json
d = json.load(open(".spinetoolbox/project.json", encoding="utf-8"))
items = d.get("items", {})
print("=== Tools: spec + cmdline ===")
for n, v in sorted(items.items()):
    if v.get("type") == "Tool":
        print("%-24s spec=%-28s args=%s" % (n[:24], str(v.get("specification"))[:28],
                                            str(v.get("cmd_line_args"))[:40]))
print()
print("=== Data Connections: refs ===")
for n, v in sorted(items.items()):
    if v.get("type") == "Data Connection":
        refs = v.get("file_references", []) or []
        print("%-22s %d refs" % (n[:22], len(refs)))
        for r in refs[:3]:
            print("      ", str(r)[:84])
