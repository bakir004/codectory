# Campus Compass web

## Local development

1. Copy `.env.sample` to the repository root as `.env` and set the PostgreSQL values.
2. Start the database only: `docker compose up -d postgres` (wait for its healthcheck).
3. Install dependencies: `bun install` from `web/`.
4. Apply migrations: `bun run db:migrate` from `web/`.
5. Start the app: `bun run dev`.

Run checks with `bun run test`, `bun run lint`, and `bun run build`. Announcements are persisted in PostgreSQL and can be created, edited, and deleted from the dashboard. Faculty viewers can use the red **Create announcement** action in the Announcements header, which reuses the accessible validated creation dialog and PostgreSQL create path. Student viewers do not see this action and receive a role-appropriate empty state. The `?role=faculty` query value is a demo UI context only, not authentication or authorization; omitted and invalid values default to the student view. Authentication, authorization, production infrastructure, and a web container are out of scope.

Verification: `bun run test`, `bun run lint`, and `bun run build` passed. Manual browser inspection and live PostgreSQL persistence verification were not performed.
