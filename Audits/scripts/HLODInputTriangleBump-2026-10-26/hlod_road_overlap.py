import csv
import re
import sys
from collections import defaultdict

BEFORE = sys.argv[1]
AFTER = sys.argv[2]


def coord(name):
    m = re.search(r"_(L\d+_X-?\d+_Y-?\d+_Z-?\d+)", name)
    return m.group(1) if m else None


def load(path, layer):
    cells = defaultdict(lambda: defaultdict(float))
    for row in csv.DictReader(open(path, newline="")):
        if row["HLODLayer"] != layer:
            continue
        c = coord(row["Name"])
        for m in ("InputActorCount", "InputTriangleCount", "MeshInstanceCount"):
            cells[c][m] += float(row[m] or 0)
    return cells


road = load(BEFORE, "LV_Overland_HLODLayer_Road_Near")
print(f"Road_Near cells before: {len(road)}, actors={sum(c['InputActorCount'] for c in road.values()):.0f}")
print("Sample road cell names:", list(road)[:5])

for layer in ("LV_Overland_HLODLayer_Near", "LV_Overland_HLODLayer_Far"):
    b = load(BEFORE, layer)
    a = load(AFTER, layer)
    by_level = defaultdict(lambda: [0.0, 0.0, 0.0, 0])
    in_road = [0.0, 0.0, 0]
    out_road = [0.0, 0.0, 0]
    for c in set(a) | set(b):
        dt = a[c]["InputTriangleCount"] - b[c]["InputTriangleCount"]
        da = a[c]["InputActorCount"] - b[c]["InputActorCount"]
        di = a[c]["MeshInstanceCount"] - b[c]["MeshInstanceCount"]
        lvl = c.split("_")[0] if c else "?"
        by_level[lvl][0] += dt
        by_level[lvl][1] += da
        by_level[lvl][2] += di
        by_level[lvl][3] += 1
        bucket = in_road if c in road else out_road
        bucket[0] += dt
        bucket[1] += da
        bucket[2] += 1
    print(f"\n== {layer} ==")
    for lvl, (dt, da, di, n) in sorted(by_level.items()):
        print(f"  {lvl}: cells={n:5d} dTri={dt / 1e9:6.2f}B dActors={da:+6.0f} dInst={di:+8.0f}")
    print(f"  cells matching a former Road_Near cell coord: n={in_road[2]} dTri={in_road[0] / 1e9:.2f}B dActors={in_road[1]:+.0f}")
    print(f"  other cells:                                  n={out_road[2]} dTri={out_road[0] / 1e9:.2f}B dActors={out_road[1]:+.0f}")
