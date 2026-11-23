import pymupdf, re
d=pymupdf.open(r"final_runs_pessimistic_ccs\NLBE_resolution_and_scope.pdf")
bad=re.compile(r"patch|leak|fix|bug|penalt|DAC|cap16|ccslow|IC1|methanation CO2|MEA|SMR\+CC|existing_units|alternative",re.I)
for i,p in enumerate(d):
    t=p.get_text(); p.get_pixmap(dpi=60).save(rf"run_logs\_slide_tmp_final3\page{i+1:02d}.png")
    hits=sorted(set(m.group(0) for m in bad.finditer(t)))
    print(i+1, t.split("\n")[0][:60], "| FLAG:" if hits else "", hits if hits else "")
