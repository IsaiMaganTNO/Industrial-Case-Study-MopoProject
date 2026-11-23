import re, sqlite3, sys
from collections import Counter
DB = sys.argv[1] if len(sys.argv) > 1 else ".spinetoolbox/items/ines_db/INES_DB.sqlite"
CC = ["DE", "DK", "NO", "UK"]
con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True); cur = con.cursor()
ents = cur.execute("SELECT e.name, c.name FROM entity e JOIN entity_class c ON e.class_id=c.id").fetchall()
print("entities", len(ents))
pv = cur.execute("""SELECT e.name, pd.name FROM parameter_value v JOIN entity e ON v.entity_id=e.id
  JOIN parameter_definition pd ON v.parameter_definition_id=pd.id""").fetchall()
def m(cc, n): return re.search(rf"(^|[_\-]){cc}($|[_\-])", n)
keys = {"heat": r"space|water|heat|DH", "transport": r"road|car|truck|bus|van|maritime|aviation|rail|transport|vehicle",
        "industry": r"cement|steel|chemical|glass|paper|wood|ammonia|industr", "bio": r"bio", "hydro": r"hydro|reservoir|ror|PHS"}
for cc in CC + ["BEC1"]:
    ce = [(n, c) for n, c in ents if m(cc, n)]
    print(f"\n### {cc}: {len(ce)} entities;", dict(Counter(c for _, c in ce).most_common(8)))
    print("   sectors:", {k: sum(1 for n, _ in ce if re.search(rx, n, re.I)) for k, rx in keys.items()})
    cp = Counter(p for n, p in pv if m(cc, n))
    print(f"   {sum(cp.values())} values:", dict(cp.most_common(10)))
    print("   bio params:", dict(Counter(p for n, p in pv if m(cc, n) and "bio" in n.lower())))
print("\n### atmosphere")
for r in cur.execute("""SELECT e.name, pd.name, a.name, v.value FROM parameter_value v JOIN entity e ON v.entity_id=e.id
  JOIN parameter_definition pd ON v.parameter_definition_id=pd.id JOIN alternative a ON v.alternative_id=a.id
  WHERE e.name LIKE '%atmosphere%'"""):
    s = r[3].decode(errors="replace") if isinstance(r[3], bytes) else str(r[3]); print("  ", r[0], r[1], r[2], s[:200])
