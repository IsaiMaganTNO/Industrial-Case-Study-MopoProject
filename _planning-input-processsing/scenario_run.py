import spinedb_api as api
from spinedb_api import DatabaseMapping
from spinedb_api.dataframes import to_dataframe
from spinedb_api.parameter_value import convert_map_to_table, IndexedValue
from sqlalchemy.exc import DBAPIError
import datetime
import pandas as pd
import sys
import numpy as np
import json
import yaml 
import time as time_lib

if len(sys.argv) > 1:
    url_spineopt = sys.argv[1]
else:
    exit("Please provide spineopt database url as argument. They should be of the form ""sqlite:///path/db_file.sqlite""")

def nested_index_names(value, names = None, depth = 0):
    if names is None:
        names = []
    if depth == len(names):
        names.append(value.index_name)
    elif value.index_name != names[-1]:
        raise RuntimeError(f"Index names at depth {depth} do no match: {value.index_name} vs. {names[-1]}")
    for y in value.values:
        if isinstance(y, IndexedValue):
            nested_index_names(y, names, depth + 1)
    return names

def update_parameter_value(db_map : DatabaseMapping, id_int : int, class_name : str,parameter : str,alternative : str,elements : tuple,value : any) -> None:
    db_value, value_type = api.to_database(value)
    _, error = db_map.update_parameter_value_item(id=id_int, entity_class_name=class_name,entity_byname=elements,parameter_definition_name=parameter,alternative_name=alternative,value=db_value,type=value_type)
    if error:
        raise RuntimeError(error)

def add_or_update_parameter_value(db_map : DatabaseMapping, class_name : str,parameter : str,alternative : str,elements : tuple,value : any) -> None:
    db_value, value_type = api.to_database(value)
    db_map.add_or_update_parameter_value(entity_class_name=class_name,entity_byname=elements,parameter_definition_name=parameter,alternative_name=alternative,value=db_value,type=value_type)

def add_entity_group(db_map : DatabaseMapping, class_name : str, group : str, member : str) -> None:
    _, error = db_map.add_entity_group_item(group_name = group, member_name = member, entity_class_name=class_name)
    if error is not None:
        raise RuntimeError(error)

def add_entity(db_map : DatabaseMapping, class_name : str, name : tuple, ent_description = None) -> None:
    _, error = db_map.add_entity_item(entity_byname=name, entity_class_name=class_name, description = ent_description)
    if error is not None:
        raise RuntimeError(error)

def add_entity_if_missing(db_map : DatabaseMapping, class_name : str, name : tuple, ent_description = None) -> None:
    """Like add_entity but silently no-ops if the entity already exists.

    Makes setup functions idempotent so scenario_run can be re-executed on an
    already-configured SpineOpt DB without having to reset from Merger.
    Only swallows RuntimeError (the 'already exists' error path); other errors
    still propagate.
    """
    try:
        add_entity(db_map, class_name, name, ent_description)
    except RuntimeError:
        pass

def add_parameter_value(db_map : DatabaseMapping,class_name : str,parameter : str,alternative : str,elements : tuple,value : any) -> None:
    db_value, value_type = api.to_database(value)
    _, error = db_map.add_parameter_value_item(entity_class_name=class_name,entity_byname=elements,parameter_definition_name=parameter,alternative_name=alternative,value=db_value,type=value_type)
    if error:
        raise RuntimeError(error)

def add_scenario(db_map : DatabaseMapping,name_scenario : str) -> None:
    _, error = db_map.add_scenario_item(name=name_scenario)
    if error is not None:
        raise RuntimeError(error)

def add_scenario_alternative(db_map : DatabaseMapping,name_scenario : str, name_alternative : str, rank_int = None) -> None:
    _, error = db_map.add_scenario_alternative_item(scenario_name = name_scenario, alternative_name = name_alternative, rank = rank_int)
    if error is not None:
        raise RuntimeError(error)

def scenario_development(config):

    with DatabaseMapping(url_spineopt) as sopt_db:

        scenarios_in_db = [scenario_i["name"] for scenario_i in sopt_db.get_scenario_items()]
        for scenario_name in config["scenarios"]:
            
            if scenario_name not in scenarios_in_db:
                add_scenario(sopt_db,scenario_name)
            
            alt_names = config["scenarios"][scenario_name]
            for alt_name in alt_names:
                try:
                    add_scenario_alternative(sopt_db,scenario_name,alt_name,alt_names.index(alt_name)+1)
                except RuntimeError as e:
                    print(f"WARNING: scenario_alternative already exists: {e}")
        try:
            sopt_db.commit_session("Added scenario")
        except:
            print("###################################################################### commit error")

