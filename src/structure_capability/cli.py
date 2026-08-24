from __future__ import annotations
import argparse, json
from pathlib import Path
from .api import StructureCapability
from .server import serve

def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def main():
    ap = argparse.ArgumentParser(prog="structure-capability")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("capabilities")
    p.add_argument("--project", default=".")

    p = sub.add_parser("tools")
    p.add_argument("--project", default=".")
    p.add_argument("--compact", action="store_true", help="Return only the token-efficient tool index.")
    p.add_argument("--name", help="Return exactly one tool contract.")
    p.add_argument("--group", help="Filter compact index by capability group.")

    p = sub.add_parser("presets")
    p.add_argument("preset_id", nargs="?")
    p.add_argument("--full", action="store_true")
    p.add_argument("--project", default=".")

    p = sub.add_parser("resolve")
    p.add_argument("request", help="JSON file containing tool, optional preset_id, and request/overrides.")
    p.add_argument("--project", default=".")

    p = sub.add_parser("inventory")
    p.add_argument("--project", default=".")

    for name in ("audit", "plan", "generate", "dungeon-layout", "infrastructure-layout"):
        p = sub.add_parser(name)
        p.add_argument("request")
        p.add_argument("--project", default=".")

    p = sub.add_parser("minecraft-version")
    p.add_argument("version")
    p.add_argument("--project", default=".")

    p = sub.add_parser("resume")
    p.add_argument("snapshot_id")
    p.add_argument("--project", default=".")

    p = sub.add_parser("serve")
    p.add_argument("--project", default=".")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8787)

    args = ap.parse_args()
    if args.cmd == "serve":
        return serve(args.project, args.host, args.port)

    cap = StructureCapability(args.project)
    if args.cmd == "capabilities":
        result = cap.capabilities()
    elif args.cmd == "inventory":
        result = cap.inventory_project()
    elif args.cmd == "tools":
        if args.name:
            result = cap.tool_contract(args.name)
        elif args.compact:
            result = cap.tool_index(group=args.group)
        else:
            result = cap.tools()
    elif args.cmd == "presets":
        result = cap.tool_preset(args.preset_id) if args.preset_id else cap.tool_presets(compact=not args.full)
    elif args.cmd == "resolve":
        result = cap.resolve_tool_request(load_json(args.request))
    elif args.cmd == "resume":
        result = cap.resume(args.snapshot_id)
    elif args.cmd == "minecraft-version":
        result = cap.minecraft_version(args.version)
    elif args.cmd == "dungeon-layout":
        result = cap.dungeon_layout(load_json(args.request))
    elif args.cmd == "infrastructure-layout":
        result = cap.infrastructure_layout(load_json(args.request))
    else:
        result = getattr(cap, args.cmd)(load_json(args.request))
    print(json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    main()
