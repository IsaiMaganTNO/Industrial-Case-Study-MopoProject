"""Quick structural summary of a Spine database.

Usage: python tools/inspect_db.py <sqlite-path-or-url> [--top N]

Used between pipeline steps to confirm a step produced what it should, rather
than discovering a silent keying or scoping bug hours later in the solve.
"""

import collections
import sys
from pathlib import Path

from spinedb_api import DatabaseMapping


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    top = 40
    if "--top" in sys.argv:
        top = int(sys.argv[sys.argv.index("--top") + 1])
    if not args:
        print(__doc__)
        return 1
    target = args[0]
    url = target if "://" in target else "sqlite:///" + str(Path(target).resolve())

    with DatabaseMapping(url) as db:
        ents = db.get_entity_items()
        vals = db.get_parameter_value_items()
        alts = [a["name"] for a in db.get_alternative_items()]
        print("url        : %s" % url)
        print("entities   : %d" % len(ents))
        print("values     : %d" % len(vals))
        print("alternatives (%d): %s" % (len(alts), ", ".join(sorted(alts))))

        counts = collections.Counter(e["entity_class_name"] for e in ents)
        print("")
        print("entity classes (%d):" % len(counts))
        for name, n in sorted(counts.items(), key=lambda x: -x[1])[:top]:
            print("  %-40s %6d" % (name, n))

        vcounts = collections.Counter(v["parameter_definition_name"] for v in vals)
        print("")
        print("top parameters:")
        for name, n in sorted(vcounts.items(), key=lambda x: -x[1])[:top]:
            print("  %-40s %6d" % (name, n))
    return 0


if __name__ == "__main__":
    sys.exit(main())
