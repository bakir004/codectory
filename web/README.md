# Campus Compass web

## Local development

1. Copy `.env.sample` to the repository root as `.env` and set the PostgreSQL values.
2. Start the database only: `docker compose up -d postgres` (wait for its healthcheck).
3. Install dependencies: `bun install` from `web/`.
4. Apply migrations: `bun run db:migrate` from `web/`.
5. Start the app: `bun run dev`.

Run checks with `bun run test`, `bun run lint`, and `bun run build`. Announcements are persisted in PostgreSQL and can be created, edited, and deleted from the dashboard. Authentication, authorization, production infrastructure, and a web container are out of scope.
