#!/usr/bin/env -S uv run
# /// script
# dependencies = ["pydantic", "python-dotenv", "pyyaml", "rich"]
# ///
"""ADW Prompt — the smallest ADW: one agent, one prompt, traced end-to-end.

Usage:
    uv run adws/adw_prompt.py "<prompt or path/to/prompt.md>" [--agent builder] [--config adws/adw_codectory_config/codectory.config.yaml] [--adw-id a1b2c3d4]

Phases: engineer(request) -> <agent>
"""

import argparse
import sys

from adw_modules import agents, session, utils
from adw_modules.data_types import LaunchOptions
from adw_modules.data_types import AgentCall, GenericOutput, PhaseParams


def main(prompt: str, projects: str, agent: str = "builder",
         config: str = "adws/adw_codectory_config/codectory.config.yaml", adw_id: str | None = None, continue_instruction: str | None = None, clarification: bool = False) -> int:
    cfg = agents.load_config(config)
    agents.validate(cfg, [agent])
    run = session.ensure(cfg, LaunchOptions(prompt=prompt, projects=projects, config_path=config,
                                                 adw_id=adw_id, continue_instruction=continue_instruction,
                                                 clarification=clarification))

    with run.phase(PhaseParams(name="request", kind="engineer", owner=run.engineer,
                               description="Capture the incoming ask")) as ph:
        ph.log(input=prompt)

    with run.phase(PhaseParams(name="prompt", kind="agent", owner=agent,
                               description=f"Send the request straight to {agent} and parse its envelope")) as ph:
        ph.call(AgentCall(output_type=GenericOutput, prompt=prompt))

    return run.finish()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt", help="inline text or a path to a prompt file")
    parser.add_argument("--agent", default="builder", help="agent name from the config")
    parser.add_argument("--config", default="adws/adw_codectory_config/codectory.config.yaml")
    parser.add_argument("--projects", required=True, help="comma-separated configured project names")
    parser.add_argument("--adw-id", default=None, help="join or pin an existing session")
    parser.add_argument("--continue", dest="continue_instruction", metavar="INSTRUCTION",
                        help="resume the first incomplete agent phase with this instruction")
    parser.add_argument("--clarification", action="store_true",
                        help="allow the planner to pause for attached caller answers")
    args = parser.parse_args()
    sys.exit(main(utils.resolve_prompt(args.prompt), args.projects, args.agent, args.config, args.adw_id, args.continue_instruction, args.clarification))
