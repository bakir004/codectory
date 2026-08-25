# Pi Bash guardrail

A project-local Pi extension which blocks `bash` tool calls whose external executables violate `guardrail-policy.json`.

## Enable

Install the pinned parser dependencies once:

```bash
npm ci
```

From this project:

```bash
pi -e ./guardrail/index.ts
```

Or copy/link `index.ts` into `.pi/extensions/` and use `/reload` after the project is trusted.

## Policy

`guardrail-policy.json` supports:

- `mode: "whitelist"`: every external executable must be in `allowed`.
- `mode: "blacklist"`: any executable is permitted unless it is in `blocked`.
- `blocked` always wins, including over `allowed`.

The extension also has a non-removable baseline blocklist for shell/interpreter escape hatches such as `bash`, `sh`, `sudo`, `eval`, `curl`, and `xargs`.

## What it handles

It checks every top-level command segment connected by `&&`, `||`, `;`, `|`, `&`, or newlines. For example, this is denied if `git` is blocked or absent from the whitelist:

```bash
cd /home && git push --force
```

`cd` is treated as a shell builtin and does not bypass checking the following `git` command.

## Intentional limits

Bash has no safe, non-executing command that emits its parsed AST: `bash -n` validates syntax but cannot report every executable; `bash -x` executes the script. This extension uses the official `tree-sitter-bash` grammar to parse a Bash AST instead. It **fails closed** for parse errors and dynamic execution constructs such as command substitution, variable expansion, process substitution, heredocs, and function definitions. It is a Pi hook guardrail, not OS containment. Pair it with a process/filesystem/network sandbox for defense in depth.