def storage_setup(config):

    with DatabaseMapping(url_spineopt) as sopt_db:
        list_rep = [entity_i["name"] for entity_i in sopt_db.get_entity_items(entity_class_name = "temporal_block") if "representative_period" in entity_i["name"]]
        list_otb = [entity_i["name"] for entity_i in sopt_db.get_entity_items(entity_class_name = "temporal_block") if "operations" in entity_i["name"]]                    
    
        for param_map in sopt_db.get_parameter_value_items(entity_class_name = "node", parameter_definition_name = "storage_active"):
            if bool(param_map["parsed_value"]):
                if all(sto+"_" not in param_map["entity_byname"][0] for sto in config["short-term-storage"]):
                    add_or_update_parameter_value(sopt_db,"node","storage_longterm_active","Base",(param_map["entity_byname"][0],),True)
                    cyclic_condition_status = [entity_i for entity_i in sopt_db.get_parameter_value_items(entity_class_name = "node__temporal_block", alternative_name = "Base", parameter_definition_name = "cyclic_condition") if param_map["entity_byname"][0] == entity_i["entity_byname"][0]]
                    if cyclic_condition_status and sopt_db.get_entity_item(entity_class_name = "temporal_block",name = "all_rps"):
                        try:
                            add_entity(sopt_db,"node__temporal_block",(param_map["entity_byname"][0],"all_rps"))
                        except:
                            print(f"Entity class node__temporal_block with all_rps already added")
                            pass
                    elif any(sto+"_" in param_map["entity_byname"][0] for sto in config["long-term-storage"]):
                        # ------------------------------------------------------------------
                        # HOTFIX-02: conditional cyclic_condition for long-term storage.
                        # See /memories/repo/hotfixes.md (HOTFIX-02) for the full write-up.
                        #
                        # Root cause: SpineOpt's `_build_constraint_cyclic_node_state`
                        # (constraints/constraint_cyclic_node_state.jl) picks the
                        # `node_state_longterm` variable when `is_longterm_storage=True`
                        # and the block is non-representative, but enumerates indices via
                        # `node_state_indices` -- whose index set additionally includes
                        # `block__starting_point` (the 1-minute history slice).
                        # `node_state_longterm_indices` does NOT include that starting-
                        # point slice, so the lookup at the pre-history time slice throws
                        # KeyError.
                        #
                        # Workaround: when representative periods are in use, put the
                        # cyclic_condition on the `all_rps` block (which is
                        # `is_representative=True` -> uses `node_state`, whose index set
                        # DOES include `block__starting_point`). Still associate the node
                        # with each `operations_yXXXX` block so `node_state_longterm` is
                        # built there, but do NOT set cyclic_condition on those.
                        #
                        # When representative periods are NOT in use, keep the original
                        # behavior (cyclic on `operations_yXXXX`) -- SpineOpt handles
                        # that case fine.
                        # ------------------------------------------------------------------
                        if list_rep:
                            add_entity(sopt_db,"node__temporal_block",(param_map["entity_byname"][0],"all_rps"))
                            add_or_update_parameter_value(sopt_db,"node__temporal_block","cyclic_condition","Base",(param_map["entity_byname"][0],"all_rps"),True)
                            for tb in list_otb:
                                add_entity(sopt_db,"node__temporal_block",(param_map["entity_byname"][0],tb))
                        else:
                            for tb in list_otb:
                                add_entity(sopt_db,"node__temporal_block",(param_map["entity_byname"][0],tb))
                                add_or_update_parameter_value(sopt_db,"node__temporal_block","cyclic_condition","Base",(param_map["entity_byname"][0],tb),True)

                else:
                    if list_rep:
                        # identifying long-term cyclic condition
                        for node_map in sopt_db.get_entity_items(entity_class_name = "node__temporal_block"):
                            if node_map["entity_byname"][0] == param_map["entity_byname"][0]:
                                item_id = node_map["id"]
                                sopt_db.remove_item("entity",item_id)
                        for rep in list_rep:
                            try:
                                add_entity(sopt_db,"node__temporal_block",(param_map["entity_byname"][0],rep))
                            except:
                                print(f"Entity node__temporal_bloc with {rep}")
                                pass
                            add_or_update_parameter_value(sopt_db,"node__temporal_block","cyclic_condition","Base",(param_map["entity_byname"][0],rep),True)
                    else:
                        add_or_update_parameter_value(sopt_db,"node","storage_longterm_active","Base",(param_map["entity_byname"][0],),True)
                        for tb in list_otb:
                            try:
                                add_entity(sopt_db,"node__temporal_block",(param_map["entity_byname"][0],tb))
                            except:
                                print(f"Entity node__temporal_bloc with {tb}")
                                pass
                            add_or_update_parameter_value(sopt_db,"node__temporal_block","cyclic_condition","Base",(param_map["entity_byname"][0],tb),True)
        try:
            sopt_db.commit_session("Added storage_setup")
        except:
            print("###################################################################### commit error") 

