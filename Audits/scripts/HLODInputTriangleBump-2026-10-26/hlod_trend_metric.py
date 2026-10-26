import json
import sys

PATH = "cursor-scratch/HLODTrendData.json"
METRIC = sys.argv[1] if len(sys.argv) > 1 else "InputTriangleCount"
LAST_N = int(sys.argv[2]) if len(sys.argv) > 2 else 20


def fmt(v):
    if v is None:
        return "-"
    a = abs(v)
    if a >= 1e9:
        return f"{v / 1e9:.2f}B"
    if a >= 1e6:
        return f"{v / 1e6:.1f}M"
    if a >= 1e3:
        return f"{v / 1e3:.1f}K"
    return str(int(v))


def cl_key(b):
    s = b["id"]
    return int(s[2:]) if s.startswith("CL") and s[2:].isdigit() else 0


data = json.load(open(PATH))
builds = sorted(data["builds"], key=cl_key)[-LAST_N:]
layers = sorted({l for b in builds for l in b.get("layers", {})})
short = [l.replace("LV_", "").replace("_HLODLayer", "") for l in layers]

print(f"Metric: {METRIC}")
print(f"{'Build':12s} {'Date':10s} {'TOTAL':>9s} " + " ".join(f"{s[:13]:>13s}" for s in short))
for b in builds:
    row = [fmt(b.get("layers", {}).get(l, {}).get(METRIC)) for l in layers]
    print(f"{b['id']:12s} {b['timestamp'][:10]} {fmt(b['totals'].get(METRIC)):>9s} " + " ".join(f"{v:>13s}" for v in row))
