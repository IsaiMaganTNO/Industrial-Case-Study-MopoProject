"""Real geography for the IC1 deck.

Reads the two GeoJSON files shipped in `geodata/` and exposes them as plain
matplotlib-ready polygon lists plus representative points. No geopandas, no
pyproj: the files are already CRS84 (lon/lat degrees) and at this latitude an
equal-aspect plot with aspect = 1/cos(lat) is visually indistinguishable from a
proper conformal projection.
"""
from __future__ import annotations

import json
import math
import os

import numpy as np
from matplotlib.collections import PolyCollection

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
GEODIR = os.path.join(ROOT, "geodata")

ONSHORE = os.path.join(GEODIR, "IC1.geojson")
OFFSHORE = os.path.join(GEODIR, "offshore.geojson")

# reservoirs actually referenced by CO2-injection-* units in the model
RESERVOIRS = ("NSNL012", "NSNL031")


# ---------------------------------------------------------------- geometry io
def _rings(geom):
    """Flatten a (Multi)Polygon geometry to a list of exterior rings."""
    t = geom["type"]
    coords = geom["coordinates"]
    if t == "Polygon":
        polys = [coords]
    elif t == "MultiPolygon":
        polys = coords
    else:
        return []
    return [np.asarray(p[0], dtype=float) for p in polys if p and len(p[0]) >= 3]


def _ring_area(ring):
    x, y = ring[:, 0], ring[:, 1]
    return 0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1)))


def _ring_centroid(ring):
    x, y = ring[:, 0], ring[:, 1]
    cross = x * np.roll(y, -1) - np.roll(x, -1) * y
    a = cross.sum() / 2.0
    if abs(a) < 1e-12:
        return float(x.mean()), float(y.mean())
    cx = ((x + np.roll(x, -1)) * cross).sum() / (6.0 * a)
    cy = ((y + np.roll(y, -1)) * cross).sum() / (6.0 * a)
    return float(cx), float(cy)


def _load(path, keep=None):
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    out = {}
    for feat in data["features"]:
        props = feat.get("properties") or {}
        key = props.get("id")
        if key is None or (keep is not None and key not in keep):
            continue
        rings = _rings(feat.get("geometry") or {})
        if rings:
            out[key] = {"rings": rings, "props": props}
    return out


_CACHE = {}


def regions():
    """id -> {rings, props, centroid, area} for the 17 IC1 onshore regions."""
    if "regions" not in _CACHE:
        d = _load(ONSHORE)
        for k, v in d.items():
            v["centroid"] = _best_point(v["rings"])
            v["area"] = sum(_ring_area(r) for r in v["rings"])
        _CACHE["regions"] = d
    return _CACHE["regions"]


def reservoirs(keep=RESERVOIRS):
    if "res" not in _CACHE:
        d = _load(OFFSHORE, keep=set(keep))
        for k, v in d.items():
            v["centroid"] = _best_point(v["rings"])
            v["area"] = sum(_ring_area(r) for r in v["rings"])
        _CACHE["res"] = d
    return _CACHE["res"]


def _best_point(rings):
    """Centroid of the largest ring - robust for regions with small islands."""
    big = max(rings, key=_ring_area)
    return _ring_centroid(big)


# ----------------------------------------------------------------- projection
def aspect(lat):
    """Aspect ratio that makes degrees of lon and lat equal on screen."""
    return 1.0 / max(math.cos(math.radians(lat)), 1e-6)


def setup_axes(ax, bounds, pad=0.06):
    x0, x1, y0, y1 = bounds
    dx, dy = (x1 - x0), (y1 - y0)
    ax.set_xlim(x0 - pad * dx, x1 + pad * dx)
    ax.set_ylim(y0 - pad * dy, y1 + pad * dy)
    ax.set_aspect(aspect(0.5 * (y0 + y1)))
    ax.set_axis_off()


def bounds_of(*collections):
    xs, ys = [], []
    for coll in collections:
        for v in coll.values():
            for r in v["rings"]:
                xs.append(r[:, 0].min()); xs.append(r[:, 0].max())
                ys.append(r[:, 1].min()); ys.append(r[:, 1].max())
    return min(xs), max(xs), min(ys), max(ys)


# ------------------------------------------------------------------- painting
def paint(ax, features, facecolors=None, edgecolor="#ffffff", lw=0.8, zorder=1,
          default="#e8edf1", alpha=1.0):
    """Draw a dict of features. `facecolors` maps id -> colour."""
    verts, cols = [], []
    for key, v in features.items():
        col = (facecolors or {}).get(key, default)
        for ring in v["rings"]:
            verts.append(ring)
            cols.append(col)
    pc = PolyCollection(verts, facecolors=cols, edgecolors=edgecolor,
                        linewidths=lw, zorder=zorder, alpha=alpha)
    ax.add_collection(pc)
    return pc


def label(ax, features, keys=None, fontsize=7.5, color="#14202b", zorder=6,
          dy=0.0, fmt=str):
    for key in (keys if keys is not None else features):
        if key not in features:
            continue
        x, y = features[key]["centroid"]
        ax.text(x, y + dy, fmt(key), fontsize=fontsize, color=color, ha="center",
                va="center", zorder=zorder)


def centroids(which="onshore"):
    src = regions() if which == "onshore" else reservoirs()
    return {k: v["centroid"] for k, v in src.items()}


def ramp(values, lo_color, hi_color, vmax=None, gamma=0.65):
    """Simple two-colour ramp returning id -> hex, for choropleths."""
    import matplotlib.colors as mcolors
    lo = np.array(mcolors.to_rgb(lo_color))
    hi = np.array(mcolors.to_rgb(hi_color))
    vmax = vmax if vmax else max(list(values.values()) + [1e-12])
    out = {}
    for k, v in values.items():
        t = 0.0 if vmax <= 0 else (max(v, 0.0) / vmax) ** gamma
        out[k] = mcolors.to_hex(lo + t * (hi - lo))
    return out
