#!/usr/bin/env python3
import argparse, hashlib, json, os, pathlib
from fnmatch import fnmatch

parser = argparse.ArgumentParser(description="Generate SHA-256 inventory and Merkle root")
parser.add_argument("root", nargs="?", default=".")
parser.add_argument("--include", action="append", help="glob include", default=["core/**","tools/**","README.md","LICENSE","Makefile"])
parser.add_argument("--out", default="manifest/hash-inventory.json")
args = parser.parse_args()

root = pathlib.Path(args.root)
files = []
for pat in args.include:
    for p in root.rglob("*"):
        # Skip __pycache__ directories and .pyc files
        if "__pycache__" in p.parts or p.suffix == ".pyc":
            continue
        if p.is_file() and fnmatch(str(p).replace("\\","/"), pat):
            files.append(p)

entries = []
for p in sorted(files):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1<<20), b""):
            h.update(chunk)
    entries.append({"path": str(p).replace("\\","/"), "sha256": h.hexdigest()})

level = [bytes.fromhex(e["sha256"]) for e in entries]
if not level:
    root_hash = hashlib.sha256(b"").hexdigest()
else:
    while len(level) > 1:
        nxt = []
        for i in range(0, len(level), 2):
            a = level[i]
            b = level[i+1] if i+1 < len(level) else a
            nxt.append(hashlib.sha256(a + b).digest())
        level = nxt
    root_hash = level[0].hex()

out = {"algo":"sha256","entries":entries,"merkle_root":root_hash}
pathlib.Path(args.out).parent.mkdir(parents=True, exist_ok=True)
with open(args.out, "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
print(root_hash)
