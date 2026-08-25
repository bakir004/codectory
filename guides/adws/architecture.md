# Architecture

- Keep ADW scripts thin: they sequence phases only; reusable logic belongs in `adws/adw_modules/`.
- Every ADW validates `REQUIRED_AGENTS` before opening a run and ends through `run.finish()`.
- Agent calls use typed envelopes, with the output type, prompt JSON example, and call site updated together.
- Deterministic commands belong in code phases, not agent prompts.
