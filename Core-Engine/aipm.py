"""AIPM P03 JSON CLI."""
from __future__ import annotations
import argparse, json

parser = argparse.ArgumentParser(prog="aipm")
parser.add_argument("command", choices=["health", "list"])
parser.add_argument("--registry")
args = parser.parse_args()
if args.command == "list":
    if not args.registry: parser.error("list requires --registry")
    data=json.loads(open(args.registry, encoding="utf-8").read())
    print(json.dumps({"schema_version":"1.0","status":"PASS","projects":data["projects"]}))
else:
    print(json.dumps({"schema_version": "1.0", "status": "PASS", "service": "aipm-core", "command": args.command}))
