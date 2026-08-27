# Plan: PostgreSQL-backed announcements CRUD

## Goal

Replace the dashboard’s static announcement records with announcements persisted in PostgreSQL and expose complete create, read, update, and delete workflows on `/`. The create and edit experiences should use the project’s existing shadcn setup, validate input before submission and again on the server, report pending/error states, and retain the dashboard’s responsive and accessible presentation. Add a root Docker Compose configuration containing PostgreSQL only, with both Compose and the web server reading the same database settings from the existing root `.env`.

## Implementation plan

### 1. Add the database dependency and migration tooling

- Update `web/package.json` and `web/bun.lock` with a PostgreSQL stack suitable for TanStack Start (use Drizzle ORM with the `postgres` driver, Drizzle Kit for migrations, and Zod for shared input validation).
- Add package scripts for generating/checking and applying migrations (for example, `db:generate` and `db:migrate`) so setup does not depend on an undocumented one-off command.
- Add `web/drizzle.config.ts`, pointing at the announcement schema and migrations directory and loading the database settings from the repository-root environment rather than expecting a second `web/.env`.
- Add a server-only environment/database module such as `web/src/db/client.server.ts`. It should validate the required `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, host, and port values, construct the connection configuration in one place, and fail with a useful server-side configuration error. Do not expose credentials through `VITE_` variables or client bundles.
- Add `web/src/db/schema.ts` with an `announcements` table. Preserve the dashboard’s useful domain shape: generated UUID id, non-empty author, constrained source (`Professor` or `Administration`), announcement body/excerpt, creation/posted timestamp, and updated timestamp. Use database defaults for ids/timestamps and a deterministic newest-first read order.
- Generate and commit the initial migration under `web/drizzle/`. The migration should create all required PostgreSQL extensions/types/table constraints. Migrate the two current dummy announcements into the database as initial records (or an idempotent seed associated with setup) so the existing dashboard content is not silently lost; remove their runtime use from `dashboard-data.ts` afterward.

### 2. Add the root PostgreSQL development service and shared environment configuration

- Add repository-root `compose.yaml` (or `docker-compose.yml`) with exactly one service: PostgreSQL. Pin an appropriate PostgreSQL Alpine image, map the configured host port, persist data in a named volume, and add a `pg_isready` healthcheck.
- Have Compose interpolate `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, and `POSTGRES_PORT` from the repository-root `.env`; do not pass unrelated API keys from that file into the container.
- Preserve all existing entries in the already-present, gitignored root `.env` and append local database values, including an explicit localhost host/port for the web process. Do not print, copy, or commit the existing provider secrets. Update the tracked `.env.sample` with a documented PostgreSQL section and safe placeholder/development values so another developer can reproduce the setup without obtaining the ignored file.
- Set `envDir: '..'` in `web/vite.config.ts` so TanStack Start server functions load the repository-root environment, and explicitly load `../.env` in `web/drizzle.config.ts` for Drizzle Kit commands launched from `web/`. Keep database access server-only and never use `VITE_`-prefixed credential names.

### 3. Implement typed, validated CRUD behind TanStack Start server functions

- Add a focused announcements feature area, for example `web/src/features/announcements/`, containing:
  - a shared Zod input schema and inferred types for create/update payloads;
  - a server-only repository that performs parameterized Drizzle list/create/update/delete queries;
  - TanStack Start server functions for list, create, update, and delete.
- Validate author, source, and body on both the client and server. Trim text, reject blank values, apply clear maximum lengths, constrain source to the two supported values, and validate UUID ids for update/delete. Treat missing update/delete targets as explicit not-found errors rather than successful no-ops.
- Keep all database imports and query execution out of route/component code, in accordance with the architecture guide. Return JSON-safe records with timestamps serialized consistently for `<time dateTime>` rendering.
- Make the `/` route loader call the list server function, then use loader data for the announcements section. After successful mutations, invalidate/reload route data so all changes are read back from PostgreSQL rather than only patched into temporary component state.

### 4. Build polished, accessible CRUD controls with the existing shadcn configuration

