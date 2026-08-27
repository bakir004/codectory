#!/usr/bin/env -S uv run
# /// script
# dependencies = ["pydantic", "python-dotenv", "pyyaml", "rich"]
# ///
"""ADW Scout — read-only recon workflow. Just looking for stuff.

Usage:
    uv run adws/adw_scout.py "<prompt or path/to/prompt.md>" [--config adws/adw_codectory_config/codectory.config.yaml] [--adw-id a1b2c3d4]

Phases: engineer(request) -> scout
"""

import argparse
import sys

from adw_modules import agents, gates, session, utils
from adw_modules.data_types import LaunchOptions
from adw_modules.data_types import AgentCall, PhaseParams, ScoutOutput

REQUIRED_AGENTS = ["scout"]


def main(prompt: str, projects: str, config: str = "adws/adw_codectory_config/codectory.config.yaml", adw_id: str | None = None, continue_instruction: str | None = None, clarification: bool = False) -> int:
    cfg = agents.load_config(config)
    agents.validate(cfg, REQUIRED_AGENTS)
    run = session.ensure(cfg, LaunchOptions(prompt=prompt, projects=projects, config_path=config,
                                                 adw_id=adw_id, continue_instruction=continue_instruction,
                                                 clarification=clarification))

    with run.phase(PhaseParams(name="request", kind="engineer", owner=run.engineer,
                               description="Capture the incoming ask")) as ph:
        ph.log(input=prompt)

    with run.phase(PhaseParams(name="scout", kind="agent", owner="scout",
                               description="Find and report where things live — change nothing")) as ph:
        ph.call(AgentCall(output_type=ScoutOutput, prompt=prompt,
                          gates=[gates.artifacts_exist]))

    return run.finish()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt", help="inline text or a path to a prompt file")
    parser.add_argument("--config", default="adws/adw_codectory_config/codectory.config.yaml")
    parser.add_argument("--projects", required=True, help="comma-separated configured project names")
    parser.add_argument("--adw-id", default=None, help="join or pin an existing session")
    parser.add_argument("--continue", dest="continue_instruction", metavar="INSTRUCTION",
                        help="resume the first incomplete agent phase with this instruction")
    parser.add_argument("--clarification", action="store_true",
                        help="allow the planner to pause for attached caller answers")
    args = parser.parse_args()
    sys.exit(main(utils.resolve_prompt(args.prompt), args.projects, args.config, args.adw_id, args.continue_instruction, args.clarification))
