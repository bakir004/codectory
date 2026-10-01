# Bun full-stack todo app

## What changed

A complete `web/` Bun workspace was added for a small todo application. It combines a TanStack Start/React/Vite frontend, a NestJS REST API backed by TypeORM/PostgreSQL, and a PostgreSQL-only Docker Compose service. The app supports listing, creating, completing/reopening, and deleting todos; the API persists records in PostgreSQL through an explicit migration.

## Where it lives

- `web/package.json` defines the Bun workspace, development, lint, build, test, and migration scripts; `web/bun.lock` records the dependency installation. `.env.example` and `.gitignore` provide local configuration and ignore local environment/dependency/build files.
- `web/apps/frontend/` contains the TanStack Start setup. `vite.config.ts` configures the Start and React Vite plugins and port 3000; `src/router.tsx`, `src/routes/__root.tsx`, and generated `src/routeTree.gen.ts` provide the router/document shell. `src/routes/index.tsx` implements the todo UI with loading, empty, validation, mutation, and error handling. `src/lib/todos-api.ts` provides typed HTTP calls to the API, using `VITE_API_URL` or `http://localhost:3001`. `src/styles.css` supplies the responsive styling. `vitest.config.ts`, `src/test-setup.ts`, and `src/smoke.test.ts` provide the frontend test setup and smoke test.
- `web/apps/api/` contains the NestJS service. `src/main.ts` applies the `/api` prefix, configured CORS, and validation; `src/app.module.ts` and `src/data-source.ts` configure TypeORM against `DATABASE_URL` with synchronization disabled. The `src/todos/` feature contains the entity, DTOs, controller, module, and repository service for the CRUD endpoints. `src/migrations/1710000000000-create-todos.ts` creates the UUID-based `todos` table and reverses it. API TypeScript/Vitest configuration and `test/smoke.test.ts` are included.
- `web/compose.yaml` runs PostgreSQL 16 Alpine, exposes the configurable host port, adds a `pg_isready` health check, and stores data in the named `todo-postgres-data` volume.
- `web/README.md` documents setup, configuration, endpoints, commands, URLs, and volume behavior.

## Use and verification

From `web/`, copy `.env.example` to `.env`, install dependencies, start PostgreSQL, run the migration, and start both apps:

```sh
cp .env.example .env
bun install
docker compose up -d
bun run migration:run
bun run dev
```

The frontend is available at `http://localhost:3000`; the API collection is at `http://localhost:3001/api/todos`. Check database health with `docker compose ps`. The documented checks are:

```sh
bun run lint
bun run test
bun run build
docker compose config
```

Individual app development commands are `bun run dev:frontend` and `bun run dev:api`; migrations can be run or reverted with `bun run migration:run` and `bun run migration:revert`. Stop PostgreSQL with `docker compose down`; use `docker compose down -v` to intentionally reset the named database volume.

The API contracts are `GET /api/todos`, `POST /api/todos` with a title, `PATCH /api/todos/:id` with title and/or completion, and `DELETE /api/todos/:id` returning 204. Validation rejects blank/oversized titles, unexpected fields, malformed UUIDs, empty updates, and unknown IDs with 4xx responses.

The committed tests are smoke tests for frontend/API loading; the configured test command runs both workspace test scripts without requiring PostgreSQL.
