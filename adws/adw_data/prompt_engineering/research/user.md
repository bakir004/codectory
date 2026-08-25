# Research Task

## Variables

### prompt

{{prompt}}

### previous_envelope

{{previous_envelope}}

### context_handoff_dir

{{context_handoff_dir}}

## Task

Research the current authoritative documentation relevant to `prompt`.

1. Use the Context7 CLI to resolve the relevant library and retrieve its current documentation.
2. Write the research notes to `<context_handoff_dir>/research.md`.
3. Emit your `Report` JSON. Its `artifacts` entry must name the file you actually wrote.

Do not implement anything. The planner will use your findings to make the implementation plan.

## Report

Respond with ONLY valid JSON matching `ResearchOutput` — no prose before or after:

```json
{
  "status": "success",
  "summary": "<one sentence summarizing the research>",
  "findings": [
    {
      "source": "<official documentation URL or Context7 library identifier>",
      "topic": "<documented API, component, or integration topic>",
      "finding": "<concise documented fact relevant to the request>",
      "excerpt": "<optional concise supporting quotation>"
    }
  ],
  "queries": ["<Context7 query you ran>"],
  "artifacts": ["<context_handoff_dir>/research.md"],
  "notes_for_next_agent": "<what the planner must know>"
}
```
