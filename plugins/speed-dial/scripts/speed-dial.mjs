#!/usr/bin/env node
// speed-dial: a Claude Code UserPromptSubmit hook.
//
// A short prompt is put to Jev (TypeSafe's jev-latest) as one typed choice over
// the entries in speed-dial.json. A confident match runs that entry's command in
// a new terminal window and blocks the prompt, so the model never spins up.
// Everything else passes through untouched.
//
// Jev only selects. It sees each entry's id and description, never the command,
// and it cannot name anything this script did not offer it.
//
// Fail-open is the one rule that matters here: every error path exits 0 with
// nothing on stdout, so a missing key, a slow network or a broken file can never
// swallow a prompt. The only prompts blocked are ones that actually ran something,
// or `speed-dial trust`.

import { spawn } from "node:child_process";
import { createHash } from "node:crypto";
import { chmodSync, existsSync, mkdirSync, openSync, readFileSync, statSync, writeFileSync } from "node:fs";
import { homedir, platform, tmpdir } from "node:os";
import { basename, delimiter, dirname, isAbsolute, join, resolve } from "node:path";

const JEV_URL = "https://api.typesafe.ai/v1/systemone";
const JEV_MODEL = "jev-latest";
// The hook itself is killed at 3s. Jev answers in ~150ms warm, so this is
// generous without letting a stalled request eat the whole hook budget.
const JEV_TIMEOUT_MS = 1500;
// Both answers must clear this. Running the wrong command is far costlier than
// falling through to Claude, which only costs the usual minute.
const GATE = 0.85;
// Commands are short. A long prompt is a question for Claude and should not
// pay the round trip at all.
const MAX_WORDS = 12;
// Jev choices cap at 255 options; one is reserved for "none".
const MAX_ENTRIES = 254;
const ENTRY_ID = /^[a-z0-9][a-z0-9_-]{0,63}$/;
const TRUST_PROMPT = "speed-dial trust";

const STATE_DIR = join(homedir(), ".claude", "speed-dial");
const STATE_FILE = join(STATE_DIR, "state.json");
const USER_FILE = join(homedir(), ".claude", "speed-dial.json");

main().catch(() => process.exit(0));

async function main() {
  const input = JSON.parse(await readStdin());
  const prompt = String(input.prompt ?? "").trim();
  const cwd = typeof input.cwd === "string" && input.cwd ? input.cwd : process.cwd();
  const root = repoRoot(cwd);
  const projectFile = join(root, ".claude", "speed-dial.json");

  if (normalized(prompt) === TRUST_PROMPT) {
    return trust(projectFile);
  }

  const state = loadState();
  const notices = [];
  const entries = new Map();

  // User file first so a project entry with the same id replaces it.
  for (const entry of loadEntries(USER_FILE, root)) entries.set(entry.id, entry);

  if (existsSync(projectFile)) {
    const hash = sha256(projectFile);
    if (state.trusted[projectFile] === hash) {
      for (const entry of loadEntries(projectFile, root)) entries.set(entry.id, entry);
    } else if (state.notified[projectFile] !== hash) {
      // Say it once per version of the file, never on every prompt.
      state.notified[projectFile] = hash;
      saveState(state);
      notices.push(
        `speed-dial: ${projectFile} is not trusted yet, so its entries are off. ` +
          `Read it, then type "${TRUST_PROMPT}".`,
      );
    }
  }

  const passThrough = () => {
    if (notices.length) emit({ systemMessage: notices.join("\n") });
    process.exit(0);
  };

  const key = process.env.TYPESAFE_API_KEY;
  const words = prompt.split(/\s+/).filter(Boolean).length;
  if (!key || entries.size === 0 || words === 0 || words > MAX_WORDS) return passThrough();
  if (prompt.startsWith("/") || prompt.startsWith("!")) return passThrough();

  const offered = [...entries.values()].slice(0, MAX_ENTRIES);
  const answers = await decide(key, prompt, basename(root), offered);
  if (!answers) return passThrough();

  const intent = answers.intent ?? {};
  const task = answers.task ?? {};
  if (intent.choice !== "run_command" || !(Number(intent.confidence) >= GATE)) return passThrough();
  if (!(Number(task.confidence) >= GATE)) return passThrough();
  const entry = entries.get(task.choice);
  if (!entry) return passThrough();

  // From here the decision WAS a command, so failing to run it has to be loud,
  // never a quiet fall-through that hands Claude a prompt the user thinks ran.
  const command = commandFor(entry);
  if (!command) {
    return block(`speed-dial: ${entry.id} has no command for ${platform()}.`);
  }
  if (!existsSync(entry.cwd) || !statSync(entry.cwd).isDirectory()) {
    return block(`speed-dial: ${entry.id} did not run, its folder does not exist: ${entry.cwd}`);
  }
  try {
    const where = launch(entry, command);
    const confidence = Math.min(Number(intent.confidence), Number(task.confidence)).toFixed(2);
    const waiting = entry.confirm ? ", waiting for Enter" : "";
    block(`speed-dial: ${entry.id} (${confidence}) ${where}${waiting}\n> ${command}`);
  } catch (error) {
    block(`speed-dial: ${entry.id} matched but could not start: ${error?.message ?? error}`);
  }
}

