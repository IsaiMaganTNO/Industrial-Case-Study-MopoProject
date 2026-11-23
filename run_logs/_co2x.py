import openpyxl
for f in ["low","high"]:
  wb=openpyxl.load_workbook(rf"verification\CO2_data_IC1_{f}_cost.xlsx",data_only=True)
  print("=====",f)
  for ws in wb.worksheets:
    print("--",ws.title,ws.max_row,ws.max_column)
    for r in ws.iter_rows(min_row=1,max_row=min(ws.max_row,40),values_only=True):
      if any(v is not None for v in r): print("  ",[v for v in r][:14])
