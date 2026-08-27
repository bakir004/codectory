"""The Run object: config + adw_id + agent_map + tracer + console, bound once.

`run.phase(PhaseParams(...))` is the ONE phase primitive — a context manager
for all three kinds (engineer, agent, code). Success must be earned: every
phase defaults to fail; only a clean exit flips it (agent phases additionally
require a parsed envelope + green gates, enforced inside ph.call).
"""

from __future__ import annotations

import json
import time
from contextlib import contextmanager
from pathlib import Path

from . import agents, checkpoints, git_helper, guidance
from .console import Console
from .data_types import AgentCall, EnvelopeBase, EventRecord, Phase, PhaseParams
from .utils import ensure_dir, now_iso


class PhaseHandle:
    def __init__(self, run: "Run", phase: Phase, restored: bool = False):
        self.run = run
        self.phase = phase
        self.restored = restored

    def log(self, **payload) -> None:
        if self.restored:
            return
        self.run.tracer.event(EventRecord(adw_id=self.run.adw_id,
                                          phase_id=self.phase.phase_id,
                                          type="log", name=self.phase.params.name,
                                          payload=payload))
        self.run.console.note(", ".join(f"{k}: {v}" for k, v in payload.items()))
        if self.phase.params.kind == "engineer" and "input" in payload:
            self.run.tracer.session_request(self.run.adw_id, str(payload["input"]))

    def call(self, call: AgentCall) -> EnvelopeBase:
        if self.phase.params.kind != "agent":
            raise RuntimeError("ph.call() is only valid inside an agent phase")
        if self.restored:
            payload = self.run.tracer.latest_valid_envelope(
                self.phase.phase_id, call.output_type.__name__)
            if payload is None:
                raise RuntimeError(
                    f"completed phase {self.phase.params.name!r} has no valid "
                    f"{call.output_type.__name__} envelope to restore")
            return call.output_type.model_validate_json(payload)
        return agents.execute(self.run, self.phase, call)


