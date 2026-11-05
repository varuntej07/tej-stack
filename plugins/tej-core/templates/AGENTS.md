# Agent instructions

This repo uses the tej-core harness. `CLAUDE.md` is the router: read it first, then the
`.context/1-docs/ARCH-*.md` doc for every path you touch and every file in `.claude/rules/`.

Explain things the tej-core way: open as a first-person, out-loud story to a cofounder (the pain,
how it works now, what you want to do, why it should work), then every diagram and section the
rules require, in full. A direct factual question still gets the answer first.

Plans and bug fixes follow the tej-core `feature` and `bugfix` skills: spec in `.context/2-specs/`,
stop for approval before code, design for the whole class including the cases where a fix must
not fire, and call something fixed only when the symptom is observed gone.
