# Can we add `atmosphere` as a commodity in the industry DB?

**Short answer: NO.** Adding it would break the CO2 budget. A different,
smaller change is required instead.

Date: 2026-10-01. Analysis only - no code changed as a result of this document.

---

## 1. Why the first attempt silently did nothing

`industry_importer` ran with `exit=0` but wrote **0** `CO2_emitted` rows.

Reproduced directly against a copy of `industry_db.sqlite`:

```
add technology__to_commodity                ('REF-SMR-MEA','atmosphere')
   -> err="non-existent elements in byname ... for class technology__to_commodity"
add technology__to_commodity__to_commodity  ('REF-SMR-MEA','HC','atmosphere')
   -> err="non-existent elements in byname ... for class ..."
add (control, the CO2 variant)
   -> err="there's already a entity with ... ('REF-SMR-MEA','HC','CO2')"
```

`atmosphere` does not exist as a `commodity` in `industry_db`, so both
`add_entity` calls fail. `add_tech_parameters()` is wrapped in a bare
`except:` that prints `"error conversion"`, so **284 exceptions were swallowed**
and the stage still reported success.

The `CO2` control proves the surrounding logic is correct - `CO2` exists only
because the capture block creates it.

> Side note: that bare `except:` is why this failure was invisible. Any future
> change in this function will fail the same silent way.

## 2. Why "just add the commodity" is the wrong fix

`atmosphere` is **not** a commodity. It is a `node`, and it carries the entire
CO2 budget.

| db | `atmosphere` | `CO2` |
|---|---|---|
| `industry_db` | absent | `commodity` |
| `INES_DB` | **`node`** | absent |

`ines_target.py::add_policy_constraints()` (line ~1424) creates it:

```python
entity_byname = ("atmosphere",)
add_entity(db_map,"node",entity_byname)
add_parameter_value(... "node_type","Base",... ,"storage")
add_parameter_value(... "storage_investment_method","Base",... ,"not_allowed")
add_parameter_value(... "storages_existing","Base",... , co2_budget)   # <-- the CO2 cap
add_parameter_value(... "storage_capacity","Base",... , 1000.0)
```

### 2.1 The ordering problem

In `main()`:

1. line ~1777 `add_industrial_sector(...)`   <- industry commodities become nodes
2. line ~1855 `add_policy_constraints(...)`  <- `atmosphere` node created here

So industry is imported **first**. If `atmosphere` were a commodity in
`industry_db`, the `commodity -> node` mapping would create the `atmosphere`
node early, and then `add_policy_constraints` would hit its `try/except` and
print `"WARNING: Node atmosphere already added"`.

### 2.2 Why that is not harmless

The `try/except` only wraps `add_entity` + `node_type`. The following lines are
**outside** it:

```python
add_parameter_value(db_map,"node","storage_investment_method",...)
add_parameter_value(db_map,"node","storages_existing",...)   # CO2 budget
add_parameter_value(db_map,"node","storage_capacity",...)
```

and `add_parameter_value` raises `RuntimeError` on any error. More importantly,
`node_type = "storage"` is set **inside** the `try`, after `add_entity` raises -
so an `atmosphere` node created by the industry path would be left
**without `node_type="storage"`**, while still receiving `storages_existing`.

A node that holds the CO2 budget but is not typed as storage does not enforce a
cumulative budget. That is exactly the class of silent failure that already cost
this project two multi-hour runs (`representative_blocks_by_period`, and the
365x cap scaling).

### 2.3 Second problem: the default parameter

`sysconfig.yaml`, `industrial_sector`:

```yaml
default:
  commodity:
    node:
      - [flow_scaling_method,use_profile_directly,[[1]],[demand]]
```

Every industry commodity-turned-node gets `flow_scaling_method`. Applying that
to the CO2 budget node is meaningless at best.

## 3. Conclusion

Creating `atmosphere` as a commodity in `industry_db` would:

- pre-empt the node that carries `storages_existing` (the CO2 cap),
- likely leave it missing `node_type="storage"`,
- attach an irrelevant `flow_scaling_method` default,
- and do all of this **silently**.

The user's instinct was right: this would have broken more than it fixed.

## 4. The correct approach instead

Keep the route emission factors keyed on something that already exists in
`industry_db`, and let the **existing** `atmosphere` plumbing in
`ines_to_spineopt.py` consume them.

`process_emissions()` already creates `unit__to_node (unit, "atmosphere")` and
the `unit_flow__unit_flow` ratio. It has the `atmosphere` node available,
because by then `add_policy_constraints` has run. The only thing it lacks is a
per-route number.

So: carry the route emission factor through as a **technology-level parameter**
(the `technology`/`co2_emission` definition already exists, unused, in
`industry_template_DB.json`), and have `process_emissions()` prefer it over
`co2_content` when present.

This keeps every change inside code that already handles `atmosphere`, adds no
new entity to `industry_db`, and leaves `add_policy_constraints` untouched.