def update_parameters(config):

    with DatabaseMapping(url_spineopt) as sopt_db:

        resolution_ = config["resolution"]
        parameter_value = {"type":"duration","data":resolution_}
        #for parameter_map in sopt_db.get_parameter_value_items(parameter_definition_name = "resolution"):
        #    if "planning" not in parameter_map["entity_byname"][0]:
        #        add_or_update_parameter_value(sopt_db, parameter_map["entity_class_name"], "resolution", parameter_map["alternative_name"], parameter_map["entity_byname"], parameter_value)
        add_or_update_parameter_value(sopt_db, "node", "storage_investment_count_initial_cumulative", "Base", ("CO2-storage", ), 0.2*1e3*config["emission_factor"])
        add_or_update_parameter_value(sopt_db, "node", "storage_investment_count_fix_cumulative", "Base", ("CO2-storage", ), 0.2*1e3*config["emission_factor"])
        add_or_update_parameter_value(sopt_db, "node", "storage_investment_count_initial_cumulative", "Base", ("atmosphere", ), 2.6*1e3*config["emission_factor"])
        indexes_ = ["2030-01-01T00:00:00","2040-01-01T00:00:00","2050-01-01T00:00:00","2060-01-01T00:00:00"]
        values_  = np.array([2.6*1e3,0.58*1e3,0.0,0.0])*config["emission_factor"]
        add_or_update_parameter_value(sopt_db, "node", "storage_investment_count_max_cumulative", "Base", ("atmosphere", ), {"type":"time_series", "data":dict(zip(indexes_,values_))})
        try:
            sopt_db.commit_session("Update parameters")
        except:
            print("###################################################################### commit error")  

def emission_cap_setup(config):
    """Enforce a BE+NL CO2 emission cap via a SpineOpt `user_constraint` on
    unit_flow to atmosphere.

    Temporal semantics (important — read carefully)
    -----------------------------------------------
    In SpineOpt v1.0.0 the `user_constraint` mechanism fires at REPRESENTATIVE
    timesteps only (see `constraint_user_constraint_indices` in
    src/constraints/constraint_user_constraint.jl and the `_is_representative(t)`
    filter). In this project, representative blocks are `all_rps` and
    `representative_period_YYYY_1` at 1-hour resolution, so the constraint
    fires per HOUR. RHS is interpreted per-hour, not per-year.

    BUT because this specific model has FLAT demand and FLAT VRE availability
    within each 24-hour representative period (verified empirically — all
    demand and availability_factor values have peak/avg = 1.0x), the per-hour
    cap is mathematically EQUIVALENT to an annual cap ÷ 8760.

    That is: setting RHS = 19.4 kt/hr per hour (=170 Mt/yr / 8760 h) enforces
    exactly the same feasible region as an annual cap of 170 Mt/yr would,
    because emissions ARE constant hour-to-hour by construction. The
    scale_factor_to_native_kt config value defaults to 0.1142 (=1000/8760)
    so the schedule can stay in familiar Mt/yr units.

    Should the model ever be extended with hourly-varying demand or VRE
    profiles (e.g., using longer representative periods with intra-day
    variance), the per-hour semantic would start over-constraining and this
    conversion factor should be re-evaluated.

    Why NOT `flow_limits_max_cumulative` (the "proper" cumulative mechanism)
    -----------------------------------------------------------------------
    `flow_limits_max_cumulative` DOES exist and produces one constraint
    summing all flows over the horizon — but it hits a KeyError in v1.0.0
    when the model uses representative_periods_mapping. The constraint code
    iterates `unit_flow_indices(temporal_block=anything)` which returns
    timesteps at non-representative blocks (operations_yXXXX at 365D), but
    the `unit_flow` variable dict only has entries at representative
    timesteps. Lookup at the annual timestep throws KeyError. Filed as a
    known SpineOpt limitation for follow-up upstream.

    Why NOT `storage_state_max` on atmosphere (the ines-spineopt intent)
    -------------------------------------------------------------------
    The `ines_to_spineopt.process_emissions()` function sets storage_state_max
    on atmosphere intending it to be an annual/cumulative cap via node_state.
    But SpineOpt v1.0.0 doesn't create a `node_state` variable for atmosphere
    (a pure-sink node with only inflows). We tried 6+ parameter combinations,
    including matching CH4-geo-formation (which works) exactly, without
    success. Likely a SpineOpt bug or undocumented requirement.

    Setup written to the SpineOpt DB
    --------------------------------
    - `user_constraint` entity named "emission_cap"
    - constraint_sense = "<="
    - right_hand_side = time series [(year, RHS(year))] in native units (kt/hr)
    - `unit_flow__user_constraint` entities linking every unit-with-flow-to-atmosphere
      to the constraint, each with coefficient_for_unit_flow = 1.0

    Configuration
    -------------
    Reads config["emission_cap"]:
      - enabled: bool
      - schedule_Mt_per_year: dict {year: X} — X interpreted as kt/hr after scaling
      - scale_factor_to_native_kt: float (default 1000; Mt -> kt)
      - (cumulative_budget_Mt: still read but unused in this per-hour version)
    """
    cap_cfg = config.get("emission_cap", {})
    if not cap_cfg.get("enabled", False):
        print("  emission_cap disabled or missing — skipping")
        return
    schedule = cap_cfg.get("schedule_Mt_per_year", {})
    scale    = float(cap_cfg.get("scale_factor_to_native_kt",
                                 cap_cfg.get("scale_factor_to_storage_units", 1000)))
    if not schedule:
        print("  emission_cap.schedule_Mt_per_year empty — skipping")
        return

    items         = sorted((int(y), float(v)) for y, v in schedule.items())
    dates         = [f"{y}-01-01T00:00:00" for y, _ in items]
    values_native = [v * scale for _, v in items]

    with DatabaseMapping(url_spineopt) as sopt_db:
        # ---- (1) create the user_constraint entity (idempotent) ----
        add_entity_if_missing(sopt_db, "user_constraint", ("emission_cap",))

        # ---- (2) constraint_sense = "<=" ----
        add_or_update_parameter_value(
            sopt_db, "user_constraint", "constraint_sense", "Base",
            ("emission_cap",), "<=",
        )

        # ---- (3) right_hand_side as time series in native units ----
        rhs_ts = {"type": "time_series", "data": dict(zip(dates, values_native))}
        add_or_update_parameter_value(
            sopt_db, "user_constraint", "right_hand_side", "Base",
            ("emission_cap",), rhs_ts,
        )

        # ---- (4) link every unit emitting to atmosphere ----
        atmosphere_units = [
            rel["entity_byname"][0]
            for rel in sopt_db.get_entity_items(entity_class_name="unit__to_node")
            if rel["entity_byname"][1] == "atmosphere"
            and rel["entity_byname"][0] != "atmosphere_emitters"
        ]

        n_linked = 0
        for unit_name in atmosphere_units:
            add_entity_if_missing(
                sopt_db, "unit_flow__user_constraint",
                (unit_name, "atmosphere", "emission_cap"),
            )
            add_or_update_parameter_value(
                sopt_db, "unit_flow__user_constraint",
                "coefficient_for_unit_flow", "Base",
                (unit_name, "atmosphere", "emission_cap"), 1.0,
            )
            n_linked += 1

        try:
            sopt_db.commit_session("Update emission cap (user_constraint, per-hour)")
            print(f"  emission_cap user_constraint set: "
                  f"{n_linked} emitting units linked, "
                  f"RHS (native units per hour) = {dict(zip([d[:4] for d in dates], values_native))}, "
                  f"config schedule Mt/yr = {dict(items)}")
        except Exception:
            print("###################################################################### emission_cap commit error")

