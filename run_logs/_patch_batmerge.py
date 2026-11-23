import io
p="tools/make_report_figs.py"; s=io.open(p,encoding="utf-8").read()
r=[('''       ("Battery discharge", lambda s: s.tech.str.startswith("battery-storage") & ~s.tech.str.contains("iron-air"), "#8d5a97"),
       ("Iron-air battery discharge", lambda s: s.tech.str.contains("iron-air"), "#c9a0dc")]''',
    '''       ("Battery discharge", lambda s: s.tech.str.startswith("battery-storage"), "#8d5a97")]'''),
   ('"Storage charging": "#8d5a97",','"Battery charging": "#8d5a97",'),
   ('"Building heat (HP, e-heating)", "Storage charging",','"Building heat (HP, e-heating)", "Battery charging",'),
   ('g = u.groupby("cat").twh.sum()','g = u.groupby("cat").twh.sum().rename({"Storage charging": "Battery charging"})')]
for a,b in r:
    assert s.count(a)==1,a; s=s.replace(a,b)
io.open(p,"w",encoding="utf-8",newline="\n").write(s)
