import csv
import re
import sys
from collections import defaultdict

BEFORE, AFTER, LAYER = sys.argv[1], sys.argv[2], sys.argv[3]
METRICS = ("InputActorCount", "InputTriangleCount", "MeshInstanceCount", "MeshTriangleCount", "MeshNaniteTriangleCount")


def load(path):
    cells = defaultdict(lambda: defaultdict(float))
    for row in csv.DictReader(open(path, newline="")):
        if row["HLODLayer"] != LAYER:
            continue
        key = re.sub(r"_d[0-9A-F]+$", "", row["Name"])
        for m in METRICS:
            cells[key][m] += float(row[m] or 0)
    return cells


b, a = load(BEFORE), load(AFTER)
buckets = defaultdict(lambda: defaultdict(float))
for k in set(a) | set(b):
    da = a[k]["InputActorCount"] - b[k]["InputActorCount"]
    label = "actors same" if da == 0 else ("actors added" if da > 0 else "actors removed")
    buckets[label]["cells"] += 1
    for m in METRICS:
        buckets[label][m] += a[k][m] - b[k][m]

for label, v in buckets.items():
    print(f"{label:15s} cells={v['cells']:5.0f} dActors={v['InputActorCount']:+7.0f} "
          f"dInputTri={v['InputTriangleCount'] / 1e9:+6.2f}B dInst={v['MeshInstanceCount']:+8.0f} "
          f"dMeshTri={v['MeshTriangleCount'] / 1e6:+7.2f}M dNaniteTri={v['MeshNaniteTriangleCount'] / 1e6:+7.2f}M")

print("\nTop 10 cells with no actor change:")
same = [(k, a[k]["InputTriangleCount"] - b[k]["InputTriangleCount"], b[k], a[k]) for k in set(a) | set(b)
        if a[k]["InputActorCount"] == b[k]["InputActorCount"]]
for k, d, bb, aa in sorted(same, key=lambda x: -x[1])[:10]:
    print(f"  {k:55s} actors={aa['InputActorCount']:5.0f} tri {bb['InputTriangleCount'] / 1e6:8.1f}M -> {aa['InputTriangleCount'] / 1e6:8.1f}M "
          f"inst {bb['MeshInstanceCount']:6.0f} -> {aa['MeshInstanceCount']:6.0f}")