def fix_no_investable_by_2030(config):

    indexes_ = ["2030-01-01T00:00:00","2040-01-01T00:00:00","2050-01-01T00:00:00","2060-01-01T00:00:00"]
    values_ = [0.0,None,None,None]
    parameter_value = {"type":"time_series","data":dict(zip(indexes_,values_))}

    parameter_name_map = {"unit":"investment_count_fix_new","node":"storage_investment_count_fix_new","connection":"investment_count_fix_new"}

    with DatabaseMapping(url_spineopt) as sopt_db:
        fix_config = config["no_investable_2030"]
        parsed_entities = {class_i:[entity_map["name"] for entity_map in sopt_db.get_entity_items(entity_class_name=class_i) if entity_map["name"].split("_")[0] in fix_config[class_i]] for class_i in ["unit","node"]}

        parsed_entities["connection"] = []
        for entity_map in sopt_db.get_entity_items(entity_class_name="connection"):
            if entity_map["name"].split("_")[1] in fix_config["connection"]:
                parsed_entities["connection"].append(entity_map["name"])
                
        for entity_class in parsed_entities:
            for entity_name in parsed_entities[entity_class]:
                check_existing_param = sopt_db.get_parameter_value_items(entity_class_name = entity_class, parameter_definition_name = parameter_name_map[entity_class], entity_byname = (entity_name,))
                if not check_existing_param:
                    add_parameter_value(sopt_db,entity_class,parameter_name_map[entity_class],"Base",(entity_name,),parameter_value)

        try:
            sopt_db.commit_session("fix invested variables")
        except:
            print("###################################################################### fix invested variables commit error")  

def ramping_constraints(config):

    if config["include_ramping"]:
        print("Ramping constraints included")
        with DatabaseMapping(url_spineopt) as sopt_db:
            entities = [entity_i for entity_i in sopt_db.get_entity_items(entity_class_name = "unit__to_node") if any(tech in entity_i["entity_byname"][0] for tech in config["ramping"])]
            for entity in entities:
                for tech in config["ramping"]:
                    if tech in entity["entity_byname"][0] and config["ramping"][tech][0] in entity["entity_byname"][1]:
                        ramp_value = config["ramping"][tech][1]
                        add_or_update_parameter_value(sopt_db,"unit__to_node","ramp_limits_up","Base",entity["entity_byname"],ramp_value)
                        add_or_update_parameter_value(sopt_db,"unit__to_node","ramp_limits_down","Base",entity["entity_byname"],ramp_value)
                        add_or_update_parameter_value(sopt_db,"unit__to_node","ramp_limits_startup","Base",entity["entity_byname"],ramp_value)
                        add_or_update_parameter_value(sopt_db,"unit__to_node","ramp_limits_shutdown","Base",entity["entity_byname"],ramp_value)
                        break

            try:
                sopt_db.commit_session("ramping constraints")
            except:
                print("###################################################################### ramping constraints commit error")  
        
