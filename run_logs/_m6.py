import pandas as pd, os
B=r"verification\Data - IC1 and PECD1"
xl=pd.ExcelFile(os.path.join(B,"Gas","Gas_Sectors_Dataset.xlsx"))
p=xl.parse("CH4_Production")
sub=p[p["To Country"].astype(str).str.strip().isin(["NO","DE","DK","UK"])]
print("=== CH4_Production NO/DE/DK/UK ==="); print(sub.iloc[:,:5].to_string())
n=xl.parse("CH4_Network")
nn=n[(n.iloc[:,0].astype(str).str.strip()=="NO")|(n.iloc[:,1].astype(str).str.strip()=="NO")]
print("\n=== CH4_Network links touching NO ==="); print(nn.iloc[:,:4].to_string())
