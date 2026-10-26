"""Sample PCG actors from a CL and check SK -> SM grass swaps between two depot states."""
import os
import re
import subprocess
import sys

CL = sys.argv[1]
BEFORE, AFTER = sys.argv[2], sys.argv[3]
SAMPLE = int(sys.argv[4]) if len(sys.argv) > 4 else 30
ROOT = "//sun/Dev/Sundance/Content/__ExternalActors__/Levels/Overland/LV_Overland/..."
OUT = "cursor-scratch/pkg/sample"
os.makedirs(OUT, exist_ok=True)

files = subprocess.run(["p4", "-ztag", "-F", "%depotFile%", "files", f"{ROOT}@={CL}"],
                       capture_output=True, text=True).stdout.split()


def fetch(depot, at, tag):
    local = os.path.join(OUT, f"{abs(hash(depot))}_{tag}.uasset")
    r = subprocess.run(["p4", "print", "-q", "-o", local, f"{depot}@{at}"], capture_output=True, text=True)
    return open(local, "rb").read() if r.returncode == 0 and os.path.exists(local) else None


def grass(data, prefix):
    return set(re.findall(rb"/Game/Environment/Foliage/Grass/[A-Za-z/]+/" + prefix + rb"_[A-Za-z0-9_]+", data))


checked = swapped = 0
size_before = size_after = 0
for depot in files:
    if checked >= SAMPLE:
        break
    b, a = fetch(depot, BEFORE, "b"), fetch(depot, AFTER, "a")
    if not b or not a or b"PCGStreamingActor" not in a:
        continue
    checked += 1
    size_before += len(b)
    size_after += len(a)
    sk_gone = len(grass(b, rb"SK") - grass(a, rb"SK"))
    sm_new = len(grass(a, rb"SM") - grass(b, rb"SM"))
    if sk_gone and sm_new:
        swapped += 1
    print(f"{depot[-40:]} {len(b):>9} -> {len(a):>9}  SK grass removed={sk_gone} SM grass added={sm_new}")

print(f"\nPCG actors checked={checked}, with SK->SM grass swap={swapped}, "
      f"total size {size_before / 1e6:.1f}MB -> {size_after / 1e6:.1f}MB")