def refinery_constraints(config):

    if config["include_refinery_trajectory"]:
        print("you are modeling imposed refinery trajectory")
        with DatabaseMapping(url_spineopt) as sopt_db:
            list_otb = [entity_i["name"] for entity_i in sopt_db.get_entity_items(entity_class_name = "temporal_block") if "operations" in entity_i["name"]]    
            entities = {type_:[entity_i["name"] for entity_i in sopt_db.get_entity_items(entity_class_name = "unit") if any(tech in entity_i["name"] for tech in config["refineries"][type_]["techs"])] for type_ in config["refineries"]}
            all_rps  = sopt_db.get_entity_item(entity_class_name = "temporal_block",name = "all_rps")
            for type_ in ["bio","syn"]:
                add_entity_if_missing(sopt_db,"investment_group",(f"{type_}fuels",))
                
                coefficient_2030 = config["refineries"][type_]["share_2030"]
                coefficient_2040 = config["refineries"][type_]["share_2040"]
                coefficient_2050 = config["refineries"][type_]["share_2050"]
                refinery_cap = 0
                for tech in entities["fossil"]:
                    initial_cap = sopt_db.get_parameter_value_item(entity_class_name = "unit", alternative_name = "Base", parameter_definition_name = "investment_count_initial_cumulative", entity_byname = (tech,))
                    if initial_cap:
                        refinery_cap += initial_cap["parsed_value"]
                for tech in entities[type_]:
                    add_entity_if_missing(sopt_db,"unit__investment_group",(tech,f"{type_}fuels"))

                index_ = ["2030-01-01T00:00:00","2040-01-01T00:00:00","2050-01-01T00:00:00","2060-01-01T00:00:00"]
                value_ = [coefficient_2030*refinery_cap,coefficient_2040*refinery_cap,coefficient_2050*refinery_cap,coefficient_2050*refinery_cap]
                parameter_value = {"type":"time_series","data":dict(zip(index_,value_))}
                add_or_update_parameter_value(sopt_db,"investment_group","investment_count_total_max_cumulative","Base",(f"{type_}fuels",),parameter_value)

            for entity_HC in [entity_i["name"] for entity_i in sopt_db.get_entity_items(entity_class_name="node") if "HC_" in entity_i["name"] and len(entity_i["name"])==5]:
                add_entity_if_missing(sopt_db,"node",(f"bunker-{entity_HC}",))
                add_or_update_parameter_value(sopt_db,"node","storage_active","Base",(f"bunker-{entity_HC}",),True)
                add_or_update_parameter_value(sopt_db,"node","storage_longterm_active","Base",(f"bunker-{entity_HC}",),True)
                # HOTFIX-02 (see storage_setup() and /memories/repo/hotfixes.md):
                # When representative periods exist, put the cyclic_condition on
                # `all_rps` (representative) instead of on `operations_yXXXX`
                # (non-representative) to avoid the SpineOpt
                # constraint_cyclic_node_state KeyError for long-term storage.
                # Still associate the node with each operations block so that
                # `node_state_longterm` is built there. When representative
                # periods are absent, keep the original behavior.
                if all_rps:
                    add_entity_if_missing(sopt_db,"node__temporal_block",(f"bunker-{entity_HC}","all_rps"))
                    add_or_update_parameter_value(sopt_db,"node__temporal_block","cyclic_condition","Base",(f"bunker-{entity_HC}","all_rps"),True)
                    for tb in list_otb:
                        add_entity_if_missing(sopt_db,"node__temporal_block",(f"bunker-{entity_HC}",tb))
                else:
                    for tb in list_otb:
                        add_entity_if_missing(sopt_db,"node__temporal_block",(f"bunker-{entity_HC}",tb))
                        add_or_update_parameter_value(sopt_db,"node__temporal_block","cyclic_condition","Base",(f"bunker-{entity_HC}",tb),True)
                add_entity_if_missing(sopt_db,"connection",(f"bunker-connection-{entity_HC}",))
                add_or_update_parameter_value(sopt_db,"connection","connection_type","Base",(f"bunker-connection-{entity_HC}",),"connection_type_lossless_bidirectional")
                add_entity_if_missing(sopt_db,"connection__from_node",(f"bunker-connection-{entity_HC}",entity_HC))
                add_entity_if_missing(sopt_db,"connection__to_node",(f"bunker-connection-{entity_HC}",f"bunker-{entity_HC}"))
                add_entity_if_missing(sopt_db,"connection__node__node",(f"bunker-connection-{entity_HC}",f"bunker-{entity_HC}",entity_HC))
                add_or_update_parameter_value(sopt_db,"connection__node__node","fix_ratio_out_in_connection_flow","Base",(f"bunker-connection-{entity_HC}",f"bunker-{entity_HC}",entity_HC),1.0)

            try:
                sopt_db.commit_session("refinery constraints")
            except:
                print("###################################################################### refinery constraints commit error")  

