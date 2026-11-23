import sqlite3
def snap(db):
    c=sqlite3.connect("file:%s?mode=ro"%db,uri=True)
    d={r[0]:(r[1],r[2]) for r in c.execute("""
       SELECT pv.id, cast(pv.value as text), typeof(pv.value)
       FROM parameter_value pv""")}
    c.close(); return d
A=snap(r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.sqlite")
B=snap(r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite")
print("rows A=%d B=%d"%(len(A),len(B)))
diff=[k for k in A if k in B and A[k]!=B[k]]
print("changed rows:",len(diff))
c=sqlite3.connect(r"checkpoints\Final_SpineOpt_Model.tiny.7day.biocap365.retireall.hcco2.co2div365.sqlite")
for k in diff:
    r=c.execute("""SELECT e.name,pd.name FROM parameter_value pv
      JOIN parameter_definition pd ON pd.id=pv.parameter_definition_id
      JOIN entity e ON e.id=pv.entity_id WHERE pv.id=?""",(k,)).fetchone()
    print("  ",r,"| type",A[k][1],"->",B[k][1])
c.close()
print("added/removed:",set(A)^set(B))
