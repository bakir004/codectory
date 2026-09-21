# Codectory

Codectory is a local, observable software factory for running repeatable AI developer workflows (ADWs). Deterministic Python workflows coordinate specialized coding agents through planning, research, implementation, quality checks, review, and documentation while typed handoffs, bounded retries, repository permissions, and SQLite traces keep each run inspectable.

This repository is an extension of [IndyDevDan's Super Simple Software Factory](https://github.com/disler/super-simple-software-factory), not a from-scratch implementation. See [Attribution](#attribution) for the project boundary and original work.

## What this project adds

Codectory retains the upstream factory's core ideas—code-owned orchestration, typed agent handoffs, deterministic gates, and local observability—and extends them with:

- **Project-aware workflows:** `projects.yaml` maps each project to its guides and deterministic checks. Relevant guides are injected into agent context for every run.
- **Conditional research:** `adw_plan_research_build_sdlc.py` allows the planner to request current external research before refining its plan.
- **Safe continuation:** interrupted runs can resume only when the workflow, prompt, project scope, and roster match the original execution.
- **Clarification support:** planners can pause for structured engineer answers before committing to a plan.
- **Additional workflow composition:** a build-quality-review chain combines implementation, deterministic verification, repair, review, and revision loops.
- **Command guardrails:** a parser-based Pi extension applies configurable policy to agent-issued shell commands.

## How it works

```text
Engineer request
      │
      ▼
Python ADW ──► Planner ──► optional Research ──► Builder
      │                                            │
      │                                            ▼
      │                                    deterministic checks
      │                                            │
      │                                            ▼
      └──── SQLite trace ◄── Documenter ◄── Reviewer/revision
```

Python owns sequencing, retries, acceptance, and process state. Agents handle tasks that require reading and deciding. Information crosses phase boundaries through Pydantic envelopes rather than unstructured prose. Known checks such as compilation, linting, tests, and builds run as ordinary subprocesses rather than being delegated to an agent.

Each run records phases, events, envelopes, gate results, agent sessions, and processes in `adws/adw_data/codectory.db`. Raw session output remains under `adws/adw_data/sessions/` for debugging and recovery.

## Workflow examples

| Workflow | Chain | Use case |
|---|---|---|
| `adw_scout.py` | scout | Read-only repository investigation |
| `adw_plan_build_test.py` | plan → build → test/fix → commit | A scoped implementation with deterministic tests |
| `adw_build_quality_review.py` | build → quality/fix → review/revise | Implement and verify a well-understood request |
| `adw_simple_sdlc.py` | plan → build → quality → review → document | Full software-development lifecycle |
| `adw_plan_research_build_sdlc.py` | plan → optional research → build generations → quality → review → document | Work that may depend on current external documentation |

All workflow entry points are under `adws/`.

## Repository structure

```text
.codectory/                    Canonical factory source, templates, and guides
adws/                          Runnable workflow installation
  adw_*.py                     Workflow entry points
  adw_modules/                 Orchestration, gates, tracing, and permissions
  adw_codectory_config/        Agent roster and runtime configuration
  adw_data/                    Prompts, guardrails, traces, and session data
projects.yaml                  Project guides and deterministic quality checks
justfile                       Workflow and observability commands
```

## Requirements

- Python 3.11+
- [uv](https://docs.astral.sh/uv/)
- [Pi coding agent](https://github.com/badlogic/pi-mono)
- [just](https://github.com/casey/just)
- SQLite CLI for trace queries
- Bun and Docker for the visualizer and Campus Compass demo
- API credentials for the model providers configured in the selected roster

## Getting started

### 1. Configure the environment

```bash
cp .env.sample .env
```

Add the API key required by the models in `adws/adw_codectory_config/codectory.config.yaml`. Model availability changes over time, so update the roster to models available through your Pi configuration when necessary.

### 2. Run a read-only scout

```bash
uv run adws/adw_scout.py \
  "Explain how workflow continuation is validated" \
  --projects adws
```

### 3. Run an end-to-end workflow

```bash
uv run adws/adw_simple_sdlc.py \
  "Add the requested feature and cover it with tests" \
  --projects web
```

The prompt can be inline text or a path to a request file. Every run must declare the projects it may modify so Codectory can load the correct guides and checks.

### 4. Inspect runs

```bash
just sessions
just phases <adw_id>
just tail <adw_id>
just procs <adw_id>
```

Launch the visualizer with:

```bash
just obs
```

### Continue an interrupted run

Use the original prompt, project scope, roster, and run ID:

```bash
uv run adws/adw_simple_sdlc.py \
  "Add the requested feature and cover it with tests" \
  --projects web \
  --adw-id <adw_id> \
  --continue "Keep the partial work and address the reported failure"
```

Codectory rejects continuation when the run identity no longer matches, preventing an old agent session from being resumed against incompatible inputs.


## Design principles

- **Agent proposes, code disposes.** Agents make judgments; deterministic code controls execution and acceptance.
- **Typed handoffs.** Every phase returns a concrete envelope that can be parsed and gated.
- **Bounded correction.** Parse, quality, and review failures return to the appropriate agent without creating unbounded loops.
- **Enforced write boundaries.** Agent write permissions are checked against repository changes after each call.
- **Observable by default.** Console output, tool calls, phase status, token usage, and gate results are persisted locally.
- **Explicit acceptance.** A completed phase or test command is not automatically the same as an accepted run.

## Current limitations

- Workflows operate on the current working tree; there is no built-in branch-per-run sandbox or merge stage.
- Provider credentials are discovered when an agent is launched rather than fully validated at startup.
- The supported coding-agent runtime is Pi; other runtime values may be schema-valid without being implemented.
- The demo's role selection is not an authentication or authorization system.
- Because this repository has independent history and renamed paths, upstream updates require semantic reconciliation rather than a normal Git merge.

## Attribution

Codectory is based on [Super Simple Software Factory](https://github.com/disler/super-simple-software-factory) by IndyDevDan. The upstream project supplied the foundational ADW architecture, including Python-controlled orchestration, typed envelopes, gates, agent permissions, deterministic quality phases, SQLite tracing, and the visualizer.

The Codectory-specific work in this repository focuses on repackaging and extending that foundation with project guide injection, conditional research, workflow continuation and clarification, additional workflow chains, command guardrails, and the Campus Compass integration.

The upstream project is distributed under the MIT License. Its copyright and license notice must be retained when redistributing substantial portions of the original software.
