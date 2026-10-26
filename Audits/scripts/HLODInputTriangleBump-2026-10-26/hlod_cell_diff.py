import csv
import re
import sys
from collections import defaultdict

BEFORE = sys.argv[1]
AFTER = sys.argv[2]
LAYER_FILTER = sys.argv[3] if len(sys.argv) > 3 else "Overland_HLODLayer_Near"
TOP = 15


def load(path):
    cells = defaultdict(lambda: defaultdict(float))
    dls = defaultdict(set)
    for row in csv.DictReader(open(path, newline="")):
        if row["HLODLayer"] != "LV_" + LAYER_FILTER:
            continue
        key = re.sub(r"_d[0-9A-F]+$", "", row["Name"])
        for m in ("InputActorCount", "InputTriangleCount", "MeshInstanceCount"):
            cells[key][m] += float(row[m] or 0)
        dls[key].add(row["DataLayers"])
    return cells, dls


b, bdl = load(BEFORE)
a, adl = load(AFTER)
keys = set(a) | set(b)
deltas = []
for k in keys:
    d = {m: a[k][m] - b[k][m] for m in ("InputActorCount", "InputTriangleCount", "MeshInstanceCount")}
    deltas.append((k, d))

tri = sum(d["InputTriangleCount"] for _, d in deltas)
up = [x for x in deltas if x[1]["InputTriangleCount"] > 1e6]
down = [x for x in deltas if x[1]["InputTriangleCount"] < -1e6]
print(f"Layer {LAYER_FILTER}: cells before={len(b)} after={len(a)} total dTri={tri / 1e9:.2f}B")
print(f"Cells +1M tris: {len(up)}  (sum {sum(x[1]['InputTriangleCount'] for x in up) / 1e9:.2f}B)")
print(f"Cells -1M tris: {len(down)} (sum {sum(x[1]['InputTriangleCount'] for x in down) / 1e9:.2f}B)")

dl_counter = defaultdict(int)
for k, _ in up:
    for dl in adl[k]:
        dl_counter[dl] += 1
print("DataLayers of increased cells:", dict(sorted(dl_counter.items(), key=lambda x: -x[1])[:10]))

print(f"\nTop {TOP} increases:")
for k, d in sorted(deltas, key=lambda x: -x[1]["InputTriangleCount"])[:TOP]:
    print(f"  {k:70s} dTri={d['InputTriangleCount'] / 1e6:9.1f}M dActors={d['InputActorCount']:+6.0f} "
          f"dInst={d['MeshInstanceCount']:+8.0f}  DL_after={sorted(adl[k])}")
