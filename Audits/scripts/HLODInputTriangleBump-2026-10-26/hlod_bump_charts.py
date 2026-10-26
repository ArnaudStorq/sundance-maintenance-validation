"""Render the SVG charts of the HLOD input-triangle bump report from HLODTrendData.json."""
import csv
import json
import os
import re
import sys
from collections import defaultdict

DATA = "cursor-scratch/HLODTrendData.json"
CSV_BEFORE = "cursor-scratch/HLODStats-CL2135649.csv"
CSV_AFTER = "cursor-scratch/HLODStats-CL2145547.csv"
OUT = sys.argv[1]
FIRST_CL = 2096757

COLORS = ["#2563eb", "#16a34a", "#dc2626", "#9333ea", "#ea580c", "#0891b2"]
FONT = "font-family='Segoe UI, Helvetica, Arial, sans-serif'"


def cl_key(b):
    s = b["id"]
    return int(s[2:]) if s.startswith("CL") and s[2:].isdigit() else 0


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def line_chart(path, title, subtitle, builds, series, markers, unit_div, unit, y_max=None):
    w, h = 960, 420
    ml, mr, mt, mb = 70, 20, 70, 70
    pw, ph = w - ml - mr, h - mt - mb
    n = len(builds)
    raw = y_max or max(v for _, vals in series for v in vals if v is not None) * 1.08
    step = next(s * unit_div for s in (1, 2, 5, 10, 20, 25, 50, 100, 200, 250, 500) if raw / (s * unit_div) <= 6)
    vmax = step * -(-raw // step)
    ticks = int(round(vmax / step))
    x = lambda i: ml + pw * i / (n - 1)
    y = lambda v: mt + ph - ph * v / vmax
    out = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {w} {h}' {FONT}>",
           f"<rect width='{w}' height='{h}' fill='white'/>",
           f"<text x='{ml}' y='28' font-size='18' font-weight='600' fill='#111'>{esc(title)}</text>",
           f"<text x='{ml}' y='48' font-size='12' fill='#555'>{esc(subtitle)}</text>"]
    for k in range(ticks + 1):
        v = step * k
        out.append(f"<line x1='{ml}' x2='{w - mr}' y1='{y(v):.1f}' y2='{y(v):.1f}' stroke='#e5e7eb'/>")
        out.append(f"<text x='{ml - 8}' y='{y(v) + 4:.1f}' font-size='11' text-anchor='end' fill='#555'>{v / unit_div:.0f}{unit}</text>")
    for i, b in enumerate(builds):
        if i % 2 == 0 or i == n - 1:
            out.append(f"<text x='{x(i):.1f}' y='{h - mb + 16}' font-size='10' text-anchor='end' fill='#555' "
                       f"transform='rotate(-35 {x(i):.1f} {h - mb + 16})'>{b['timestamp'][5:10]}</text>")
    for mi, (label, idx, color) in enumerate(markers):
        xm = x(idx)
        ly = mt + ph - 10 - (len(markers) - 1 - mi) * 16
        out.append(f"<line x1='{xm:.1f}' x2='{xm:.1f}' y1='{mt}' y2='{mt + ph}' stroke='{color}' stroke-dasharray='5,4' stroke-width='1.5'/>")
        out.append(f"<text x='{xm - 5:.1f}' y='{ly}' font-size='11' text-anchor='end' fill='{color}' font-weight='600'>{esc(label)}</text>")
    for si, (label, vals) in enumerate(series):
        color = COLORS[si % len(COLORS)]
        pts = " ".join(f"{x(i):.1f},{y(v):.1f}" for i, v in enumerate(vals) if v is not None)
        out.append(f"<polyline points='{pts}' fill='none' stroke='{color}' stroke-width='2.5'/>")
        for i, v in enumerate(vals):
            if v is not None:
                out.append(f"<circle cx='{x(i):.1f}' cy='{y(v):.1f}' r='2.5' fill='{color}'/>")
        lx = ml + 10 + si * 210
        out.append(f"<rect x='{lx}' y='{mt - 14}' width='14' height='4' fill='{color}'/>")
        out.append(f"<text x='{lx + 20}' y='{mt - 9}' font-size='12' fill='#111'>{esc(label)}</text>")
    out.append("</svg>")
    open(path, "w", encoding="utf-8").write("\n".join(out))


def bar_chart(path, title, subtitle, bars, unit_div, unit, fmt="{:+.2f}"):
    w, bh, gap = 960, 34, 14
    ml, mr, mt = 300, 120, 70
    h = mt + len(bars) * (bh + gap) + 20
    vmax = max(abs(v) for _, v, _ in bars)
    vmin = min(0, min(v for _, v, _ in bars))
    span = vmax - vmin
    pw = w - ml - mr
    x0 = ml + pw * (-vmin) / span
    out = [f"<svg xmlns='http://www.w3.org/2000/svg' width='{w}' height='{h}' viewBox='0 0 {w} {h}' {FONT}>",
           f"<rect width='{w}' height='{h}' fill='white'/>",
           f"<text x='20' y='28' font-size='18' font-weight='600' fill='#111'>{esc(title)}</text>",
           f"<text x='20' y='48' font-size='12' fill='#555'>{esc(subtitle)}</text>",
           f"<line x1='{x0:.1f}' x2='{x0:.1f}' y1='{mt - 6}' y2='{h - 14}' stroke='#9ca3af'/>"]
    for i, (label, v, color) in enumerate(bars):
        yb = mt + i * (bh + gap)
        bw = pw * abs(v) / span
        bx = x0 if v >= 0 else x0 - bw
        out.append(f"<text x='{ml - 10}' y='{yb + bh / 2 + 4}' font-size='13' text-anchor='end' fill='#111'>{esc(label)}</text>")
        out.append(f"<rect x='{bx:.1f}' y='{yb}' width='{bw:.1f}' height='{bh}' rx='3' fill='{color}'/>")
        tx = bx + bw + 8 if v >= 0 else x0 + 8
        anchor = "start"
        out.append(f"<text x='{tx:.1f}' y='{yb + bh / 2 + 4}' font-size='13' text-anchor='{anchor}' fill='#111' font-weight='600'>"
                   f"{fmt.format(v / unit_div)}{unit}</text>")
    out.append("</svg>")
    open(path, "w", encoding="utf-8").write("\n".join(out))


