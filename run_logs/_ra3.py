import openpyxl, sys
p = r"data-pipelines/europe/_ines-builder/region_transformation.xlsx"
rows = [("DE","IC1",237.302523,357105.079912,"DE"),
        ("DK","IC1",141.678891,42585.056921,"DK"),
        ("NO","IC1",17.411418,323025.002853,"NO"),
        ("UK","IC1",272.715028,244480.713358,"UK")]
wb = openpyxl.load_workbook(p)
assert len(wb.sheetnames)==32, wb.sheetnames
ws = wb["IC1"]
hdr = [c.value for c in ws[1]][:5]
assert hdr == ["id","level","per_km2","area_km2","country"], hdr
existing = {ws.cell(r,1).value for r in range(2, ws.max_row+1)}
assert ws.max_row == 18, ws.max_row
for r in rows:
    assert r[0] not in existing, r[0]
    ws.append(r)
wb.save(p)
wb2 = openpyxl.load_workbook(p)
assert len(wb2.sheetnames)==32
w2 = wb2["IC1"]
for r in range(2, w2.max_row+1):
    print([w2.cell(r,c).value for c in range(1,6)])
print("rows", w2.max_row-1, "sheets", len(wb2.sheetnames))
