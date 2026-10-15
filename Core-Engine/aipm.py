"""AIPM P03 JSON CLI."""
from __future__ import annotations
import argparse
import json

parser = argparse.ArgumentParser(prog="aipm")
parser.add_argument("command", choices=["health"])
args = parser.parse_args()
print(json.dumps({"schema_version": "1.0", "status": "PASS", "service": "aipm-core", "command": args.command}))
