# Tej Stack contributor instructions

- Keep distributable plugin files under `plugins/tej-stack/`.
- Keep every skill focused on one recognizable user goal with clear triggers, boundaries, and output expectations.
- Store detailed examples and background material in a skill's `references/` directory.
- Update the matching file under `evals/` whenever skill behavior changes.
- Keep the Codex and Claude manifests aligned and use the version in `VERSION`.
- Run `python scripts/validate.py` before committing.
- Test installer changes on both PowerShell and a POSIX shell.
- Use short, direct commit messages that describe the shipped outcome.