class Run:
    def __init__(self, cfg, adw_id: str, tracer, engineer: str, options):
        self.cfg = cfg
        self.adw_id = adw_id
        self.tracer = tracer
        self.console = Console(tracer, adw_id)
        self.engineer = engineer
        self.phases: list[Phase] = []
        self.tokens = 0
        self.cost = 0.0
        self.clarification = options.clarification
        self.continuing = options.continue_instruction is not None
        self.continue_instruction = options.continue_instruction
        self._continue_consumed = False
        self._seq = 0 if self.continuing else tracer.max_phase_seq(adw_id)
        self.repo_root = git_helper.repo_root()    # where every agent is spawned to work
        # Quality's changed scope is measured from this immutable run-start pin,
        # never from a branch name that a commit phase can move underneath it.
        self.baseline_commit = git_helper.rev("HEAD") if git_helper.is_repo() else ""
        self.session_dir = ensure_dir(Path(cfg.defaults.data_dir) / "sessions" / adw_id)
        self.context_handoff_dir = ensure_dir(self.session_dir / "context_handoff")
        self._agent_map_path = self.session_dir / "agent_map.json"
        self.agent_map: dict = (json.loads(self._agent_map_path.read_text())
                                if self._agent_map_path.exists() else {})
        self.project_scope = tuple(name.strip() for name in options.projects.split(",") if name.strip())
        if not self.project_scope:
            raise RuntimeError(
                "--projects is required (comma-separated configured projects); "
                "the workflow harness must declare every project the request might touch")
        expected = checkpoints.identity(
            workflow=Path(__import__("sys").argv[0]).stem,
            prompt=options.prompt,
            projects=self.project_scope,
            config_path=options.config_path)
        self.checkpoint = checkpoints.load_or_create(
            self.session_dir, expected, self.continuing)
        # Guides are core factory context, not a workflow-specific phase. Every
        # agent receives this same packet through agents.execute().
        self.project_guides = guidance.load(self)

    # ── agent map (adw_id -> per-agent coding-agent session ids) ────────────
    def save_agent_map(self, agent: str, entry: dict) -> None:
        self.agent_map[agent] = entry
        self._agent_map_path.write_text(json.dumps(self.agent_map, indent=2))

    # ── usage (run totals mirror what the tracer accumulates in sqlite) ─────
    def add_usage(self, tokens: int, cost: float) -> None:
        self.tokens += tokens
        self.cost += cost
        self.tracer.session_add_usage(self.adw_id, tokens, cost)

    def take_continue_instruction(self, phase: Phase) -> str | None:
        if not self.continuing or self._continue_consumed:
            return None
        self._continue_consumed = True
        instruction = self.continue_instruction
        self.tracer.event(EventRecord(
            adw_id=self.adw_id, phase_id=phase.phase_id, type="log",
            name="continue_instruction",
            payload={"instruction_sha256": __import__("hashlib").sha256(instruction.encode()).hexdigest()}))
        return instruction

    # ── the phase primitive ─────────────────────────────────────────────────
    @contextmanager
    def phase(self, params: PhaseParams):
        self._seq += 1
        phase = Phase(phase_id=f"{self.adw_id}_{self._seq:02d}_{params.name}",
                      adw_id=self.adw_id, seq=self._seq, params=params,
                      status="running", started_at=now_iso())
        if self.continuing:
            row = self.tracer.phase_get(self.adw_id, self._seq)
            if row:
                _, name, kind, owner, description, status, attempt, _, error, started, ended = row
                actual = (name, kind, owner, description)
                expected = (params.name, params.kind, params.owner, params.description)
                if actual != expected:
                    raise RuntimeError(
                        f"cannot continue: phase {self._seq} definition changed "
                        f"(stored={actual!r}, current={expected!r})")
                if status == "success":
                    if params.kind == "code":
                        raise RuntimeError(
                            f"cannot safely restore completed code phase {params.name!r}; "
                            "this workflow must checkpoint its typed deterministic result")
                    phase.status, phase.attempt, phase.error = status, attempt, error
                    phase.started_at, phase.ended_at = started, ended
                    self.phases.append(phase)
                    yield PhaseHandle(self, phase, restored=True)
                    return
        self.phases.append(phase)
        self.tracer.phase_upsert(phase)
        self.tracer.event(EventRecord(adw_id=self.adw_id, phase_id=phase.phase_id,
                                      type="phase_start", name=params.name,
                                      payload={"kind": params.kind, "owner": params.owner,
                                               "description": params.description}))
        self.console.phase_started(phase)
        clock = time.monotonic()
        try:
            yield PhaseHandle(self, phase)
        except BaseException as error:
            phase.status = "fail"                      # success must be earned
            phase.error = str(error)[:1000]
            phase.ended_at = now_iso()
            self.tracer.event(EventRecord(adw_id=self.adw_id, phase_id=phase.phase_id,
                                          type="error", name=params.name,
                                          payload={"error": phase.error}))
            self.tracer.event(EventRecord(adw_id=self.adw_id, phase_id=phase.phase_id,
                                          type="phase_end", name=params.name,
                                          payload={"status": "fail"}))
            self.tracer.phase_upsert(phase)
            self.tracer.session_finish(self.adw_id, ok=False)
            self.console.phase_ended(phase, time.monotonic() - clock)
            self.console.session_finished(False, self.tokens, self.cost,
                                          self.cfg.observability.db)
            raise
        else:
            phase.status = "success"
            phase.ended_at = now_iso()
            self.tracer.event(EventRecord(adw_id=self.adw_id, phase_id=phase.phase_id,
                                          type="phase_end", name=params.name,
                                          payload={"status": "success"}))
            self.tracer.phase_upsert(phase)
            self.console.phase_ended(phase, time.monotonic() - clock)

    # ── run outcome ─────────────────────────────────────────────────────────
    def finish(self, accepted: bool = True, reason: str = "") -> int:
        """Finalize the run and return its exit code. Call this exactly once.

        Two criteria, not one. Every phase must have passed, AND the ADW's own
        acceptance test must hold. They are different questions on purpose: a
        test phase that ran the suite did its job even when the suite came back
        red, so the PHASE succeeds while the RUN must not.

        This replaces a `succeeded` property that answered only the first
        question — and, being a property with side effects, wrote the session
        status and printed the banner before the caller's `and test.passed` was
        ever evaluated. A run whose suite never passed was recorded green in the
        db, on the terminal, and in the UI while exiting 1. Anyone reading the
        trace saw success; only a CI job checking `$?` saw the truth. One call
        now settles the db, the banner, and the exit code together, so the three
        cannot disagree.
        """
        phases_ok = bool(self.phases) and all(p.status == "success" for p in self.phases)
        instruction_ok = not self.continuing or self._continue_consumed
        if not instruction_ok:
            accepted = False
            reason = reason or "the continuation instruction had no incomplete agent phase to receive it"
        ok = phases_ok and accepted
        if phases_ok and not accepted:
            note = reason or "the run's acceptance criterion was not met"
            self.tracer.event(EventRecord(
                adw_id=self.adw_id,
                phase_id=self.phases[-1].phase_id if self.phases else "",
                type="error", name="not_accepted", payload={"reason": note}))
            self.console.note(f"not accepted: {note}")
        self.tracer.session_finish(self.adw_id, ok=ok)
        self.console.session_finished(ok, self.tokens, self.cost, self.cfg.observability.db)
        return 0 if ok else 1
