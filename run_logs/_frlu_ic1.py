import openpyxl
F = r"data-pipelines\europe\_ines-builder\region_transformation.xlsx"
o = open(r"run_logs\_frlu_ic1.out", "w", encoding="utf8"); P = lambda *a: (print(*a, file=o), o.flush())
wb = openpyxl.load_workbook(F)
ic, pe = wb["IC1"], wb["PECD1"]
hdr_ic = [c.value for c in ic[1]]; hdr_pe = [c.value for c in pe[1]]
P("IC1 hdr", hdr_ic, "PECD1 hdr", hdr_pe)
ids = [r[0].value for r in ic.iter_rows(min_row=2)]
P("IC1 ids before", ids)
for r in ic.iter_rows(min_row=2):
    if r[0].value in ("DE", "UK"): P("existing", [c.value for c in r])
src = {r[hdr_pe.index("id")].value: [c.value for c in r] for r in pe.iter_rows(min_row=2)}
for cc in ("FR", "LU"):
    if cc in ids: P(cc, "already present - skip"); continue
    row = src[cc]; P("PECD1", cc, row)
    new = [row[hdr_pe.index(h)] if h in hdr_pe else None for h in hdr_ic]
    if "level" in hdr_ic: new[hdr_ic.index("level")] = "IC1"
    ic.append(new); P("added", new)
wb.save(F)
wb2 = openpyxl.load_workbook(F, read_only=True)
P("IC1 ids after", [r[0] for r in wb2["IC1"].iter_rows(min_row=2, values_only=True)])
P("sheets", wb2.sheetnames == wb.sheetnames)
P("DONE"); o.close()
