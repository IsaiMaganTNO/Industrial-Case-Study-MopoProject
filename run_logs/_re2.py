import openpyxl
p=r"verification\global_constraints_industry_case_study.xlsx"
for do in (False,True):
    wb=openpyxl.load_workbook(p,data_only=do)
    print("################ data_only=",do)
    for ws in wb.worksheets:
        print("\n=== SHEET:",ws.title)
        for row in ws.iter_rows():
            cells=[]
            for c in row:
                if c.value is not None:
                    cells.append("%s=%r"%(c.coordinate,c.value))
            if cells: print("  "+" | ".join(cells))
