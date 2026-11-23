import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
import pandas as pd, numpy as np, spine_io as sio, model as M
pd.set_option('display.width', 230); pd.set_option('display.max_rows', 200)

icon = sio.connect(os.path.join(ROOT, 'INPUT_Final_SpineOpt_Model.tiny.summer_co2rebuild.sqlite'))
rcon = sio.connect(os.path.join(ROOT, 'RESULTS_Investment_Results.summer_co2rebuild.sqlite'))
ym, w = M.temporal_structure(icon)
uf = M.unit_flows(rcon, ym, w)
uf['carrier'] = uf['node'].astype(str).str.rsplit('_', n=1).str[0]
atmc = M.atmosphere_coefficients(icon)
booking = set(atmc['unit'])

print('### does CCGT / OCGT have an atmosphere relationship at all in the INPUT db?')
for pat in ['CCGT-existing_BEC6', 'OCGT_NLC3', 'CCGT_NLC5', 'LNG-terminal_BEC4', '(NG)PEA_BEC4']:
    print(f'  {pat:22s} atmosphere relationship: {pat in booking}')

print()
print('### HC chain (refinery products)')
hc = uf[uf['carrier'] == 'HC']
for p in [2030, 2050]:
    s = hc[(hc['direction'] == 'to_node') & (hc['period'] == p)].groupby('unit')['value_annual'].sum()
    c = hc[(hc['direction'] == 'from_node') & (hc['period'] == p)].groupby('unit')['value_annual'].sum()
    print(f'\n-- {p} --')
    print(f'  suppliers booking an emission : '
          f'{s[[u in booking for u in s.index]].sum():,.0f} of {s.sum():,.0f} supplied')
    print(f'  consumers booking an emission : '
          f'{c[[u in booking for u in c.index]].sum():,.0f} of {c.sum():,.0f} consumed')
    top = c.sort_values(ascending=False).head(6)
    print('  top consumers:', [(u, round(v), u in booking) for u, v in top.items()])

print()
print('### coal chain (BF-BOF)')
coal = uf[uf['carrier'] == 'coal']
s = coal[coal['direction'] == 'to_node'].groupby(['unit', 'period'])['value_annual'].sum()
c = coal[coal['direction'] == 'from_node'].groupby(['unit', 'period'])['value_annual'].sum()
print('  suppliers:', [(u, p, round(v), u in booking) for (u, p), v in s.items() if v > 1][:6])
print('  consumers:', [(u, p, round(v), u in booking) for (u, p), v in c.items() if v > 1][:8])

print()
print('### domestic gas extraction (never used?)')
ge = uf[uf['unit'].astype(str).str.startswith('gas-extraction')]
print(ge.groupby(['direction', 'period'])['value_annual'].sum().to_string())