def onshore_potentials(config_renewable):

    config = config_renewable["renewable_potentials"]
    if config["include_onshore_potential_limitations"]:
        print("WARNING: If you haven't reset the model, you are reducing the VRE potentials once again.")
        with DatabaseMapping(url_spineopt) as sopt_db:
            maximum_entities = [parameter_map  for parameter_map in sopt_db.get_parameter_value_items(parameter_definition_name = "investment_count_total_max_cumulative") if "wind-on" in parameter_map["entity_byname"][0] or "solar-PV" in parameter_map["entity_byname"][0]]

            for max_entity in maximum_entities:
                if "MT" not in max_entity["entity_byname"][0]:
                    tech_type = "wind-on" if "wind-on" in max_entity["entity_byname"][0] else "solar-PV"
                    polygon = max_entity["entity_byname"][0].split("_")[1]
                    initial_value = config["max_capacity_history"][tech_type][polygon]
                    parameter_value = max_entity["parsed_value"]*config["onshore_potentials"] if max_entity["parsed_value"]*config["onshore_potentials"] > initial_value else initial_value
                    add_or_update_parameter_value(sopt_db,"investment_group","investment_count_total_max_cumulative","Base",max_entity["entity_byname"],parameter_value)

            try:
                sopt_db.commit_session("vre onshore potentials update")
            except:
                print("###################################################################### vre onshore potentials update commit error")  

def biomass_limitations(config):
    if config["include_biomass_potential_limitations"]:
        print("WARNING: If you haven't reset the model, you are reducing the biomass potentials once again.")
        with DatabaseMapping(url_spineopt) as sopt_db:
            for parameter_name in ["storage_investment_count_max_cumulative","storage_state_fix","storage_investment_count_fix_cumulative","storage_investment_count_initial_cumulative"]:
                for parameter_map in sopt_db.get_parameter_value_items(parameter_definition_name = parameter_name):
                    if "biomass-stock" in parameter_map["entity_byname"][0]:
                        if parameter_map["type"] == "float":
                            parameter_value = config["biomass_potential_realistic"]*parameter_map["parsed_value"]
                        elif parameter_map["type"] == "time_series":
                            values_ = config["biomass_potential_realistic"]*parameter_map["parsed_value"].values
                            indexes_ = [pd.Timestamp(i).isoformat() for i in parameter_map["parsed_value"].indexes]
                            parameter_value = {"type":"time_series","data":dict(zip(indexes_,values_))}
                        add_or_update_parameter_value(sopt_db,parameter_map["entity_class_name"],parameter_name,parameter_map["alternative_name"],parameter_map["entity_byname"],parameter_value)
            try:
                sopt_db.commit_session("vre biomass potentials update")
            except:
                print("###################################################################### vre biomass potentials update commit error")  

