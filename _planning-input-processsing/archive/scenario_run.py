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
                    add_scenario_alternative(sopt_db,scenario_name,alt_name,alt_names.index(alt_name)+1)
        try:
            sopt_db.commit_session("Added scenario")
        except:
            print("###################################################################### commit error")  

def storage_setup(config):

    with DatabaseMapping(url_spineopt) as sopt_db:
        list_rep = [entity_i["name"] for entity_i in sopt_db.get_entity_items(entity_class_name = "temporal_block") if "representative_period" in entity_i["name"]]
        list_otb = [entity_i["name"] for entity_i in sopt_db.get_entity_items(entity_class_name = "temporal_block") if "operations" in entity_i["name"]]                    
    
        for param_map in sopt_db.get_parameter_value_items(entity_class_name = "node", parameter_definition_name = "has_state"):
            if bool(param_map["parsed_value"]):
                if all(sto+"_" not in param_map["entity_byname"][0] for sto in config["short-term-storage"]):
                    add_or_update_parameter_value(sopt_db,"node","is_longterm_storage","Base",(param_map["entity_byname"][0],),True)
                    cyclic_condition_status = [entity_i for entity_i in sopt_db.get_parameter_value_items(entity_class_name = "node__temporal_block", alternative_name = "Base", parameter_definition_name = "cyclic_condition") if param_map["entity_byname"][0] == entity_i["entity_byname"][0]]
                    if cyclic_condition_status and sopt_db.get_entity_item(entity_class_name = "temporal_block",name = "all_rps"):
                        try:
                            add_entity(sopt_db,"node__temporal_block",(param_map["entity_byname"][0],"all_rps"))
                        except:
                            print(f"Entity class node__temporal_block with all_rps already added")
                            pass
                    elif any(sto+"_" in param_map["entity_byname"][0] for sto in config["long-term-storage"]):
                        if list_rep:
                            add_entity(sopt_db,"node__temporal_block",(param_map["entity_byname"][0],"all_rps"))
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
                        add_or_update_parameter_value(sopt_db,"node","is_longterm_storage","Base",(param_map["entity_byname"][0],),True)
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
        add_or_update_parameter_value(sopt_db, "node", "initial_storages_invested_available", "Base", ("CO2-storage", ), 0.2*1e3*config["emission_factor"])
        add_or_update_parameter_value(sopt_db, "node", "fix_storages_invested_available", "Base", ("CO2-storage", ), 0.2*1e3*config["emission_factor"])
        add_or_update_parameter_value(sopt_db, "node", "initial_storages_invested_available", "Base", ("atmosphere", ), 2.6*1e3*config["emission_factor"])
        indexes_ = ["2030-01-01T00:00:00","2040-01-01T00:00:00","2050-01-01T00:00:00","2060-01-01T00:00:00"]
        values_  = np.array([2.6*1e3,0.58*1e3,0.0,0.0])*config["emission_factor"]
        add_or_update_parameter_value(sopt_db, "node", "candidate_storages", "Base", ("atmosphere", ), {"type":"time_series", "data":dict(zip(indexes_,values_))})
        try:
            sopt_db.commit_session("Update parameters")
        except:
            print("###################################################################### commit error")  