- Use the aliases and style declared in `web/components.json` to add locally owned shadcn primitives needed by the feature, including at minimum `web/src/components/ui/dialog.tsx`; add Button, Input, Label, Textarea, and Alert Dialog primitives where they improve consistency. Do not introduce a second component system.
- Extract the announcements presentation and form into focused components under `web/src/features/announcements/` instead of making `web/src/routes/index.tsx` substantially denser.
- Replace the current presentational “View all” announcement control with a clearly labeled red “Create announcement” button. It must open a shadcn Dialog with author, source, and announcement body inputs, explanatory title/description, inline field errors, cancel/close and submit controls, and focus/label behavior suitable for keyboard and assistive-technology users.
- Disable duplicate submissions while saving, show a clear saving state, keep entered values when the server rejects a submission, surface a form-level server error, and close/reset the dialog only after a confirmed database write.
- Add red edit and delete controls to each announcement. Reuse the dialog in edit mode with existing values prefilled; use a shadcn Alert Dialog (or equivalently polished accessible confirmation) before deletion. Pending operations should not be repeatable, and mutation errors should remain visible to the user.
- Render the database timestamp with the existing date formatter and semantic `<time dateTime>`, retain textual source badges, separators, list/article semantics, and add an intentional empty state when no announcements remain.
- Enforce the project-specific style rule on every newly introduced HTML button, including shadcn dialog close buttons, alert-dialog cancel/confirm buttons, icon buttons, and disabled/pending states: red background, accessible contrasting text, and a visible keyboard focus indicator. Check generated shadcn defaults rather than assuming every variant complies.
- Leave activities, assignments, scores, and courses on their existing typed dummy data; only announcements become server-backed.

### 5. Add focused tests

- Add unit tests alongside the announcement feature for accepted input, whitespace normalization, missing/oversized fields, invalid source values, and malformed ids.
- Add database-backed repository tests that run against the Compose PostgreSQL instance and prove create/read persistence, update, delete, newest-first ordering, and not-found behavior. Isolate test records and clean them up so the tests can be rerun safely without deleting normal development data.
- If server-function wrappers contain meaningful mapping/error behavior beyond the tested schemas and repository, add focused tests for that behavior; avoid testing framework internals.
- Retain the existing assignment sorting tests.

### 6. Update project documentation

- Replace the generic `web/README.md` content with concise local setup instructions: populate the root `.env`, start only PostgreSQL with Docker Compose, wait for health, install dependencies, apply migrations, run the web app, and run tests/checks.
- Update `guides/web/student-faculty-dashboard.md` because its current statement that all announcements are dummy data and that there are no APIs/persistence will become false. Describe the PostgreSQL-backed CRUD UI, shared environment arrangement, accessible dialog behavior, and the actual verification performed.
- State that authentication/authorization, production deployment infrastructure, and a web application container remain out of scope. No guide override is required.

## Verification

Run from the repository root unless noted:

1. `docker compose config --services` and confirm the only service emitted is PostgreSQL; also inspect `docker compose config` to confirm credentials/port are interpolated without adding a web service.
2. `docker compose up -d` and wait for `docker compose ps`/the configured healthcheck to report PostgreSQL healthy.
3. From `web/`, install/update dependencies and run the migration script; run it again (or otherwise check migration state) to verify setup is safely repeatable.
4. From `web/`, run `bun run test`, including the validation and live repository CRUD tests.
5. From `web/`, run the required `bun run lint` and `bun run build` checks and judge each by exit status.
6. Start the web app and manually verify at mobile and desktop widths: initial announcements come from PostgreSQL; invalid create input shows inline errors and does not insert; a valid create survives reload; edit survives reload; delete requires confirmation and survives reload; the empty state works; all controls are red with contrasting text and visible keyboard focus; dialogs trap/restore focus and are operable by keyboard; no database credentials appear in browser-delivered code or network payloads.
7. Record the exact commands/results and manual-browser status in `guides/web/student-faculty-dashboard.md`.

## Constraints and cautions

- The root `.env` already contains ignored local factory credentials. Modify it in place only to add database settings, never overwrite it, expose its contents, or force-add it to Git. The tracked `.env.sample` is the shareable template.
- PostgreSQL is the only container in Compose; the web application continues to run directly through Bun/TanStack Start.
- Database operations belong in server-only modules reached through TanStack Start server functions, not directly in `src/routes/index.tsx`.
- Generated shadcn controls must be adjusted to satisfy the repository’s stricter all-buttons-red rule.
