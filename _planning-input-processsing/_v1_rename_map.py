"""SpineOpt v0.11.1 -> v1.0.0 rename map.

Sourced from:
  C:\\Users\\maganih\\.julia\\packages\\SpineOpt\\1NRBB\\src\\data_structure\\versions\\major_upgrade_1.jl

This module is the single source of truth for the parameter/class/value renames
we apply across the pipeline scripts. Import it wherever we need to translate
old identifiers to new ones, and reference `apply_param_rename(...)` /
`apply_class_rename(...)` /  `apply_value_rename(...)` helpers.

Kept intentionally as pure data + tiny helpers so the pipeline scripts don't
gain a heavy new dependency.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Class renames: {old_class: new_class}. Straight renames, no dimension change.
# ---------------------------------------------------------------------------
CLASS_RENAMES: dict[str, str] = {
    "commodity": "grid",
}

# ---------------------------------------------------------------------------
# Class structural updates: {old_class: (new_class, arg_mapping)}
# arg_mapping is 1-indexed positions from the OLD entity_byname to the NEW.
# Example: unit__from_node(unit=1, node=2)  ->  node__to_unit(node, unit)
#   mapping = [2, 1] means: new_byname[0] = old_byname[2-1]; new_byname[1] = old_byname[1-1]
# For the multi->unit_flow superclass moves the arg mapping still describes
# how the old tuple maps to the new tuple (the new tuple's first element is a
# (unit, node) pair that spinedb_api treats as a unit_flow superclass byname).
# ---------------------------------------------------------------------------
CLASS_UPDATES: dict[str, tuple[str, list[int]]] = {
    "unit__from_node": ("node__to_unit", [2, 1]),
    "unit__from_node__investment_group": ("unit_flow__investment_group", [2, 1, 3]),
    "unit__from_node__user_constraint": ("unit_flow__user_constraint", [2, 1, 3]),
    "unit__to_node__investment_group": ("unit_flow__investment_group", [1, 2, 3]),
    "unit__to_node__user_constraint": ("unit_flow__user_constraint", [1, 2, 3]),
}

# Classes that no longer exist and were not renamed. Do NOT create these
# entities in the new pipeline; if you need the semantics, use the mentioned
# replacement (may need architectural adaptation).
REMOVED_CLASSES: dict[str, str] = {
    "unit__commodity": "commodities are gone; use node__grid or model directly",
    "unit__node__node": "moved to unit_flow__unit_flow with new coefficient names",
}

# ---------------------------------------------------------------------------
# Parameter renames within same class: {(class, old_name): new_name}
# Extracted verbatim from major_upgrade_1.jl parameters_to_be_renamed.
# ---------------------------------------------------------------------------
PARAM_RENAMES: dict[tuple[str, str], str] = {
    # ---- unit ----
    ("unit", "number_of_units"): "existing_units",
    ("unit", "fix_units_out_of_service"): "out_of_service_count_fix",
    ("unit", "initial_units_out_of_service"): "out_of_service_count_initial",
    ("unit", "scheduled_outage_duration"): "outage_scheduled_duration",
    ("unit", "unit_availability_factor"): "availability_factor",
    ("unit", "units_unavailable"): "out_of_service_count_fix",  # merge=sum
    ("unit", "fix_units_on"): "online_count_fix",
    ("unit", "initial_units_on"): "online_count_initial",
    ("unit", "unit_decommissioning_time"): "decommissioning_time",
    ("unit", "unit_discount_rate_technology_specific"): "discount_rate_technology_specific",
    ("unit", "unit_investment_econ_lifetime"): "lifetime_economic",
    ("unit", "unit_investment_tech_lifetime"): "lifetime_technical",
    ("unit", "unit_investment_lifetime_sense"): "lifetime_constraint_sense",
    ("unit", "unit_investment_variable_type"): "investment_variable_type",
    ("unit", "unit_lead_time"): "lead_time",
    ("unit", "candidate_units"): "investment_count_max_cumulative",
    ("unit", "fix_units_invested"): "investment_count_fix_new",
    ("unit", "fix_units_invested_available"): "investment_count_fix_cumulative",
    ("unit", "initial_units_invested"): "investment_count_initial_new",
    ("unit", "initial_units_invested_available"): "investment_count_initial_cumulative",
    ("unit", "units_invested_big_m_mga"): "mga_investment_big_m",
    ("unit", "units_invested_mga"): "mga_investment_active",
    ("unit", "units_invested_mga_weight"): "mga_investment_weight",

    # ---- node ----
    ("node", "has_state"): "storage_active",
    ("node", "fractional_demand"): "demand_fraction",
    ("node", "min_capacity_margin"): "capacity_margin_min",
    ("node", "min_capacity_margin_penalty"): "capacity_margin_penalty",
    ("node", "nodal_balance_sense"): "balance_sense",
    ("node", "node_slack_penalty"): "balance_penalty",
    ("node", "frac_state_loss"): "storage_self_discharge",
    ("node", "number_of_storages"): "existing_storages",
    ("node", "state_coeff"): "storage_state_coefficient",
    ("node", "storage_fom_cost"): "storage_fixed_annual_cost",
    ("node", "is_longterm_storage"): "storage_longterm_active",
    ("node", "fix_node_state"): "storage_state_fix",
    ("node", "initial_node_state"): "storage_state_initial",
    ("node", "node_state_cap"): "storage_state_max",
    ("node", "node_state_min"): "storage_state_min",
    ("node", "node_availability_factor"): "storage_state_max_fraction",
    ("node", "node_state_min_factor"): "storage_state_min_fraction",
    ("node", "fix_node_pressure"): "pressure_fix",
    ("node", "initial_node_pressure"): "pressure_initial",
    ("node", "max_node_pressure"): "pressure_max",
    ("node", "min_node_pressure"): "pressure_min",
    ("node", "fix_node_voltage_angle"): "voltage_angle_fix",
    ("node", "initial_node_voltage_angle"): "voltage_angle_initial",
    ("node", "max_voltage_angle"): "voltage_angle_max",
    ("node", "min_voltage_angle"): "voltage_angle_min",
    ("node", "storage_investment_econ_lifetime"): "storage_lifetime_economic",
    ("node", "storage_investment_tech_lifetime"): "storage_lifetime_technical",
    ("node", "storage_investment_lifetime_sense"): "storage_lifetime_constraint_sense",
    ("node", "candidate_storages"): "storage_investment_count_max_cumulative",
    ("node", "fix_storages_invested"): "storage_investment_count_fix_new",
    ("node", "fix_storages_invested_available"): "storage_investment_count_fix_cumulative",
    ("node", "initial_storages_invested"): "storage_investment_count_initial_new",
    ("node", "initial_storages_invested_available"): "storage_investment_count_initial_cumulative",
    ("node", "storages_invested_big_m_mga"): "mga_storage_investment_big_m",
    ("node", "storages_invested_mga"): "mga_storage_investment_active",
    ("node", "storages_invested_mga_weight"): "mga_storage_investment_weight",
    ("node", "downward_reserve"): "reserve_downward",
    ("node", "upward_reserve"): "reserve_upward",
    ("node", "is_reserve_node"): "reserve_active",

    # ---- connection ----
    ("connection", "connection_availability_factor"): "availability_factor",
    ("connection", "connection_contingency"): "contingency_active",
    ("connection", "connection_monitored"): "monitoring_active",
    ("connection", "connection_reactance"): "reactance",
    ("connection", "connection_reactance_base"): "reactance_base",
    ("connection", "connection_resistance"): "resistance",
    ("connection", "number_of_connections"): "existing_connections",
    ("connection", "has_binary_gas_flow"): "binary_gas_flow_active",
    ("connection", "connection_decommissioning_cost"): "decommissioning_cost",
    ("connection", "connection_decommissioning_time"): "decommissioning_time",
    ("connection", "connection_discount_rate_technology_specific"): "discount_rate_technology_specific",
    ("connection", "connection_investment_econ_lifetime"): "lifetime_economic",
    ("connection", "connection_investment_lifetime_sense"): "lifetime_constraint_sense",
    ("connection", "connection_investment_tech_lifetime"): "lifetime_technical",
    ("connection", "connection_investment_variable_type"): "investment_variable_type",
    ("connection", "connection_lead_time"): "lead_time",
    ("connection", "candidate_connections"): "investment_count_max_cumulative",
    ("connection", "fix_connections_invested"): "investment_count_fix_new",
    ("connection", "fix_connections_invested_available"): "investment_count_fix_cumulative",
    ("connection", "initial_connections_invested"): "investment_count_initial_new",
    ("connection", "initial_connections_invested_available"): "investment_count_initial_cumulative",
    ("connection", "connections_invested_big_m_mga"): "mga_investment_big_m",
    ("connection", "connections_invested_mga"): "mga_investment_active",
    ("connection", "connections_invested_mga_weight"): "mga_investment_weight",

    # ---- commodity (class itself renamed to grid; parameters carry over) ----
    ("commodity", "commodity_lodf_tolerance"): "lodf_tolerance",
    ("commodity", "commodity_physics"): "physics_type",
    ("commodity", "commodity_physics_duration"): "physics_duration",
    ("commodity", "commodity_ptdf_threshold"): "ptdf_threshold",

    # ---- investment_group ----
    ("investment_group", "equal_investments"): "equal_investments_active",
    ("investment_group", "maximum_capacity_invested_available"): "investment_capacity_total_max_cumulative",
    ("investment_group", "maximum_entities_invested_available"): "investment_count_total_max_cumulative",
    ("investment_group", "minimum_capacity_invested_available"): "investment_capacity_total_min_cumulative",
    ("investment_group", "minimum_entities_invested_available"): "investment_count_total_min_cumulative",

    # ---- model ----
    ("model", "db_lp_solver"): "solver_lp",
    ("model", "db_lp_solver_options"): "solver_lp_options",
    ("model", "db_mip_solver"): "solver_mip",
    ("model", "db_mip_solver_options"): "solver_mip_options",
    ("model", "max_gap"): "decomposition_max_gap",
    ("model", "max_iterations"): "decomposition_max_iterations",
    ("model", "max_mga_iterations"): "mga_max_iterations",
    ("model", "max_mga_slack"): "mga_max_slack",
    ("model", "min_iterations"): "decomposition_min_iterations",
    ("model", "report_benders_iterations"): "benders_iterations_reporting_active",
    ("model", "use_connection_intact_flow"): "connection_investment_power_flow_impact_active",
    ("model", "use_highest_resolution_constraint_ratio_out_in_connection_flow"): "connection_flow_highest_resolution_active",
    ("model", "use_tight_compact_formulations"): "tight_compact_formulations_active",

    # ---- node__node ----
    ("node__node", "diff_coeff"): "diffusion_coefficient",

    # ---- node__user_constraint ----
    ("node__user_constraint", "demand_coefficient"): "coefficient_for_demand",
    ("node__user_constraint", "node_state_coefficient"): "coefficient_for_node_state",
    ("node__user_constraint", "storages_invested_available_coefficient"): "coefficient_for_storages_invested_available",
    ("node__user_constraint", "storages_invested_coefficient"): "coefficient_for_storages_invested",

    # ---- unit__to_node / node__to_unit (parameter renames are the same) ----
    ("unit__to_node", "fix_unit_flow"): "flow_limits_fix",
    ("node__to_unit", "fix_unit_flow"): "flow_limits_fix",
    ("unit__to_node", "fix_unit_flow_op"): "flow_limits_fix_op",
    ("node__to_unit", "fix_unit_flow_op"): "flow_limits_fix_op",
    ("unit__to_node", "initial_unit_flow"): "flow_limits_initial",
    ("node__to_unit", "initial_unit_flow"): "flow_limits_initial",
    ("unit__to_node", "initial_unit_flow_op"): "flow_limits_initial_op",
    ("node__to_unit", "initial_unit_flow_op"): "flow_limits_initial_op",
    ("node__to_unit", "max_total_cumulated_unit_flow_from_node"): "flow_limits_max_cumulative",
    ("node__to_unit", "min_total_cumulated_unit_flow_from_node"): "flow_limits_min_cumulative",
    ("unit__to_node", "max_total_cumulated_unit_flow_to_node"): "flow_limits_max_cumulative",
    ("unit__to_node", "min_total_cumulated_unit_flow_to_node"): "flow_limits_min_cumulative",
    ("unit__to_node", "min_unit_flow"): "flow_limits_min",
    ("node__to_unit", "min_unit_flow"): "flow_limits_min",
    ("unit__to_node", "ramp_down_limit"): "ramp_limits_down",
    ("node__to_unit", "ramp_down_limit"): "ramp_limits_down",
    ("unit__to_node", "ramp_up_limit"): "ramp_limits_up",
    ("node__to_unit", "ramp_up_limit"): "ramp_limits_up",
    ("unit__to_node", "shut_down_limit"): "ramp_limits_shutdown",
    ("node__to_unit", "shut_down_limit"): "ramp_limits_shutdown",
    ("unit__to_node", "start_up_limit"): "ramp_limits_startup",
    ("node__to_unit", "start_up_limit"): "ramp_limits_startup",
    ("unit__to_node", "unit_capacity"): "capacity_per_unit",
    ("node__to_unit", "unit_capacity"): "capacity_per_unit",
    ("unit__to_node", "unit_conv_cap_to_flow"): "capacity_to_flow_conversion_factor",
    ("node__to_unit", "unit_conv_cap_to_flow"): "capacity_to_flow_conversion_factor",

    # ---- unit__user_constraint ----
    ("unit__user_constraint", "units_invested_available_coefficient"): "coefficient_for_units_invested_available",
    ("unit__user_constraint", "units_invested_coefficient"): "coefficient_for_units_invested",
    ("unit__user_constraint", "units_on_coefficient"): "coefficient_for_units_on",
    ("unit__user_constraint", "units_started_up_coefficient"): "coefficient_for_units_started_up",

    # ---- unit_flow__user_constraint (post class-rename) ----
    ("unit_flow__user_constraint", "unit_flow_coefficient"): "coefficient_for_unit_flow",

    # ---- connection__from_node / connection__to_node ----
    ("connection__from_node", "fix_binary_gas_connection_flow"): "binary_gas_flow_limits_fix",
    ("connection__to_node", "fix_binary_gas_connection_flow"): "binary_gas_flow_limits_fix",
    ("connection__from_node", "initial_binary_gas_connection_flow"): "binary_gas_flow_limits_initial",
    ("connection__to_node", "initial_binary_gas_connection_flow"): "binary_gas_flow_limits_initial",
    ("connection__from_node", "fix_connection_flow"): "flow_limits_fix",
    ("connection__to_node", "fix_connection_flow"): "flow_limits_fix",
    ("connection__from_node", "fix_connection_intact_flow"): "flow_limits_fix_intact",
    ("connection__to_node", "fix_connection_intact_flow"): "flow_limits_fix_intact",
    ("connection__from_node", "initial_connection_flow"): "flow_limits_initial",
    ("connection__to_node", "initial_connection_flow"): "flow_limits_initial",
    ("connection__from_node", "initial_connection_intact_flow"): "flow_limits_initial_intact",
    ("connection__to_node", "initial_connection_intact_flow"): "flow_limits_initial_intact",
    ("connection__from_node", "connection_capacity"): "capacity_per_connection",
    ("connection__to_node", "connection_capacity"): "capacity_per_connection",
    ("connection__from_node", "connection_conv_cap_to_flow"): "capacity_to_flow_conversion_factor",
    ("connection__to_node", "connection_conv_cap_to_flow"): "capacity_to_flow_conversion_factor",

    # ---- connection__from_node__user_constraint (also moved to unit_flow__user_constraint) ----
    ("connection__from_node__user_constraint", "connection_flow_coefficient"): "coefficient_for_connection_flow",
    ("connection__to_node__user_constraint", "connection_flow_coefficient"): "coefficient_for_connection_flow",

    # ---- connection__user_constraint ----
    ("connection__user_constraint", "connections_invested_available_coefficient"): "coefficient_for_connections_invested_available",
    ("connection__user_constraint", "connections_invested_coefficient"): "coefficient_for_connections_invested",

    # ---- temporal_block ----
    ("temporal_block", "representative_period_index"): "representative_block_index",
    ("temporal_block", "representative_periods_mapping"): "representative_blocks_by_period",
}

# Parameters that were removed with no replacement.
REMOVED_PARAMS: dict[tuple[str, str], str] = {
    ("user_constraint", "include_in_non_representative_periods"):
        "Removed; user constraint temporal control now via unit_flow class structure",
    ("node", "has_pressure"):
        "Moved to grid::physics_type (value 'pressure_physics')",
    ("node", "has_voltage_angle"):
        "Moved to grid::physics_type (value 'voltage_angle_physics')",
}

# ---------------------------------------------------------------------------
# Parameter value list renames: {old_list: new_list}
# ---------------------------------------------------------------------------
LIST_RENAMES: dict[str, str] = {
    "commodity_physics_list": "grid_physics_list",
    "db_lp_solver_list": "solver_lp_list",
    "db_mip_solver_list": "solver_mip_list",
    # These four all merged into variable_type_list:
    "unit_investment_variable_type_list": "variable_type_list",
    "connection_investment_variable_type_list": "variable_type_list",
    "storage_investment_variable_type_list": "variable_type_list",
    "unit_online_variable_type_list": "variable_type_list",
}

# ---------------------------------------------------------------------------
# Individual value renames within value lists.
# {old_value: new_value}
# Includes the variable-type list merge (unit_investment_variable_type_continuous -> linear etc.).
# ---------------------------------------------------------------------------
VALUE_RENAMES: dict[str, str] = {
    # grid physics
    "commodity_physics_lodf": "lodf_physics",
    "commodity_physics_none": "none",
    "commodity_physics_ptdf": "ptdf_physics",
    # balance types
    "balance_type_none": "none",
    "balance_type_node": "node_balance",
    "balance_type_group": "group_balance",
    # unit investment variable type
    "unit_investment_variable_type_continuous": "linear",
    "unit_investment_variable_type_integer": "integer",
    # connection investment variable type
    "connection_investment_variable_type_continuous": "linear",
    "connection_investment_variable_type_integer": "integer",
    # storage investment variable type
    "storage_investment_variable_type_continuous": "linear",
    "storage_investment_variable_type_integer": "integer",
    # unit online variable type
    "unit_online_variable_type_linear": "linear",
    "unit_online_variable_type_binary": "binary",
    "unit_online_variable_type_integer": "integer",
    "unit_online_variable_type_none": "none",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def rename_param(class_name: str, param_name: str) -> tuple[str, str]:
    """Return (new_class, new_param) for a given (class, param). Handles the
    case where the class itself was renamed / restructured.

    For simple parameter renames: (class, "old") -> (class, "new").
    For class renames (commodity -> grid): (commodity, p) -> (grid, new_p_if_any_else_p).
    For class structural updates (unit__from_node -> node__to_unit): the arg
    order swap is separate; this only handles the class + name translation.
    """
    # 1. Class rename first
    effective_class = CLASS_RENAMES.get(class_name, class_name)
    # For class updates (dimension swap or unit_flow), the class name still
    # changes; look up the new name.
    if class_name in CLASS_UPDATES:
        effective_class = CLASS_UPDATES[class_name][0]
    # 2. Parameter rename (may be keyed on old or new class)
    for lookup_class in (class_name, effective_class):
        if (lookup_class, param_name) in PARAM_RENAMES:
            return effective_class, PARAM_RENAMES[(lookup_class, param_name)]
    # No rename; return effective class + original param
    return effective_class, param_name


def is_removed_param(class_name: str, param_name: str) -> bool:
    return (class_name, param_name) in REMOVED_PARAMS


def is_removed_class(class_name: str) -> bool:
    return class_name in REMOVED_CLASSES


def swap_class_bynames(class_name: str, byname: tuple) -> tuple[str, tuple]:
    """For a class-updated entity_byname, return (new_class, new_byname).
    If class has no update, returns (class_name, byname) unchanged.
    """
    if class_name not in CLASS_UPDATES:
        return class_name, tuple(byname)
    new_class, mapping = CLASS_UPDATES[class_name]
    new_byname = tuple(byname[i - 1] for i in mapping)
    return new_class, new_byname


def rename_list(list_name: str) -> str:
    return LIST_RENAMES.get(list_name, list_name)


def rename_value(value: str) -> str:
    return VALUE_RENAMES.get(value, value)


# ---------------------------------------------------------------------------
# Convenience: sets for quick lookup by scripts wanting to find obsolete refs.
# ---------------------------------------------------------------------------
OLD_PARAM_NAMES: frozenset[str] = frozenset(p for _, p in PARAM_RENAMES.keys())
OLD_CLASS_NAMES: frozenset[str] = (
    frozenset(CLASS_RENAMES.keys()) | frozenset(CLASS_UPDATES.keys()) | frozenset(REMOVED_CLASSES.keys())
)
OLD_LIST_NAMES: frozenset[str] = frozenset(LIST_RENAMES.keys())
OLD_VALUE_NAMES: frozenset[str] = frozenset(VALUE_RENAMES.keys())


if __name__ == "__main__":
    print(f"PARAM_RENAMES:   {len(PARAM_RENAMES)} entries")
    print(f"CLASS_RENAMES:   {len(CLASS_RENAMES)} entries")
    print(f"CLASS_UPDATES:   {len(CLASS_UPDATES)} entries")
    print(f"REMOVED_CLASSES: {len(REMOVED_CLASSES)} entries")
    print(f"REMOVED_PARAMS:  {len(REMOVED_PARAMS)} entries")
    print(f"LIST_RENAMES:    {len(LIST_RENAMES)} entries")
    print(f"VALUE_RENAMES:   {len(VALUE_RENAMES)} entries")
