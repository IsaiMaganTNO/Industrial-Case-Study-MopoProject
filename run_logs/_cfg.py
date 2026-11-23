import yaml
c=yaml.safe_load(open(r"Pan-European-Framework-Energy-System-Planning\src\_planning-input-processsing\scenario_config.yml"))
rp=c["renewable_potentials"]
print("include_onshore_potential_limitations:",rp["include_onshore_potential_limitations"])
print("onshore_potentials:",rp["onshore_potentials"])
for t in rp["max_capacity_history"]:
    d=rp["max_capacity_history"][t]
    print(f"  {t}: BE={d.get('BE')} NL={d.get('NL')}  (keys are countries, n={len(d)})")