os.makedirs(OUT, exist_ok=True)
data = json.load(open(DATA))
builds = [b for b in sorted(data["builds"], key=cl_key) if cl_key(b) >= FIRST_CL]
idx = {b["id"]: i for i, b in enumerate(builds)}


def layer(name, metric="InputTriangleCount"):
    return [b.get("layers", {}).get(name, {}).get(metric) for b in builds]


markers = [("SK->SM grass CL 2132784", idx["CL2131937"] + 0.5, "#b45309"),
           ("PCG Force Regen Oct 18-20", idx["CL2135649"] + 0.5, "#7c3aed"),
           ("Rules CL 2148816", idx["CL2145547"] + 0.5, "#0f766e")]

line_chart(os.path.join(OUT, "input-triangles-overland.svg"),
           "Overland HLOD input triangles per build",
           "InputTriangleCount, LV_Overland. The jump lands in the first HLOD build after the PCG regen picked up the SM grass.",
           builds,
           [("Total (all layers)", [b["totals"]["InputTriangleCount"] for b in builds]),
            ("Overland_HLODLayer_Near", layer("LV_Overland_HLODLayer_Near")),
            ("Overland_HLODLayer_Far", layer("LV_Overland_HLODLayer_Far"))],
           markers, 1e9, "B")

line_chart(os.path.join(OUT, "input-triangles-hw.svg"),
           "Hogwarts HLOD input triangles per build",
           "HW_Mid and HW_Far (identical, the lines overlap) jumped on Oct 16; the Rules CL brought them back down on Oct 23.",
           builds,
           [("HW_HLODLayer_Near", layer("LV_HW_HLODLayer_Near")),
            ("HW_HLODLayer_Mid", layer("LV_HW_HLODLayer_Mid")),
            ("HW_HLODLayer_Far", layer("LV_HW_HLODLayer_Far"))],
           markers, 1e6, "M")

line_chart(os.path.join(OUT, "mesh-instances-overland.svg"),
           "Overland HLOD mesh instances per build",
           "MeshInstanceCount. Grass ISM instances now reach the HLOD output.",
           builds,
           [("Overland_HLODLayer_Near", layer("LV_Overland_HLODLayer_Near", "MeshInstanceCount")),
            ("Overland_HLODLayer_Far", layer("LV_Overland_HLODLayer_Far", "MeshInstanceCount"))],
           markers, 1e3, "K")


def load_cells(path, layer_name):
    cells = defaultdict(lambda: defaultdict(float))
    for row in csv.DictReader(open(path, newline="")):
        if row["HLODLayer"] == layer_name:
            key = re.sub(r"_d[0-9A-F]+$", "", row["Name"])
            for m in ("InputActorCount", "InputTriangleCount"):
                cells[key][m] += float(row[m] or 0)
    return cells


b_cells = load_cells(CSV_BEFORE, "LV_Overland_HLODLayer_Near")
a_cells = load_cells(CSV_AFTER, "LV_Overland_HLODLayer_Near")
split = defaultdict(float)
count = defaultdict(int)
for k in set(a_cells) | set(b_cells):
    da = a_cells[k]["InputActorCount"] - b_cells[k]["InputActorCount"]
    label = "same actor count" if da == 0 else ("actors added" if da > 0 else "actors removed")
    split[label] += a_cells[k]["InputTriangleCount"] - b_cells[k]["InputTriangleCount"]
    count[label] += 1

bar_chart(os.path.join(OUT, "cell-split-overland-near.svg"),
          "Where the Overland_Near increase comes from (Oct 18 -> Oct 22 builds)",
          "Net InputTriangleCount delta per group of HLOD cells. Most of it is in cells whose source actors did not change.",
          [(f"Cells with {k} ({count[k]})", split[k], c) for k, c in
           (("same actor count", "#dc2626"), ("actors added", "#f97316"), ("actors removed", "#16a34a"))],
          1e9, "B")

t0 = next(b for b in builds if b["id"] == "CL2135649")["totals"]
t1 = next(b for b in builds if b["id"] == "CL2145547")["totals"]
pct = lambda m: 100.0 * (t1[m] - t0[m]) / t0[m]
bar_chart(os.path.join(OUT, "input-vs-output.svg"),
          "Input vs output change, all layers (Oct 18 -> Oct 22 builds)",
          "The builders receive +35% triangles, but the HLOD output geometry barely moves.",
          [("InputTriangleCount", pct("InputTriangleCount"), "#dc2626"),
           ("MeshInstanceCount", pct("MeshInstanceCount"), "#f97316"),
           ("BuildTimeTotalMilliseconds", pct("BuildTimeTotalMilliseconds"), "#eab308"),
           ("MeshTriangleCount", pct("MeshTriangleCount"), "#2563eb"),
           ("MeshNaniteTriangleCount", pct("MeshNaniteTriangleCount"), "#16a34a")],
          1, "%", fmt="{:+.1f}")
print("charts written to", OUT)
