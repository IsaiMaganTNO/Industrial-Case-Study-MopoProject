import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
import pandas as pd, spine_io as sio, model as M
pd.set_option('display.width', 220); pd.set_option('display.max_rows', 300)
pd.set_option('display.max_colwidth', 110)

icon = sio.connect(os.path.join(ROOT, 'INPUT_Final_SpineOpt_Model.tiny.summer_co2rebuild.sqlite'))
rcon = sio.connect(os.path.join(ROOT, 'RESULTS_Investment_Results.summer_co2rebuild.sqlite'))

TARGET = sys.argv[1] if len(sys.argv) > 1 else 'LNG-terminal'

print('=== INPUT: every relationship/parameter mentioning', TARGET, '===')
df, _ = sio.parameter_frame(icon, [
    'flow_ratio_equality_coefficient', 'capacity_per_unit', 'vom_cost', 'fom_cost',
    'unit_investment_cost', 'investment_count_initial_cumulative',
    'investment_count_max_cumulative', 'investment_count_fix_cumulative',
    'investment_count_fix_new', 'availability_factor', 'lifetime_technical'])
df['value'] = df['value'].map(lambda b: b.decode() if isinstance(b, (bytes, bytearray)) else b)
sub = df[df['entity_name'].astype(str).str.contains(TARGET, regex=False, na=False)]
one = sub[sub['entity_name'].astype(str).str.contains('BEC4', regex=False)]
print(one[['param', 'entity_name', 'value']].to_string(index=False))

print()
print('=== entity classes this unit appears in ===')
q = """select ec.name cls, e.name ename from entity e join entity_class ec on ec.id=e.class_id
       where e.name like ?"""
print(pd.read_sql(q, icon, params=('%' + TARGET + '%BEC4%',)).to_string(index=False))

print()
print('=== RESULTS: annual flows of every', TARGET, 'unit ===')
ym, w = M.temporal_structure(icon)
uf = M.unit_flows(rcon, ym, w)
t = uf[uf['unit'].astype(str).str.startswith(TARGET)]
agg = t.groupby(['unit', 'node', 'direction', 'period'])['value_annual'].sum().unstack(-1).fillna(0.0)
print(agg.round(1).to_string())
