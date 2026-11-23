import sys, pickle, re, types
sys.path.insert(0, "tools")
src = open(r"tools\postprocess.py", encoding="utf8").read()
assert src.count('if bn[2] == "atmosphere":') == 1
src = src.replace('if bn[2] == "atmosphere":', 'if bn[2].startswith("atmosphere"):')
src = src.replace('if node == "atmosphere":', 'if node.startswith("atmosphere"):')
PP = types.ModuleType("pp_patched"); PP.__file__ = r"tools\postprocess.py"; exec(compile(src, "pp_patched", "exec"), PP.__dict__)
o = open(r"run_logs\_ctryco2_load.out", "w", encoding="utf8")
for tag, R in [("ctryco2_mr", r"runs\ctryco2_mr"), ("ctryco2B_mr", r"runs\ctryco2B_mr")]:
    name = f"{tag}_ccslow_ccu_cap16_dac0"
    wmap = PP.load_weights(rf"{R}\Final_SpineOpt_Model.tiny.3day.{name}.sqlite")
    d = PP.load(rf"{R}\output\Investment_Results.{name}.sqlite", wmap=wmap)
    pickle.dump(d, open(rf"run_logs\{name}.pkl", "wb"))
    e = d["emis"]; o.write(f"{name} rows emis {len(e)} co2pipe {len(d['co2pipe'])} supply {len(d['supply'])}\n")
    o.write(str(e.groupby(["year", e.region.str[:2]]).co2.sum().div(1e3).round(2).to_dict()) + "\n")
    o.write("obj " + str(d["obj"].to_dict()) + "\n"); o.flush()
o.close()
