"""Shared settings for the course figures.

Figures are drawn with schematic.py (a copy of the HaLab schematic-draw skill's script) and
saved as SVG with live text in assets/img/wNN/. Run a week's script from the repo root:

    python3 figs/w01.py

Colours follow the slide-gallery charcoal palette (kkonoo.github.io/slide-gallery):
primary #2F343B, tints at 35/60/82% white, accent #E5484D (once per figure at most).
Icons are Lucide (lucide-static 1.45.0, ISC licence) in figs/icons/.
"""
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import schematic as sc  # noqa: E402

ROOT = HERE.parent
ICONS = HERE / "icons"

# slide-gallery 차콜: 주조색, 그라데이션 짝 색 두 개, 강조색
sc.THEMES[("charcoal", "clean")] = dict(primary="2F343B", emerald="33496B", teal="3F6A92", accent="E5484D")
# "faint" = 90% white, the slide-gallery 옅은 면, for bands behind other boxes
sc.TINTS["faint"] = 0.90
sc.FILLED.add("faint")
# Web figure: 240 mm wide (about 900 px), shown at the page's body width.
sc.SIZES["web"] = dict(w=240, h=None, margin=4, title=0, name=13, sub=10.5, label=10, floor=9.5, stroke=0.75, pad=1.8)

INK = "2F343B"
MUTED = "6B7280"


def scene(h, alt, budget=9):
    """A web figure of height h (mm). alt is the accessible title."""
    return sc.Scene("web", theme="charcoal", mode="clean", h=h, alt=alt, budget=budget)


def icon(name, x, y, size=7, color=INK):
    """A Lucide icon as an SVG group, top-left at (x, y) mm, size in mm."""
    svg = (ICONS / f"{name}.svg").read_text(encoding="utf-8")
    inner = re.search(r"<svg[^>]*>(.*)</svg>", svg, re.S).group(1).strip()
    return (f'<g transform="translate({x:.2f},{y:.2f}) scale({size / 24:.4f})" fill="none" stroke="#{color}" '
            f'stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{inner}</g>')


def save(s, week, name, extra=()):
    """Save to assets/img/<week>/<name>.svg and add extra SVG elements (icons) on top."""
    out = ROOT / "assets" / "img" / week / f"{name}.svg"
    out.parent.mkdir(parents=True, exist_ok=True)
    s.save(str(out))
    if extra:
        text = out.read_text(encoding="utf-8")
        text = text.replace("</svg>", "".join(extra) + "</svg>")
        out.write_text(text, encoding="utf-8")
    return out
