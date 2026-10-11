#!/usr/bin/env python3
"""Quick structural scan of a file or repo, to find entry points and trace calls.

It does NOT replace reading the code. It gives a map so you know which files to read.

Usage:
  python3 scan_repo.py PATH                 # summary: languages, entry points, biggest modules
  python3 scan_repo.py PATH --json idx.json # full symbol index as JSON
  python3 scan_repo.py PATH --find NAME     # where NAME is defined and every line that calls it

Python files use the ast module (exact). JS/TS/Go/Java/Rust/etc. use regex (approximate).
Standard library only.
"""
import argparse
import ast
import json
import os
import re
import sys

SKIP_DIRS = {".git", "node_modules", "venv", ".venv", "env", "__pycache__", "dist", "build", ".next",
             ".nuxt", "target", ".idea", ".vscode", "coverage", ".mypy_cache", ".pytest_cache", "vendor",
             ".turbo", ".cache", "out", "Pods", ".gradle", ".dart_tool"}
LANG = {".py": "python", ".js": "js", ".jsx": "js", ".mjs": "js", ".cjs": "js", ".ts": "ts", ".tsx": "ts",
        ".go": "go", ".java": "java", ".kt": "kotlin", ".rs": "rust", ".rb": "ruby", ".php": "php",
        ".cs": "csharp", ".swift": "swift", ".dart": "dart", ".c": "c", ".cc": "cpp", ".cpp": "cpp", ".h": "c"}
MAX_BYTES = 600_000

ROUTE_RX = re.compile(r"""\b(app|router|api|server|bp|blueprint|r|e|g)\s*\.\s*(get|post|put|patch|delete|route|all|use|options|head|websocket)\s*\(\s*['"`]([^'"`]+)""", re.I)
DECOR_ROUTE_RX = re.compile(r"""\.(get|post|put|patch|delete|route|websocket|api_route)\(\s*['"]([^'"]+)""")
GENERIC_DEF = {
    "js": [re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:async\s+)?function\s*\*?\s*([A-Za-z_$][\w$]*)\s*\("),
           re.compile(r"^\s*(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?(?:\([^)]*\)|[A-Za-z_$][\w$]*)\s*=>"),
           re.compile(r"^\s*(?:export\s+)?(?:default\s+)?(?:abstract\s+)?class\s+([A-Za-z_$][\w$]*)"),
           re.compile(r"^\s+(?:public\s+|private\s+|protected\s+|static\s+|async\s+)*([A-Za-z_$][\w$]*)\s*\([^)]*\)\s*(?::\s*[^{]+)?\{\s*$")],
    "go": [re.compile(r"^\s*func\s+(?:\([^)]*\)\s*)?([A-Za-z_]\w*)\s*\("), re.compile(r"^\s*type\s+([A-Za-z_]\w*)\s+(?:struct|interface)")],
    "java": [re.compile(r"^\s*(?:public|private|protected|static|final|abstract|synchronized|\s)+[\w<>\[\],\s]+\s+([a-zA-Z_]\w*)\s*\([^;]*$"), re.compile(r"\b(?:class|interface|enum|record)\s+([A-Z]\w*)")],
    "kotlin": [re.compile(r"^\s*(?:\w+\s+)*fun\s+(?:<[^>]+>\s*)?(?:[\w.]+\.)?([a-zA-Z_]\w*)\s*\("), re.compile(r"\b(?:class|interface|object)\s+([A-Z]\w*)")],
    "rust": [re.compile(r"^\s*(?:pub(?:\([^)]*\))?\s+)?(?:async\s+)?fn\s+([a-zA-Z_]\w*)"), re.compile(r"^\s*(?:pub\s+)?(?:struct|enum|trait|impl)\s+([A-Z]\w*)")],
    "ruby": [re.compile(r"^\s*def\s+(?:self\.)?([a-zA-Z_]\w*[!?]?)"), re.compile(r"^\s*class\s+([A-Z]\w*)")],
    "php": [re.compile(r"function\s+([a-zA-Z_]\w*)\s*\("), re.compile(r"^\s*(?:abstract\s+|final\s+)?class\s+([A-Z]\w*)")],
    "csharp": [re.compile(r"^\s*(?:public|private|protected|internal|static|async|virtual|override|\s)+[\w<>\[\],\s]+\s+([A-Z]\w*)\s*\("), re.compile(r"\b(?:class|interface|record|struct)\s+([A-Z]\w*)")],
    "swift": [re.compile(r"^\s*(?:\w+\s+)*func\s+([a-zA-Z_]\w*)"), re.compile(r"\b(?:class|struct|protocol|enum)\s+([A-Z]\w*)")],
    "dart": [re.compile(r"^\s*(?:[\w<>?]+\s+)+([a-zA-Z_]\w*)\s*\([^;]*\)\s*(?:async\s*)?\{"), re.compile(r"^\s*(?:abstract\s+)?class\s+([A-Z]\w*)")],
    "c": [re.compile(r"^[A-Za-z_][\w\s\*]*\s\**([A-Za-z_]\w*)\s*\([^;]*$")],
}
GENERIC_DEF["ts"] = GENERIC_DEF["js"]
GENERIC_DEF["cpp"] = GENERIC_DEF["c"]
IMPORT_RX = {
    "js": re.compile(r"""(?:import\s[^'"]*from\s*|import\s*\(\s*|require\s*\(\s*)['"]([^'"]+)['"]"""),
    "go": re.compile(r'^\s*(?:import\s+)?"([^"]+)"'),
    "java": re.compile(r"^\s*import\s+([\w.]+)"),
    "kotlin": re.compile(r"^\s*import\s+([\w.]+)"),
    "rust": re.compile(r"^\s*use\s+([\w:]+)"),
    "ruby": re.compile(r"""^\s*require(?:_relative)?\s+['"]([^'"]+)"""),
    "dart": re.compile(r"""^\s*import\s+['"]([^'"]+)"""),
    "csharp": re.compile(r"^\s*using\s+([\w.]+);"),
    "swift": re.compile(r"^\s*import\s+(\w+)"),
}
IMPORT_RX["ts"] = IMPORT_RX["js"]
CALL_RX = re.compile(r"\b([A-Za-z_$][\w$]*)\s*\(")
KEYWORDS = set("if for while switch return catch function typeof new await async print len range super self this elif else try with def class lambda import from sizeof".split())
ENTRY_NAMES = {"main", "handler", "lambda_handler", "run", "start", "serve", "app", "create_app", "bootstrap", "init", "cli"}
ENTRY_FILES = {"main.py", "app.py", "server.py", "manage.py", "wsgi.py", "asgi.py", "cli.py", "__main__.py", "index.js", "index.ts",
               "server.js", "server.ts", "app.js", "app.ts", "main.go", "main.rs", "Main.java", "main.dart", "main.ts", "main.tsx", "App.tsx"}


