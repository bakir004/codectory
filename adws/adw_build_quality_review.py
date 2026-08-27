#!/usr/bin/env -S uv run
# /// script
# dependencies = ["pydantic", "python-dotenv", "pyyaml", "rich"]
# ///
"""ADW Build Quality Review — implement, verify deterministic checks, and review.

Usage:
    CODECTORY_PROJECTS=<project[,project...]> uv run adws/adw_build_quality_review.py "<prompt or path/to/prompt.md>" [--config adws/adw_codectory_config/codectory.config.yaml] [--adw-id a1b2c3d4]

Phases: engineer(request) -> builder -> [code(quality) -> builder(fix)] bounded
        -> reviewer [-> builder(revise) -> quality -> reviewer ... bounded]

Quality answers whether the configured commands pass; review answers whether
the implementation fulfills the request. Every reviewer-requested revision
returns through deterministic quality before another review. The workflow does
not commit: use it when a plan already exists or the request is understood.
"""

import argparse
import sys

from adw_modules import agents, gates, quality, session, utils
from adw_modules.data_types import AgentCall, BuildOutput, PhaseParams, ReviewOutput

REQUIRED_AGENTS = ["builder", "reviewer"]
MAX_QUALITY_FIX_LOOPS = 3
MAX_REVIEW_LOOPS = 3


def main(prompt: str, config: str = "adws/adw_codectory_config/codectory.config.yaml", adw_id: str | None = None) -> int:
    cfg = agents.load_config(config)
    agents.validate(cfg, REQUIRED_AGENTS)
    run = session.ensure(cfg, adw_id)

    def record(ph, result) -> None:
        passed = sum(1 for check in result.checks if check.passed)
        ph.log(passed=result.passed, checks=f"{passed}/{len(result.checks)}",
               artifacts=", ".join(result.artifacts))

    def repair_quality(prefix: str, current_build):
        result = None
        for attempt in range(1, MAX_QUALITY_FIX_LOOPS + 2):
            with run.phase(PhaseParams(
                name=f"{prefix}_quality_{attempt}", kind="code", owner="quality",
                description="Run every configured check before the implementation is reviewed",
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
                               description="Capture the incoming implementation request")) as ph:
        ph.log(input=prompt)

    with run.phase(PhaseParams(name="build", kind="agent", owner="builder", retries=1,
                               description="Implement the request before deterministic verification begins")) as ph:
        build = ph.call(AgentCall(output_type=BuildOutput, prompt=prompt,
                                  gates=[gates.diff_matches_claims]))

    quality_result = None
    review = None
    for review_attempt in range(1, MAX_REVIEW_LOOPS + 1):
        quality_result, build = repair_quality(f"review_{review_attempt}", build)
        if not quality_result.passed:
            break

        with run.phase(PhaseParams(
            name=f"review_{review_attempt}", kind="agent", owner="reviewer", retries=1,
            description="Confirm the quality-clean build satisfies every requested requirement",
        )) as ph:
            review = ph.call(AgentCall(output_type=ReviewOutput, prompt=prompt, previous=build,
                                       gates=[gates.artifacts_exist, gates.verdict_consistent]))
        if review.approved or review_attempt == MAX_REVIEW_LOOPS:
            break

        with run.phase(PhaseParams(
            name=f"revise_{review_attempt}", kind="agent", owner="builder", retries=1,
            description="Address the reviewer's blocking findings before fresh verification",
        )) as ph:
            build = ph.call(AgentCall(output_type=BuildOutput, prompt=prompt, previous=review,
                                      gates=[gates.diff_matches_claims]))

    accepted = (quality_result is not None and quality_result.passed
                and review is not None and review.approved)
    return run.finish(accepted=accepted,
                      reason="quality checks or review did not accept the build")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt", help="inline text or a path to a prompt file")
    parser.add_argument("--config", default="adws/adw_codectory_config/codectory.config.yaml")
    parser.add_argument("--adw-id", default=None, help="join or pin an existing session")
    args = parser.parse_args()
    sys.exit(main(utils.resolve_prompt(args.prompt), args.config, args.adw_id))
