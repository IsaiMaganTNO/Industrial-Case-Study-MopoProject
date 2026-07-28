"""Sanity check on the SpineOpt Investment_results_DB after a successful run.

Reports:
- Alternatives / scenarios present
- Which output parameters have values (with counts)
- Total invested capacity by class
- Non-zero investment count (units, connections, storages)
- A few example nodes' storage state (to confirm rep-period wiring)
- Total costs breakdown from objective term outputs
"""

from __future__ import annotations
import sys
from collections import defaultdict
from spinedb_api import DatabaseMapping

URL = "sqlite:///c:/Users/maganih/Documents/Industrial-Case-Study-MopoProject/.spinetoolbox/items/investment_results_db/Investment_results_DB.sqlite"


def main() -> int:
    with DatabaseMapping(URL) as db:
        # Alternatives / scenarios
        alts = [a["name"] for a in db.get_alternative_items()]
        scns = [s["name"] for s in db.get_scenario_items()]
        print(f"Alternatives  ({len(alts)}): {alts[:5]}{'...' if len(alts) > 5 else ''}")
        print(f"Scenarios     ({len(scns)}): {scns[:5]}{'...' if len(scns) > 5 else ''}")

        # Parameters written to the DB, with counts
        print("\n=== Output parameters and value counts ===")
        param_counts: dict[tuple[str, str], int] = defaultdict(int)
        for pv in db.get_parameter_value_items():
            key = (pv["entity_class_name"], pv["parameter_definition_name"])
            param_counts[key] += 1
        # Show only parameters with >0 values, ordered by count
        for (cls, name), n in sorted(param_counts.items(), key=lambda x: -x[1])[:30]:
            print(f"  {n:8d}  {cls}::{name}")

        # Investment counts
        print("\n=== Investments where >0 units/connections/storages were built ===")
        for pdef in ("units_invested_available", "connections_invested_available", "storages_invested_available"):
            hits = 0
            total_invested = 0.0
            examples: list[str] = []
            for pv in db.get_parameter_value_items(parameter_definition_name=pdef):
                pv_val = pv.get("parsed_value")
                # value may be a scalar or a time-series/map; try both
                try:
                    if pv_val is None:
                        continue
                    values = list(pv_val.values) if hasattr(pv_val, "values") else [pv_val]
                except Exception:
                    values = []
                max_v = max((float(v) for v in values if v is not None), default=0.0)
                if max_v > 1e-6:
                    hits += 1
                    total_invested += max_v
                    if len(examples) < 5:
                        ent = "/".join(pv["entity_byname"])
                        examples.append(f"{ent}={max_v:.2f}")
            print(f"  {pdef}: {hits} entities invested (>0), total={total_invested:.1f}")
            for e in examples:
                print(f"     e.g. {e}")

        # Iron-air storage state sanity
        print("\n=== Iron-air storage: node_state at a few time slices ===")
        for pv in db.get_parameter_value_items(parameter_definition_name="node_state"):
            n = pv["entity_byname"][0]
            if "iron-air" in n:
                pv_val = pv.get("parsed_value")
                if pv_val is None or not hasattr(pv_val, "values"):
                    continue
                vals = [float(v) for v in list(pv_val.values)[:3] if v is not None]
                if any(abs(v) > 1e-6 for v in vals):
                    print(f"  {n}  ({pv['alternative_name']}): first 3 values = {vals}")
                    break

        # Total costs from objective terms
        print("\n=== Total costs (from objective_terms) ===")
        cost_terms = [
            "unit_investment_costs",
            "connection_investment_costs",
            "storage_investment_costs",
            "fixed_om_costs",
            "variable_om_costs",
            "connection_flow_costs",
            "taxes",
            "total_costs",
        ]
        for term in cost_terms:
            values = db.get_parameter_value_items(parameter_definition_name=term)
            n = len(values)
            if n > 0:
                # Sum scalar values only (most cost terms are scalar per report/alternative)
                total = 0.0
                for pv in values:
                    pv_val = pv.get("parsed_value")
                    if pv_val is None:
                        continue
                    if isinstance(pv_val, (int, float)):
                        total += float(pv_val)
                    elif hasattr(pv_val, "values"):
                        total += sum(float(v) for v in pv_val.values if v is not None)
                print(f"  {term:<30s} count={n:<4d}  sum={total:.2f}")


if __name__ == "__main__":
    sys.exit(main())
