import sqlite3
def xb(db):
    c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
    rows=c.execute("""SELECT e.name,cast(pv.value as text) FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id
      JOIN entity_class ec ON ec.id=e.class_id
      WHERE pd.name='investment_count_initial_cumulative'
        AND ec.name='connection'""").fetchall()
    t=0.0; n=0
    for name,v in rows:
        try: t+=float(v); n+=1
        except Exception: pass
    c.close(); return n,t
a=xb(r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.sqlite")
b=xb(r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite")
print("pre-patch  rows=%d sum=%.3f"%a)
print("post-patch rows=%d sum=%.3f"%b)
print("IDENTICAL" if a==b else "*** DIFFERS ***")