// ---------------------------------------------------------------------------
// Registry

function loadEntries(file, root) {
  let parsed;
  try {
    parsed = JSON.parse(readFileSync(file, "utf8"));
  } catch {
    return [];
  }
  const list = Array.isArray(parsed?.entries) ? parsed.entries : [];
  const out = [];
  for (const raw of list) {
    if (!raw || typeof raw !== "object") continue;
    if (typeof raw.id !== "string" || !ENTRY_ID.test(raw.id)) continue;
    if (typeof raw.description !== "string" || !raw.description.trim()) continue;
    if (typeof raw.command !== "string" && (typeof raw.command !== "object" || !raw.command)) continue;
    const dir = typeof raw.cwd === "string" && raw.cwd ? raw.cwd : ".";
    out.push({
      id: raw.id,
      description: raw.description.trim(),
      command: raw.command,
      // Relative folders resolve against the repo the prompt came from, which
      // is what lets one user-level entry like "npm test" follow you around.
      cwd: isAbsolute(dir) ? dir : resolve(root, dir),
      confirm: raw.confirm === true,
    });
  }
  return out;
}

/** A string runs everywhere; an object picks { windows, macos, linux }. */
function commandFor(entry) {
  if (typeof entry.command === "string") return entry.command.trim() || null;
  const key = { win32: "windows", darwin: "macos" }[platform()] ?? "linux";
  const value = entry.command[key];
  return typeof value === "string" && value.trim() ? value.trim() : null;
}

function repoRoot(start) {
  let dir = resolve(start);
  for (;;) {
    if (existsSync(join(dir, ".git"))) return dir;
    const parent = dirname(dir);
    if (parent === dir) return resolve(start);
    dir = parent;
  }
}

// ---------------------------------------------------------------------------
// Trust

function trust(projectFile) {
  if (!existsSync(projectFile)) {
    return block(`speed-dial: there is no ${projectFile} to trust.`);
  }
  const state = loadState();
  state.trusted[projectFile] = sha256(projectFile);
  saveState(state);
  const count = loadEntries(projectFile, dirname(dirname(projectFile))).length;
  block(
    `speed-dial: trusted ${count} ${count === 1 ? "entry" : "entries"} in ${projectFile}. ` +
      `Editing the file turns them off again until you re-trust it.`,
  );
}

function loadState() {
  try {
    const parsed = JSON.parse(readFileSync(STATE_FILE, "utf8"));
    return { trusted: parsed.trusted ?? {}, notified: parsed.notified ?? {} };
  } catch {
    return { trusted: {}, notified: {} };
  }
}

function saveState(state) {
  mkdirSync(STATE_DIR, { recursive: true });
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2));
}

function sha256(file) {
  return createHash("sha256").update(readFileSync(file)).digest("hex");
}

// ---------------------------------------------------------------------------
// The decision

async function decide(key, utterance, repo, entries) {
  const taskCriteria = {};
  for (const entry of entries) taskCriteria[entry.id] = entry.description;
  taskCriteria.none = "None of these commands is what the user is asking for.";

  const body = {
    model: JEV_MODEL,
    state: { utterance, repo },
    questions: {
      intent: {
        type: "choice",
        instructions:
          "The user typed this into an AI coding assistant. Decide whether it is a request to run one of their saved project commands right now, or anything else for the assistant: a question, a code change, a request with extra conditions, or a request about a command rather than to run it.",
        criteria: {
          run_command: "A plain request to run a saved command now, with nothing else asked.",
          ask_claude: "Anything else, including questions about a command or a command with extra steps or changes.",
        },
      },
      task: {
        type: "choice",
        instructions: "If this is a request to run a saved command, which one?",
        criteria: taskCriteria,
      },
    },
  };

  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), JEV_TIMEOUT_MS);
  try {
    const response = await fetch(JEV_URL, {
      method: "POST",
      headers: { Authorization: `Bearer ${key}`, "Content-Type": "application/json" },
      body: JSON.stringify(body),
      signal: controller.signal,
    });
    if (!response.ok) return null;
    const parsed = await response.json();
    return parsed && typeof parsed.answers === "object" ? parsed.answers : null;
  } catch {
    return null;
  } finally {
    clearTimeout(timer);
  }
}

