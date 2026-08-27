# Plan: safely continue interrupted Codectory workflows

## Goal

Add an explicit continuation mode that reopens an existing run at its first incomplete phase while treating successful phases as immutable checkpoints. A normal `--adw-id` invocation must retain its current pin/join behavior for chaining workflows; continuation is opt-in and must never silently reinterpret an unrelated session. The continue flag accepts a required instruction string for the resumed agent, for example `--continue "Use the existing partial work and finish the migration without changing the API."`; this is a new turn delivered only to the agent phase being resumed, not a replacement for the workflow's original request.

## Implementation approach

### 1. Define typed continuation/checkpoint contracts

- Extend `adws/adw_modules/data_types.py` with concrete models for session launch/continuation metadata and deterministic phase results (for example, a launch options object, workflow identity/fingerprint metadata, and a typed code-phase call/result contract). This avoids pushing a fifth argument into every `main()`/session helper and keeps the four-parameter rule intact.
- Represent enough immutable identity to reject unsafe continuation before any phase or agent starts: `adw_id`, workflow script/name and version/fingerprint, the stored original request hash, declared project scope, and configuration/roster identity. Preserve the original run baseline needed by changed-project quality and documentation rather than recomputing it from a repository that earlier phases may already have committed. The continuation instruction is intentionally excluded from compatibility identity: it is appended as a new agent turn and may differ on each continuation attempt without changing the original request.
- Keep agent envelopes typed exactly as they are; this feature does not change output envelopes, prompts, gates, agents, or models.
- Mirror the reusable type changes into `.codectory/templates/adws/adw_modules/data_types.py`, because those templates are the factory source stamped into downstream repositories.

### 2. Add reusable checkpoint and compatibility logic

- Add a focused module such as `adws/adw_modules/checkpoints.py` and its template counterpart under `.codectory/templates/adws/adw_modules/`.
- On an ordinary new run, create a per-workflow checkpoint manifest under that run’s existing session directory. Store workflow compatibility metadata, the original baseline, the ordered phase definitions encountered, and typed results required to reconstruct control flow. Write updates atomically so a killed process cannot leave partially parsed JSON.
- On `--continue`, require an explicitly supplied, already-existing `adw_id` and checkpoint manifest. Compare the current workflow/request/projects/config fingerprint with the stored metadata and fail with a clear message before `session_start`, process registration, phase mutation, or agent invocation when they differ. Also reject a session created by another/chained workflow or an older session with no safe checkpoint metadata instead of guessing.
- Determine phase state by stable workflow-local order plus the full `PhaseParams` identity, not merely by a repeated phase name. Successful phases remain immutable. A failed phase and a stale `running` phase are incomplete and eligible to run again in place; phases after the first incomplete point remain pending. Reject phase-order/definition drift so edited workflows cannot resume against an incompatible trace.
- Before reclaiming a `running` session, inspect its recorded process rows and verify whether a matching ADW process is actually alive. Refuse concurrent continuation if it is; if rows are stale, close them and mark the interrupted phase recoverable before proceeding. Put process/PID validation in reusable module code, not shell output parsing or ADW scripts.
- Persist and restore typed results needed by downstream Python control flow. Agent phases should load the latest valid envelope for their exact completed phase from the trace and validate it against the requested `output_type` without spawning an agent or rerunning gates. Deterministic phases should execute through a reusable typed code/checkpoint primitive that can return a stored `QualityResult`, `ChangeSet`, commit result, or other declared result on continuation without repeating side effects.
- Make checkpoint finalization and trace status updates occur in a consistent order. Journal deterministic side-effect phases so interruption after the action but before final phase bookkeeping can be reconciled instead of blindly repeating a git commit. A restored checkpoint must never truncate or overwrite existing handoff artifacts, quality logs, envelopes, raw agent output, commits, or `agent_map.json`.

### 3. Integrate continuation with the runner and tracer

