"""Bundle every PNG in a report directory into one ordered PDF.

    python tools/make_report_pdf.py <dir> [-o out.pdf] [--title "..."]

Deck slides (deck/P*.png) come first in page order, then the analysis figures
(figures/v2_F*.png). Images are placed on landscape pages at their own aspect
ratio, so nothing is stretched.
"""
from __future__ import annotations

import argparse
import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.backends.backend_pdf import PdfPages

PAGE = (13.33, 7.5)


def collect(root):
    """Ordered list of (path, section) for everything we want in the PDF."""
    out = []
    deck = os.path.join(root, "deck")
    figs = os.path.join(root, "figures")
    if os.path.isdir(deck):
        for f in sorted(os.listdir(deck)):
            if f.lower().endswith(".png"):
                out.append((os.path.join(deck, f), "deck"))
    if os.path.isdir(figs):
        for f in sorted(os.listdir(figs)):
            if f.lower().endswith(".png"):
                out.append((os.path.join(figs, f), "figures"))
    return out


def add_image(pdf, path):
    img = mpimg.imread(path)
    h, w = img.shape[0], img.shape[1]
    fig = plt.figure(figsize=PAGE)
    fig.patch.set_facecolor("white")
    # fit the image inside the page, preserving aspect
    page_ar = PAGE[0] / PAGE[1]
    img_ar = w / h
    if img_ar >= page_ar:
        iw = 1.0
        ih = page_ar / img_ar
    else:
        ih = 1.0
        iw = img_ar / page_ar
    ax = fig.add_axes([(1 - iw) / 2, (1 - ih) / 2, iw, ih])
    ax.imshow(img)
    ax.set_axis_off()
    pdf.savefig(fig, facecolor="white")
    plt.close(fig)


def divider(pdf, title, subtitle=""):
    fig = plt.figure(figsize=PAGE)
    fig.patch.set_facecolor("white")
    fig.text(0.07, 0.56, title, fontsize=34, color="#14202b", fontweight="bold",
             va="center")
    if subtitle:
        fig.text(0.07, 0.46, subtitle, fontsize=14, color="#5c6b77", va="center")
    fig.patches.append(plt.Rectangle((0.07, 0.64), 0.10, 0.006, color="#0e7c86",
                                     transform=fig.transFigure, figure=fig))
    pdf.savefig(fig, facecolor="white")
    plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root", help="report directory containing deck/ and figures/")
    ap.add_argument("-o", "--out", default=None, help="output PDF path")
    ap.add_argument("--title", default=None, help="title for the cover divider")
    args = ap.parse_args(argv)

    root = os.path.abspath(args.root)
    if not os.path.isdir(root):
        raise SystemExit(f"not a directory: {root}")
    items = collect(root)
    if not items:
        raise SystemExit(f"no PNGs found under {root}/deck or {root}/figures")

    out = args.out or os.path.join(root, os.path.basename(root) + "_FULL.pdf")
    n_deck = sum(1 for _, s in items if s == "deck")
    n_fig = sum(1 for _, s in items if s == "figures")

    seen = set()
    with PdfPages(out) as pdf:
        for path, section in items:
            if section not in seen:
                seen.add(section)
                if section == "deck":
                    divider(pdf, args.title or os.path.basename(root),
                            f"Presentation deck \u2014 {n_deck} slides")
                else:
                    divider(pdf, "Technical appendix",
                            f"Analysis figures \u2014 {n_fig} charts")
            add_image(pdf, path)
    print(f"  {len(items)} pages ({n_deck} slides + {n_fig} figures) -> {out}")
    return out


if __name__ == "__main__":
    main()