// ---------------------------------------------------------------------------
// Launching. The one platform seam. Each branch writes the command into a
// script file and opens a terminal on that file, so no command ever has to
// survive being quoted through a second shell.

function launch(entry, command) {
  const dir = join(tmpdir(), "speed-dial");
  mkdirSync(dir, { recursive: true });
  const title = `speed-dial: ${entry.id}`;

  if (platform() === "win32") {
    const script = join(dir, `${entry.id}.ps1`);
    const lines = [
      `$Host.UI.RawUI.WindowTitle = ${psQuote(title)}`,
      `Set-Location -LiteralPath ${psQuote(entry.cwd)}`,
      `Write-Host ${psQuote(`> ${command}`)} -ForegroundColor Cyan`,
    ];
    if (entry.confirm) lines.push(`Read-Host 'Press Enter to run, or close this window to cancel' | Out-Null`);
    lines.push(command);
    // BOM so Windows PowerShell 5.1 reads non-ASCII paths as UTF-8.
    writeFileSync(script, "﻿" + lines.join("\r\n") + "\r\n");
    const shell = onPath("pwsh.exe") ? "pwsh.exe" : "powershell.exe";
    // `start` needs its first quoted argument to be a title, which Node's own
    // argument quoting cannot express, hence the verbatim command line.
    const child = spawn(
      "cmd.exe",
      [`/d /s /c start "${title}" ${shell} -NoExit -NoProfile -ExecutionPolicy Bypass -File "${script}"`],
      { cwd: entry.cwd, detached: true, stdio: "ignore", windowsVerbatimArguments: true, windowsHide: true },
    );
    child.unref();
    return "is running in a new window";
  }

  const script = join(dir, `${entry.id}.${platform() === "darwin" ? "command" : "sh"}`);
  const lines = [
    "#!/usr/bin/env bash",
    `printf '\\033]0;%s\\007' ${shQuote(title)}`,
    `cd ${shQuote(entry.cwd)} || exit 1`,
    `printf '\\033[36m%s\\033[0m\\n' ${shQuote(`> ${command}`)}`,
  ];
  if (entry.confirm) lines.push(`read -r -p 'Press Enter to run, or close this window to cancel ' _`);
  lines.push(command, `echo`, `echo "speed-dial: finished with exit code $?"`, `exec "\${SHELL:-bash}"`);
  writeFileSync(script, lines.join("\n") + "\n");
  chmodSync(script, 0o755);

  if (platform() === "darwin") {
    // Terminal runs an executable .command file in a new window.
    spawn("open", ["-a", "Terminal", script], { detached: true, stdio: "ignore" }).unref();
    return "is running in a new Terminal window";
  }

  if (onPath("x-terminal-emulator")) {
    spawn("x-terminal-emulator", ["-e", "bash", script], { detached: true, stdio: "ignore" }).unref();
    return "is running in a new terminal window";
  }
  // No terminal to open (a server, WSL without a desktop): run it anyway and
  // say where the output went.
  const log = join(STATE_DIR, "last.log");
  mkdirSync(STATE_DIR, { recursive: true });
  const out = openSync(log, "w");
  spawn("bash", [script], { cwd: entry.cwd, detached: true, stdio: ["ignore", out, out] }).unref();
  return `is running in the background, output in ${log}`;
}

function onPath(name) {
  for (const dir of (process.env.PATH ?? "").split(delimiter)) {
    if (dir && existsSync(join(dir, name))) return true;
  }
  return false;
}

function psQuote(value) {
  return `'${String(value).replace(/'/g, "''")}'`;
}

function shQuote(value) {
  return `'${String(value).replace(/'/g, `'\\''`)}'`;
}

// ---------------------------------------------------------------------------
// Hook I/O

function block(reason) {
  emit({ decision: "block", reason });
  process.exit(0);
}

function emit(object) {
  process.stdout.write(JSON.stringify(object));
}

function normalized(prompt) {
  return prompt.toLowerCase().replace(/[.!\s]+$/, "").replace(/\s+/g, " ");
}

function readStdin() {
  return new Promise((resolvePromise, reject) => {
    let data = "";
    process.stdin.setEncoding("utf8");
    process.stdin.on("data", (chunk) => (data += chunk));
    process.stdin.on("end", () => resolvePromise(data));
    process.stdin.on("error", reject);
  });
}
