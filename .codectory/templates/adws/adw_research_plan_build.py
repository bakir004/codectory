#!/usr/bin/env -S uv run
# /// script
# dependencies = ["pydantic", "python-dotenv", "pyyaml", "rich"]
# ///
"""Research current docs with Context7, then plan and implement the request."""
import argparse
import sys

from adw_modules import agents, gates, session, utils
from adw_modules.data_types import AgentCall, BuildOutput, PhaseParams, PlanOutput, ResearchOutput

REQUIRED_AGENTS = ["research", "planner", "builder"]


def main(prompt: str, config: str = "adws/adw_codectory_config/codectory.config.yaml", adw_id: str | None = None) -> int:
    cfg = agents.load_config(config)
    agents.validate(cfg, REQUIRED_AGENTS)
    run = session.ensure(cfg, adw_id)

    with run.phase(PhaseParams(name="request", kind="engineer", owner=run.engineer,
                               description="Capture the request before researching its moving parts")) as ph:
        ph.log(input=prompt)

    with run.phase(PhaseParams(name="research", kind="agent", owner="research", retries=1,
                               description="Look up current library guidance so the plan does not rely on stale memory")) as ph:
        research = ph.call(AgentCall(output_type=ResearchOutput, prompt=prompt,
                                     gates=[gates.artifacts_exist, gates.files_non_empty]))

    with run.phase(PhaseParams(name="plan", kind="agent", owner="planner", retries=1,
                               description="Turn the request and current documentation into an implementable plan")) as ph:
        plan = ph.call(AgentCall(output_type=PlanOutput, prompt=prompt, previous=research,
                                 gates=[gates.artifacts_exist, gates.files_non_empty]))

    with run.phase(PhaseParams(name="build", kind="agent", owner="builder", retries=1,
                               description="Implement the documented plan without rediscovering its research")) as ph:
        build = ph.call(AgentCall(output_type=BuildOutput, prompt=prompt, previous=plan,
                                  gates=[gates.diff_matches_claims]))

    return run.finish(accepted=build.status == "success", reason="builder did not report success")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt")
    parser.add_argument("--config", default="adws/adw_codectory_config/codectory.config.yaml")
    parser.add_argument("--adw-id", default=None)
    args = parser.parse_args()
    sys.exit(main(utils.resolve_prompt(args.prompt), args.config, args.adw_id))
