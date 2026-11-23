"""Shared visual language for the IC1 result deck.

Muted, print-safe palette; direct labelling instead of dense legends; one
headline per figure. Nothing here depends on the scenario.
"""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.path import Path
from matplotlib.patches import PathPatch, FancyBboxPatch

# --------------------------------------------------------------------------- ink
INK = "#14202b"
SUB = "#5c6b77"
FAINT = "#9aa8b4"
RULE = "#dde3e8"
PANEL = "#f4f7f9"
WHITE = "#ffffff"

TEAL = "#0e7c86"
BLUE = "#2d6cb3"
GREEN = "#2f9e62"
AMBER = "#e0a526"
CORAL = "#d1495b"
VIOLET = "#6a4c93"
SLATE = "#8b9aa8"
SAND = "#b8873b"
MINT = "#5fb49c"
PLUM = "#9e4770"

CYCLE = [TEAL, AMBER, CORAL, BLUE, GREEN, VIOLET, SAND, MINT, PLUM, SLATE]


def apply():
    plt.rcParams.update({
        "figure.dpi": 160,
        "savefig.dpi": 160,
        "figure.facecolor": WHITE,
        "savefig.facecolor": WHITE,
        "font.family": ["Segoe UI", "DejaVu Sans"],
        "font.size": 10,
        "text.color": INK,
        "axes.edgecolor": RULE,
        "axes.labelcolor": SUB,
        "axes.titlecolor": INK,
        "axes.facecolor": WHITE,
        "axes.grid": True,
        "axes.axisbelow": True,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.spines.left": False,
        "grid.color": RULE,
        "grid.linewidth": 0.8,
        "xtick.color": SUB,
        "ytick.color": SUB,
        "xtick.major.size": 0,
        "ytick.major.size": 0,
        "legend.frameon": False,
    })


# ------------------------------------------------------------------- furniture
def headline(fig, kicker, title, standfirst=None, x=0.045, y=0.965):
    fig.text(x, y, "  ".join(kicker.upper()), fontsize=8.5, color=TEAL,
             fontweight="bold", va="top")
    fig.text(x, y - 0.052, title, fontsize=20, color=INK, fontweight="bold", va="top")
    if standfirst:
        fig.text(x, y - 0.115, standfirst, fontsize=11, color=SUB, va="top")


def source_note(fig, text, x=0.045, y=0.022):
    fig.text(x, y, text, fontsize=8, color=FAINT, va="bottom")


def card(fig, rect, value, label, note=None, accent=TEAL):
    """A KPI tile drawn in figure coordinates: rect = (x, y, w, h)."""
    x, y, w, h = rect
    ax = fig.add_axes(rect)
    ax.set_axis_off()
    ax.add_patch(FancyBboxPatch((0, 0), 1, 1, boxstyle="round,pad=0,rounding_size=0.06",
                                transform=ax.transAxes, facecolor=PANEL,
                                edgecolor="none", zorder=0))
    ax.add_patch(FancyBboxPatch((0, 0), 0.018, 1, boxstyle="square,pad=0",
                                transform=ax.transAxes, facecolor=accent,
                                edgecolor="none", zorder=1))
    ax.text(0.09, 0.66, value, fontsize=24, fontweight="bold", color=INK,
            va="center", ha="left", transform=ax.transAxes)
    ax.text(0.09, 0.33, label, fontsize=9.5, color=SUB, va="center", ha="left",
            transform=ax.transAxes)
    if note:
        ax.text(0.09, 0.14, note, fontsize=8, color=FAINT, va="center", ha="left",
                transform=ax.transAxes)
    return ax


def strip_axes(ax, keep_x=True):
    ax.grid(axis="x", visible=False)
    ax.tick_params(length=0)
    for s in ax.spines.values():
        s.set_visible(False)
    if not keep_x:
        ax.set_xticks([])


def label_bar(ax, x, y, text, color=INK, dy=0, **kw):
    ax.annotate(text, (x, y), ha="center", va="bottom", fontsize=kw.pop("fontsize", 10),
                color=color, fontweight=kw.pop("fontweight", "bold"),
                xytext=(0, 4 + dy), textcoords="offset points", **kw)