def fix_no_investable_by_2030(config):

    indexes_ = ["2030-01-01T00:00:00","2040-01-01T00:00:00","2050-01-01T00:00:00","2060-01-01T00:00:00"]
    values_ = [0.0,None,None,None]
    parameter_value = {"type":"time_series","data":dict(zip(indexes_,values_))}

    parameter_name_map = {"unit":"fix_units_invested","node":"fix_storages_invested","connection":"fix_connections_invested"}

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
                        add_or_update_parameter_value(sopt_db,"unit__to_node","ramp_up_limit","Base",entity["entity_byname"],ramp_value)
                        add_or_update_parameter_value(sopt_db,"unit__to_node","ramp_down_limit","Base",entity["entity_byname"],ramp_value)
                        add_or_update_parameter_value(sopt_db,"unit__to_node","start_up_limit","Base",entity["entity_byname"],ramp_value)
                        add_or_update_parameter_value(sopt_db,"unit__to_node","shut_down_limit","Base",entity["entity_byname"],ramp_value)
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
                add_entity(sopt_db,"investment_group",(f"{type_}fuels",))
                
                coefficient_2030 = config["refineries"][type_]["share_2030"]
                coefficient_2040 = config["refineries"][type_]["share_2040"]
                coefficient_2050 = config["refineries"][type_]["share_2050"]
                refinery_cap = 0
                for tech in entities["fossil"]:
                    initial_cap = sopt_db.get_parameter_value_item(entity_class_name = "unit", alternative_name = "Base", parameter_definition_name = "initial_units_invested_available", entity_byname = (tech,))
                    if initial_cap:
                        refinery_cap += initial_cap["parsed_value"]
                for tech in entities[type_]:
                    add_entity(sopt_db,"unit__investment_group",(tech,f"{type_}fuels"))

                index_ = ["2030-01-01T00:00:00","2040-01-01T00:00:00","2050-01-01T00:00:00","2060-01-01T00:00:00"]
                value_ = [coefficient_2030*refinery_cap,coefficient_2040*refinery_cap,coefficient_2050*refinery_cap,coefficient_2050*refinery_cap]
                parameter_value = {"type":"time_series","data":dict(zip(index_,value_))}
                add_parameter_value(sopt_db,"investment_group","maximum_entities_invested_available","Base",(f"{type_}fuels",),parameter_value)

            for entity_HC in [entity_i["name"] for entity_i in sopt_db.get_entity_items(entity_class_name="node") if "HC_" in entity_i["name"]]:
                add_entity(sopt_db,"node",(f"bunker-{entity_HC}",))
                add_parameter_value(sopt_db,"node","has_state","Base",(f"bunker-{entity_HC}",),True)
                add_parameter_value(sopt_db,"node","is_longterm_storage","Base",(f"bunker-{entity_HC}",),True)
                for tb in list_otb:
                    add_entity(sopt_db,"node__temporal_block",(f"bunker-{entity_HC}",tb))
                    add_parameter_value(sopt_db,"node__temporal_block","cyclic_condition","Base",(f"bunker-{entity_HC}",tb),True)
                if all_rps:
                    add_entity(sopt_db,"node__temporal_block",(f"bunker-{entity_HC}","all_rps"))
                add_entity(sopt_db,"connection",(f"bunker-connection-{entity_HC}",))
                add_parameter_value(sopt_db,"connection","connection_type","Base",(f"bunker-connection-{entity_HC}",),"connection_type_lossless_bidirectional")
                add_entity(sopt_db,"connection__from_node",(f"bunker-connection-{entity_HC}",entity_HC))
                add_entity(sopt_db,"connection__to_node",(f"bunker-connection-{entity_HC}",f"bunker-{entity_HC}"))
                add_entity(sopt_db,"connection__node__node",(f"bunker-connection-{entity_HC}",f"bunker-{entity_HC}",entity_HC))
                add_parameter_value(sopt_db,"connection__node__node","fix_ratio_out_in_connection_flow","Base",(f"bunker-connection-{entity_HC}",f"bunker-{entity_HC}",entity_HC),1.0)

            try:
                sopt_db.commit_session("refinery constraints")
            except:
                print("###################################################################### refinery constraints commit error")  

def onshore_potentials(config_renewable):

    config = config_renewable["renewable_potentials"]
    if config["include_onshore_potential_limitations"]:
        print("WARNING: If you haven't reset the model, you are reducing the VRE potentials once again.")
        with DatabaseMapping(url_spineopt) as sopt_db:
            maximum_entities = [parameter_map  for parameter_map in sopt_db.get_parameter_value_items(parameter_definition_name = "maximum_entities_invested_available") if "wind-on" in parameter_map["entity_byname"][0] or "solar-PV" in parameter_map["entity_byname"][0]]

            for max_entity in maximum_entities:
                if "MT" not in max_entity["entity_byname"][0]:
                    tech_type = "wind-on" if "wind-on" in max_entity["entity_byname"][0] else "solar-PV"
                    polygon = max_entity["entity_byname"][0].split("_")[1]
                    initial_value = config["max_capacity_history"][tech_type][polygon]
                    parameter_value = max_entity["parsed_value"]*config["onshore_potentials"] if max_entity["parsed_value"]*config["onshore_potentials"] > initial_value else initial_value
                    add_or_update_parameter_value(sopt_db,"investment_group","maximum_entities_invested_available","Base",max_entity["entity_byname"],parameter_value)

            try:
                sopt_db.commit_session("vre onshore potentials update")
            except:
                print("###################################################################### vre onshore potentials update commit error")  

