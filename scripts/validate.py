from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PLUGIN = ROOT / "plugins" / "tej-stack"
SEMVER = re.compile(r"^\d+\.\d+\.\d+$")
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def fail(message: str) -> None:
    print(f"ERROR: {message}", file=sys.stderr)
    raise SystemExit(1)


def load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        fail(f"invalid JSON at {path.relative_to(ROOT)}: {error}")


def frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if len(lines) < 3 or lines[0] != "---":
        fail(f"missing YAML frontmatter at {path.relative_to(ROOT)}")
    values: dict[str, str] = {}
    for line in lines[1:]:
        if line == "---":
            return values
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            values[key.strip()] = value.strip().strip('"')
    fail(f"unclosed YAML frontmatter at {path.relative_to(ROOT)}")


def validate_plugin() -> None:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if not SEMVER.fullmatch(version):
        fail("VERSION must use strict semantic versioning")

    for manifest_path in (
        PLUGIN / ".codex-plugin" / "plugin.json",
        PLUGIN / ".claude-plugin" / "plugin.json",
    ):
        manifest = load_json(manifest_path)
        if manifest.get("name") != "tej-stack":
            fail(f"wrong plugin name in {manifest_path.relative_to(ROOT)}")
        if manifest.get("version") != version:
            fail(f"version mismatch in {manifest_path.relative_to(ROOT)}")
        if not manifest.get("description") or not manifest.get("author", {}).get("name"):
            fail(f"incomplete metadata in {manifest_path.relative_to(ROOT)}")
        if manifest.get("skills") != "./skills/":
            fail(f"wrong skills path in {manifest_path.relative_to(ROOT)}")

    codex_market = load_json(ROOT / ".agents" / "plugins" / "marketplace.json")
    claude_market = load_json(ROOT / ".claude-plugin" / "marketplace.json")
    if codex_market.get("name") != "tej-stack" or claude_market.get("name") != "tej-stack":
        fail("marketplace names must be tej-stack")
    codex_entry = codex_market.get("plugins", [{}])[0]
    claude_entry = claude_market.get("plugins", [{}])[0]
    if codex_entry.get("source", {}).get("path") != "./plugins/tej-stack":
        fail("Codex marketplace path must target ./plugins/tej-stack")
    if claude_entry.get("source") != "./plugins/tej-stack":
        fail("Claude marketplace path must target ./plugins/tej-stack")

    for entry in claude_market.get("plugins", [])[1:]:
        validate_hook_plugin(entry, version)


def validate_hook_plugin(entry: dict, version: str) -> None:
    """A Claude-only plugin that ships hooks instead of skills (speed-dial)."""
    name = entry.get("name", "")
    if not SKILL_NAME.fullmatch(name):
        fail(f"invalid plugin name in Claude marketplace: {name!r}")
    if entry.get("source") != f"./plugins/{name}" or not entry.get("description"):
        fail(f"Claude marketplace entry for {name} must target ./plugins/{name} and have a description")
    plugin = ROOT / "plugins" / name
    manifest_path = plugin / ".claude-plugin" / "plugin.json"
    manifest = load_json(manifest_path)
    if manifest.get("name") != name:
        fail(f"wrong plugin name in {manifest_path.relative_to(ROOT)}")
    if manifest.get("version") != version:
        fail(f"version mismatch in {manifest_path.relative_to(ROOT)}")
    if not manifest.get("description") or not manifest.get("author", {}).get("name"):
        fail(f"incomplete metadata in {manifest_path.relative_to(ROOT)}")

    hooks_path = plugin / "hooks" / "hooks.json"
    hooks = load_json(hooks_path).get("hooks")
    if not isinstance(hooks, dict) or not hooks:
        fail(f"no hooks declared in {hooks_path.relative_to(ROOT)}")
    for groups in hooks.values():
        for group in groups:
            for hook in group.get("hooks", []):
                for relative in re.findall(r"\$\{CLAUDE_PLUGIN_ROOT\}/([^\"'\s]+)", hook.get("command", "")):
                    if not (plugin / relative).is_file():
                        fail(f"hook in {name} points at a missing file: {relative}")


def validate_skills() -> int:
    skills_dir = PLUGIN / "skills"
    skill_dirs = sorted(path for path in skills_dir.iterdir() if path.is_dir())
    if not skill_dirs:
        fail("no skills found")

    for skill_dir in skill_dirs:
        if not SKILL_NAME.fullmatch(skill_dir.name):
            fail(f"invalid skill folder name: {skill_dir.name}")
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.is_file():
            fail(f"missing SKILL.md for {skill_dir.name}")
        metadata = frontmatter(skill_file)
        if metadata.get("name") != skill_dir.name:
            fail(f"skill name does not match folder: {skill_dir.name}")
        if not metadata.get("description"):
            fail(f"missing skill description: {skill_dir.name}")
        text = skill_file.read_text(encoding="utf-8")
        if "[TODO" in text or "PLACEHOLDER" in text:
            fail(f"placeholder found in {skill_file.relative_to(ROOT)}")
        for relative in re.findall(r"\]\((?!https?://|#)([^)]+)\)", text):
            target = (skill_file.parent / relative).resolve()
            if not target.is_file() or PLUGIN.resolve() not in target.parents:
                fail(f"broken or escaping link in {skill_file.relative_to(ROOT)}: {relative}")

        openai_yaml = skill_dir / "agents" / "openai.yaml"
        if not openai_yaml.is_file():
            fail(f"missing agents/openai.yaml for {skill_dir.name}")
        icon_match = re.search(r'^\s*icon_(?:small|large):\s*"([^"]+)"', openai_yaml.read_text(encoding="utf-8"), re.MULTILINE)
        if icon_match and not (skill_dir / icon_match.group(1)).resolve().is_file():
            fail(f"missing icon for {skill_dir.name}: {icon_match.group(1)}")

        eval_file = ROOT / "evals" / f"{skill_dir.name}.md"
        if not eval_file.is_file():
            fail(f"missing evaluation file for {skill_dir.name}")

    return len(skill_dirs)


def main() -> None:
    validate_plugin()
    count = validate_skills()
    hook_plugins = len(load_json(ROOT / ".claude-plugin" / "marketplace.json").get("plugins", [])) - 1
    print(f"Tej Stack is valid: {count} skills, {2 + hook_plugins} plugin manifests, 2 marketplaces")


if __name__ == "__main__":
    main()
