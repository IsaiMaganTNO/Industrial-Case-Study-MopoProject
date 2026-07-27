"""
inspect_storage_state.py -- read-only diagnostic (originally HOTFIX-03)

Adapted 2026-07-22 for SpineOpt v1.0.0 schema:
  has_state           -> storage_active
  is_longterm_storage -> storage_longterm_active
  initial_node_state  -> storage_state_initial
  fix_node_state      -> storage_state_fix

Prints, for every node with `storage_active = True` in the given SpineOpt DB:
- `storage_longterm_active` value (if set)
- Whether `storage_state_initial` and/or `storage_state_fix` are set
- Every `node__temporal_block(node, tb)` association, its `cyclic_condition`
  value, and what kind of block `tb` is (representative period, `all_rps`,
  operations year, or something else).

Purpose: sanity-check the DB state that is produced by `scenario_run.py`
after `HOTFIX-02` is applied, and detect any storage node that is still
in the trap that used to cause the SpineOpt `constraint_cyclic_node_state`
`KeyError` in v0.11.1 (long-term storage + `cyclic_condition = True` on a
non-representative temporal block, when representative periods are in use).
With v1.0.0 the underlying SpineOpt bug is expected to be fixed but this
diagnostic remains a useful DB integrity check.

Usage (from the repo root, using the project's Python env):

    C:\\Users\\maganih\\Documents\\spinetools\\environments\\penv\\Scripts\\python.exe ^
        _planning-input-processsing\\inspect_storage_state.py ^
        "sqlite:///.spinetoolbox/items/spineopt_final_db/SpineOpt_final_DB.sqlite"

This script never writes to the database.
"""

import sys
from collections import defaultdict

from spinedb_api import DatabaseMapping


REP_PREFIX = "representative_period"
OPS_PREFIX = "operations_"
ALL_RPS = "all_rps"


def _classify_block(tb_name, rep_members):
    if tb_name == ALL_RPS:
        return "all_rps (representative group)"
    if tb_name in rep_members:
        return "member of all_rps group"
    if tb_name.startswith(REP_PREFIX):
        return "representative_period_*"
    if tb_name.startswith(OPS_PREFIX):
        return "operations_yXXXX (non-representative)"
    return "other"


def _parsed(value_item):
    if value_item is None:
        return None
    return value_item.get("parsed_value")


def main(url):
    with DatabaseMapping(url) as db:
        # Nodes with storage_active=True (v1.0.0; formerly has_state)
        has_state_nodes = []
        for pv in db.get_parameter_value_items(
            entity_class_name="node", parameter_definition_name="storage_active"
        ):
            if bool(pv["parsed_value"]):
                has_state_nodes.append(pv["entity_byname"][0])
        has_state_nodes = sorted(set(has_state_nodes))

        if not has_state_nodes:
            print("No nodes with storage_active=True found.")
            return

        # Membership of all_rps group -> members it contains (so we can
        # classify per-block correctly).
        rep_members = set()
        for grp in db.get_entity_group_items(entity_class_name="temporal_block"):
            if grp.get("group_name") == ALL_RPS:
                rep_members.add(grp.get("member_name"))

        # is_representative flag per temporal_block (if present in this DB).
        is_representative = {}
        for pv in db.get_parameter_value_items(
            entity_class_name="temporal_block",
            parameter_definition_name="is_representative",
        ):
            is_representative[pv["entity_byname"][0]] = bool(pv["parsed_value"])

        # cyclic_condition values keyed by (node, temporal_block)
        cyclic_by_pair = defaultdict(list)
        for pv in db.get_parameter_value_items(
            entity_class_name="node__temporal_block",
            parameter_definition_name="cyclic_condition",
        ):
            key = tuple(pv["entity_byname"])
            cyclic_by_pair[key].append((pv["alternative_name"], bool(pv["parsed_value"])))

        # All node__temporal_block associations grouped by node
        assoc_by_node = defaultdict(list)
        for ent in db.get_entity_items(entity_class_name="node__temporal_block"):
            n, tb = ent["entity_byname"]
            assoc_by_node[n].append(tb)

        # Per-node summary
        trap_hits = []  # (node, tb) pairs still in the SpineOpt trap
        for node in has_state_nodes:
            print("=" * 72)
            print(f"Node: {node}")

            longterm = _parsed(
                db.get_parameter_value_item(
                    entity_class_name="node",
                    entity_byname=(node,),
                    parameter_definition_name="storage_longterm_active",
                    alternative_name="Base",
                )
            )
            print(f"  storage_longterm_active : {longterm}")

            init_state = db.get_parameter_value_item(
                entity_class_name="node",
                entity_byname=(node,),
                parameter_definition_name="storage_state_initial",
                alternative_name="Base",
            )
            fix_state = db.get_parameter_value_item(
                entity_class_name="node",
                entity_byname=(node,),
                parameter_definition_name="storage_state_fix",
                alternative_name="Base",
            )
            print(f"  storage_state_initial   : {'set' if init_state else 'unset'}")
            print(f"  storage_state_fix       : {'set' if fix_state else 'unset'}")

            tbs = sorted(assoc_by_node.get(node, []))
            if not tbs:
                print("  node__temporal_block: (none)")
                continue

            print("  node__temporal_block associations:")
            for tb in tbs:
                klass = _classify_block(tb, rep_members)
                cyc_rows = cyclic_by_pair.get((node, tb), [])
                if cyc_rows:
                    cyc_str = ", ".join(f"{alt}={val}" for alt, val in cyc_rows)
                else:
                    cyc_str = "unset"
                rep_flag = is_representative.get(tb)
                rep_str = "" if rep_flag is None else f"  is_representative={rep_flag}"
                print(f"    - {tb:<40s} [{klass}]  cyclic_condition: {cyc_str}{rep_str}")

                # Detect the SpineOpt trap: long-term storage with cyclic on a
                # non-representative operations block, while rep periods exist
                # in the DB.
                is_ops = tb.startswith(OPS_PREFIX)
                has_true_cyclic_on_pair = any(val for _, val in cyc_rows)
                if bool(longterm) and is_ops and has_true_cyclic_on_pair:
                    trap_hits.append((node, tb))

        # Summary
        print("=" * 72)
        print("Summary")
        print(f"  Nodes with storage_active=True ............... {len(has_state_nodes)}")
        print(f"  all_rps group members (rep-period blocks) .... {len(rep_members)}")
        rep_period_blocks_present = any(m.startswith(REP_PREFIX) for m in rep_members)
        print(f"  Representative periods present in DB ......... {rep_period_blocks_present}")

        if trap_hits:
            print()
            print("  WARNING: SpineOpt cyclic_node_state KeyError trap:")
            print("  (long-term storage + cyclic_condition=True on operations_yXXXX)")
            for n, tb in trap_hits:
                print(f"    - node={n}  temporal_block={tb}")
            print()
            print("  These pairs will trigger the KeyError at")
            print("  SpineOpt/src/constraints/constraint_cyclic_node_state.jl.")
            print("  Rerun scenario_run after HOTFIX-02 to clear them.")
        else:
            print("  No storage node currently in the SpineOpt cyclic trap.")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(
            "Usage: inspect_storage_state.py <spineopt_db_url>\n"
            "Example:\n"
            "  inspect_storage_state.py sqlite:///.spinetoolbox/items/spineopt_final_db/SpineOpt_final_DB.sqlite"
        )
    main(sys.argv[1])
