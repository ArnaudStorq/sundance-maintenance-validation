"""Read depot paths on stdin, find the packages mentioning a cell name, and list the strings they reference."""
import re
import sys

ROOT = "D:/Sun/"
needle = sys.argv[1].encode()
show_all = len(sys.argv) > 2 and sys.argv[2] == "--strings"

for line in sys.stdin:
    depot = line.strip()
    if not depot.startswith("//sun/"):
        continue
    local = ROOT + depot.split("/", 4)[4]
    try:
        data = open(local, "rb").read()
    except OSError:
        continue
    if needle not in data:
        continue
    print(f"MATCH {depot} ({len(data)} bytes)")
    strings = sorted(set(re.findall(rb"[A-Za-z_/][A-Za-z0-9_/.:\-]{7,}", data)))
    for s in strings:
        s = s.decode(errors="replace")
        if show_all or "__ExternalActors__" in s or "HLODLayer" in s or "_L1_" in s or "_L0_" in s:
            print("   ", s)
