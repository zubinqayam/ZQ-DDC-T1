#!/usr/bin/env python3
import argparse, json, os, subprocess, sys, tempfile, yaml, datetime

def canonical(obj):
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"), sort_keys=True)

parser = argparse.ArgumentParser(description="Sign manifest via minisign")
parser.add_argument("manifest", help="YAML manifest path")
parser.add_argument("--key", required=True, help="minisign secret key path (-s)")
parser.add_argument("--pub", required=False, help="minisign pubkey to embed (optional)")
parser.add_argument("--update", action="store_true", help="write signature back into YAML")
args = parser.parse_args()

with open(args.manifest, "r", encoding="utf-8") as f:
    data = yaml.safe_load(f)

payload = canonical(data.get("doc_index", {}))
now = datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

with tempfile.TemporaryDirectory() as td:
    pjson = os.path.join(td, "payload.json")
    with open(pjson, "w", encoding="utf-8") as pf:
        pf.write(payload)
    subprocess.check_call(["minisign", "-Sm", pjson, "-s", args.key, "-m", "-q"])
    sig_path = pjson + ".minisig"
    with open(sig_path, "r", encoding="utf-8") as sf:
        sig = sf.read().strip()

if args.pub:
    data.setdefault("doc_index", {}).setdefault("signing", {}).setdefault("key_id", os.path.basename(args.pub))

if args.update:
    di = data.setdefault("doc_index", {})
    di.setdefault("signing", {}).setdefault("signature", {})
    di["signing"]["signature"]["value"] = sig
    di["signing"]["signature"]["created_at"] = now
    with open(args.manifest, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, sort_keys=False, allow_unicode=True)
print(sig)