- Update `adws/adw_modules/tracer.py` with narrowly scoped queries for session metadata, ordered phases, exact valid envelopes, live/stale processes, and reopening an incomplete phase. Use additive schema/migrations only if checkpoint state must be queryable; do not alter visualizer behavior.
- Update `adws/adw_modules/session.py` so launch options distinguish three cases: fresh/minted run, existing-session join/chaining without continuation, and strict continuation. Validate compatibility and liveness before changing the session to `running`; preserve the original request/start baseline and then register the new ADW process. Keep signal finalization behavior, but ensure interrupted phase state remains resumable.
- Update `adws/adw_modules/runner.py` so `Run` has an explicit continuation/checkpoint controller. When phases are encountered in deterministic order:
  - append restored successful phases to the run’s phase accounting without inserting duplicate rows/events or changing their sequence/status;
  - restore completed agent/code results rather than execute their bodies;
  - reopen the first failed/stale-running phase with the same stable phase identity and a new execution attempt, clearing stale error/end state while retaining historical events;
  - allocate later phase sequence numbers deterministically and execute normally;
  - reject any attempt to skip over an incomplete phase or diverge from the stored phase definition.
- Ensure `run.finish()` evaluates both restored and newly executed phases, keeps prior token/cost totals, produces one consistent final session status/exit code, and treats a fully completed continued run as a safe no-op success rather than rerunning it.
- Mirror all runner/session/tracer/checkpoint changes into `.codectory/templates/adws/adw_modules/`. Merge with the current project-scope/guidance work already present in the live `adws/` files; do not replace those uncommitted changes with older template copies.

### 4. Wire every workflow CLI and phase result

- Update every live `adws/adw_*.py` entry point to accept `--continue INSTRUCTION` (a required non-empty string value) and require it to be paired with `--adw-id`. The positional workflow prompt remains the original request and must match the stored request; the continue instruction is separate, may be supplied inline or resolved from a file using the same safe prompt-file convention, and is sent only to the resumed agent phase. Bundle config, projects, adw id, and continuation state in the concrete launch options type rather than creating five-argument functions. Keep `REQUIRED_AGENTS` validation before opening a run and keep every workflow ending through `run.finish()`.
- Update each ADW’s `Usage:` docstring to show continuation and clarify its `Phases:` line where needed. `--adw-id` alone remains the existing cross-workflow join/pin mechanism; `--adw-id X --continue` means resume this exact workflow.
- Route every deterministic phase action through the typed checkpoint primitive, including quality/test runs, change capture, worktree fingerprints that decide whether rechecks run, and git commits. Restore their typed values so bounded quality/fix and review/revision loops make the same branching decisions and phase names as the original execution.
- Ensure request/log-only phases are replay-safe, completed agent calls return restored envelopes, and failed agent phases reuse the existing coding-agent session only when the phase itself is resumed. When that resumed phase reaches `ph.call()`, append the continuation instruction as a clearly delimited new-turn directive after the preserved original task/context; do not rewrite stored prompts, replace `AgentCall.prompt`, resend completed prompts, or rerun completed gates. Consume the instruction exactly once, record its hash and target phase in checkpoint/trace metadata, and ensure later agent phases receive only their normal typed handoff unless the workflow is interrupted and explicitly continued again.
- Pay special attention to `adw_build_test.py`, `adw_plan_build_test.py`, `adw_plan_build_test_quality.py`, `adw_build_quality_review.py`, `adw_build_review.py`, `adw_simple_sdlc.py`, and `adw_plan_research_build_sdlc.py`: their dynamic loops and acceptance variables must be reconstructed from checkpoints so continuation chooses the exact next test/fix/review/revision/commit phase.
- Apply equivalent CLI and sequencing changes to every corresponding starter under `.codectory/templates/adws/adw_*.py`. Update `.codectory/scripts/make_adw.py` so newly generated workflows use the same launch-options/`--continue` pattern rather than generating workflows that cannot resume.

### 5. Document operator behavior and commands

