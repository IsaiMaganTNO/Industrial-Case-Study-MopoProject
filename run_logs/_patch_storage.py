import io
p="tools/make_report_figs.py"; s=io.open(p,encoding="utf-8").read()
old='("Biomass power + CCS", lambda s: s.tech.str.startswith("bio") & s.tech.str.contains("+CC", regex=False), "#386641")]'
new=old[:-1]+''',
       ("Coal power", lambda s: s.tech.str.startswith("SCPC"), "#3d2b1f"), ("Oil power", lambda s: s.tech.str.startswith("oil-eng"), "#7f5539"),
       ("Waste incineration", lambda s: s.tech.str.startswith("wasteST"), "#b5838d"), ("Hydro (run-of-river)", lambda s: s.tech.str.startswith("RoR"), "#48cae4"),
       ("Battery discharge", lambda s: s.tech.str.startswith("battery-storage") & ~s.tech.str.contains("iron-air"), "#8d5a97"),
       ("Iron-air battery discharge", lambda s: s.tech.str.contains("iron-air"), "#c9a0dc")]'''
assert old in s; s=s.replace(old,new,1)
old2='    return [(n, s[q(s)].energy.sum() / 1e3, col) for n, q, col in ELC]'
new2='''    out = [(n, s[q(s)].energy.sum() / 1e3, col) for n, q, col in ELC]
    rest = s.energy.sum() / 1e3 - sum(v for _, v, _ in out)
    out.append(("Other", max(rest, 0), "#ced4da")); return out'''
assert old2 in s; s=s.replace(old2,new2,1)
io.open(p,"w",encoding="utf-8",newline="\n").write(s)
