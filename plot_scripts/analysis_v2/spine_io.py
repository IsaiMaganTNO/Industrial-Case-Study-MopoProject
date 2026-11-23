"""Readers for Spine Toolbox SQLite databases (Spine DB schema, alembic rev with
`entity`/`entity_element`/`parameter_value`).

Entity names are NOT parsed by splitting on '__' -- element names in this model
contain '__' themselves. Dimensions are resolved through `entity_element`.
"""
from __future__ import annotations

import json
import sqlite3
from functools import lru_cache

import pandas as pd


def connect(path):
    con = sqlite3.connect(path)
    con.row_factory = sqlite3.Row
    return con


def _decode(v):
    return v.decode("utf-8") if isinstance(v, (bytes, bytearray)) else v


def class_dimensions(con):
    """{class_name: [dimension class names in position order]}"""
    q = """
    select ec.name as cls, dc.name as dim, ecd.position as pos
    from entity_class_dimension ecd
    join entity_class ec on ec.id = ecd.entity_class_id
    join entity_class dc on dc.id = ecd.dimension_id
    order by ec.name, ecd.position
    """
    out = {}
    for r in con.execute(q):
        out.setdefault(r["cls"], []).append(r["dim"])
    return out


@lru_cache(maxsize=None)
def _elements_frame(con_id, con):
    q = """
    select ee.entity_id, ee.position, el.name as element
    from entity_element ee
    join entity el on el.id = ee.element_id
    """
    return pd.read_sql(q, con)


def elements(con):
    """entity_id -> one `dim<N>` column per element position."""
    df = _elements_frame(id(con), con)
    wide = df.pivot(index="entity_id", columns="position", values="element")
    # integer column labels would be mangled by DataFrame.itertuples
    wide.columns = [f"dim{int(c)}" for c in wide.columns]
    return wide


def parameter_frame(con, param_names):
    """Raw parameter_value rows for the given parameter names, with dimension columns."""
    marks = ",".join("?" * len(param_names))
    q = f"""
    select pv.entity_id, pd.name as param, ec.name as cls, e.name as entity_name,
           pv.type as vtype, pv.value as value
    from parameter_value pv
    join parameter_definition pd on pd.id = pv.parameter_definition_id
    join entity_class ec on ec.id = pv.entity_class_id
    join entity e on e.id = pv.entity_id
    where pd.name in ({marks})
    """
    df = pd.read_sql(q, con, params=list(param_names))
    df["value"] = df["value"].map(_decode)
    el = elements(con)
    dims = class_dimensions(con)
    df = df.join(el, on="entity_id")
    # name the positional columns per class where unambiguous
    return df, dims


def _unpack(vtype, value):
    """Return list of (index, float) for scalars / time_series / maps / arrays."""
    try:
        obj = json.loads(value)
    except (TypeError, ValueError):
        try:
            return [(None, float(value))]
        except (TypeError, ValueError):
            return []
    if isinstance(obj, (int, float)):
        return [(None, float(obj))]
    if isinstance(obj, dict):
        data = obj.get("data", obj)
        if isinstance(data, dict):
            return [(k, float(v)) for k, v in data.items()]
        if isinstance(data, list):
            out = []
            for item in data:
                if isinstance(item, list) and len(item) == 2:
                    try:
                        out.append((item[0], float(item[1])))
                    except (TypeError, ValueError):
                        pass
                else:
                    try:
                        out.append((None, float(item)))
                    except (TypeError, ValueError):
                        pass
            return out
    return []


def timeseries(con, param_names, dim_cols):
    """Long-format frame: one row per (entity dimensions, timestamp).

    `dim_cols` maps `dim<N>` column name -> output column name.
    """
    df, _ = parameter_frame(con, param_names)
    missing = [k for k in dim_cols if k not in df.columns]
    if missing:
        raise KeyError(f"dimension columns {missing} absent; present: {list(df.columns)}")
    recs = []
    for row in df.itertuples(index=False):
        d = row._asdict()
        base = {name: d.get(src) for src, name in dim_cols.items()}
        base["param"] = d["param"]
        for ts, val in _unpack(d["vtype"], d["value"]):
            rec = dict(base)
            rec["ts"] = ts
            rec["value"] = val
            recs.append(rec)
    out = pd.DataFrame.from_records(recs)
    if not out.empty:
        out["ts"] = pd.to_datetime(out["ts"], errors="coerce")
    return out


def scalars(con, param_names):
    df, _ = parameter_frame(con, param_names)
    recs = []
    for row in df.itertuples(index=False):
        d = row._asdict()
        for ts, val in _unpack(d["vtype"], d["value"]):
            recs.append({"param": d["param"], "entity": d["entity_name"],
                         "ts": ts, "value": val})
    return pd.DataFrame.from_records(recs)