- Update `.codectory/cookbooks/codectory_overview.md` and `.codectory/cookbooks/run_adw.md` with direct examples such as `uv run adws/adw_simple_sdlc.py "<original prompt>" --projects adws --adw-id a1b2c3d4 --continue "Use the partial implementation and address the reported failure"`, the difference between joining and continuing, instruction delivery semantics, first-incomplete semantics, no-op behavior for an already complete run, active-process refusal, and compatibility rejection rules.
- Update `.codectory/cookbooks/create_adw.md`, `.codectory/cookbooks/update_adw.md`, and `.codectory/cookbooks/update_modules.md` so custom workflows checkpoint deterministic results, preserve deterministic phase identity/order, expose the standard continuation CLI, and keep side effects inside reusable code-phase execution rather than raw replayable bodies. Update `.codectory/cookbooks/install.md` if the stamped file/module inventory changes.
- Add a generic continuation recipe to both `justfile` and `.codectory/templates/justfile` (with a concise usage comment) that passes workflow, prompt/options, `--adw-id`, and `--continue` without hiding required `--projects`. Existing recipes should continue accepting raw `--continue` arguments.
- Do not update the visualizer beyond any schema-tolerant backend necessity; visualizer redesign is explicitly out of scope.

### 6. Add focused factory regressions

- Add `.codectory/tests/test_continue.py` (or split narrowly if clearer), importing the canonical template modules as existing factory tests do and using temporary session directories/SQLite databases/repositories.
- Cover at least:
  - a successful prefix plus a failed phase resumes at that failed phase, with earlier call counters/side effects unchanged;
  - a stale `running` phase is reclaimed, while a genuinely live matching process causes a safe refusal;
  - valid agent envelopes and deterministic results are restored with their concrete types and no agent/gate/action rerun;
  - completed artifacts, envelope rows/files, quality logs, commits, and handoff files remain byte-for-byte present;
  - loop results restore the same next phase name/order and repeated continuation does not create duplicate successful phases;
  - failed phases rerun, then allow subsequent phases to proceed in stable sequence;
  - an already successful workflow continues as a no-op success;
  - missing `--adw-id`, an empty/missing continue instruction, unknown ids, legacy/no-manifest sessions, different workflow/script fingerprint, changed original request, changed project scope, and incompatible config are rejected before session/phase mutation;
  - the instruction is delivered exactly once to the resumed agent's existing coding-agent session, is traced against that phase without replacing the original request, and is not leaked into completed or later phases;
  - repeated continuation may supply a different instruction while retaining compatibility with the stored original request;
  - if the first incomplete phase is deterministic code, the workflow executes/restores deterministic phases until it reaches the first incomplete agent phase and consumes the instruction there; if the workflow reaches completion without an agent phase, it fails clearly rather than silently discarding the instruction;
  - plain `--adw-id` still supports the existing join/chaining behavior and does not accidentally enable checkpoint skipping;
  - CLI/help/docstring wiring exists for every shipped ADW and generated skeleton.
- Keep tests isolated from `adws/adw_data/sessions/`; never use or modify real runtime records.

## Verification

Run all commands by exit status:

1. Compile every changed live Python module/script explicitly with `python -m py_compile ...`, including the new checkpoint module, runner/session/tracer/data types, all `adws/adw_*.py`, and `.codectory/scripts/make_adw.py`.
2. Compile the corresponding canonical templates with `python -m py_compile .codectory/templates/adws/adw_modules/*.py .codectory/templates/adws/adw_*.py` (or an equivalent shell expansion that passes every file).
3. Run focused and full factory tests: `python -m unittest .codectory.tests.test_continue` and `python -m unittest discover -s .codectory/tests`.
4. Run the relevant deterministic project quality command from `projects.yaml`: `(cd adws && python -m compileall -q .)`.
5. In a disposable temporary repo/session (not `adws/adw_data/sessions/`), run a deterministic fake workflow that intentionally stops after a completed side-effect phase, then invoke it with the same id and `--continue`; assert the completed action count is still one, the failed phase is retried, artifacts are unchanged, phase sequence is stable, and the final exit status is correct. Also verify an incompatible workflow and a simultaneously live run are refused with nonzero exit status before mutation.

## Scope and safeguards

- Do not repair failed application code automatically; continuation only re-enters the workflow’s existing failed/incomplete phase behavior.
- Do not change agent prompts, output contracts, model selection, or roster semantics.
- Do not redesign the visualizer.
- Preserve the repository’s current unrelated uncommitted changes, especially the in-progress project-scope/guidance edits in live ADWs, modules, cookbooks, and `justfile`; merge continuation support around them rather than resetting or wholesale-copying files.
- The requested handoff file under `adws/adw_data/sessions/fced99f1/context_handoff/` is the only intentional runtime-session write for this planning task; implementation and tests must not edit real session records.