def investment_cost_update(config):
    
    default_technology_discount_rate = config["default_technology_discount_rate"]
    future_inflation = config["future_inflation"]
    with DatabaseMapping(url_spineopt) as sopt_db:

        dates = []
        for date_dict in sopt_db.get_parameter_value_items(parameter_definition_name = "block_start"):
            if "operations" in date_dict["entity_byname"][0]:
                dates.append(pd.Timestamp(date_dict["parsed_value"].value).isoformat())
        final_date = [pd.Timestamp(i["parsed_value"].value) for i in sopt_db.get_parameter_value_items(parameter_definition_name = "model_end", alternative_name = "Base")][0]
        dates.append(final_date.isoformat())
        final_year = final_date.year

        entities = ["unit","connection","node"]
        icost    = ["unit_investment_cost","connection_investment_cost","storage_investment_cost"]
        fcost    = ["fom_cost","","storage_fixed_annual_cost"]
        ilife    = ["lifetime_economic","lifetime_economic","storage_lifetime_economic"]
        tlife    = ["lifetime_technical","lifetime_technical","storage_lifetime_technical"]
        isense   = ["lifetime_constraint_sense","lifetime_constraint_sense","storage_lifetime_constraint_sense"]
        irate    = ["discount_rate_technology_specific","discount_rate_technology_specific","storage_discount_rate_technology_specific"]
        
        for index, entity_class_name in enumerate(entities): 

            for parameter_map in sopt_db.get_parameter_value_items(entity_class_name = entities[index], parameter_definition_name = icost[index]):
                
                lifetime_dict = sopt_db.get_parameter_value_item(entity_class_name = entities[index], parameter_definition_name = ilife[index], alternative_name = parameter_map["alternative_name"], entity_byname = parameter_map["entity_byname"])
                if not lifetime_dict:
                    print("Annuities are implemented using economic lifetime. Economic lifetime not found.")
                    continue
                else:
                    lifetime = int(json.loads(lifetime_dict["value"])["data"][:-1])
                    techlife_dict = sopt_db.get_parameter_value_item(entity_class_name = entities[index], parameter_definition_name = tlife[index], alternative_name = parameter_map["alternative_name"], entity_byname = parameter_map["entity_byname"])
                    add_or_update_parameter_value(sopt_db,entity_class_name,isense[index],"Base",techlife_dict["entity_byname"],"<=")
                
                rate_dict = sopt_db.get_parameter_value_item(entity_class_name = entities[index], parameter_definition_name = irate[index], alternative_name = parameter_map["alternative_name"], entity_byname = parameter_map["entity_byname"])
                if not rate_dict:
                    rate_list = sopt_db.get_parameter_value_items(parameter_definition_name = "discount_rate")
                    if not rate_list:
                        print("Model discount rate not found. Using 0.05 as default")
                        rate = default_technology_discount_rate
                    else:
                        rate = rate_list[0]["parsed_value"]
                else:
                    rate = rate_dict["parsed_value"]

                # fom cost
                fom_dict = sopt_db.get_parameter_value_item(entity_class_name = entities[index], parameter_definition_name = fcost[index], alternative_name = parameter_map["alternative_name"], entity_byname = parameter_map["entity_byname"])
                if not fom_dict:
                    fom_cost_condition = False
                    print("FOM cost not found for ", parameter_map["entity_name"])
                else:
                    fom_cost_condition = True
                    add_or_update_parameter_value(sopt_db, parameter_map["entity_class_name"], fcost[index], fom_dict["alternative_name"], fom_dict["entity_byname"], (fom_dict["parsed_value"].values[2] if fom_dict["type"]=="time_series" else fom_dict["parsed_value"]))

                value_dict = {}
                crf = rate * (1 + rate)**lifetime / ((1 + rate)**lifetime - 1)
                if parameter_map["type"] == "float":                 
                    for date in dates:
                        if date != dates[-1]:
                            year = pd.Timestamp(date).year
                            n_years = min(lifetime, final_year - year)
                            annual_cost_nominal = parameter_map["parsed_value"] * (1 + future_inflation)**(year - 2025) * crf
                            value_dict[date] = sum(annual_cost_nominal * (1 + future_inflation)**(2025 - i) for i in range(year, year + n_years))
                        else:
                            value_dict[dates[-1]] = value_dict[dates[-2]]
                    new_value   = {"type":"time_series","data":value_dict}
                else:
                    if fom_cost_condition:
                        if fom_dict["type"] == "float":
                            fixed_cost = [fom_dict["parsed_value"],fom_dict["parsed_value"],fom_dict["parsed_value"]]
                        else:
                            fixed_cost = [fom_dict["parsed_value"].values[0],fom_dict["parsed_value"].values[1],fom_dict["parsed_value"].values[2]]

                    map_table = convert_map_to_table(parameter_map["parsed_value"])
                    index_names = nested_index_names(parameter_map["parsed_value"])
                    data = pd.DataFrame(map_table, columns=index_names + ["value"]).set_index(index_names[0])["value"]
                    data.index = [pd.Timestamp(i).isoformat() for i in data.index]
                    #print(data)
                    for date in dates:
                        if date != dates[-1]:
                            year = pd.Timestamp(date).year
                            n_years = min(lifetime, final_year - year)
                            annual_cost_nominal = data[date]* (1 + future_inflation)**(year - 2025) * crf
                            value_dict[date] = sum(annual_cost_nominal * (1 + future_inflation)**(2025 - i) for i in range(year, year + n_years)) + ((fixed_cost[dates.index(date)] - fixed_cost[2])*8760 if fom_cost_condition else 0.0)*n_years
                        else:
                            value_dict[dates[-1]] = value_dict[dates[-2]] 
                    new_value   = {"type":"time_series","data":value_dict} 
                
                # print("new value for the value cost", parameter_map["entity_class_name"], parameter_map["parameter_definition_name"], parameter_map["alternative_name"], parameter_map["entity_byname"], new_value)
                add_or_update_parameter_value(sopt_db, parameter_map["entity_class_name"], parameter_map["parameter_definition_name"], parameter_map["alternative_name"], parameter_map["entity_byname"], new_value)
        
        try:
            sopt_db.commit_session("Update Investment Costs")
        except:
            print("###################################################################### commit error investment costs")  

def air_ground_heatpump(config):

    with DatabaseMapping(url_spineopt) as sopt_db:
        
        for entity_name in [element["name"] for element in sopt_db.get_entity_items(entity_class_name = "unit") if "ground-heatpump_" in element["name"]]:
            polygon_name = entity_name.split("_")[1]
            add_entity(sopt_db,"user_constraint",("heatpump-ratio"+"_"+polygon_name,))
            add_entity(sopt_db,"unit__user_constraint",(entity_name,"heatpump-ratio"+"_"+polygon_name))
            add_parameter_value(sopt_db,"unit__user_constraint","coefficient_for_units_invested","Base",(entity_name,"heatpump-ratio"+"_"+polygon_name),1.0)
            add_entity(sopt_db,"unit__user_constraint",("air-heatpump"+"_"+polygon_name,"heatpump-ratio"+"_"+polygon_name))
            add_parameter_value(sopt_db,"unit__user_constraint","coefficient_for_units_invested","Base",("air-heatpump"+"_"+polygon_name,"heatpump-ratio"+"_"+polygon_name),-config["ratio_ground_air_HP"])
        
        try:
            sopt_db.commit_session("Add User Constraint Heat Pumps")
        except:
            print("######################## commit error heat pump ratio")  