def biomass_limitations(config):
    if config["include_biomass_potential_limitations"]:
        print("WARNING: If you haven't reset the model, you are reducing the biomass potentials once again.")
        with DatabaseMapping(url_spineopt) as sopt_db:
            for parameter_name in ["candidate_storages","fix_node_state","fix_storages_invested_available","initial_storages_invested_available"]:
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
        fcost    = ["fom_cost","","storage_fom_cost"]
        ilife    = ["unit_investment_econ_lifetime","connection_investment_econ_lifetime","storage_investment_econ_lifetime"]
        tlife    = ["unit_investment_tech_lifetime","connection_investment_tech_lifetime","storage_investment_tech_lifetime"]
        isense   = ["unit_investment_lifetime_sense","connection_investment_lifetime_sense","storage_investment_lifetime_sense"]
        irate    = ["unit_discount_rate_technology_specific","connection_discount_rate_technology_specific","storage_discount_rate_technology_specific"]
        
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
            add_parameter_value(sopt_db,"unit__user_constraint","units_invested_coefficient","Base",(entity_name,"heatpump-ratio"+"_"+polygon_name),1.0)
            add_entity(sopt_db,"unit__user_constraint",("air-heatpump"+"_"+polygon_name,"heatpump-ratio"+"_"+polygon_name))
            add_parameter_value(sopt_db,"unit__user_constraint","units_invested_coefficient","Base",("air-heatpump"+"_"+polygon_name,"heatpump-ratio"+"_"+polygon_name),-config["ratio_ground_air_HP"])
        
        try:
            sopt_db.commit_session("Add User Constraint Heat Pumps")
        except:
            print("######################## commit error heat pump ratio")  

def manage_output():
    with DatabaseMapping(url_spineopt) as sopt_db:

        report_name = "default_report"
        add_entity(sopt_db,"report",(report_name,))
        add_entity(sopt_db,"model__report",("capacity_planning",report_name))
        outputs = ["unit_capacity","connection_capacity","node_state_cap","demand",
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
        
        add_parameter_value(sopt_db,"model","db_mip_solver_options","Base",("capacity_planning",),map_options)
        add_parameter_value(sopt_db,"model","db_mip_solver","Base",("capacity_planning",),config["solver"])
        try:
            sopt_db.commit_session("Added solver_options")
        except:
            print("############################## error committing solver options")

def update_economic_parameters(config):

    with DatabaseMapping(url_spineopt) as sopt_db:

        economic_lifetime = {"unit":"unit_investment_econ_lifetime","connection":"connection_investment_econ_lifetime","node":"storage_investment_econ_lifetime"}
        discount_rate = {"unit":"unit_discount_rate_technology_specific","connection":"connection_discount_rate_technology_specific","node":"storage_discount_rate_technology_specific"}
        
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
    
    print("Updating invesment costs and FOM costs")
    investment_cost_update(config)

    print("Heat pump constraints")
    air_ground_heatpump(config)

    print("managing outputs")
    manage_output()

    print("adding solver options")
    solver_options(config)

    print("adding scenarios to be analyzed")
    scenario_development(config)

    print("storage_setup")
    storage_setup(config)

    print("updating_parameters")
    update_parameters(config)

    print("fixing invested variables")
    fix_no_investable_by_2030(config)

    print("ramping constraints")
    ramping_constraints(config)

    print("refinery constraints")
    refinery_constraints(config)

    print("vre onshore potentials updates")
    onshore_potentials(config)

    print("biomass potentials updates")
    biomass_limitations(config)

if __name__ == "__main__":
    main()