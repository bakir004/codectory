# Pi Bash guardrail

A project-local Pi extension that blocks `curl` Bash invocations and permits every other command.

## Enable

Install the pinned parser dependencies once:

```bash
npm ci
```

From this project:

```bash
pi -e ./guardrail/index.ts
```

## Policy

`guardrail-policy.json` has exactly two arrays: `whitelist` and `blacklist`. They are validated as disjoint; an executable cannot appear in both. An empty `whitelist` permits every executable; a non-empty whitelist permits only its entries. An empty `blacklist` blocks nothing. The active blacklist contains only `curl`, so the extension blocks `curl`, including a path-qualified invocation such as `/usr/bin/curl`, and allows everything else.
