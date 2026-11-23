import ast, io, sys

P = "data-pipelines/europe/_power/power_DB.py"
src = open(P, encoding="utf-8").read()
orig = src
NL = "\n"

# --- FIX 1: the quoted-literal date lookups -------------------------------
old1 = (
    '    try:' + NL +
    '        datein_ppm = float("DateIn")' + NL +
    '    except:' + NL +
    '        datein_ppm = None' + NL +
    '    try:' + NL +
    '        dateout_ppm = float("DateOut")' + NL +
    '    except:' + NL +
    '        dateout_ppm = None' + NL
)
new1 = (
    '    # FIX (2026-10-08): these previously read float("DateIn") /' + NL +
    '    # float("DateOut"), i.e. the literal column *name*, which always raised' + NL +
    '    # ValueError and forced both to None for every plant. That sent 100% of' + NL +
    '    # units down the random-retirement branch of decay_capacity().' + NL +
    '    # See docs/FINDING_random_retirement_dates.md' + NL +
    '    try:' + NL +
    '        datein_ppm = float(unit_ppm["DateIn"])' + NL +
    '    except (KeyError, TypeError, ValueError):' + NL +
    '        datein_ppm = None' + NL +
    '    try:' + NL +
    '        dateout_ppm = float(unit_ppm["DateOut"])' + NL +
    '    except (KeyError, TypeError, ValueError):' + NL +
    '        dateout_ppm = None' + NL
)
assert src.count(old1) == 1, "FIX1 anchor count=%d" % src.count(old1)
src = src.replace(old1, new1)

# --- FIX 2: wrong dict key in decay_capacity ------------------------------
old2 = '            if int(milestoneyear[1:]) < int(float(unit["DateIn"])) + int('
new2 = (
    '            # FIX (2026-10-08): was unit["DateIn"] - a key absent from this' + NL +
    '            # dict (it is "date_in"). Latent KeyError, never reached while' + NL +
    '            # date_in was always None.' + NL +
    '            if int(milestoneyear[1:]) < int(float(unit["date_in"])) + int('
)
assert src.count(old2) == 1, "FIX2 anchor count=%d" % src.count(old2)
src = src.replace(old2, new2)

# --- FIX 3: seed the RNG --------------------------------------------------
old3 = 'import random' + NL
new3 = (
    'import random' + NL +
    NL +
    '# FIX (2026-10-08): seed so any residual random branch is reproducible.' + NL +
    'random.seed(20261008)' + NL
)
assert src.count(old3) == 1, "FIX3 anchor count=%d" % src.count(old3)
src = src.replace(old3, new3, 1)

ast.parse(src)
open(P, "w", encoding="utf-8", newline="\n").write(src)
print("OK bytes %d -> %d" % (len(orig), len(src)))