def manage_output():
    with DatabaseMapping(url_spineopt) as sopt_db:

        report_name = "default_report"
        add_entity(sopt_db,"report",(report_name,))
        add_entity(sopt_db,"model__report",("capacity_planning",report_name))
        outputs = ["capacity_per_unit","capacity_per_connection","storage_state_max","demand",
                   "connections_invested","connections_invested_available","connections_decommissioned","units_invested","units_invested_available","units_mothballed",
                   "storages_invested","storages_invested_available","storages_decommissioned","unit_flow","connection_flow","node_state","node_state_longterm","node_injection",
                   #"unit_investment_cost","connection_investment_cost","storage_investment_cost",
                   "unit_investment_costs","connection_investment_costs","storage_investment_costs","fixed_om_costs","variable_om_costs","fuel_costs","connection_flow_costs","taxes","objective_penalties",
                   "total_costs"]
                   #"node_slack_neg","node_slack_pos",
                   #"constraint_nodal_balance","constraint_units_available",
                   #"bound_units_on"]
        
        for output in outputs:
            add_entity(sopt_db,"output",(output,))
            add_entity(sopt_db,"report__output",(report_name,output))
        try:
            sopt_db.commit_session("Added outputs")
        except:
            print("############################## error commit adding output")

def solver_options(config):

    with DatabaseMapping(url_spineopt) as sopt_db:
        map_options = {"type":"map","index_type":"str","index_name":"x","data":
                       {"HiGHS.jl" :{"type":"map","index_type":"str","index_name":"x","data":{"presolve":"on","time_limit":3600.01}},
                        "Gurobi.jl":{"type":"map","index_type":"str","index_name":"x","data":{"Method":2.0,"NumericFocus":2.0,"Crossover":0.0}}}}
        
        add_parameter_value(sopt_db,"model","solver_mip_options","Base",("capacity_planning",),map_options)
        add_parameter_value(sopt_db,"model","solver_mip","Base",("capacity_planning",),config["solver"])
        try:
            sopt_db.commit_session("Added solver_options")
        except:
            print("############################## error committing solver options")

def update_economic_parameters(config):

    with DatabaseMapping(url_spineopt) as sopt_db:

        economic_lifetime = {"unit":"lifetime_economic","connection":"lifetime_economic","node":"storage_lifetime_economic"}
        discount_rate = {"unit":"discount_rate_technology_specific","connection":"discount_rate_technology_specific","node":"storage_discount_rate_technology_specific"}
        
        for entity_class in config["economic_parameters"]:
            for entity_item in sopt_db.get_entity_items(entity_class_name = entity_class):
                if entity_item["name"].split("_")[0] in config["economic_parameters"][entity_class]:
                    if "WACC" in config["economic_parameters"][entity_class][entity_item["name"].split("_")[0]]:
                        add_or_update_parameter_value(sopt_db,entity_class,discount_rate[entity_class],"Base",entity_item["entity_byname"],config["economic_parameters"][entity_class][entity_item["name"].split("_")[0]]["WACC"])
                    if "economic_lifetime" in config["economic_parameters"][entity_class][entity_item["name"].split("_")[0]]:
                        add_or_update_parameter_value(sopt_db,entity_class,economic_lifetime[entity_class],"Base",entity_item["entity_byname"],{"type":"duration","data":config["economic_parameters"][entity_class][entity_item["name"].split("_")[0]]["economic_lifetime"]})
                    
        try:
            sopt_db.commit_session("Added economic parameters")
        except:
            print("############################## error committing economic parameters")

def main():

    with open(sys.argv[2], 'r') as file:
        config = yaml.safe_load(file)

    print("Updating economic parameters, econ lifetime and discount rate")
    update_economic_parameters(config)
    
    #done in previous sccript (planning_setup)
    #print("Updating invesment costs and FOM costs")
    #investment_cost_update(config)

    #print("Heat pump constraints")
    #air_ground_heatpump(config)

    #print("managing outputs")
    #manage_output()

    #print("adding solver options")
    #solver_options(config)

    print("adding scenarios to be analyzed")
    scenario_development(config)

    print("storage_setup")
    storage_setup(config)

    print("emission_cap_setup")
    emission_cap_setup(config)

    print("updating_parameters")
    # update_parameters(config)

    print("fixing invested variables")
    fix_no_investable_by_2030(config)

    print("ramping constraints")
    ramping_constraints(config)

    print("refinery constraints")
    refinery_constraints(config)

    #not defined for IC1`regions, for now left as is
    #print("vre onshore potentials updates")
    #onshore_potentials(config)

    print("biomass potentials updates")
    biomass_limitations(config)

if __name__ == "__main__":
    main()