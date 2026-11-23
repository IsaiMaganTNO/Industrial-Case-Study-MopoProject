# Direct behavioural proof of the L1489/L1493 defect.
for lit in ["DateIn", "DateOut"]:
    try:
        v = float(lit)
        print(lit, "->", v)
    except Exception as e:
        print('float("%s") RAISES %s: %s  => None' % (lit, type(e).__name__, e))
print()
# Therefore both keys are always None, regardless of source data:
import csv
rows = list(csv.DictReader(open("data/Energy_Conversion/powerplants.csv",
            newline="", encoding="utf-8", errors="replace")))
nlbe = [r for r in rows if r["Country"] in ("Belgium", "Netherlands")]
pop_in = sum(1 for r in nlbe if (r["DateIn"] or "").strip())
pop_out = sum(1 for r in nlbe if (r["DateOut"] or "").strip())
print("NL+BE plants:", len(nlbe))
print("  with DateIn  populated in SOURCE:", pop_in)
print("  with DateOut populated in SOURCE:", pop_out)
print("  reaching pipeline as non-None   : 0  (both forced None by the bug)")
print()
print("=> 100% of plants take the random branch.")
