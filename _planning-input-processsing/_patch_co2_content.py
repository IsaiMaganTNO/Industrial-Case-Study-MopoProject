"""Patch INES DB: add co2_content to polygon-specific fossil nodes.

Root cause: the pipeline sets co2_content on GLOBAL commodities
(CH4=0.2, HC=0.24, coal=0.35, etc.) and on external-country nodes
(CH4_UK, HC_FR, etc.), but NOT on the per-polygon fossil nodes
(CH4_BEC*, CH4_NLC*, HC_BEC*, HC_NLC*, etc.). Because
ines_to_spineopt.process_emissions() looks up co2_content on nodes to
decide which units to attach to atmosphere, all BE+NL units consuming
these fossil nodes end up with no emission tracking — that's why the
model reports ~11 Mt/yr total emissions instead of ~230 Mt/yr.

This script backfills the missing co2_content values so that the
downstream ines_to_spineopt run generates the emission-tracking
constraints for gas-boilers, oil-eng, CCGT, and industrial units that
were previously silent.

After running this patch, re-run the pipeline FROM ines_to_spineopt onwards:
  ines_to_spineopt -> planning_setup -> Merger -> clustering (3 stages)
  -> scenario_run -> Run SpineOpt -> visualization -> generate_report
"""
from spinedb_api import DatabaseMapping, to_database

INES_URL = 'sqlite:///c:/Users/maganih/Documents/Industrial-Case-Study-MopoProject/.spinetoolbox/items/ines_db/ines_db.sqlite'

# Emission factors (tCO2 / MWh_th) - matches values in
# data-pipelines/europe/_commodities/commodity_data.csv and
# data-pipelines/europe/_heat/heat_DB.py
CO2_FACTORS = {
    "CH4":        0.20,   # natural gas (methane)
    "HC":         0.24,   # light oil / hydrocarbons
    "coal":       0.35,   # bituminous coal
    "crude":      0.26,   # crude oil
    "waste":      0.30,   # fossil non-renewable waste
    "MeOH":       0.20,   # methanol (fossil-derived)
    "fossil-CH4": 0.20,
    "fossil-HC":  0.24,
}


def main():
    added = 0
    already = 0
    with DatabaseMapping(INES_URL) as db:
        # Find all nodes and their existing co2_content
        existing = set()
        for p in db.get_parameter_value_items(
            entity_class_name="node", parameter_definition_name="co2_content"
        ):
            existing.add(p["entity_byname"][0])

        # For each polygon-specific fossil node, backfill co2_content
        for n in db.get_entity_items(entity_class_name="node"):
            name = n["name"]
            if name in existing:
                already += 1
                continue
            # Match "<fuel>_<polygon>" pattern (e.g., CH4_BEC1, HC_NLC5)
            # Prefer longest prefix match to handle fossil-CH4_X before CH4_X.
            best_prefix = None
            for fuel in sorted(CO2_FACTORS, key=len, reverse=True):
                if name.startswith(fuel + "_"):
                    best_prefix = fuel
                    break
            if best_prefix is None:
                continue

            co2 = CO2_FACTORS[best_prefix]
            db_value, value_type = to_database(co2)
            _, err = db.add_parameter_value_item(
                entity_class_name="node",
                entity_byname=(name,),
                parameter_definition_name="co2_content",
                alternative_name="Base",
                value=db_value,
                type=value_type,
            )
            if err:
                # Some nodes may not be able to accept parameters directly — skip.
                print(f"  skip {name}: {err}")
                continue
            added += 1
            print(f"  {name:35s}  <-  co2_content = {co2}  (matched prefix {best_prefix!r})")

        try:
            db.commit_session("Backfill co2_content on polygon-specific fossil nodes")
        except Exception as e:
            print(f"commit error: {e}")
            return

    print()
    print(f"Summary: added co2_content to {added} nodes; {already} already had it.")


if __name__ == "__main__":
    main()
