import pandas as pd
x = r"data-pipelines\europe\_ines-builder\region_transformation.xlsx"
for sh in ("NUTS3_IC1", "IC1_NUTS3"):
    d = pd.read_excel(x, sh).astype(str)
    print("==", sh, d.columns.tolist()); print(d[d.apply(lambda r: r.str.contains("NL112|NL124|NL125|NL321|NL341|BE251|NL329|NL33|NL327").any(), axis=1)].to_string())
d = pd.read_excel(x, "NUTS3_IC1").astype(str)
print(d[d.apply(lambda r: r.str.contains("NLC2|NLC5|NLC6").any(), axis=1)].to_string())
