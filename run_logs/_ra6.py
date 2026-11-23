import openpyxl
p = r"data-pipelines/europe/_ines-builder/region_transformation.xlsx"
C = {"DE","DK","NO","UK"}
wb = openpyxl.load_workbook(p)
assert len(wb.sheetnames)==32

ws = wb["PECD1_IC1"]
hdr=[c.value for c in ws[1]]; assert hdr[:2]==["source","target"],hdr
n=0
for r in range(2,ws.max_row+1):
    if ws.cell(r,1).value in C:
        assert ws.cell(r,2).value is None, (r,ws.cell(r,2).value)
        ws.cell(r,2).value = ws.cell(r,1).value; n+=1
assert n==4,n

wm = wb["OFF3_map"]
hm=[c.value for c in wm[1]]; ic=hm.index("IC1")+1; pc=hm.index("PECD1")+1
m=0
for r in range(2,wm.max_row+1):
    if wm.cell(r,pc).value in C:
        assert wm.cell(r,ic).value is None
        wm.cell(r,ic).value = wm.cell(r,pc).value; m+=1
print("off3_map filled",m)
wb.save(p)

import pandas as pd
d=pd.read_excel(p,"PECD1_IC1"); print(d[d.source.isin(C)].to_string())
o=pd.read_excel(p,"OFF3_map"); print(o[o.PECD1.isin(C)][["source","PECD1","IC1"]].to_string())
print("sheets",len(pd.ExcelFile(p).sheet_names))
