# PostgreSQL announcement CRUD

## What changed

The dashboard’s `/` route now reads announcements from PostgreSQL and provides complete create, edit, and delete workflows. The announcement controls live in `web/src/features/announcements/announcement-controls.tsx`: a red **Create announcement** button opens a shadcn/Radix dialog, while each announcement has edit and delete actions. Forms validate author, source, and body, normalize whitespace, show inline and server errors, disable duplicate submissions, and refresh route data after successful writes. Deletion requires an accessible confirmation dialog. The UI also handles pending states, timestamps, semantic articles, source badges, and an empty state.

Server-only CRUD is split across `web/src/features/announcements/server.ts` and `repository.server.ts`. TanStack Start server functions validate payloads and serialize timestamps; the repository performs Drizzle queries and reports missing update/delete records. `web/src/db/schema.ts` defines the PostgreSQL `announcements` table, and `web/src/db/client.server.ts` validates the required database environment variables before creating the connection. The root Vite environment directory is configured in `web/vite.config.ts`.

`web/drizzle/0000_initial_announcements.sql` creates the table, enables `pgcrypto`, and seeds the two existing dashboard announcements. Drizzle configuration and scripts are provided by `web/drizzle.config.ts` and `web/package.json`; dependencies and lockfile changes are in `web/package.json` and `web/bun.lock`. Focused validation coverage is in `web/src/features/announcements/validation.test.ts`.

## Database setup

The repository-root `compose.yaml` contains exactly one service, `postgres`, using PostgreSQL 16 Alpine, a named persistent volume, configured port mapping, and a `pg_isready` healthcheck. Compose reads `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_PORT` from the root environment. `.env.sample` documents those values plus `POSTGRES_HOST` for the web process. `web/README.md` documents the local flow: provide the root `.env`, run `docker compose up -d postgres`, install from `web/`, apply `bun run db:migrate`, then run `bun run dev`.

## Verification

The project documentation records these completed checks:

- `bun run test` — validation and existing assignment-sorting tests pass.
- `bun run lint` — passed.
- `bun run build` — passed.
- `docker compose config --services` — emits only `postgres`.

Manual browser inspection and live PostgreSQL repository tests were not performed. Authentication/authorization, production deployment infrastructure, and a web application container remain out of scope. No project-guide override was recorded.
