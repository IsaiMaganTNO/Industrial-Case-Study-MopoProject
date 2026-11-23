import openpyxl
p=r"verification\global_constraints_industry_case_study.xlsx"
wb=openpyxl.load_workbook(p,data_only=False)
print("SHEETS:",wb.sheetnames)
for ws in wb.worksheets:
    print("\n=== %s  dims=%s  max_row=%d max_col=%d"%(ws.title,ws.dimensions,ws.max_row,ws.max_column))
