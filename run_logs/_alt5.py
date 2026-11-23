import pickle
d=pickle.load(open(r"run_logs\hcco2.pkl","rb"))
p=d["prod"]
for y in (2030,2040,2050):
    r=p[(p["tech"]=="aluminium-primary-production-reference")&(p["year"]==y)]["output"].sum()
    a=p[(p["tech"]=="aluminium-primary-production-alternative")&(p["year"]==y)]["output"].sum()
    print("%d  ref %8.2f x1.8419 = %8.2f | alt %8.2f x1.4447 = %8.2f | TOTAL %8.2f"
          %(y,r,r*1.841858,a,a*1.444697,r*1.841858+a*1.444697))
print("\nmodel currently books 2050 aluminium CO2 = 0.000")
