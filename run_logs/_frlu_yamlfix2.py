import re, yaml, difflib
F = r"data-pipelines\europe\userconfig.yaml"
B = r"backups\pre-frlu\data-pipelines__europe__userconfig.yaml.pre-frlu"
o = open(r"run_logs\_frlu_yamlfix.out", "w", encoding="utf8")
def P(*a): print(*a, file=o); print(*a); o.flush()
raw = open(F, "rb").read()
P("bytes", len(raw), "CRLF", raw.count(b"\r\n"), "LF", raw.count(b"\n"))
txt = raw.decode("utf8").replace("\r\n", "\n").replace("\r", "\n")
fixed = []
for ln in txt.split("\n"):
    m = re.match(r'^(\s*- "[A-Z]{2}")\s+(- "[A-Z]{2}".*)$', ln)
    if m:
        P("SPLIT", repr(ln)); ind = re.match(r"^\s*", ln).group(0); fixed += [m.group(1), ind + m.group(2)]
    else:
        fixed.append(ln)
nl = "\r\n" if raw.count(b"\r\n") > raw.count(b"\n") / 2 else "\n"
new = nl.join(fixed)
yaml.safe_load(new)
open(F, "w", encoding="utf8", newline="").write(new)
c2 = yaml.safe_load(open(F, "rb"))
P("countries", c2["countries"])
def walk(d, p=""):
    if isinstance(d, dict):
        for k, v in d.items():
            if k == "co2_annual_budget": P("budget", p + k, v)
            walk(v, p + str(k) + ".")
walk(c2)
b = open(B, "rb").read().decode("utf8").replace("\r\n", "\n").split("\n")
a = open(F, "rb").read().decode("utf8").replace("\r\n", "\n").split("\n")
P("lines backup", len(b), "now", len(a))
for d in difflib.unified_diff(b, a, "backup", "now", n=0, lineterm=""): P(d)
P("DONE"); o.close()
