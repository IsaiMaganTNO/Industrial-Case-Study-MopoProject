import openpyxl, pandas as pd
p = r"data-pipelines/europe/_ines-builder/region_transformation.xlsx"
C = {"DE","DK","NO","UK"}
wb = openpyxl.load_workbook(p)
assert len(wb.sheetnames)==32
ws = wb["PECD1_IC1"]
assert [c.value for c in ws[1]][:2]==["source","target"]
n=0
for r in range(2,ws.max_row+1):
    s=ws.cell(r,1).value
    if s in C:
        v=ws.cell(r,2).value
        assert v is None or (isinstance(v,str) and v.startswith("=")), (r,v)
        ws.cell(r,2).value = s; n+=1
assert n==4,n
wm = wb["OFF3_map"]
hm=[c.value for c in wm[1]]; ic=hm.index("IC1")+1; pc=hm.index("PECD1")+1
m=0
for r in range(2,wm.max_row+1):
    if wm.cell(r,pc).value in C:
        wm.cell(r,ic).value = wm.cell(r,pc).value; m+=1
wb.save(p)
print("pecd1_ic1",n,"off3_map",m)
d=pd.read_excel(p,"PECD1_IC1"); print(d[d.source.isin(C)].to_string())
o=pd.read_excel(p,"OFF3_map"); print(o[o.PECD1.isin(C)][["source","PECD1","IC1"]].to_string())
print("sheets",len(pd.ExcelFile(p).sheet_names), "ic1rows", len(pd.read_excel(p,"IC1")))
