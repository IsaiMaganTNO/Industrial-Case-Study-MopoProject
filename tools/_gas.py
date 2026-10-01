import pandas as pd, sys

path = sys.argv[1]
sheet = sys.argv[2] if len(sys.argv) > 2 else None
xl = pd.ExcelFile(path)
if sheet is None:
    print("SHEETS:", xl.sheet_names)
    sys.exit()
df = xl.parse(sheet)
print("shape:", df.shape)
print("cols:", list(df.columns))
