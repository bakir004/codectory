# Research request

Research the current documentation relevant to this request:

{{prompt}}

Return JSON with:
- `status`: `success` or `fail`
- `summary`
- `queries`: Context7 queries you ran
- `findings`: objects containing `source`, `topic`, `finding`, and optional `excerpt`
- `artifacts` and `notes_for_next_agent`

Do not implement anything. The planner will use your findings to make the implementation plan.