# ---------------------------------------------------------------------- sankey
def sankey(ax, links, columns, node_colors=None, link_colors=None,
           node_width=0.022, gap_frac=0.035, alpha=0.55,
           label_fmt="{name}", value_fmt="{v:,.0f}", fontsize=9):
    """Multi-column Sankey drawn with bezier ribbons.

    links    : list of (source, target, value)
    columns  : list of lists of node names, left to right
    """
    size = {}
    for s, t, v in links:
        size[s] = size.get(s, 0.0) + v
        size[t] = size.get(t, 0.0) + v
    # a node's height is max(inflow, outflow), not their sum
    inflow, outflow = {}, {}
    for s, t, v in links:
        outflow[s] = outflow.get(s, 0.0) + v
        inflow[t] = inflow.get(t, 0.0) + v
    size = {n: max(inflow.get(n, 0.0), outflow.get(n, 0.0))
            for col in columns for n in col}

    col_totals = [sum(size[n] for n in col) for col in columns]
    scale = max(col_totals) if col_totals else 1.0

    pos = {}
    n_cols = len(columns)
    for ci, col in enumerate(columns):
        gaps = gap_frac * max(len(col) - 1, 0)
        avail = 1.0 - gaps
        total = col_totals[ci] or 1.0
        y = 1.0 - (1.0 - (col_totals[ci] / scale * avail + gaps)) / 2.0
        x = ci / max(n_cols - 1, 1)
        for n in col:
            h = size[n] / scale * avail
            pos[n] = {"x": x, "y0": y - h, "y1": y, "col": ci,
                      "out_cur": y, "in_cur": y}
            y -= h + gap_frac

    node_colors = node_colors or {}
    link_colors = link_colors or {}

    for s, t, v in sorted(links, key=lambda r: -r[2]):
        a, b = pos[s], pos[t]
        ha = v / scale * (1.0 - gap_frac * max(len(columns[a["col"]]) - 1, 0))
        hb = v / scale * (1.0 - gap_frac * max(len(columns[b["col"]]) - 1, 0))
        y0t, y0b = a["out_cur"], a["out_cur"] - ha
        y1t, y1b = b["in_cur"], b["in_cur"] - hb
        a["out_cur"] -= ha
        b["in_cur"] -= hb
        x0 = a["x"] + node_width / 2
        x1 = b["x"] - node_width / 2
        xm = (x0 + x1) / 2
        verts = [(x0, y0t), (xm, y0t), (xm, y1t), (x1, y1t),
                 (x1, y1b), (xm, y1b), (xm, y0b), (x0, y0b), (x0, y0t)]
        codes = [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4,
                 Path.LINETO, Path.CURVE4, Path.CURVE4, Path.CURVE4, Path.CLOSEPOLY]
        c = link_colors.get((s, t), node_colors.get(s, SLATE))
        ax.add_patch(PathPatch(Path(verts, codes), facecolor=c, edgecolor="none",
                               alpha=alpha, zorder=1))

    for n, p in pos.items():
        ax.add_patch(plt.Rectangle((p["x"] - node_width / 2, p["y0"]), node_width,
                                   p["y1"] - p["y0"], facecolor=node_colors.get(n, INK),
                                   edgecolor="none", zorder=3))
        left = p["col"] == len(columns) - 1
        name = label_fmt.format(name=n)
        value = value_fmt.format(v=size[n])
        # a short node cannot carry a stacked label without colliding with its neighbour
        sep = "\n" if (p["y1"] - p["y0"]) > 0.05 else "  ·  "
        ax.text(p["x"] + (-1 if left else 1) * (node_width / 2 + 0.012),
                (p["y0"] + p["y1"]) / 2, name + sep + value,
                ha="right" if left else "left", va="center", fontsize=fontsize,
                color=INK, linespacing=1.45, zorder=4)

    ax.set_xlim(-0.30, 1.30)
    ax.set_ylim(-0.04, 1.04)
    ax.set_axis_off()
    return pos
