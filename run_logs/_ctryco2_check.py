import sqlite3, glob
a = glob.glob(r"final_runs_pessimistic_ccs\3_MixedRes_NLBE17zones_plus_DE_DK_NO_UK\input\*.sqlite")[0]
b = r"runs\ctryco2_mr\Final_SpineOpt_Model.tiny.3day.ctryco2_mr_ccslow_ccu_cap16_dac0.sqlite"
def snap(p):
    c = sqlite3.connect(p)
    pv = c.execute("select e.name, pd.name, al.name, pv.value from parameter_value pv join entity e on e.id=pv.entity_id join parameter_definition pd on pd.id=pv.parameter_definition_id join alternative al on al.id=pv.alternative_id").fetchall()
    en = c.execute("select ec.name, e.name from entity e join entity_class ec on ec.id=e.class_id").fetchall()
    sc = c.execute("select s.name, a.name, sa.rank from scenario_alternative sa join scenario s on s.id=sa.scenario_id join alternative a on a.id=sa.alternative_id").fetchall()
    return set(pv), set(en), set(sc)
A, B = snap(a), snap(b)
o = open(r"run_logs\_ctryco2_check.out", "w", encoding="utf8"); P = lambda *x: print(*x, file=o)
norm = lambda s: s.replace("atmosphere_NL","atmosphere").replace("atmosphere_BE","atmosphere").replace("atmosphere_DE","atmosphere").replace("atmosphere_DK","atmosphere").replace("atmosphere_NO","atmosphere").replace("atmosphere_UK","atmosphere")
enA = A[1]; enB = {(c, norm(n)) for c, n in B[1]}
P("entities only in A", len(enA - enB), list(enA - enB)[:5]); P("entities only in B (normed)", len(enB - enA), list(enB - enA)[:5])
pvA = {x for x in A[0] if x[0] != "atmosphere"}; pvB = {(norm(x[0]),)+x[1:] for x in B[0] if not x[0].startswith("atmosphere_")}
P("pv diff non-atm", len(pvA ^ pvB)); P("pv counts", len(A[0]), len(B[0])); P("scenarios equal", A[2] == B[2])
o.close()

