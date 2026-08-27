# Student faculty dashboard

The `/` route provides a responsive, student-facing Campus Compass dashboard with activities, assignments, scores, courses, and PostgreSQL-backed announcements. Announcements support create, read, update, and delete through validated accessible shadcn dialogs and confirmation controls. Database credentials are kept server-side and shared by the repository-root `.env` and the PostgreSQL-only Docker Compose service.

Assignments remain typed dummy data and are rendered from `sortAssignmentsByDueDate`, a stable ascending copy. The announcement UI includes semantic articles, source badges, timestamps, an empty state, inline validation, pending/error states, focusable labels, and red buttons with visible focus indicators.

## Verification

- `bun run test` — validation and existing sorting tests pass.
- `bun run lint` — passed.
- `bun run build` — passed.
- `docker compose config --services` — emits only `postgres`.

Manual browser inspection and live PostgreSQL repository tests were not performed in this change. Authentication/authorization, production deployment infrastructure, and a web application container remain out of scope.
