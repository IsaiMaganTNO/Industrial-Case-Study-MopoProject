"""Quantify fuel carbon that is booked as an emission at more than one step of
the same supply chain.

Convention check: this model books the carbon content of fossil methane at the
*supply* step (`LNG-terminal`, 0.2 per unit delivered). Power units rely on that
and book nothing. Several industrial units book their own combustion emission on
top, at essentially the same factor.

    python analysis_v2\\audit_double_fuel.py
"""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
ROOT = os.path.dirname(HERE)
import pandas as pd, numpy as np, spine_io as sio, model as M
pd.set_option('display.width', 240); pd.set_option('display.max_rows', 400)

icon = sio.connect(os.path.join(ROOT, 'INPUT_Final_SpineOpt_Model.tiny.summer_co2rebuild.sqlite'))
rcon = sio.connect(os.path.join(ROOT, 'RESULTS_Investment_Results.summer_co2rebuild.sqlite'))
ym, w = M.temporal_structure(icon)
uf = M.unit_flows(rcon, ym, w)
uf['carrier'] = uf['node'].astype(str).str.rsplit('_', n=1).str[0]

atm = (uf[(uf['node'] == 'atmosphere') & (uf['direction'] == 'to_node')]
       .groupby(['unit', 'period'])['value_annual'].sum())

print('=' * 100)
print('PART 1 - which fossil carriers carry an emission already booked at the supply step?')
print('=' * 100)
rows = []
for carrier in M.FOSSIL_CARRIERS:
    f = uf[uf['carrier'] == carrier]
    if f.empty:
        continue
    sup = f[f['direction'] == 'to_node'].groupby(['unit', 'period'])['value_annual'].sum()
    if sup.empty:
        continue
    for (u, p), v in sup.items():
        e = atm.get((u, p), 0.0)
        if v > 1e-6:
            rows.append({'carrier': carrier, 'supplier': u, 'period': p,
                         'supplied': v, 'emission_at_supply': e, 'factor': e / v})
sup_df = pd.DataFrame(rows)
by = (sup_df.groupby(['carrier', 'period'])
      .agg(supplied=('supplied', 'sum'), emission_at_supply=('emission_at_supply', 'sum')))
by['implied_supply_factor'] = by['emission_at_supply'] / by['supplied']
print(by.round(4).to_string())

print()
print('=' * 100)
print('PART 2 - CH4: carbon booked at the terminal AND again at the consumer')
print('=' * 100)
SUPPLY_FACTOR = 0.2    # LNG-terminal__atmosphere coefficient in the input DB

ch4 = uf[uf['carrier'] == 'CH4']
con = ch4[ch4['direction'] == 'from_node'].groupby(['unit', 'period'])['value_annual'].sum()
d = pd.DataFrame({'ch4_consumed': con})
d['own_emission'] = [atm.get(k, 0.0) for k in d.index]
d['ch4_carbon_already_booked'] = d['ch4_consumed'] * SUPPLY_FACTOR
d['duplicate'] = np.minimum(d['own_emission'], d['ch4_carbon_already_booked'])
d['emission_per_ch4'] = d['own_emission'] / d['ch4_consumed']
d = d[d['ch4_consumed'] > 1.0]

print('\n-- consumers that book NOTHING (consistent with the supply-step convention) --')
none = d[d['own_emission'] <= 1e-9]
print(none.groupby(level='period')['ch4_consumed'].agg(['count', 'sum']).round(1).to_string())
print('  examples:', sorted({u for u, _ in none.index})[:8])

print('\n-- consumers that book their own emission ON TOP (top 15 by duplicate) --')
booking = d[d['own_emission'] > 1e-9].sort_values('duplicate', ascending=False)
print(booking.head(15).round(3).to_string())

print('\n-- duplicate per period --')
summary = booking.groupby(level='period')[['ch4_consumed', 'own_emission', 'duplicate']].sum()
tot_supply_em = (sup_df[sup_df['carrier'] == 'CH4']
                 .groupby('period')['emission_at_supply'].sum())
gross = (uf[(uf['node'] == 'atmosphere') & (uf['direction'] == 'to_node')]
         .groupby('period')['value_annual'].sum())
summary['emission_booked_at_terminals'] = tot_supply_em
summary['gross_emissions_all_sources'] = gross
summary['duplicate_pct_of_gross'] = summary['duplicate'] / summary['gross_emissions_all_sources'] * 100
print(summary.round(2).to_string())

print()
print('=' * 100)
print('PART 3 - where does methane actually come from?')
print('=' * 100)
src = (ch4[ch4['direction'] == 'to_node']
       .assign(tech=lambda x: x['unit'].map(M.tech_of))
       .groupby(['tech', 'period'])['value_annual'].sum().unstack('period').fillna(0.0))
print(src[src.sum(axis=1) > 0].round(1).to_string())
