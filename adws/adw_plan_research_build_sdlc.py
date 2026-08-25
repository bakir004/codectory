#!/usr/bin/env -S uv run
# /// script
# dependencies = ["pydantic", "python-dotenv", "pyyaml", "rich"]
# ///
"""ADW Plan Research Build SDLC — plan, research only when needed, then deliver.

Usage:
    uv run adws/adw_plan_research_build_sdlc.py "<prompt or path/to/prompt.md>" [--config adws/adw_codectory_config/codectory.config.yaml] [--adw-id a1b2c3d4]

Phases: engineer(request) -> planner(decide research) -> [research -> planner(refine)]
        -> builder generation -> [code(quality) -> builder(fix) -> reviewer -> builder(revise)]
           bounded per generation -> fresh builder generation ... bounded
        -> git(commit_build) -> code(changes) -> documenter -> git(commit_docs)

The first plan decides whether current external documentation is required. When
it is, the research agent uses ctx7 and the planner refines the implementation
plan from its findings. Each builder generation keeps its context for bounded
quality repairs and reviewer exchanges. A rejected final review retires that
builder's context; the next fresh builder receives the same plan and that last
review before it takes over.
"""

import argparse
import sys

from adw_modules import agents, changes, gates, git_helper, quality, session, utils
from adw_modules.data_types import (AgentCall, BuildOutput, ChangeCapture,
                                    DocumentOutput, PhaseParams, PlanOutput,
                                    ResearchOutput, ReviewOutput)

REQUIRED_AGENTS = ["planner", "research", "builder", "reviewer", "documenter"]
MAX_QUALITY_FIX_LOOPS = 3
MAX_FIX_RETRIES = 2
MAX_BUILDER_GENERATIONS = 3
DOCUMENT_NOTES = ("Read diff_path in full before writing. Document only what the "
                  "diff shows, then copy the write-up into app_docs/ as your task "
                  "describes.")


