import pandas as pd
p=r"data-pipelines\europe\_ines-builder\region_transformation.xlsx"
o=pd.read_excel(p,sheet_name="OFF3")
print(o[o.id.isin(["NSBE01","NSNL011","NSNL012","NSNL031","NSNL032","NSNL033"])].to_string())
