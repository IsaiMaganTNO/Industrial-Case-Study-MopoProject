import pandas as pd
d='EU_case_updated_results/baseline_csv/'
u=pd.read_csv(d+'unit_to_flows.csv',index_col=0); u=u[u.polygon.isin(['NL','BE'])]
Y=['y2030','y2040','y2050']
EL={'Offshore Wind':'Offshore wind','Onshore Wind':'Onshore wind','Solar':'Solar PV','Nuclear':'Nuclear','Combined-cycle Gas Turbine':'Gas power','Open-cycle Gas Turbine':'Gas power'}
H2={'Electrolyzer':'Electrolysis','LH2-terminal':'LH2 import terminal','Steam Methane Reforming':'Gas reforming'}
rows=[]
for nd,m,k in [('electricity',EL,'EL'),('hydrogen',H2,'H2')]:
    s=u[u.node==nd].copy(); s['item']=s.technology.map(m).fillna('Other')
    g=s.groupby(['polygon','item'])[Y].sum()/1000
    for (c,i),r in g.iterrows():
        for y in Y: rows.append(('EU baseline',k,c,int(y[1:]),i,r[y]))
eu=pd.DataFrame(rows,columns=['run','kind','country','year','item','twh'])
ours=[]
for f,k in [('A1_electricity_generation.csv','EL'),('A2_hydrogen_supply.csv','H2')]:
    a=pd.read_csv('results_2050_analysis/data/'+f); a['kind']=k; a['run']=a['label']; ours.append(a[['run','kind','country','year','item','twh']])
df=pd.concat([eu]+ours)
p=df.pivot_table(index=['kind','country','item'],columns=['year','run'],values='twh',aggfunc='sum').round(0)
pd.set_option('display.width',300,'display.max_columns',30,'display.max_rows',200)
for y in [2030,2040,2050]:
    print('=====',y); print(p[y].loc[lambda x:(x.abs().sum(axis=1)>0.5)])
df.to_csv('results_2050_analysis/data/EU_baseline_comparison.csv',index=False)