def walk(root):
    if os.path.isfile(root):
        yield root
        return
    for d, dirs, files in os.walk(root):
        dirs[:] = sorted(x for x in dirs if x not in SKIP_DIRS and not x.startswith("."))
        for f in sorted(files):
            if os.path.splitext(f)[1] in LANG:
                yield os.path.join(d, f)


def scan_python(path, src):
    out = {"defs": [], "imports": [], "routes": [], "calls": []}
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        out["error"] = f"syntax error line {e.lineno}"
        return out

    class V(ast.NodeVisitor):
        def __init__(self):
            self.stack = []

        def _def(self, node, kind):
            name = ".".join(self.stack + [node.name])
            decos = []
            for d in getattr(node, "decorator_list", []):
                try:
                    decos.append(ast.unparse(d))
                except Exception:
                    pass
            args = []
            if kind != "class":
                try:
                    args = [a.arg for a in node.args.args]
                except Exception:
                    pass
            out["defs"].append({"name": name, "kind": kind, "line": node.lineno, "end_line": getattr(node, "end_lineno", None),
                                "args": args, "decorators": decos, "doc": (ast.get_docstring(node) or "").split("\n")[0][:160]})
            for d in decos:
                m = DECOR_ROUTE_RX.search(d)
                if m:
                    out["routes"].append({"method": m.group(1).upper(), "path": m.group(2), "handler": name, "line": node.lineno})
            self.stack.append(node.name)
            self.generic_visit(node)
            self.stack.pop()

        def visit_FunctionDef(self, n):
            self._def(n, "method" if self.stack and self._in_class else "function")

        def visit_AsyncFunctionDef(self, n):
            self.visit_FunctionDef(n)

        def visit_ClassDef(self, n):
            prev = getattr(self, "_in_class", False)
            self._in_class = True
            self._def(n, "class")
            self._in_class = prev

        def visit_Import(self, n):
            out["imports"] += [a.name for a in n.names]

        def visit_ImportFrom(self, n):
            mod = ("." * n.level) + (n.module or "")
            out["imports"].append(mod + ":" + ",".join(a.name for a in n.names))

        def visit_Call(self, n):
            try:
                fn = ast.unparse(n.func)
            except Exception:
                fn = None
            if fn and len(fn) < 80:
                out["calls"].append({"in": ".".join(self.stack) or "<module>", "call": fn, "line": n.lineno})
            self.generic_visit(n)

    v = V()
    v._in_class = False
    v.visit(tree)
    if re.search(r"""if\s+__name__\s*==\s*['"]__main__['"]""", src):
        out["main_guard"] = True
    return out


