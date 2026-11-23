import openpyxl
p = r"data-pipelines\europe\_ines-builder\region_transformation.xlsx"
wb = openpyxl.load_workbook(p); ws = wb["OFF3_map"]
h = [c.value for c in ws[1]]; ci = h.index("IC1") + 1; cp = h.index("PECD1") + 1; cs = h.index("source") + 1
n = 0
for r in range(2, ws.max_row + 1):
    if ws.cell(r, cp).value == "FR":
        ws.cell(r, ci).value = "FR"; n += 1; print(ws.cell(r, cs).value)
wb.save(p); print("set", n)
import pandas as pd
d = pd.read_excel(p, sheet_name="OFF3_map"); print(d[d.PECD1=="FR"].to_string())
