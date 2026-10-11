#!/usr/bin/env python3
"""Validate an x-ray graph JSON and render it into the canvas HTML page.

Usage:
  python3 build.py graph.json -o x-ray-auth.html            # local file (full HTML document)
  python3 build.py graph.json -o x-ray-auth.html --target artifact   # fragment for an Artifact publish
  python3 build.py graph.json --check                           # validate only

Exit code 0 = built (warnings allowed), 1 = errors in the graph.
Standard library only.
"""
import argparse
import datetime as dt
import html
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "..", "assets", "template.html")

KINDS = {
    "entry", "route", "function", "method", "class", "module", "component", "hook", "middleware",
    "service", "external", "model", "datastore", "cache", "queue", "data", "file", "config",
    "decision", "error", "step", "concept", "formula", "output", "test",
}
EDGE_KINDS = {"call", "data", "async", "return", "conditional"}
MODES = {"code", "concept", "hybrid"}


def validate(g):
    errors, warnings = [], []
    if not isinstance(g, dict):
        return ["Top level must be a JSON object."], []
    if not g.get("title"):
        errors.append("Missing 'title'.")
    mode = g.get("mode", "code")
    if mode not in MODES:
        warnings.append(f"Unknown mode '{mode}'. Use one of {sorted(MODES)}.")
    nodes = g.get("nodes")
    if not isinstance(nodes, list) or not nodes:
        errors.append("'nodes' must be a non-empty list.")
        return errors, warnings
    ids = set()
    groups = {x.get("id") for x in g.get("groups", []) if isinstance(x, dict)}
    for i, n in enumerate(nodes):
        where = f"nodes[{i}]"
        if not isinstance(n, dict):
            errors.append(f"{where} must be an object.")
            continue
        nid = n.get("id")
        if not nid or not isinstance(nid, str):
            errors.append(f"{where} needs a string 'id'.")
            continue
        where = f"node '{nid}'"
        if nid in ids:
            errors.append(f"Duplicate node id '{nid}'.")
        ids.add(nid)
        if not n.get("title"):
            warnings.append(f"{where} has no 'title'; the id is shown instead.")
        if n.get("kind") and n["kind"] not in KINDS:
            warnings.append(f"{where} kind '{n['kind']}' is not standard; it renders in slate.")
        if n.get("group") and n["group"] not in groups:
            warnings.append(f"{where} group '{n['group']}' is not in 'groups'.")
        m = n.get("metadata") or {}
        if not isinstance(m, dict):
            errors.append(f"{where} 'metadata' must be an object.")
            continue
        if not m.get("summary"):
            warnings.append(f"{where} has no metadata.summary.")
        loc = m.get("location")
        if mode == "code" and n.get("kind") not in {"external", "service", "datastore", "cache", "queue", "model", "data", "concept", "step", "output", "decision"}:
            if not (isinstance(loc, dict) and loc.get("file")):
                warnings.append(f"{where} is a code block without metadata.location.file.")
        if isinstance(loc, dict) and loc.get("line") is not None and not isinstance(loc.get("line"), int):
            errors.append(f"{where} location.line must be an integer.")
        for s in m.get("sources", []) or []:
            url = s.get("url") if isinstance(s, dict) else s
            if not (isinstance(url, str) and url.startswith(("http://", "https://"))):
                warnings.append(f"{where} has a source without an http(s) URL; it is hidden.")
        if m.get("runtime") and not m.get("runtime_source"):
            warnings.append(f"{where} has runtime values without 'runtime_source' (for example 'app.log 2026-10-10').")
    if g.get("root") and g["root"] not in ids:
        errors.append(f"root '{g['root']}' is not a node id.")
    for i, e in enumerate(g.get("edges", []) or []):
        if not isinstance(e, dict):
            errors.append(f"edges[{i}] must be an object.")
            continue
        for end in ("from", "to"):
            if e.get(end) not in ids:
                errors.append(f"edges[{i}] '{end}' = '{e.get(end)}' is not a node id.")
        if e.get("kind") and e["kind"] not in EDGE_KINDS:
            warnings.append(f"edges[{i}] kind '{e['kind']}' is not standard ({sorted(EDGE_KINDS)}).")
    connected = {e.get("from") for e in g.get("edges", []) or []} | {e.get("to") for e in g.get("edges", []) or []}
    lonely = [i for i in ids if i not in connected]
    if len(ids) > 1 and lonely:
        warnings.append(f"Unconnected blocks: {', '.join(sorted(lonely)[:8])}.")
    if len(ids) > 40:
        warnings.append(f"{len(ids)} blocks is a lot for one view. Split into an overview map plus detail maps.")
    return errors, warnings


def render(g, target):
    with open(TEMPLATE, encoding="utf-8") as f:
        tpl = f.read()
    g.setdefault("generated_at", dt.datetime.now().strftime("%Y-%m-%d %H:%M"))
    g.setdefault("generator", "x-ray skill")
    data = json.dumps(g, ensure_ascii=False, indent=None, separators=(",", ":"))
    data = data.replace("</", "<\\/").replace("<!--", "<\\!--")
    title = html.escape(str(g.get("title", "X-Ray"))[:80])
    out = tpl.replace("__XRAY_TITLE__", title, 1).replace("/*__XRAY_DATA__*/", data, 1)
    if target == "local":
        out = ('<!doctype html>\n<html lang="en">\n<head>\n<meta charset="utf-8">\n'
               '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
               '</head>\n<body>\n' + out + '\n</body>\n</html>\n')
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("graph", help="path to graph JSON")
    ap.add_argument("-o", "--out", help="output HTML path (default: x-ray-<graph name>.html)")
    ap.add_argument("--target", choices=["local", "artifact"], default="local",
                    help="local = full HTML document to open in a browser; artifact = fragment for the Artifact tool")
    ap.add_argument("--check", action="store_true", help="validate only")
    a = ap.parse_args()
    try:
        with open(a.graph, encoding="utf-8") as f:
            g = json.load(f)
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: cannot read graph: {e}")
        return 1
    errors, warnings = validate(g)
    for w in warnings:
        print(f"warn: {w}")
    for e in errors:
        print(f"ERROR: {e}")
    if errors:
        print(f"\n{len(errors)} error(s). Fix the graph and run again.")
        return 1
    n, m = len(g["nodes"]), len(g.get("edges", []))
    if a.check:
        print(f"OK: {n} blocks, {m} links, {len(warnings)} warning(s).")
        return 0
    out = a.out or "x-ray-" + os.path.splitext(os.path.basename(a.graph))[0] + ".html"
    with open(out, "w", encoding="utf-8") as f:
        f.write(render(g, a.target))
    print(f"OK: wrote {out} ({n} blocks, {m} links, {len(warnings)} warning(s), target={a.target}).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