def scan_generic(lang, src):
    out = {"defs": [], "imports": [], "routes": [], "calls": []}
    rx_defs = GENERIC_DEF.get(lang, [])
    rx_imp = IMPORT_RX.get(lang)
    current = "<module>"
    for i, line in enumerate(src.splitlines(), 1):
        s = line.strip()
        if s.startswith(("//", "#", "*", "/*")):
            continue
        for rx in rx_defs:
            m = rx.search(line)
            if m and m.group(1) not in KEYWORDS:
                kind = "class" if re.search(r"\b(class|struct|interface|trait|type|enum|record|protocol|object)\b", line) else "function"
                out["defs"].append({"name": m.group(1), "kind": kind, "line": i})
                if kind == "function":
                    current = m.group(1)
                break
        if rx_imp:
            for m in rx_imp.finditer(line):
                out["imports"].append(m.group(1))
        m = ROUTE_RX.search(line)
        if m:
            out["routes"].append({"method": m.group(2).upper(), "path": m.group(3), "line": i})
        for m in CALL_RX.finditer(line):
            name = m.group(1)
            if name not in KEYWORDS and len(name) > 1:
                out["calls"].append({"in": current, "call": name, "line": i})
    return out


def scan(root):
    files = []
    for p in walk(root):
        try:
            if os.path.getsize(p) > MAX_BYTES:
                files.append({"path": p, "lang": LANG[os.path.splitext(p)[1]], "skipped": "too large"})
                continue
            with open(p, encoding="utf-8", errors="replace") as f:
                src = f.read()
        except OSError:
            continue
        lang = LANG[os.path.splitext(p)[1]]
        info = scan_python(p, src) if lang == "python" else scan_generic(lang, src)
        info.update({"path": os.path.relpath(p, root if os.path.isdir(root) else os.path.dirname(root) or "."),
                     "lang": lang, "lines": src.count("\n") + 1})
        files.append(info)
    return files


def entry_points(files):
    eps = []
    for f in files:
        base = os.path.basename(f["path"])
        for r in f.get("routes", []):
            eps.append(f"route  {r['method']:<6} {r['path']:<32} {f['path']}:{r['line']}" + (f"  {r.get('handler')}" if r.get("handler") else ""))
        if f.get("main_guard"):
            eps.append(f"main   __main__ guard                        {f['path']}")
        if base in ENTRY_FILES:
            eps.append(f"file   conventional entry file                {f['path']}")
        for d in f.get("defs", []):
            short = d["name"].split(".")[-1]
            if short in ENTRY_NAMES and d["kind"] != "class":
                eps.append(f"name   {d['name']:<38} {f['path']}:{d['line']}")
    seen, outl = set(), []
    for e in eps:
        if e not in seen:
            seen.add(e)
            outl.append(e)
    return outl


def find(files, name):
    short = name.split(".")[-1]
    print(f"Definitions of '{name}':")
    hit = False
    for f in files:
        for d in f.get("defs", []):
            if d["name"] == name or d["name"].split(".")[-1] == short:
                hit = True
                extra = f"  ({', '.join(d.get('args', []))})" if d.get("args") is not None and d["kind"] != "class" else ""
                print(f"  {f['path']}:{d['line']}  {d['kind']} {d['name']}{extra}")
    if not hit:
        print("  none found (it may come from a library; check the imports)")
    print(f"\nCall sites of '{short}':")
    n = 0
    for f in files:
        for c in f.get("calls", []):
            if c["call"] == name or c["call"].split(".")[-1] == short:
                print(f"  {f['path']}:{c['line']}  in {c['in']}  -> {c['call']}")
                n += 1
                if n >= 80:
                    print("  ... (truncated at 80)")
                    return
    if n == 0:
        print("  none found")


def summary(files, root):
    langs = {}
    for f in files:
        langs[f["lang"]] = langs.get(f["lang"], 0) + 1
    total = sum(f.get("lines", 0) for f in files)
    print(f"Scanned {len(files)} source files, {total} lines under {root}")
    print("Languages: " + ", ".join(f"{k} {v}" for k, v in sorted(langs.items(), key=lambda x: -x[1])))
    eps = entry_points(files)
    print("\nEntry point candidates:")
    for e in eps[:60] or ["  none detected; ask the user which function or command starts the flow"]:
        print("  " + e)
    print("\nLargest modules (by definitions):")
    for f in sorted(files, key=lambda x: -len(x.get("defs", [])))[:15]:
        names = ", ".join(d["name"] for d in f.get("defs", [])[:6])
        print(f"  {f['path']} ({f.get('lines', 0)} lines, {len(f.get('defs', []))} defs): {names}")
    ext = {}
    for f in files:
        for imp in f.get("imports", []):
            top = imp.split(":")[0].lstrip(".").split("/")[0].split(".")[0]
            if top and not imp.startswith((".", "@/", "~/")):
                ext[top] = ext.get(top, 0) + 1
    print("\nMost imported packages (candidates for external blocks and docs lookups):")
    print("  " + ", ".join(f"{k} ({v})" for k, v in sorted(ext.items(), key=lambda x: -x[1])[:25]))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("path")
    ap.add_argument("--json", help="write the full index to this file")
    ap.add_argument("--find", help="show definitions and call sites of a symbol")
    a = ap.parse_args()
    if not os.path.exists(a.path):
        print(f"ERROR: {a.path} does not exist")
        return 1
    files = scan(a.path)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            json.dump(files, f, indent=1)
        print(f"wrote {a.json}")
    if a.find:
        find(files, a.find)
    elif not a.json:
        summary(files, a.path)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except BrokenPipeError:
        sys.exit(0)