def main(prompt: str, config: str = "adws/adw_codectory_config/codectory.config.yaml", adw_id: str | None = None) -> int:
    cfg = agents.load_config(config)
    agents.validate(cfg, REQUIRED_AGENTS)
    run = session.ensure(cfg, adw_id)
    baseline = git_helper.rev("HEAD")
    run.baseline_commit = baseline

    def commit(ph, envelope) -> None:
        message = envelope.commit_message or f"codectory({run.adw_id}): {envelope.summary}"
        ph.log(sha=git_helper.commit_all(message), message=message)

    def record(ph, result) -> None:
        passed = sum(1 for check in result.checks if check.passed)
        ph.log(passed=result.passed, checks=f"{passed}/{len(result.checks)}",
               artifacts=", ".join(result.artifacts))

    def repair_quality(prefix: str, current_build):
        result = None
        for attempt in range(1, MAX_QUALITY_FIX_LOOPS + 2):
            with run.phase(PhaseParams(
                name=f"{prefix}_quality_{attempt}", kind="code", owner="quality",
                description="Run every configured check on the changed projects before review",
            )) as ph:
                result = quality.run_checks(run, scope="changed")
                record(ph, result)
            if result.passed or attempt > MAX_QUALITY_FIX_LOOPS:
                break
            with run.phase(PhaseParams(
                name=f"{prefix}_fix_{attempt}", kind="agent", owner="builder", retries=1,
                description="Repair every deterministic quality failure from its captured output",
            )) as ph:
                current_build = ph.call(AgentCall(
                    output_type=BuildOutput, prompt=prompt,
                    previous=quality.as_envelope(result, "project quality checks"),
                    gates=[gates.diff_matches_claims]))
        return result, current_build

    with run.phase(PhaseParams(name="request", kind="engineer", owner=run.engineer,
                               description="Capture the request and pin the baseline before work begins")) as ph:
        ph.log(input=prompt, baseline=git_helper.short_sha(baseline))

    with run.phase(PhaseParams(name="plan", kind="agent", owner="planner", retries=1,
                               description="Draft an implementable plan and decide whether current documentation is needed")) as ph:
        initial_plan = ph.call(AgentCall(
            output_type=PlanOutput, prompt=prompt,
            gates=[gates.artifacts_exist, gates.files_non_empty]))

    plan = initial_plan
    if initial_plan.research_required:
        with run.phase(PhaseParams(name="research", kind="agent", owner="research", retries=1,
                                   description="Retrieve the current external guidance the provisional plan identified")) as ph:
            research = ph.call(AgentCall(
                output_type=ResearchOutput, prompt=prompt, previous=initial_plan,
                gates=[gates.artifacts_exist, gates.files_non_empty]))

        with run.phase(PhaseParams(name="refine_plan", kind="agent", owner="planner", retries=1,
                                   description="Refine the plan from current research before implementation starts")) as ph:
            plan = ph.call(AgentCall(
                output_type=PlanOutput, prompt=prompt, previous=research,
                gates=[gates.artifacts_exist, gates.files_non_empty]))

    with run.phase(PhaseParams(name="build", kind="agent", owner="builder", retries=1,
                               description="Implement the final plan without changing its accepted scope")) as ph:
        build = ph.call(AgentCall(output_type=BuildOutput, prompt=prompt, previous=plan,
                                  gates=[gates.diff_matches_claims]))

    quality_result = None
    review = None
    last_review = None
    build = None
    for generation in range(1, MAX_BUILDER_GENERATIONS + 1):
        # This is intentionally workflow-local: dropping the in-memory map entry
        # makes the next builder call mint a new Pi session. agents.execute() then
        # saves that generation as the session to resume for its own repair loop.
        run.agent_map.pop("builder", None)
        with run.phase(PhaseParams(
            name=f"builder_generation_{generation}", kind="code", owner="workflow",
            description="Establish an isolated builder context so each generation can reconsider the plan cleanly", 
        )) as ph:
            ph.log(generation=generation, fresh_context=True,
                   prior_review=last_review.summary if last_review else "none")

        with run.phase(PhaseParams(
            name=f"build_generation_{generation}", kind="agent", owner="builder", retries=1,
            description="Implement the plan in this builder generation, informed by the last review if any",
        )) as ph:
            build = ph.call(AgentCall(
                output_type=BuildOutput, prompt=prompt,
                previous=last_review or plan,
                gates=[gates.diff_matches_claims]))

        generation_rejected = False
        for fix_retry in range(1, MAX_FIX_RETRIES + 1):
            quality_result, build = repair_quality(
                f"generation_{generation}_retry_{fix_retry}", build)
            if not quality_result.passed:
                generation_rejected = True
                break

            with run.phase(PhaseParams(
                name=f"review_generation_{generation}_{fix_retry}", kind="agent",
                owner="reviewer", retries=1,
                description="Judge this generation's verified build against the request and final plan",
            )) as ph:
                review = ph.call(AgentCall(
                    output_type=ReviewOutput, prompt=prompt, previous=build,
                    gates=[gates.artifacts_exist, gates.verdict_consistent]))
            if review.approved:
                break

            last_review = review
            if fix_retry == MAX_FIX_RETRIES:
                generation_rejected = True
                break

            with run.phase(PhaseParams(
                name=f"revise_generation_{generation}_{fix_retry}", kind="agent",
                owner="builder", retries=1,
                description="Address the reviewer's blocking findings without leaving this builder's context",
            )) as ph:
                build = ph.call(AgentCall(
                    output_type=BuildOutput, prompt=prompt, previous=review,
                    gates=[gates.diff_matches_claims]))

        if review is not None and review.approved:
            break
        if not generation_rejected:
            break

    verified = (quality_result is not None and quality_result.passed
                and review is not None and review.approved)
    if verified:
        with run.phase(PhaseParams(name="commit_build", kind="code", owner="git",
                                   description="Commit only code that passed deterministic checks and review")) as ph:
            commit(ph, build)

        with run.phase(PhaseParams(name="changes", kind="code", owner="git",
                                   description="Capture the completed diff from the pinned baseline for documentation")) as ph:
            changeset = changes.capture(run, ChangeCapture(base=baseline))
            ph.log(base=f"{changeset.base.label} @ {changeset.base.commit[:7]}",
                   reason=changeset.base.reason,
                   files=len(changeset.files) + len(changeset.untracked),
                   lines=f"+{changeset.insertions} -{changeset.deletions}",
                   diff=changeset.diff_path)
            if changeset.empty:
                raise RuntimeError("nothing changed since the pinned baseline — there is nothing to document")

        with run.phase(PhaseParams(name="document", kind="agent", owner="documenter", retries=1,
                                   description="Write up the accepted change from the captured diff")) as ph:
            document = ph.call(AgentCall(
                output_type=DocumentOutput, prompt=prompt,
                previous=changes.as_envelope(changeset, DOCUMENT_NOTES),
                gates=[gates.artifacts_exist, gates.files_non_empty]))

        with run.phase(PhaseParams(name="commit_docs", kind="code", owner="git",
                                   description="Commit the write-up as the final record of accepted work")) as ph:
            commit(ph, document)

    return run.finish(accepted=verified,
                      reason="quality checks or review did not accept the completed build")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt", help="inline text or a path to a prompt file")
    parser.add_argument("--config", default="adws/adw_codectory_config/codectory.config.yaml")
    parser.add_argument("--adw-id", default=None, help="join or pin an existing session")
    args = parser.parse_args()
    sys.exit(main(utils.resolve_prompt(args.prompt), args.config, args.adw_id))
