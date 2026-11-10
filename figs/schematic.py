#!/usr/bin/env python3
"""Editable schematics from one scene: PowerPoint native shapes (.pptx) or SVG, plus rule checks.

Geometry is in mm, font sizes in pt. Colours are named by role, so a .pptx follows the deck's theme.

    from schematic import Scene
    s = Scene("slide", theme="teal", mode="clean", title="...", section="...")
    a = s.box(13, 60, 60, 24, "검체 수집", sub="n = 12")
    b = s.box(95, 60, 60, 24, "snRNA-seq", style="soft")
    s.link(a, b, label="제공")
    s.save("out.pptx")            # or "out.svg"; prints check results
"""
import io
import math
import re
import subprocess
import sys
import unicodedata
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

THEMES = {  # role values from "PPT 디자인 규칙 v0.1"
    ("teal", "clean"): dict(primary="0F4C6E", emerald="1E9E86", teal="3DB5C2", accent="E5484D"),
    ("teal", "rich"): dict(primary="13394F", emerald="1A9A8B", teal="57BCC8", accent="E94F4F"),
    ("blue", "clean"): dict(primary="2563C9", emerald="14A884", teal="36B3C2", accent="FFD93D"),
    ("blue", "rich"): dict(primary="122F6B", emerald="14A884", teal="36B3C2", accent="FFD93D"),
}
NEUTRAL = dict(paper="FBFBFB", ink="262B33", muted="6B7280", border="E2E5EA", white="FFFFFF", navy="0D2250")
TINTS = dict(strong=0.35, mid=0.60, soft=0.82)  # share of white mixed into primary

SIZES = {
    "slide": dict(w=338.67, h=190.5, margin=13, title=28, name=18, sub=13, label=12, floor=12, stroke=1.0, pad=2.0),
    "slide-dense": dict(w=338.67, h=190.5, margin=13, title=22, name=13, sub=10, label=10, floor=10, stroke=0.75, pad=1.5),
    "a4": dict(w=297, h=210, margin=13, title=22, name=13, sub=10, label=10, floor=10, stroke=0.75, pad=1.5),
    "paper-180": dict(w=180, h=None, margin=1, title=0, name=7, sub=6, label=6, floor=6, stroke=0.5, pad=0.8),
    "paper-85": dict(w=85, h=None, margin=1, title=0, name=7, sub=6, label=6, floor=6, stroke=0.5, pad=0.8),
}
FILLED = {"primary", "emerald", "teal", "accent", "strong", "mid", "soft"}
PT = 0.3528  # mm per pt
LINE = 1.3   # line height, em (PowerPoint multiple 1.1 on Pretendard comes to about this)
SUB_GAP = 0.3  # space between a name and its sub, in em of the sub
FONT = "Pretendard, 'Noto Sans KR', 'Malgun Gothic', 'Apple SD Gothic Neo', sans-serif"
KINDS = {"flow", "inhibit", "indirect", "plain", "dots"}


def char_em(ch):
    if unicodedata.combining(ch):
        return 0
    return 1.0 if unicodedata.east_asian_width(ch) in "WF" else 0.6


def text_mm(s, pt):
    """Width budget: per character, wide = 1em, everything else = 0.6em. Do not count by script."""
    return sum(char_em(c) for c in s) * pt * PT


def wrap(text, width, pt):
    lines = []
    for para in str(text).split("\n"):
        cur = ""
        for word in para.split(" "):
            trial = f"{cur} {word}" if cur else word
            if text_mm(trial, pt) <= width:
                cur = trial
                continue
            if cur:
                lines.append(cur)
            cur = ""
            for ch in word:  # a single word wider than the box breaks by character
                if text_mm(cur + ch, pt) > width and cur:
                    lines.append(cur)
                    cur = ""
                cur += ch
        lines.append(cur)
    return lines


def rgb(h):
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix_white(h, t):
    return "".join(f"{round(c + (255 - c) * t):02X}" for c in rgb(h))


def luminance(h):
    def f(c):
        c /= 255
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb(h)
    return 0.2126 * f(r) + 0.7152 * f(g) + 0.0722 * f(b)


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


class Node:
    def __init__(self, kind, x, y, w, h, text="", sub="", style="plain", **kw):
        self.kind, self.x, self.y, self.w, self.h = kind, x, y, w, h
        self.text, self.sub, self.style = text, sub, style
        self.bg = kw.pop("bg", False)
        self.align = kw.pop("align", "center")
        self.valign = kw.pop("valign", "middle")
        self.name_pt = kw.pop("name_pt", None)
        self.sub_pt = kw.pop("sub_pt", None)
        self.bold = kw.pop("bold", True)
        self.color = kw.pop("color", None)
        self.points = kw.pop("points", None)
        if kw:
            raise TypeError(f"unknown options: {sorted(kw)}")

    @property
    def cx(self):
        return self.x + self.w / 2

    @property
    def cy(self):
        return self.y + self.h / 2

    @property
    def label(self):
        return (self.text or self.sub or self.kind).replace("\n", " ")

    def contains(self, o):
        return (self is not o and self.x <= o.x and self.y <= o.y
                and self.x + self.w >= o.x + o.w and self.y + self.h >= o.y + o.h)


class Link:
    def __init__(self, a, b, sides, label, kind, mid, color, label_side):
        if kind not in KINDS:
            raise ValueError(f"kind must be one of {sorted(KINDS)}")
        self.a, self.b, self.sides, self.text, self.kind = a, b, sides, label, kind
        self.mid, self.color, self.label_side = mid, color, label_side
        self.pts, self.glue_a, self.glue_b, self.label_box = [], False, False, None


