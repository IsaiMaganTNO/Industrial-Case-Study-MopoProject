import re, yaml, difflib
F = r"data-pipelines\europe\userconfig.yaml"
B = r"backups\pre-frlu\data-pipelines__europe__userconfig.yaml.pre-frlu"
o = open(r"run_logs\_frlu_yamlfix.out", "w", encoding="utf8"); P = lambda *a: (print(*a, file=o), o.flush())
raw = open(F, "rb").read()
P("bytes", len(raw), "CRLF", raw.count(b"\r\n"), "lone CR", raw.count(b"\r") - raw.count(b"\r\n"), "LF", raw.count(b"\n"))
txt = raw.decode("utf8").replace("\r\n", "\n").replace("\r", "\n")
lines = txt.split("\n")
# split any line holding two list entries, e.g.  - "NL"  - "DE"
fixed = []
for ln in lines:
    m = re.match(r'^(\s*- "[A-Z]{2}")\s+(- "[A-Z]{2}".*)$', ln)
    if m:
        P("SPLIT", repr(ln)); fixed += [m.group(1), "  " + m.group(2)]
    else:
        fixed.append(ln)
new = "\r\n".join(fixed) if raw.count(b"\r\n") > raw.count(b"\n") / 2 else "\n".join(fixed)
c = yaml.safe_load(new)
P("countries", c["countries"])
open(F, "w", encoding="utf8", newline="").write(new)
c2 = yaml.safe_load(open(F, "rb"))
P("reparse countries", c2["countries"])
for k, v in c2.items():
    if isinstance(v, dict) and "co2_annual_budget" in v: P("budget", k, v["co2_annual_budget"])
b = open(B, "rb").read().decode("utf8").replace("\r\n", "\n").split("\n")
a = open(F, "rb").read().decode("utf8").replace("\r\n", "\n").split("\n")
P("lines backup", len(b), "now", len(a))
for d in difflib.unified_diff(b, a, "backup", "now", n=0, lineterm=""): P(d)
P("DONE"); o.close()
