import openpyxl
wb=openpyxl.load_workbook(r"verification\global_constraints_industry_case_study.xlsx")
for ws in wb.worksheets:
    for row in ws.iter_rows():
        for c in row:
            if c.value is not None and (isinstance(c.value,str) and len(c.value)>35 or c.column>6 or (isinstance(c.value,str) and c.value.startswith("="))):
                print(ws.title, c.coordinate, repr(c.value)[:200])
            if c.comment: print("COMMENT", ws.title, c.coordinate, c.comment.text[:200])
