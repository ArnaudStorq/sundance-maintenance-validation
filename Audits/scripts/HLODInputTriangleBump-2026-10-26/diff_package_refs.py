"""Diff the /Game and /Script references between two revisions of a package."""
import re
import sys

PATTERN = rb"/(?:Game|Script)/[A-Za-z0-9_/.]+"


def refs(path):
    data = open(path, "rb").read()
    return len(data), set(s.decode() for s in re.findall(PATTERN, data))


size_a, a = refs(sys.argv[1])
size_b, b = refs(sys.argv[2])
print(f"before: {size_a} bytes, {len(a)} refs")
print(f"after:  {size_b} bytes, {len(b)} refs")
print("\nAdded:")
for s in sorted(b - a):
    print("  +", s)
print("\nRemoved:")
for s in sorted(a - b):
    print("  -", s)
