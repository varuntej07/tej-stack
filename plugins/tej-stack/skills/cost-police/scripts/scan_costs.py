#!/usr/bin/env python3
"""Cost Police inventory scan. Standard library only, Python 3.9+.

Lists places in a repository where money is spent or could run away:
LLM SDK call sites, model ids, metered services, likely leaked keys,
and IaC resources. Every result is a CANDIDATE for a human or agent to
read, never a finding on its own.

Usage:
    python3 scan_costs.py <repo-or-file>
    python3 scan_costs.py <repo> --json
    python3 scan_costs.py <repo> --find <regex>
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path

SKIP_DIRS = {
    ".git", ".hg", ".svn", "node_modules", "dist", "build", "out", ".next", ".nuxt",
    ".output", ".svelte-kit", "venv", ".venv", "env", "__pycache__", ".dart_tool",
    ".gradle", "Pods", "target", "vendor", ".terraform", "coverage", ".idea",
    ".vscode", "site-packages", ".pytest_cache", ".mypy_cache", ".cache", ".turbo",
}
CODE_EXT = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".dart", ".go"}
CONFIG_EXT = {".tf", ".yml", ".yaml", ".json", ".toml"}
MAX_BYTES = 1_000_000
NEARBY = 25  # lines around a call to look for batch usage

# --- LLM detection -----------------------------------------------------------

LLM_IMPORTS = {
    "anthropic": re.compile(r"(import\s+anthropic|from\s+anthropic|@anthropic-ai/sdk|anthropic-sdk-go|package:anthropic)"),
    "openai": re.compile(r"(import\s+openai|from\s+openai|['\"]openai['\"]|openai-go|sashabaranov/go-openai|package:openai)"),
    "google-genai": re.compile(r"(google\.genai|google\.generativeai|@google/genai|@google/generative-ai|vertexai|firebase_vertexai|firebase_ai|google_generative_ai|google\.golang\.org/genai|cloud\.google\.com/go/vertexai)"),
    "litellm": re.compile(r"(import\s+litellm|from\s+litellm)"),
    "langchain": re.compile(r"(langchain|@langchain/)"),
    "vercel-ai": re.compile(r"from\s+['\"]ai['\"]|require\(['\"]ai['\"]\)|@ai-sdk/"),
    "openrouter": re.compile(r"openrouter\.ai|@openrouter/"),
}
LLM_CALLS = re.compile(
    r"(\.messages\.(create|stream|count_tokens|countTokens)\s*\(|\.Messages\.New\s*\("
    r"|\.chat\.completions\.(create|parse|stream)\s*\(|\.Chat\.Completions\.New\s*\("
    r"|\.responses\.(create|parse|stream)\s*\(|\.embeddings\.create\s*\("
    r"|\.models\.generate_content(_stream)?\s*\(|\.generate_content\s*\(|\.generateContent(Stream)?\s*\("
    r"|\blitellm\.a?completion\s*\(|\blitellm\.a?embedding\s*\("
    r"|\b(generateText|streamText|generateObject|streamObject|embedMany|embed)\s*\("
    r"|\b(ChatOpenAI|ChatAnthropic|ChatVertexAI|ChatGoogleGenerativeAI|AzureChatOpenAI)\s*\("
    r"|\.(invoke|ainvoke|batch|abatch)\s*\(\s*(messages|prompt|\[))"
)
BATCH_CALLS = re.compile(r"(\.batches\.create\s*\(|\.messages\.batches\.|\.batches\.create|batch_create|BatchJob|/v1/batches|\.batches\.)")
MODEL_ID = re.compile(
    r"['\"`]((?:claude-[a-z0-9][a-z0-9.\-]*)|(?:gpt-[0-9][a-z0-9.\-]*)|(?:o[1-9](?:-mini|-pro)?(?:-[0-9-]+)?)"
    r"|(?:gemini-[0-9a-z][a-z0-9.\-]*)|(?:text-embedding-[a-z0-9\-]+))['\"`]"
)
OPENROUTER_MODEL = re.compile(r"['\"`]((?:anthropic|openai|google|meta-llama|mistralai|deepseek|qwen|x-ai)/[a-z0-9.\-:]+)['\"`]")
MAX_TOKENS = re.compile(r"(max_tokens|maxTokens|max_output_tokens|maxOutputTokens|max_completion_tokens|maxCompletionTokens|MaxTokens)")
CACHING = re.compile(r"(cache_control|cacheControl|prompt_cache_key|cachedContent|cached_content|CacheControl|providerOptions[^\n]*cache)")

# --- Metered services --------------------------------------------------------

LISTENER = re.compile(r"(\bonSnapshot\s*\(|\.snapshots\s*\(\s*\)|\.on_snapshot\s*\()")
FS_READ = re.compile(r"(\bgetDocs?\s*\(|\.get\s*\(\s*\)|\.getDocuments\s*\(|\.stream\s*\(\s*\))")
LIMIT = re.compile(r"(\blimit\s*\(|\.limit\s*\(|limitToLast\s*\(|\.limit\()")
TRIGGER = re.compile(
    r"(onDocument(Written|Created|Updated|Deleted)(WithAuthContext)?\s*\(\s*(\{[^}]*document\s*:\s*)?['\"`]([^'\"`]+)['\"`]"
    r"|firestore\.document\s*\(\s*['\"`]([^'\"`]+)['\"`]"
    r"|on_document_(written|created|updated|deleted)\s*\(\s*document\s*=\s*['\"]([^'\"]+)['\"]"
    r"|\bref\s*\(\s*['\"`]([^'\"`]+)['\"`]\s*\)\s*\.\s*on(Write|Create|Update|Delete))"
)
STORAGE_TRIGGER = re.compile(r"(onObjectFinalized|onObjectArchived|onObjectDeleted|onObjectMetadataUpdated|storage\.object\(\)|on_object_finalized)")
WRITE_CALL = re.compile(r"\.(set|update|add|create|setDoc|updateDoc|addDoc|delete)\s*\(|\b(setDoc|updateDoc|addDoc)\s*\(")
SELF_WRITE = re.compile(r"(event\.data(\.after)?\.ref\.(set|update)|change\.after\.ref\.(set|update)|snap(shot)?\.ref\.(set|update)|event\.data\.after\.reference\.(set|update))")
PUBLIC_STORAGE = re.compile(r"(public-read(-write)?|['\"]allUsers['\"]|\ballUsers\b|makePublic\s*\(|block_public_acls\s*=\s*false|BlockPublicAcls:\s*false|PublicAccessBlockConfiguration[^\n]*false)")
SMS_IMPORTS = re.compile(r"(twilio|@vonage|vonage|messagebird|plivo|telnyx|sinch)", re.I)
SMS_CALLS = re.compile(
    r"(\.verifications\.create\s*\(|\.messages\.create\s*\(|\bsignInWithPhoneNumber\s*\(|\bverifyPhoneNumber\s*\("
    r"|\.sms\.send\s*\(|PhoneNumber\s*[:=]|\.publish\s*\(\s*\{[^}]*PhoneNumber)"
)
KEY_PATTERNS = [
    ("anthropic key", re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("openai key", re.compile(r"sk-(?!ant-)(?:proj-)?[A-Za-z0-9_\-]{32,}")),
    ("google api key (often a public client key by design; check its restrictions)", re.compile(r"AIza[0-9A-Za-z_\-]{35}")),
    ("aws access key id", re.compile(r"\b(AKIA|ASIA)[0-9A-Z]{16}\b")),
    ("stripe secret key", re.compile(r"sk_live_[0-9A-Za-z]{20,}")),
    ("twilio auth token or key", re.compile(r"\bSK[0-9a-f]{32}\b")),
]

# --- Loops -------------------------------------------------------------------

LOOP_LINE = re.compile(
    r"^\s*(for\b|while\b|async\s+for\b)|\.forEach\s*\(|\.map\s*\(\s*(async\s*)?\(?|\bfor\s*\(|\bfor\s+await\b|Promise\.all\s*\(|asyncio\.gather\s*\(|\bfor\s+\w+\s*:?=\s*range\b|\.(each|times)\b"
)

# --- IaC ---------------------------------------------------------------------

TF_RESOURCE = re.compile(r'^\s*resource\s+"([a-z0-9_]+)"\s+"([^"]+)"')
CFN_TYPE = re.compile(r"^\s*['\"]?Type['\"]?\s*:\s*['\"]?(AWS::[A-Za-z0-9]+::[A-Za-z0-9]+)")
TF_WATCH = {
    "aws_nat_gateway": "NAT gateway: hourly plus per-GB processing; check count per AZ and per environment",
    "aws_eip": "public IP: check per-address hourly charges on the VPC pricing page",
    "aws_instance": "instance: check instance_type per environment",
    "aws_db_instance": "database: check instance_class, multi_az, and storage type per environment",
    "aws_rds_cluster": "database cluster: check instance count and class per environment",
    "aws_ebs_volume": "volume: check type (gp2, io1, io2) and iops",
    "aws_lb": "load balancer: hourly; check it has targets in every environment",
    "aws_alb": "load balancer: hourly; check it has targets in every environment",
    "aws_cloudwatch_log_group": "log group: check retention_in_days is set",
    "aws_s3_bucket": "bucket: check lifecycle rules and public access",
    "aws_lambda_function": "function: check memory_size, timeout, reserved concurrency",
    "aws_elasticache_cluster": "cache: always-on node; check node_type per environment",
    "aws_opensearch_domain": "search domain: always-on; check instance type and count",
    "aws_vpc_endpoint": "VPC endpoint: interface endpoints bill hourly per AZ",
    "google_compute_instance": "VM: check machine_type per environment",
    "google_sql_database_instance": "Cloud SQL: always-on; check tier and availability_type",
    "google_container_cluster": "GKE: check node pools and autoscaling minimums",
    "google_compute_router_nat": "Cloud NAT: check per-hour and per-GB charges",
    "google_storage_bucket": "bucket: check lifecycle_rule and public IAM",
    "google_cloudfunctions2_function": "function: check memory, max instances, min instances",
    "google_cloud_run_v2_service": "Cloud Run: check min_instance_count (above zero bills while idle)",
    "azurerm_linux_virtual_machine": "VM: check size per environment",
    "azurerm_windows_virtual_machine": "VM: check size per environment",
    "azurerm_kubernetes_cluster": "AKS: check node pool sizes and autoscaling minimums",
    "azurerm_nat_gateway": "NAT gateway: hourly plus per-GB processing",
    "azurerm_public_ip": "public IP: check per-address charges",
}
PLATFORM_FILES = {
    "firebase.json": "Firebase config", "vercel.json": "Vercel config", "fly.toml": "Fly config",
    "render.yaml": "Render config", "netlify.toml": "Netlify config", "Pulumi.yaml": "Pulumi project",
    "cdk.json": "CDK app (synthesize to CloudFormation to price)", "serverless.yml": "Serverless Framework",
    "serverless.yaml": "Serverless Framework", "template.yaml": "possible SAM template",
    "docker-compose.yml": "docker-compose services", "docker-compose.yaml": "docker-compose services",
    "compose.yml": "docker-compose services", "compose.yaml": "docker-compose services",
    "app.yaml": "possible App Engine config", "wrangler.toml": "Cloudflare Workers config",
    "supabase/config.toml": "Supabase config",
}


@dataclass
class Candidate:
    category: str
    kind: str
    file: str
    line: int
    detail: str
    flags: list = field(default_factory=list)


def iter_files(root: Path):
    if root.is_file():
        yield root
        return
    this_script = Path(__file__).resolve()
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".terraform")]
        for name in filenames:
            path = Path(dirpath) / name
            if path.resolve() == this_script:
                continue  # its own patterns would match themselves
            if path.suffix.lower() in CODE_EXT | CONFIG_EXT or name in PLATFORM_FILES:
                try:
                    if path.stat().st_size <= MAX_BYTES:
                        yield path
                except OSError:
                    continue


def read_lines(path: Path):
    try:
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return None


def indent_of(line: str) -> int:
    return len(line) - len(line.lstrip(" \t"))


def enclosing_loop(lines, index: int, lookback: int = 20):
    """Return the 1-based line of a loop that likely encloses lines[index], else None."""
    target = indent_of(lines[index])
    floor = target
    for j in range(index - 1, max(-1, index - lookback - 1), -1):
        text = lines[j]
        if not text.strip():
            continue
        ind = indent_of(text)
        if ind < floor:
            if LOOP_LINE.search(text):
                return j + 1
            floor = ind
            if ind == 0:
                break
        elif j == index - 1 and LOOP_LINE.search(text) and ind <= target:
            return j + 1  # same-line style: items.map(x => client.call(...))
    if LOOP_LINE.search(lines[index]) and LLM_CALLS.search(lines[index]):
        return index + 1
    return None


def window(lines, index: int, size: int = NEARBY) -> str:
    return "\n".join(lines[max(0, index - size): index + size + 1])


def call_span(lines, index: int, before: int = 3, limit: int = 60) -> str:
    """The call's own arguments: from its line until parentheses balance, plus a few lines before.

    Config passed through a variable built earlier is missed; the agent must read the source.
    """
    depth, started = 0, False
    end = index
    for j in range(index, min(len(lines), index + limit)):
        for ch in lines[j]:
            if ch == "(":
                depth, started = depth + 1, True
            elif ch == ")":
                depth -= 1
        end = j
        if started and depth <= 0:
            break
    return "\n".join(lines[max(0, index - before): end + 1])


def rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root if root.is_dir() else root.parent).as_posix()
    except ValueError:
        return path.as_posix()


def scan_code(path: Path, lines, root: Path, out: list):
    text = "\n".join(lines)
    providers = [name for name, rx in LLM_IMPORTS.items() if rx.search(text)]
    is_sms_file = bool(SMS_IMPORTS.search(text))
    is_firestore = bool(re.search(r"firestore|cloud_firestore|firebase-admin|firebase/firestore|google\.cloud\.firestore", text, re.I))
    name = rel(path, root)

    trigger_collections = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(("#", "//", "*", "/*")):
            continue

        # LLM call sites
        if providers and LLM_CALLS.search(line) and not (is_sms_file and ".messages.create" in line and "anthropic" not in providers):
            span = call_span(lines, i)
            flags = []
            flags.append("max_tokens in call" if MAX_TOKENS.search(span) else "NO max_tokens in call")
            flags.append("caching in call" if CACHING.search(span) else "no caching in call")
            if BATCH_CALLS.search(window(lines, i)):
                flags.append("batch usage nearby")
            loop = enclosing_loop(lines, i)
            if loop:
                flags.append(f"inside loop at line {loop}")
            out.append(Candidate("llm", "call site", name, i + 1, f"{'/'.join(providers)}: {stripped[:140]}", flags))
        elif providers and BATCH_CALLS.search(line):
            out.append(Candidate("llm", "batch usage", name, i + 1, stripped[:140]))

        for m in MODEL_ID.finditer(line):
            out.append(Candidate("llm", "model id", name, i + 1, m.group(1)))
        if providers:
            for m in OPENROUTER_MODEL.finditer(line):
                out.append(Candidate("llm", "model id", name, i + 1, m.group(1)))

        # Firestore listeners and reads
        if is_firestore and LISTENER.search(line):
            near = window(lines, i, 8)
            flags = ["limit nearby" if LIMIT.search(near) else "NO limit nearby"]
            if not re.search(r"(unsubscribe|cancel\(\)|\.cancel\(|dispose|return\s+\(\)\s*=>|off\()", window(lines, i, 15)):
                flags.append("no detach seen nearby")
            out.append(Candidate("metered", "firestore listener", name, i + 1, stripped[:140], flags))
        elif is_firestore and FS_READ.search(line):
            loop = enclosing_loop(lines, i)
            if loop:
                out.append(Candidate("metered", "firestore read in loop", name, i + 1, stripped[:140], [f"inside loop at line {loop}"]))

        # Function triggers
        tm = TRIGGER.search(line)
        if tm:
            doc_path = next((g for g in (tm.group(5), tm.group(6), tm.group(8), tm.group(9)) if g), "")
            collection = doc_path.strip("/").split("/")[0] if doc_path else ""
            trigger_collections.append((i, collection, doc_path))
        if STORAGE_TRIGGER.search(line):
            out.append(Candidate("runaway", "storage trigger", name, i + 1, stripped[:140], ["check it never writes into the bucket it watches"]))

        if PUBLIC_STORAGE.search(line):
            out.append(Candidate("runaway", "public storage", name, i + 1, stripped[:140]))

        if (is_sms_file and SMS_CALLS.search(line)) or re.search(r"\b(signInWithPhoneNumber|verifyPhoneNumber)\s*\(", line):
            out.append(Candidate("runaway", "sms or otp send", name, i + 1, stripped[:140], ["check per-number, per-IP, and per-country limits"]))

        for label, rx in KEY_PATTERNS:
            if rx.search(line):
                out.append(Candidate("runaway", "possible key in source", name, i + 1, label + " (value not printed)"))

    # Self-triggering: a trigger whose body writes to the collection it watches
    for idx, (i, collection, doc_path) in enumerate(trigger_collections):
        end = trigger_collections[idx + 1][0] if idx + 1 < len(trigger_collections) else min(len(lines), i + 120)
        body = lines[i:end]
        flags = []
        for k, bl in enumerate(body):
            if SELF_WRITE.search(bl):
                flags.append(f"writes to the triggering document at line {i + k + 1}")
            elif collection and WRITE_CALL.search(bl) and re.search(r"['\"`]" + re.escape(collection) + r"(['\"`/])", bl):
                flags.append(f"writes to watched collection '{collection}' at line {i + k + 1}")
            elif collection and re.search(r"collection\s*\(\s*['\"`]" + re.escape(collection) + r"['\"`]", bl):
                if any(WRITE_CALL.search(x) for x in body[k:k + 4]):
                    flags.append(f"writes to watched collection '{collection}' near line {i + k + 1}")
        kind = "self-trigger risk" if flags else "function trigger"
        out.append(Candidate("runaway" if flags else "metered", kind, name, i + 1, f"watches {doc_path or 'unknown path'}", flags))


def scan_terraform(path: Path, lines, root: Path, out: list):
    name = rel(path, root)
    blocks = []
    for i, line in enumerate(lines):
        m = TF_RESOURCE.match(line)
        if m:
            blocks.append((i, m.group(1), m.group(2)))
    for idx, (i, rtype, rname) in enumerate(blocks):
        end = blocks[idx + 1][0] if idx + 1 < len(blocks) else len(lines)
        body = "\n".join(lines[i:end])
        flags = []
        if re.search(r"^\s*(count|for_each)\s*=", body, re.M):
            flags.append("multiplied by count or for_each")
        if rtype == "aws_cloudwatch_log_group" and "retention_in_days" not in body:
            flags.append("NO retention_in_days")
        if re.search(r'type\s*=\s*"(gp2|io1|io2|standard)"', body):
            flags.append("volume type " + re.search(r'type\s*=\s*"(gp2|io1|io2|standard)"', body).group(1))
        if re.search(r"^\s*(iops|throughput|provisioned_throughput)\s*=", body, re.M):
            flags.append("provisioned iops or throughput")
        size = re.search(r'(instance_type|instance_class|machine_type|node_type|size|tier)\s*=\s*"([^"]+)"', body)
        if size:
            flags.append(f"{size.group(1)}={size.group(2)}")
        if PUBLIC_STORAGE.search(body):
            flags.append("public access setting")
        out.append(Candidate("iac", rtype, name, i + 1, f"{rtype}.{rname}" + (f": {TF_WATCH[rtype]}" if rtype in TF_WATCH else ""), flags))


def scan_cloudformation(path: Path, lines, root: Path, out: list):
    text = "\n".join(lines)
    if "AWS::" not in text or not re.search(r"(AWSTemplateFormatVersion|Resources\s*:|\"Resources\")", text):
        return
    name = rel(path, root)
    for i, line in enumerate(lines):
        m = CFN_TYPE.match(line)
        if m:
            out.append(Candidate("iac", m.group(1), name, i + 1, m.group(1)))


def scan_serverless(path: Path, lines, root: Path, out: list):
    name = rel(path, root)
    in_functions = False
    fn_indent = None
    for i, line in enumerate(lines):
        if re.match(r"^functions\s*:", line):
            in_functions, fn_indent = True, None
            continue
        if in_functions:
            if line.strip() and indent_of(line) == 0:
                in_functions = False
                continue
            m = re.match(r"^(\s+)([A-Za-z0-9_\-]+)\s*:\s*$", line)
            if m and (fn_indent is None or len(m.group(1)) == fn_indent):
                fn_indent = len(m.group(1))
                out.append(Candidate("iac", "serverless function", name, i + 1, m.group(2)))
        mm = re.match(r"^\s*(memorySize|timeout|reservedConcurrency|provisionedConcurrency)\s*:\s*(\S+)", line)
        if mm:
            out.append(Candidate("iac", "serverless setting", name, i + 1, f"{mm.group(1)}: {mm.group(2)}"))


def scan(root: Path):
    out: list = []
    platforms = []
    for path in iter_files(root):
        r = rel(path, root)
        for marker, label in PLATFORM_FILES.items():
            if r == marker or r.endswith("/" + marker):
                platforms.append(Candidate("iac", "platform config", r, 1, label))
        lines = read_lines(path)
        if lines is None:
            continue
        suffix = path.suffix.lower()
        if suffix in CODE_EXT:
            scan_code(path, lines, root, out)
        elif suffix == ".tf":
            scan_terraform(path, lines, root, out)
        elif path.name in ("serverless.yml", "serverless.yaml"):
            scan_serverless(path, lines, root, out)
        elif suffix in (".yml", ".yaml", ".json"):
            scan_cloudformation(path, lines, root, out)
            if suffix in (".yml", ".yaml"):
                for i, line in enumerate(lines):
                    if PUBLIC_STORAGE.search(line):
                        out.append(Candidate("runaway", "public storage", r, i + 1, line.strip()[:140]))
                    for label, rx in KEY_PATTERNS:
                        if rx.search(line):
                            out.append(Candidate("runaway", "possible key in source", r, i + 1, label + " (value not printed)"))
    return platforms + out


def find(root: Path, pattern: str):
    rx = re.compile(pattern)
    for path in iter_files(root):
        lines = read_lines(path)
        if not lines:
            continue
        for i, line in enumerate(lines):
            if rx.search(line):
                print(f"{rel(path, root)}:{i + 1}: {line.strip()[:200]}")


SECTIONS = [
    ("llm", "LLM and AI API usage"),
    ("runaway", "Runaway risk candidates"),
    ("metered", "Metered service usage"),
    ("iac", "Infrastructure and platform configs"),
]


def print_text(cands, root: Path):
    print(f"Cost Police scan of {root}")
    print("Every line below is a CANDIDATE. Read the source before reporting anything.\n")
    for key, title in SECTIONS:
        items = [c for c in cands if c.category == key]
        print(f"== {title} ({len(items)}) ==")
        if not items:
            print("  none found\n")
            continue
        models = sorted({c.detail for c in items if c.kind == "model id"})
        for c in items:
            if c.kind == "model id":
                continue
            flags = f"  [{'; '.join(c.flags)}]" if c.flags else ""
            print(f"  {c.file}:{c.line}  {c.kind}: {c.detail}{flags}")
        if models:
            print(f"  model ids referenced: {', '.join(models)}")
        print()
    calls = [c for c in cands if c.kind == "call site"]
    print("== Totals ==")
    print(f"  LLM call sites: {len(calls)}, without max_tokens in the call: {sum('NO max_tokens in call' in c.flags for c in calls)}, "
          f"inside loops: {sum(any(f.startswith('inside loop') for f in c.flags) for c in calls)}")
    print(f"  runaway candidates: {sum(c.category == 'runaway' for c in cands)}, IaC resources and configs: {sum(c.category == 'iac' for c in cands)}")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    ap = argparse.ArgumentParser(description="Inventory where a repository spends money. Results are candidates, not findings.")
    ap.add_argument("path", help="repository root or a single file")
    ap.add_argument("--json", action="store_true", help="print candidates as JSON")
    ap.add_argument("--find", metavar="REGEX", help="print every line matching REGEX with file:line")
    args = ap.parse_args()
    root = Path(args.path).resolve()
    if not root.exists():
        print(f"ERROR: {root} does not exist", file=sys.stderr)
        return 2
    if args.find:
        find(root, args.find)
        return 0
    cands = scan(root)
    if args.json:
        print(json.dumps({"root": str(root), "note": "candidates, not findings", "candidates": [asdict(c) for c in cands]}, indent=2))
    else:
        print_text(cands, root)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
