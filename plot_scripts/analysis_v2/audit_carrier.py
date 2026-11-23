"""Audit a commodity node: who supplies it, who consumes it, and which of them
book an atmospheric emission. Used to detect carbon counted at more than one
step of the same chain.

    python analysis_v2\\audit_carrier.py CH4
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
import pandas as pd, numpy as np, spine_io as sio, model as M
pd.set_option('display.width', 230); pd.set_option('display.max_rows', 400)

CARRIER = sys.argv[1] if len(sys.argv) > 1 else 'CH4'
PERIOD = int(sys.argv[2]) if len(sys.argv) > 2 else 2030

icon = sio.connect(os.path.join(ROOT, 'INPUT_Final_SpineOpt_Model.tiny.summer_co2rebuild.sqlite'))
rcon = sio.connect(os.path.join(ROOT, 'RESULTS_Investment_Results.summer_co2rebuild.sqlite'))
ym, w = M.temporal_structure(icon)
uf = M.unit_flows(rcon, ym, w)
uf['carrier'] = uf['node'].astype(str).str.rsplit('_', n=1).str[0]

atm = (uf[(uf['node'] == 'atmosphere') & (uf['direction'] == 'to_node')]
       .groupby(['unit', 'period'])['value_annual'].sum())

f = uf[(uf['carrier'] == CARRIER) & (uf['period'] == PERIOD)]
sup = f[f['direction'] == 'to_node'].groupby('unit')['value_annual'].sum()
con = f[f['direction'] == 'from_node'].groupby('unit')['value_annual'].sum()

def table(s, label):
    d = pd.DataFrame({label: s})
    d['atmosphere_emission'] = [atm.get((u, PERIOD), 0.0) for u in d.index]
    d['emission_per_' + CARRIER] = d['atmosphere_emission'] / d[label]
    d['books_emission'] = d['atmosphere_emission'] > 1e-9
    return d.sort_values(label, ascending=False)

print(f'### {PERIOD}: units SUPPLYING {CARRIER}_* nodes')
ts = table(sup, CARRIER + '_supplied')
print(ts.head(20).round(4).to_string())
print(f'\n total supplied            {sup.sum():,.1f}')
print(f' emissions booked by suppliers (full) {ts.loc[ts["books_emission"], "atmosphere_emission"].sum():,.1f}')
print(f' supplied by units that book an emission {ts.loc[ts["books_emission"], CARRIER + "_supplied"].sum():,.1f}')

print(f'\n### {PERIOD}: units CONSUMING {CARRIER}_* nodes')
tc = table(con, CARRIER + '_consumed')
print(tc.head(25).round(4).to_string())
print(f'\n total consumed            {con.sum():,.1f}')
print(f' consumed by units that ALSO book an emission {tc.loc[tc["books_emission"], CARRIER + "_consumed"].sum():,.1f}')

overlap = tc.loc[tc['books_emission'], CARRIER + '_consumed'].sum()
supplier_booked = ts.loc[ts['books_emission'], CARRIER + '_supplied'].sum()
print(f'\n>>> {CARRIER} that passes a booking supplier AND a booking consumer is counted twice.')
print(f'    supplied by booking units : {supplier_booked:,.1f} of {sup.sum():,.1f}'
      f'  ({supplier_booked / max(sup.sum(), 1e-9):.1%})')
print(f'    consumed by booking units : {overlap:,.1f} of {con.sum():,.1f}'
      f'  ({overlap / max(con.sum(), 1e-9):.1%})')