class Scene:
    def __init__(self, size="slide", theme="teal", mode="clean", title="", section="", tag="", h=None, budget=9, font=FONT, alt="", top=None):
        self.size_name = size
        self.S = dict(SIZES[size])
        if self.S["h"] is None:
            if h is None:
                raise ValueError(f"{size} needs a height: Scene('{size}', h=<mm>)")
            self.S["h"] = h
        self.theme, self.mode = theme, mode
        self.colors = {**NEUTRAL, **THEMES[(theme, mode)]}
        for k, t in TINTS.items():
            self.colors[k] = mix_white(self.colors["primary"], t)
        self.title, self.section, self.tag, self.budget, self.font, self.alt = title, section, tag, budget, font, alt
        self.top_override = top
        self.nodes, self.links, self.lines, self.rings = [], [], [], []

    # ---- content area -------------------------------------------------
    @property
    def has_header(self):
        return bool(self.title and self.S["title"])

    @property
    def title_lines(self):
        S = self.S
        return wrap(self.title, S["w"] - 2 * S["margin"], S["title"]) if self.has_header else []

    @property
    def rule_y(self):
        """Thin line under the header. The header grows with the title."""
        S = self.S
        return S["margin"] + (6 if self.section or self.tag else 0) + len(self.title_lines) * S["title"] * PT * LINE + 1.5

    @property
    def top(self):
        if self.top_override is not None:
            return self.top_override
        return self.rule_y + 4 if self.has_header else self.S["margin"]

    @property
    def body(self):
        """(x, y, w, h) of the free drawing area: under the header, or the whole page when there is no title."""
        S = self.S
        return S["margin"], self.top, S["w"] - 2 * S["margin"], S["h"] - self.top - S["margin"]

    # ---- primitives ---------------------------------------------------
    def _add(self, n):
        self.nodes.append(n)
        return n

    def box(self, x, y, w, h, text="", sub="", style="plain", **kw):
        return self._add(Node("box", x, y, w, h, text, sub, style, **kw))

    def pill(self, x, y, w, h, text, sub="", style="plain", **kw):
        return self._add(Node("pill", x, y, w, h, text, sub, style, **kw))

    def circle(self, cx, cy, r, text="", sub="", style="mid", **kw):
        return self._add(Node("circle", cx - r, cy - r, 2 * r, 2 * r, text, sub, style, **kw))

    def chevron(self, x, y, w, h, text="", sub="", style="mid", **kw):
        return self._add(Node("chevron", x, y, w, h, text, sub, style, **kw))

    def band(self, x, y, w, h, text="", style="soft", **kw):
        """Pale background column or zone. Nodes may sit inside; links may cross it."""
        kw.setdefault("align", "left")
        kw.setdefault("valign", "top")
        return self._add(Node("box", x, y, w, h, text, "", style, bg=True, **kw))

    def text(self, x, y, w, h, text, sub="", **kw):
        kw.setdefault("align", "left")
        kw.setdefault("bold", False)
        return self._add(Node("text", x, y, w, h, text, sub, "ghost", **kw))

    def line(self, x1, y1, x2, y2, dash=False, color="border"):
        self.lines.append((x1, y1, x2, y2, dash, color))

    def ring(self, cx, cy, r_out, r_in, labels, styles=None, gap_deg=2.5, start_deg=-90, arrows=True, name_pt=None):
        """Ring cut into len(labels) segments, clockwise from start_deg, with a direction mark at each joint.
        One tint by default: a cycle has no ranking."""
        n = len(labels)
        polar = lambda r, a: (cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a)))
        for i, lab in enumerate(labels):
            a0 = start_deg + 360 * i / n + gap_deg / 2
            a1 = start_deg + 360 * (i + 1) / n - gap_deg / 2
            arc = [a0 + (a1 - a0) * k / 24 for k in range(25)]
            pts = [polar(r_out, a) for a in arc] + [polar(r_in, a) for a in reversed(arc)]
            w, h = (r_out - r_in) * 1.45, (r_out - r_in) * 0.9
            mx, my = polar((r_out + r_in) / 2, (a0 + a1) / 2)
            style = styles[i] if styles else "mid"
            self.rings.append(Node("seg", mx - w / 2, my - h / 2, w, h, lab, "", style, points=pts, name_pt=name_pt))
        if arrows:  # a small triangle on each joint, pointing along the ring
            size, rm = (r_out - r_in) * 0.13, (r_out + r_in) / 2
            for i in range(n):
                a = math.radians(start_deg + 360 * i / n)
                px, py = cx + rm * math.cos(a), cy + rm * math.sin(a)
                tx, ty, nx, ny = -math.sin(a), math.cos(a), math.cos(a), math.sin(a)
                pts = [(px + tx * size, py + ty * size),
                       (px - tx * size * 0.7 + nx * size, py - ty * size * 0.7 + ny * size),
                       (px - tx * size * 0.7 - nx * size, py - ty * size * 0.7 - ny * size)]
                xs, ys = [q[0] for q in pts], [q[1] for q in pts]
                self.rings.append(Node("seg", min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys), "", "", "primary", points=pts))

    def link(self, a, b, sides=None, label="", kind="flow", mid=None, color="muted", label_side=None, width=None):
        """Orthogonal connector. sides like 'right>left'; omitted sides are picked from positions.
        kind: flow (arrow), inhibit (T-bar), indirect (dashed arrow), plain, dots (dotted, no arrow).
        mid: absolute mm position of the middle segment of an elbow, to route around something.
        width: line weight in pt, to separate main flows from coordination lines."""
        if sides and sides.split(">")[0] == sides.split(">")[1]:
            raise ValueError(f"sides='{sides}': a line leaving and entering the same side is not supported, because "
                             "PowerPoint can't store it reliably. Use other sides or move a box.")
        link = Link(a, b, sides, label, kind, mid, color, label_side)
        link.width = width
        self.links.append(link)
        return link

    # ---- routing --------------------------------------------------------
    @staticmethod
    def _auto_sides(a, b):
        if b.x >= a.x + a.w:
            return "right", "left"
        if b.x + b.w <= a.x:
            return "left", "right"
        if b.y >= a.y + a.h:
            return "bottom", "top"
        return "top", "bottom"

    def _resolve(self):
        ends = {}
        for link in self.links:
            sa, sb = link.sides.split(">") if link.sides else self._auto_sides(link.a, link.b)
            link.sa, link.sb = sa, sb
            ends.setdefault((id(link.a), sa), []).append((link, "a", link.a, link.b))
            ends.setdefault((id(link.b), sb), []).append((link, "b", link.b, link.a))
        for (_, side), items in ends.items():
            across = side in ("top", "bottom")
            items.sort(key=lambda it: it[3].cx if across else it[3].cy)
            for k, (link, end, n, _) in enumerate(items, 1):
                off = (n.w if across else n.h) * k / (len(items) + 1)
                if across:
                    p = (n.x + off, n.y if side == "top" else n.y + n.h)
                else:
                    p = (n.x if side == "left" else n.x + n.w, n.y + off)
                setattr(link, "p" + end, p)
                setattr(link, "glue_" + end, len(items) == 1 and n.kind in ("box", "pill", "circle"))
        for link in self.links:
            link.pts = self._route(link)
            link.label_box = self._label_box(link)

    @staticmethod
    def _route(link):
        (x0, y0), (x1, y1) = link.pa, link.pb
        ha, hb = link.sa in ("left", "right"), link.sb in ("left", "right")
        if ha and hb:
            if abs(y0 - y1) < 0.01:
                return [(x0, y0), (x1, y0)]
            m = link.mid if link.mid is not None else (x0 + x1) / 2
            return [(x0, y0), (m, y0), (m, y1), (x1, y1)]
        if not ha and not hb:
            if abs(x0 - x1) < 0.01:
                return [(x0, y0), (x0, y1)]
            m = link.mid if link.mid is not None else (y0 + y1) / 2
            return [(x0, y0), (x0, m), (x1, m), (x1, y1)]
        return [(x0, y0), (x1, y0), (x1, y1)] if ha else [(x0, y0), (x0, y1), (x1, y1)]

    def _label_box(self, link):
        if not link.text:
            return None
        pt = self.S["label"]
        w, h = text_mm(link.text, pt) + 1, pt * PT * LINE
        segs = list(zip(link.pts, link.pts[1:]))
        (ax, ay), (bx, by) = max(segs, key=lambda s: abs(s[0][0] - s[1][0]) + abs(s[0][1] - s[1][1]))
        gap = max(1.0, pt * PT * 0.35)
        mx, my = (ax + bx) / 2, (ay + by) / 2
        if abs(ay - by) < 0.01:
            y = my + gap if link.label_side == "below" else my - gap - h
            return mx - w / 2, y, w, h
        x = mx - gap - w if link.label_side == "left" else mx + gap
        return x, my - h / 2, w, h

    # ---- checks ---------------------------------------------------------
    def check(self):
        """Returns findings. ERROR = the rule is broken, fix it. WARN = look at it."""
        self._resolve()
        S, out = self.S, []
        err = lambda m: out.append(f"ERROR {m}")
        warn = lambda m: out.append(f"WARN  {m}")
        solid = [n for n in self.nodes if not n.bg]
        counted = [n for n in solid if n.kind in ("box", "circle")]  # pills are keywords, not nodes
        aligned = counted + [n for n in solid if n.kind == "pill"]

        if len(counted) > self.budget:
            warn(f"{len(counted)} nodes over budget {self.budget}: merge, or split into overview + detail")
        if len(self.links) > 12:
            warn(f"{len(self.links)} links over budget 12")
        if sum(n.style == "accent" for n in self.nodes) > 1:
            warn("accent colour used more than once: keep it to one place")
        if sum(n.style == "primary" and n.kind in ("box", "circle") for n in self.nodes) > 2:
            warn("more than 2 dark primary fills: keep dark colour for the conclusion or key item")

        m = S["margin"]
        inside = lambda x, y: m - 0.01 <= x <= S["w"] - m + 0.01 and self.top - 0.01 <= y <= S["h"] - m + 0.01
        for n in self.nodes + self.rings:
            corners = n.points or [(n.x, n.y), (n.x + n.w, n.y + n.h)]
            if not all(inside(a, b) for a, b in corners):
                err(f"'{n.label}' leaves the drawing area")
            self._check_text(n, err, warn)
        for link in self.links:
            if not all(inside(*p) for p in link.pts):
                err(f"link '{link.a.label}' > '{link.b.label}' leaves the drawing area")
        if len(self.title_lines) > 2:
            err(f"title runs to {len(self.title_lines)} lines: keep it to 2")
        for seg in self.rings:
            for n in solid:
                if n.kind == "circle":
                    hit = any(math.hypot(a - n.cx, b - n.cy) < n.w / 2 for a, b in seg.points)
                else:
                    hit = any(n.x < a < n.x + n.w and n.y < b < n.y + n.h for a, b in seg.points)
                if hit:
                    err(f"'{n.label}' overlaps the ring")
                    break

        for i, a in enumerate(solid):
            for b in solid[i + 1:]:
                if a.contains(b) or b.contains(a):
                    continue
                if a.kind == b.kind == "chevron" and min(a.x + a.w, b.x + b.w) - max(a.x, b.x) <= a.h / 2:
                    continue  # chevrons interlock: the point of one sits in the notch of the next
                if a.x < b.x + b.w and b.x < a.x + a.w and a.y < b.y + b.h and b.y < a.y + a.h:
                    err(f"'{a.label}' overlaps '{b.label}'")

        eps = 0.5 if S["w"] < 200 else 1.5
        seen = set()
        for i, a in enumerate(aligned):
            for b in aligned[i + 1:]:
                if a.kind != b.kind:
                    continue
                for name, u, v in (("left", a.x, b.x), ("centre x", a.cx, b.cx), ("right", a.x + a.w, b.x + b.w),
                                   ("top", a.y, b.y), ("centre y", a.cy, b.cy), ("bottom", a.y + a.h, b.y + b.h)):
                    if 0.01 < abs(u - v) < eps and (id(a), id(b)) not in seen:
                        seen.add((id(a), id(b)))
                        warn(f"'{a.label}' and '{b.label}' almost align on {name} ({abs(u - v):.1f} mm off)")
        self._check_gaps(aligned, warn)
        self._check_links(err, warn)
        return out

    def _check_text(self, n, err, warn):
        if (n.text or n.sub) and n.style in FILLED and n.kind != "seg":
            ratio = contrast(self._hex(n.style), self._ink_on(n.style))
            size = n.name_pt or self.S["name"]
            if ratio < (3.0 if size >= 18 and n.bold and not n.sub else 4.5):
                warn(f"'{n.label}' text on {n.style} has {ratio:.1f}:1 contrast: use a lighter or darker fill")
        name_pt = n.name_pt or self.S["name"]
        sub_pt = n.sub_pt or self.S["sub"]
        if n.text and name_pt < self.S["floor"]:
            err(f"'{n.label}' name {name_pt}pt is under the {self.S['floor']}pt floor")
        if n.sub and sub_pt < self.S["floor"]:
            err(f"'{n.label}' sub {sub_pt}pt is under the {self.S['floor']}pt floor")
        pad = 0 if n.kind == "text" else self.S["pad"]
        inner = n.w - 2 * pad
        if n.kind == "pill":
            inner -= n.h * 0.5
        if n.kind == "circle":
            inner = n.w * 0.8 - 2 * pad
        if n.kind == "chevron":
            inner -= n.h
        need = sub_pt * PT * SUB_GAP if n.text and n.sub else 0
        for s, pt in ((n.text, name_pt), (n.sub, sub_pt)):
            if s:
                need += len(wrap(s, inner, pt)) * pt * PT * LINE
        if need > n.h - 2 * pad + 0.01:
            err(f"'{n.label}' text needs {need:.1f} mm of height, has {n.h - 2 * pad:.1f}")

    @staticmethod
    def _check_gaps(nodes, warn):
        for axis in ("row", "column"):
            groups = {}
            for n in nodes:
                groups.setdefault((n.kind, round(n.cy if axis == "row" else n.cx, 1)), []).append(n)
            for items in groups.values():
                if len(items) < 3:
                    continue
                items.sort(key=lambda n: n.x if axis == "row" else n.y)
                gaps = [(b.x - a.x - a.w) if axis == "row" else (b.y - a.y - a.h) for a, b in zip(items, items[1:])]
                if max(gaps) - min(gaps) > 0.5:
                    warn(f"{axis} starting '{items[0].label}' has uneven gaps: {[round(g, 1) for g in gaps]}")

    def _check_links(self, err, warn):
        solid = [n for n in self.nodes if not n.bg]
        segs = []
        for link in self.links:
            name = f"link '{link.a.label}' > '{link.b.label}'"
            dx0 = link.pts[1][0] - link.pts[0][0]
            dy0 = link.pts[1][1] - link.pts[0][1]
            dxn = link.pts[-1][0] - link.pts[-2][0]
            dyn = link.pts[-1][1] - link.pts[-2][1]
            if (link.sa == "right" and dx0 <= 0) or (link.sa == "left" and dx0 >= 0) \
                    or (link.sa == "bottom" and dy0 <= 0) or (link.sa == "top" and dy0 >= 0):
                err(f"{name} leaves '{link.a.label}' backwards: change sides or move a box")
            if (link.sb == "left" and dxn <= 0) or (link.sb == "right" and dxn >= 0) \
                    or (link.sb == "top" and dyn <= 0) or (link.sb == "bottom" and dyn >= 0):
                err(f"{name} enters '{link.b.label}' backwards: change sides or move a box")
            for p, q in zip(link.pts, link.pts[1:]):
                segs.append((link, p, q))
                for n in solid:
                    if n is link.a or n is link.b or n.contains(link.a) or n.contains(link.b):
                        continue
                    if self._seg_hits_box(p, q, (n.x, n.y, n.w, n.h)):
                        err(f"{name} passes through '{n.label}': reroute with mid= or move a box")
            if len(link.pts) == 4 and min(abs(link.pts[1][0] - link.pts[2][0]) + abs(link.pts[1][1] - link.pts[2][1]), 99) < 2:
                warn(f"{name} has a {abs(link.pts[1][0] - link.pts[2][0]) + abs(link.pts[1][1] - link.pts[2][1]):.1f} mm jog: align the boxes")
            if link.label_box:
                self._check_label(link, name, solid, err, warn)
        for i, (la, p, q) in enumerate(segs):
            for lb, r, s in segs[i + 1:]:
                if la is lb:
                    continue
                h1, h2 = abs(p[1] - q[1]) < 0.01, abs(r[1] - s[1]) < 0.01
                names = f"'{la.a.label}'>'{la.b.label}' and '{lb.a.label}'>'{lb.b.label}'"
                if h1 == h2:
                    k = 1 if h1 else 0
                    o = 0 if h1 else 1
                    close = abs(p[k] - r[k])
                    overlap = min(max(p[o], q[o]), max(r[o], s[o])) - max(min(p[o], q[o]), min(r[o], s[o]))
                    if overlap > 0.01 and close < 0.01:
                        err(f"links {names} share a stroke")
                    elif overlap > 0.01 and close < (1.0 if self.S["w"] < 200 else 3.0):
                        warn(f"links {names} run {close:.1f} mm apart: spread them")
                else:
                    hz, vt = ((p, q), (r, s)) if h1 else ((r, s), (p, q))
                    if min(hz[0][0], hz[1][0]) < vt[0][0] < max(hz[0][0], hz[1][0]) \
                            and min(vt[0][1], vt[1][1]) < hz[0][1] < max(vt[0][1], vt[1][1]):
                        warn(f"links {names} cross: rearrange so they do not")

    def _check_label(self, link, name, solid, err, warn):
        x, y, w, h = link.label_box
        for n in solid:
            if x < n.x + n.w and n.x < x + w and y < n.y + n.h and n.y < y + h:
                err(f"{name} label '{link.text}' overlaps '{n.label}'")
        for other in self.links:
            for p, q in zip(other.pts, other.pts[1:]):
                if self._seg_hits_box(p, q, (x, y, w, h)):
                    err(f"{name} label '{link.text}' touches a line: use label_side or move it")
            if other is not link and other.label_box:
                ox, oy, ow, oh = other.label_box
                if x < ox + ow and ox < x + w and y < oy + oh and oy < y + h:
                    err(f"labels '{link.text}' and '{other.text}' overlap")
        if len(link.text) > 14:
            warn(f"{name} label is {len(link.text)} characters: keep to one short verb")
        longest = max(abs(p[0] - q[0]) + abs(p[1] - q[1]) for p, q in zip(link.pts, link.pts[1:]))
        horizontal = any(abs(p[1] - q[1]) < 0.01 and abs(p[0] - q[0]) == longest for p, q in zip(link.pts, link.pts[1:]))
        if horizontal and w > longest:
            warn(f"{name} label '{link.text}' is wider than its line ({w:.0f} > {longest:.0f} mm): widen the gap")

    @staticmethod
    def _seg_hits_box(p, q, box):
        x, y, w, h = box
        x0, x1 = sorted((p[0], q[0]))
        y0, y1 = sorted((p[1], q[1]))
        return x0 < x + w and x1 > x and y0 < y + h and y1 > y

    # ---- output -----------------------------------------------------------
    def save(self, path, template=None, layout=None, append=False):
        """template: the deck's .potx/.pptx, drawn on its L4 layout. append: add a slide to an existing plain output."""
        findings = self.check()
        path = str(path)
        if path.endswith(".svg"):
            Path(path).write_text(self._svg(), encoding="utf-8")
        elif path.endswith(".pptx"):
            findings += self._pptx(path, template, layout, append)
        else:
            raise ValueError("save to .pptx or .svg")
        print(f"saved {path}")
        print("\n".join(findings) if findings else "check: no findings")
        return findings

    # SVG ---------------------------------------------------------------------
    def _hex(self, role):
        return self.colors.get(role, role)

    def _ink_on(self, style):
        if style not in FILLED:
            return self._hex("ink")
        fill = self._hex(style)
        if style == "accent" and fill == "FFD93D":
            return self._hex("navy")
        return "FFFFFF" if contrast(fill, "FFFFFF") >= contrast(fill, self._hex("ink")) else self._hex("ink")

    def _svg_text(self, n):
        pad = 0 if n.kind == "text" else self.S["pad"]
        inner = n.w - 2 * pad - (n.h * 0.5 if n.kind == "pill" else 0) - (n.h if n.kind == "chevron" else 0)
        if n.kind == "circle":
            inner = n.w * 0.8 - 2 * pad
        name_pt, sub_pt = n.name_pt or self.S["name"], n.sub_pt or self.S["sub"]
        name_c = "#" + (self._hex(n.color) if n.color else self._ink_on(n.style))
        sub_c = name_c if n.style in FILLED else "#" + self._hex("muted")
        rows = [(s, name_pt, name_c, n.bold) for s in wrap(n.text, inner, name_pt)] if n.text else []
        rows += [(s, sub_pt, sub_c, False) for s in wrap(n.sub, inner, sub_pt)] if n.sub else []
        if not rows:
            return []
        gap = sub_pt * PT * SUB_GAP if n.text and n.sub else 0
        total = sum(pt * PT * LINE for _, pt, _, _ in rows) + gap
        y = {"top": n.y + pad, "middle": n.cy - total / 2, "bottom": n.y + n.h - pad - total}[n.valign]
        anchor, x = {"left": ("start", n.x + pad), "center": ("middle", n.cx), "right": ("end", n.x + n.w - pad)}[n.align]
        spans = []
        names = len(wrap(n.text, inner, name_pt)) if n.text else 0
        for i, (s, pt, c, bold) in enumerate(rows):
            if i == names and gap:
                y += gap
            size = pt * PT
            base = y + size * (LINE - 1) / 2 + size * 0.84
            weight = ' font-weight="700"' if bold else ""
            spans.append(f'<tspan x="{x:.2f}" y="{base:.2f}" font-size="{size:.3f}" fill="{c}"{weight}>{escape(s)}</tspan>')
            y += size * LINE
        return [f'<text text-anchor="{anchor}"{self._tracking()}>{"".join(spans)}</text>']

    def _tracking(self):
        return "" if self.size_name.startswith("paper") else ' letter-spacing="-0.015em"'

    def _svg_shape(self, n):
        if n.style == "ghost":
            return []
        fill = "#" + (self._hex(n.style) if n.style in FILLED else "FFFFFF")
        stroke = f' stroke="#{self._hex("border")}" stroke-width="{0.75 * PT:.3f}"' if n.style == "plain" else ""
        if n.kind == "circle":
            return [f'<circle cx="{n.cx:.2f}" cy="{n.cy:.2f}" r="{n.w / 2:.2f}" fill="{fill}"{stroke}/>']
        if n.kind == "pill":
            return [f'<rect x="{n.x:.2f}" y="{n.y:.2f}" width="{n.w:.2f}" height="{n.h:.2f}" rx="{n.h / 2:.2f}" fill="{fill}"{stroke}/>']
        if n.kind == "chevron":
            t = n.h * 0.5
            p = [(n.x, n.y), (n.x + n.w - t, n.y), (n.x + n.w, n.cy), (n.x + n.w - t, n.y + n.h), (n.x, n.y + n.h), (n.x + t, n.cy)]
            return [f'<polygon points="{" ".join(f"{a:.2f},{b:.2f}" for a, b in p)}" fill="{fill}"{stroke}/>']
        if n.kind == "seg":
            return [f'<polygon points="{" ".join(f"{a:.2f},{b:.2f}" for a, b in n.points)}" fill="{fill}"/>']
        return [f'<rect x="{n.x:.2f}" y="{n.y:.2f}" width="{n.w:.2f}" height="{n.h:.2f}" rx="{min(0.8, n.h / 8):.2f}" fill="{fill}"{stroke}/>']

    def _svg(self):
        S = self.S
        sw = S["stroke"] * PT
        parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{S["w"]}mm" height="{S["h"]}mm" '
                 f'viewBox="0 0 {S["w"]} {S["h"]}" role="img" aria-labelledby="fig-title" font-family="{escape(self.font, {chr(34): "&quot;"})}">',
                 f'<title id="fig-title">{escape(self.alt or self.title or "Schematic")}</title>',
                 f'<rect width="{S["w"]}" height="{S["h"]}" fill="#FFFFFF"/>']
        markers = sorted({link.color for link in self.links})
        parts.append("<defs>" + "".join(
            f'<marker id="arrow-{c}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="{sw * 6:.2f}" markerHeight="{sw * 6:.2f}" '
            f'markerUnits="userSpaceOnUse" orient="auto"><path d="M0,1 L10,5 L0,9 z" fill="#{self._hex(c)}"/></marker>'
            for c in markers) + "</defs>")
        if self.has_header:
            self._svg_header(parts)
        order = [n for n in self.nodes if n.bg] + self.rings + [n for n in self.nodes if not n.bg]
        for n in order:  # one group per node, so a box and its text move together in Illustrator or Inkscape
            parts.append(f'<g id="{escape(re.sub(r"[^0-9A-Za-z가-힣_-]+", "-", n.label))[:40] or "node"}">')
            parts += self._svg_shape(n) + self._svg_text(n) + ["</g>"]
        for x1, y1, x2, y2, dash, c in self.lines:
            d = f' stroke-dasharray="{sw * 2:.2f} {sw * 3:.2f}"' if dash else ""
            parts.append(f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" stroke="#{self._hex(c)}" stroke-width="{sw:.3f}"{d}/>')
        for link in self.links:
            parts += self._svg_link(link, sw)
        for link in self.links:
            if link.label_box:
                x, y, w, h = link.label_box
                size = S["label"] * PT
                parts.append(f'<text x="{x + w / 2:.2f}" y="{y + h * 0.72:.2f}" font-size="{size:.3f}" fill="#{self._hex(self._label_role(link))}" '
                             f'text-anchor="middle"{self._tracking()}>{escape(link.text)}</text>')
        parts.append("</svg>")
        return "\n".join(parts)

    def _svg_link(self, link, sw):
        sw = link.width * PT if link.width else sw
        c = self._hex(link.color)
        pts = " ".join(f"{x:.2f},{y:.2f}" for x, y in link.pts)
        dash = {"indirect": f' stroke-dasharray="{sw * 4:.2f} {sw * 3:.2f}"', "dots": f' stroke-dasharray="0.01 {sw * 4:.2f}" stroke-linecap="round"'}.get(link.kind, "")
        head = f' marker-end="url(#arrow-{link.color})"' if link.kind in ("flow", "indirect") else ""
        out = [f'<polyline points="{pts}" fill="none" stroke="#{c}" stroke-width="{sw * (1.5 if link.kind == "dots" else 1):.3f}" stroke-linejoin="round"{dash}{head}/>']
        if link.kind == "inhibit":
            for t in self._tbar(link):
                out.append(f'<line x1="{t[0]:.2f}" y1="{t[1]:.2f}" x2="{t[2]:.2f}" y2="{t[3]:.2f}" stroke="#{c}" stroke-width="{sw * 1.5:.3f}"/>')
        return out

    def _tbar(self, link):
        (ax, ay), (bx, by) = link.pts[-2], link.pts[-1]
        half = max(1.0, self.S["name"] * PT * 0.3)
        if abs(ay - by) < 0.01:
            return [(bx, by - half, bx, by + half)]
        return [(bx - half, by, bx + half, by)]

    def _label_role(self, link):
        """Muted grey falls under 4.5:1 on a tinted band, so labels sitting on one use ink."""
        x, y, w, h = link.label_box
        on_band = any(n.bg and n.x <= x and n.y <= y and n.x + n.w >= x + w and n.y + n.h >= y + h for n in self.nodes)
        return "ink" if on_band else "muted"

    def _svg_header(self, parts):
        S = self.S
        m = S["margin"]
        size = S["title"] * PT
        small = max(S["floor"], 10) * PT
        y = m
        if self.tag:
            parts.append(f'<text x="{S["w"] - m}" y="{y + small:.2f}" text-anchor="end" font-size="{small:.3f}" fill="#{self._hex("muted")}">{escape(self.tag)}</text>')
        if self.section:
            parts.append(f'<text x="{m}" y="{y + small:.2f}" font-size="{small:.3f}" fill="#{self._hex("primary")}" font-weight="700">{escape(self.section)}</text>')
        if self.section or self.tag:
            y += small * 1.5
        for line in self.title_lines:
            parts.append(f'<text x="{m}" y="{y + size * 1.05:.2f}" font-size="{size:.3f}" fill="#{self._hex("ink")}" font-weight="700" letter-spacing="-0.02em">{escape(line)}</text>')
            y += size * LINE
        parts.append(f'<line x1="{m}" y1="{self.rule_y:.2f}" x2="{S["w"] - m}" y2="{self.rule_y:.2f}" stroke="#{self._hex("border")}" stroke-width="{0.75 * PT:.3f}"/>')

    # PPTX --------------------------------------------------------------------
    def _open_deck(self, template, append, path):
        from pptx import Presentation
        from pptx.util import Mm
        if append:
            return Presentation(path), False
        if template:
            data = Path(template).read_bytes()
            if str(template).endswith(".potx"):  # python-pptx refuses the template content type
                src = zipfile.ZipFile(io.BytesIO(data))
                buf = io.BytesIO()
                with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as dst:
                    for item in src.infolist():
                        blob = src.read(item.filename)
                        if item.filename == "[Content_Types].xml":
                            blob = blob.replace(b"presentationml.template.main+xml", b"presentationml.presentation.main+xml")
                        dst.writestr(item, blob)
                data = buf.getvalue()
            return Presentation(io.BytesIO(data)), True
        prs = Presentation()
        prs.slide_width, prs.slide_height = Mm(self.S["w"]), Mm(self.S["h"])
        self._patch_theme(prs)
        return prs, False

    def _patch_theme(self, prs):
        from pptx.opc.constants import RELATIONSHIP_TYPE as RT
        theme = prs.slide_master.part.part_related_by(RT.THEME)
        c = self.colors
        slots = dict(dk1=c["ink"], lt1="FFFFFF", dk2=c["muted"], lt2=c["paper"], accent1=c["primary"], accent2=c["emerald"],
                     accent3=c["teal"], accent4=c["accent"], accent5=c["mid"], accent6=c["border"], hlink=c["primary"], folHlink=c["muted"])
        scheme = "".join(f'<a:{k}><a:srgbClr val="{v}"/></a:{k}>' for k, v in slots.items())
        xml = theme.blob.decode("utf-8")
        xml = re.sub(r'(<a:clrScheme [^>]*>).*?(</a:clrScheme>)', lambda m: m.group(1) + scheme + m.group(2), xml, flags=re.S)
        def fonts(m):
            block = re.sub(r'<a:latin typeface="[^"]*"', '<a:latin typeface="Pretendard"', m.group(0))
            return re.sub(r'<a:ea typeface="[^"]*"', '<a:ea typeface="Pretendard"', block)
        xml = re.sub(r'<a:fontScheme.*?</a:fontScheme>', fonts, xml, flags=re.S)
        theme._blob = xml.encode("utf-8")

    @staticmethod
    def _pick_layout(prs, wanted):
        layouts = list(prs.slide_layouts)
        names = [lay.name for lay in layouts]
        keys = [wanted] if wanted else ["L4", "빈 본문", "헤더", "Title Only"]
        for key in keys:
            for lay in layouts:
                if key in lay.name:
                    return lay
        raise ValueError(f"no layout matches {keys}; this deck has: {names}")

    def _pptx(self, path, template, layout, append):
        from pptx.dml.color import RGBColor
        from pptx.util import Mm
        prs, real = self._open_deck(template, append, path)
        findings = []
        W, H = prs.slide_width / 36000, prs.slide_height / 36000
        if abs(W - self.S["w"]) > 1 or abs(H - self.S["h"]) > 1:
            findings.append(f"ERROR deck is {W:.0f}x{H:.0f} mm but this scene is {self.S['w']:.0f}x{self.S['h']:.0f} mm: use the matching size")
        if real:
            slide = prs.slides.add_slide(self._pick_layout(prs, layout))
            findings += self._fill_header(slide)
        else:
            slide = prs.slides.add_slide(prs.slide_layouts[6])
            slide.background.fill.solid()
            slide.background.fill.fore_color.rgb = RGBColor.from_string(self.colors["paper"])
            if self.has_header:
                self._pptx_header(slide)
        shapes = slide.shapes
        order = [n for n in self.nodes if n.bg] + self.rings + [n for n in self.nodes if not n.bg]
        made = {}
        for n in order:  # a ring segment and its label are grouped, so they move together
            made[id(n)] = self._pptx_node(shapes.add_group_shape().shapes if n.kind == "seg" and n.text else shapes, n)
        for x1, y1, x2, y2, dash, c in self.lines:
            cx = shapes.add_connector(1, Mm(x1), Mm(y1), Mm(x2), Mm(y2))
            self._pptx_stroke(cx, c, 0.75 if c == "border" else self.S["stroke"], "dots" if dash else "plain")
        for link in self.links:
            self._pptx_link(shapes, link, made)
        prs.save(path)
        return findings

    def _fill_header(self, slide):
        out, placed = [], set()
        title = slide.shapes.title
        if self.title and title is not None:
            title.text_frame.text = self.title
            placed.add("title")
            bottom = (title.top + title.height) / 36000
            if bottom > self.top:
                out.append(f"WARN  template title ends at {bottom:.0f} mm, below the drawing top {self.top:.0f} mm: pass Scene(top=<mm>)")
        for ph in slide.placeholders:
            name = ph.name.lower()
            if ("섹션" in name or "section" in name) and self.section:
                ph.text_frame.text = self.section
                placed.add("section")
            elif ("지표" in name or "태그" in name or "tag" in name) and self.tag:
                ph.text_frame.text = self.tag
                placed.add("tag")
        for key, val in (("title", self.title), ("section", self.section), ("tag", self.tag)):
            if val and key not in placed:
                out.append(f"WARN  template layout has no placeholder for {key}: '{val}' was not placed")
        return out

    def _color(self, target, role):
        from pptx.dml.color import RGBColor
        from pptx.enum.dml import MSO_THEME_COLOR as T
        slots = dict(primary=T.ACCENT_1, emerald=T.ACCENT_2, teal=T.ACCENT_3, accent=T.ACCENT_4, border=T.ACCENT_6, ink=T.TEXT_1, muted=T.TEXT_2)
        if role in slots:
            target.theme_color = slots[role]
        else:
            target.rgb = RGBColor.from_string(self.colors.get(role, role))

    def _pptx_header(self, slide):
        from pptx.util import Mm, Pt
        S = self.S
        m, full = S["margin"], S["w"] - 2 * S["margin"]
        y = m
        if self.tag:
            tag = Node("text", m, y, full, 6, self.tag, "", "ghost", name_pt=max(S["floor"], 10), bold=False, color="muted", align="right", valign="top")
            self._pptx_node(slide.shapes, tag)
        if self.section:
            small = Node("text", m, y, full, 6, self.section, "", "ghost", name_pt=max(S["floor"], 10), bold=True, color="primary", align="left", valign="top")
            self._pptx_node(slide.shapes, small)
        if self.section or self.tag:
            y += 6
        title = Node("text", m, y, full, self.rule_y - 1.5 - y, self.title, "", "ghost", name_pt=S["title"], bold=True, align="left", valign="top")
        self._pptx_node(slide.shapes, title).name = "제목"
        rule = slide.shapes.add_connector(1, Mm(m), Mm(self.rule_y), Mm(S["w"] - m), Mm(self.rule_y))
        self._pptx_stroke(rule, "border", 0.75, "plain")

    def _pptx_node(self, shapes, n):
        from pptx.enum.shapes import MSO_SHAPE
        from pptx.util import Mm, Pt
        if n.kind == "text":
            sh = shapes.add_textbox(Mm(n.x), Mm(n.y), Mm(n.w), Mm(n.h))
        elif n.kind == "seg":
            pts = [(Mm(a), Mm(b)) for a, b in n.points]
            ff = shapes.build_freeform(pts[0][0], pts[0][1], scale=1.0)
            ff.add_line_segments(pts[1:], close=True)
            seg = ff.convert_to_shape()
            self._pptx_fill(seg, n.style)
            seg.name = n.label[:40]
            if not n.text:
                return seg
            sh = shapes.add_textbox(Mm(n.x), Mm(n.y), Mm(n.w), Mm(n.h))
        else:
            kind = dict(box=MSO_SHAPE.RECTANGLE, pill=MSO_SHAPE.ROUNDED_RECTANGLE, circle=MSO_SHAPE.OVAL, chevron=MSO_SHAPE.CHEVRON)[n.kind]
            sh = shapes.add_shape(kind, Mm(n.x), Mm(n.y), Mm(n.w), Mm(n.h))
            if n.kind == "pill":
                sh.adjustments[0] = 0.5
            if n.kind == "chevron":
                sh.adjustments[0] = 0.5
            self._pptx_fill(sh, n.style)
        sh.name = n.label[:40]
        self._pptx_text(sh, n)
        return sh

    def _pptx_fill(self, sh, style):
        """Tints are the primary colour with transparency: a true mix with the white page that still follows the theme."""
        from pptx.oxml import parse_xml
        from pptx.oxml.ns import qn
        from pptx.util import Pt
        strip_style(sh)
        if style in FILLED:
            sh.fill.solid()
            self._color(sh.fill.fore_color, "primary" if style in TINTS else style)
            if style in TINTS:
                clr = sh._element.spPr.find(qn("a:solidFill"))[0]
                clr.append(parse_xml(f'<a:alpha xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" val="{round((1 - TINTS[style]) * 100000)}"/>'))
            sh.line.fill.background()
        elif style == "plain":
            sh.fill.solid()
            self._color(sh.fill.fore_color, "white")
            sh.line.width = Pt(0.75)
            self._color(sh.line.color, "border")

    def _pptx_text(self, sh, n):
        from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
        from pptx.util import Mm, Pt
        S = self.S
        tf = sh.text_frame
        tf.word_wrap = True
        pad = 0 if n.kind == "text" else S["pad"]
        tf.margin_left = tf.margin_right = Mm(pad)
        tf.margin_top = tf.margin_bottom = Mm(pad)
        tf.vertical_anchor = dict(top=MSO_ANCHOR.TOP, middle=MSO_ANCHOR.MIDDLE, bottom=MSO_ANCHOR.BOTTOM)[n.valign]
        align = dict(left=PP_ALIGN.LEFT, center=PP_ALIGN.CENTER, right=PP_ALIGN.RIGHT)[n.align]
        name_c = n.color or (self._ink_on(n.style) if n.style in FILLED else "ink")
        sub_c = name_c if n.style in FILLED else "muted"
        rows = [(p, n.name_pt or S["name"], name_c, n.bold, 1.05) for p in n.text.split("\n")] if n.text else []
        rows += [(p, n.sub_pt or S["sub"], sub_c, False, 1.1) for p in n.sub.split("\n")] if n.sub else []
        first, sub_started = True, False
        for s, pt, c, bold, spacing in rows:
            para = tf.paragraphs[0] if first else tf.add_paragraph()
            first = False
            para.alignment = align
            para.line_spacing = spacing
            if spacing == 1.1 and para is not tf.paragraphs[0] and not sub_started:
                para.space_before = Pt(pt * SUB_GAP)
                sub_started = True
            run = para.add_run()
            run.text = s
            run.font.size = Pt(pt)
            run.font.bold = bold
            self._color(run.font.color, self._text_role(c))
            run._r.get_or_add_rPr().set("spc", "-40")

    def _text_role(self, c):
        for role in ("white", "ink", "navy", "muted", "primary", "emerald", "teal", "accent"):
            if c == role or c == self.colors[role]:
                return role
        return c

    def _pptx_stroke(self, cx, color, width, kind):
        from pptx.enum.dml import MSO_LINE
        from pptx.oxml import parse_xml
        from pptx.util import Pt
        strip_style(cx)
        cx.line.width = Pt(width * 1.5 if kind == "dots" else width)
        self._color(cx.line.color, color)
        if kind == "indirect":
            cx.line.dash_style = MSO_LINE.DASH
        elif kind == "dots":
            cx.line.dash_style = MSO_LINE.ROUND_DOT
        if kind in ("flow", "indirect"):
            ln = cx.line._get_or_add_ln()
            ln.append(parse_xml('<a:tailEnd xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" type="triangle" w="med" len="med"/>'))

    def _pptx_link(self, shapes, link, made):
        from pptx.oxml import parse_xml
        from pptx.util import Mm, Pt
        pts = link.pts
        cx = shapes.add_connector(1, 0, 0, 0, 0)
        cx.name = f"{link.a.label[:18]} > {link.b.label[:18]}"
        write_connector_geometry(cx, pts)
        self._pptx_stroke(cx, link.color, link.width or self.S["stroke"], link.kind)
        ns = 'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"'
        c_nv = cx._element.nvCxnSpPr.cNvCxnSpPr
        sites = dict(top=0, left=1, bottom=2, right=3)
        oval = dict(top=0, left=2, bottom=4, right=6)
        if link.glue_a:
            idx = (oval if link.a.kind == "circle" else sites)[link.sa]
            c_nv.append(parse_xml(f'<a:stCxn {ns} id="{made[id(link.a)].shape_id}" idx="{idx}"/>'))
        if link.glue_b:
            idx = (oval if link.b.kind == "circle" else sites)[link.sb]
            c_nv.append(parse_xml(f'<a:endCxn {ns} id="{made[id(link.b)].shape_id}" idx="{idx}"/>'))
        if link.kind == "inhibit":
            for x1, y1, x2, y2 in self._tbar(link):
                bar = shapes.add_connector(1, Mm(x1), Mm(y1), Mm(x2), Mm(y2))
                self._pptx_stroke(bar, link.color, self.S["stroke"] * 1.5, "plain")
        if link.label_box:
            x, y, w, h = link.label_box
            lab = Node("text", x - 2, y, w + 4, h, link.text, "", "ghost", name_pt=self.S["label"], bold=False, color=self._label_role(link), align="center", valign="middle")
            self._pptx_node(shapes, lab)


def strip_style(sh):
    """Drop python-pptx's theme style reference: it brings the theme's shadow onto shapes and connectors."""
    from pptx.oxml.ns import qn
    st = sh._element.find(qn("p:style"))
    if st is not None:
        sh._element.remove(st)


def write_connector_geometry(cx, pts):
    """Store an orthogonal polyline as a PowerPoint connector preset, including the rotated forms
    PowerPoint itself uses when a connector starts vertically."""
    from pptx.oxml import parse_xml
    from pptx.oxml.ns import qn
    (x0, y0), (x1, y1) = pts[0], pts[-1]
    dx, dy = x1 - x0, y1 - y0
    starts_vertical = abs(pts[0][0] - pts[1][0]) < 0.01 and len(pts) > 2
    prst = {2: "straightConnector1", 3: "bentConnector2", 4: "bentConnector3"}[len(pts)]
    rot = flip_h = flip_v = 0
    if starts_vertical:
        w, h = abs(dy), abs(dx)  # local box before rotation
        rot = 5400000 if dy > 0 else 16200000
        flip_v = int((dy > 0 and dx > 0) or (dy < 0 and dx < 0))
    else:
        w, h = abs(dx), abs(dy)
        flip_h, flip_v = int(dx < 0), int(dy < 0)
    centre_x, centre_y = (x0 + x1) / 2, (y0 + y1) / 2
    emu = lambda mm: int(round(mm * 36000))
    sp = cx._element.spPr
    xf = sp.find(qn("a:xfrm"))
    for key in ("rot", "flipH", "flipV"):
        if key in xf.attrib:
            del xf.attrib[key]
    if rot:
        xf.set("rot", str(rot))
    if flip_h:
        xf.set("flipH", "1")
    if flip_v:
        xf.set("flipV", "1")
    off, ext = xf.find(qn("a:off")), xf.find(qn("a:ext"))
    off.set("x", str(emu(centre_x - w / 2)))
    off.set("y", str(emu(centre_y - h / 2)))
    ext.set("cx", str(emu(w)))
    ext.set("cy", str(emu(h)))
    geom = sp.find(qn("a:prstGeom"))
    geom.set("prst", prst)
    av = geom.find(qn("a:avLst"))
    if av is None:
        av = parse_xml('<a:avLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"/>')
        geom.append(av)
    if len(pts) == 4:
        span = dy if starts_vertical else dx
        adj = ((pts[1][1] - y0) if starts_vertical else (pts[1][0] - x0)) / span if span else 0.5
        av.append(parse_xml(f'<a:gd xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="adj1" fmla="val {int(round(adj * 100000))}"/>'))


def preview(path):
    """Render to PNG beside the file so it can be looked at. Returns one path per slide."""
    path = Path(path).resolve()
    png = path.with_suffix(".png")
    if path.suffix == ".svg":
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            browser = p.chromium.launch()
            pg = browser.new_page(viewport={"width": 1400, "height": 900}, device_scale_factor=2)
            pg.goto(path.as_uri())
            pg.locator("svg").first.screenshot(path=str(png))
            browser.close()
        return [png]
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(path.parent), str(path)],
                   check=True, capture_output=True, timeout=170)
    pdf = path.with_suffix(".pdf")
    from pptx import Presentation
    if len(Presentation(path).slides) == 1:
        subprocess.run(["pdftoppm", "-png", "-r", "110", "-singlefile", str(pdf), str(png.with_suffix(""))], check=True)
        pngs = [png]
    else:
        subprocess.run(["pdftoppm", "-png", "-r", "110", str(pdf), str(png.with_suffix(""))], check=True)
        pngs = sorted(path.parent.glob(f"{path.stem}-*.png"))
    pdf.unlink()
    return pngs


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "preview":
        print(*preview(sys.argv[2]), sep="\n")
    else:
        print(__doc__)
