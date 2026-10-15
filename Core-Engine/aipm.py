"""AIPM P03 JSON CLI."""
from __future__ import annotations
import argparse, json

parser = argparse.ArgumentParser(prog="aipm")
parser.add_argument("command", choices=["health", "list", "inspect", "state-read"])
parser.add_argument("--registry")
parser.add_argument("--project-id")
args = parser.parse_args()
if args.command in {"list", "inspect", "state-read"}:
    if not args.registry: parser.error(f"{args.command} requires --registry")
    data=json.loads(open(args.registry, encoding="utf-8").read())
    if args.command == "list": print(json.dumps({"schema_version":"1.0","status":"PASS","projects":data["projects"]}))
    else:
        project=next((item for item in data["projects"] if item["project_id"]==args.project_id),None)
        if not project: print(json.dumps({"schema_version":"1.0","status":"BLOCKED","reason":"PROJECT_NOT_REGISTERED"}))
        elif args.command == "inspect": print(json.dumps({"schema_version":"1.0","status":"PASS","project":project}))
        else:
            state=open(__import__('pathlib').Path(project["root_path"])/"Shared-Project-State-Manager"/"State-Manifest.json",encoding="utf-8").read()
            print(json.dumps({"schema_version":"1.0","status":"PASS","state":json.loads(state)}))
else:
    print(json.dumps({"schema_version": "1.0", "status": "PASS", "service": "aipm-core", "command": args.command}))
