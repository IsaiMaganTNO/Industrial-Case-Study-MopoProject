import openpyxl
wb=openpyxl.load_workbook(r"verification\global_constraints_industry_case_study.xlsx",data_only=True)
for ws in wb.worksheets:
    print("\n########", ws.title, ws.max_row, "x", ws.max_column)
    for row in ws.iter_rows(values_only=True):
        if any(v is not None for v in row):
            print(" | ".join("" if v is None else str(v)[:40] for v in row))
