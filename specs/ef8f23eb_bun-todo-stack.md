# Plan: Bun TanStack Start Todo Application

## Goal and constraints

Create a self-contained application under `web/` consisting of a Bun-managed React/TanStack Start frontend, a NestJS REST API, and a PostgreSQL Docker Compose service. The todo workflow will support listing, creating, completing/reopening, and deleting todos, with all state stored in PostgreSQL. Keep authentication, deployment services, and unrelated features out of scope. The repository’s `web` quality contract is authoritative: from `web/`, both `bun run lint` and `bun run build` must succeed.

## Assumptions

- Use a small Bun workspace rooted at `web/`, with `apps/frontend` and `apps/api`; place `compose.yaml`, shared developer scripts, environment examples, lockfile, and application documentation at the workspace root.
- Use port `3000` for TanStack Start, port `3001` for NestJS, and host port `5432` for PostgreSQL unless environment variables override them.
- Docker Compose is responsible only for PostgreSQL. The two application processes run with Bun on the host.
- Use TypeORM through Nest’s official integration for the API persistence layer. Manage the schema with a checked-in migration rather than depending on runtime schema synchronization.
- Keep the frontend as a genuine TanStack Start app using its Vite integration and file-based routes; do not replace it with a plain Vite SPA or a TanStack Router-only starter.
- Commit the generated Bun lockfile and generated TanStack route tree when the selected official starter expects that file to be checked in.

## Current-documentation research gate

Before generating files, consult current official documentation and record/apply the exact current commands and supported package combinations for:

1. TanStack Start’s recommended React project bootstrap flow, including the current official CLI/package name, selecting Vite, and running the generated project with Bun.
2. TanStack Start’s current Vite plugin, file-based route, root route, and generated route-tree conventions, so the implementation follows the current starter rather than an obsolete beta layout.
3. Bun workspace/script conventions needed to install and run the frontend and API from one `web/package.json`.

Prefer the official generator output and current documented package versions over guessed commands or stale examples. If the generated naming differs from the illustrative paths below, retain its canonical equivalents and document them in `web/README.md`.

## Implementation steps

### 1. Establish the `web/` Bun workspace

- Add `web/package.json` with private workspace declarations for `apps/frontend` and `apps/api`, an explicit Bun package-manager version, and root scripts for:
  - running both development servers together (plus individual frontend/API development scripts),
  - linting both workspaces,
  - building both workspaces,
  - running both workspaces’ focused tests,
  - invoking the API’s TypeORM migration command.
- Add the current Bun lockfile produced by one install at `web/bun.lock`; do not introduce npm/yarn/pnpm lockfiles.
- Add `web/.env.example` with non-secret local defaults for PostgreSQL credentials/port, `DATABASE_URL` (or the equivalent explicit Nest database settings), API port, allowed frontend origin, and the frontend’s public API base URL. Ensure actual `.env` files remain ignored.
- If orchestration of parallel dev scripts needs a package such as `concurrently`, add it explicitly rather than relying on shell-specific backgrounding. Root `lint` and `build` scripts should deterministically execute both child projects and propagate a child failure.

### 2. Bootstrap and shape the TanStack Start frontend

- Under `web/apps/frontend`, use the current official TanStack Start React/Vite bootstrap procedure discovered in research, running it through Bun and stripping only demo/sample routes and assets that are not part of the todo app.
- Preserve the starter’s required Vite/TanStack configuration and route-tree generation setup (`vite.config.ts`, TypeScript config, route generator integration, and the current equivalents of `src/router.tsx`, `src/routes/__root.tsx`, `src/routes/index.tsx`, and `src/routeTree.gen.ts`).
- Implement a focused todo screen on the index route:
  - fetch and display persisted todos;
  - submit a trimmed, non-empty title to create a todo;
  - toggle each item between complete and incomplete;
  - delete an item;
  - expose loading, empty, saving, and recoverable error states;
  - disable controls while the relevant mutation is pending and use semantic labels/buttons so keyboard and screen-reader behavior is clear.
- Add a typed API client module (for example `src/lib/todos-api.ts`) containing the shared frontend `Todo` shape and all HTTP calls. Read the API base URL from the documented Vite public environment variable, with a local `http://localhost:3001` fallback, and turn non-2xx responses into useful UI errors.
- Keep state handling intentionally local and simple; no authentication, routing beyond the application shell/index, global state framework, filtering, due dates, categories, or other todo extensions.
- Replace starter styling/assets with a small responsive stylesheet for the todo form/list, completed state, action buttons, focus indicators, and status messages. Set appropriate document title/meta in the TanStack root route.
- Add frontend lint configuration/scripts compatible with the generated stack and focused tests using the starter-compatible Vitest setup and Testing Library (or the current template’s equivalent). Cover initial loading/list rendering, validation/create behavior, toggle, delete, and an API error state with network calls mocked rather than requiring PostgreSQL.

### 3. Build the NestJS API

- Under `web/apps/api`, create a Bun-runnable NestJS TypeScript application with canonical Nest configuration (`nest-cli.json`, TypeScript build configs, source entry point, lint config, and package scripts). Retain Bun as package manager/runtime while using Nest’s compiler/build tooling where required.
- In `src/main.ts`, configure:
  - a global `/api` prefix;
  - environment-driven port (default `3001`);
  - CORS restricted to the configured frontend origin (default `http://localhost:3000`);
  - a global `ValidationPipe` with whitelist/transform behavior.
- Configure `@nestjs/config`, `@nestjs/typeorm`, TypeORM, and the PostgreSQL driver in the root module. Validate/clearly fail on missing or malformed database configuration. Disable `synchronize`; use the same database options for the Nest runtime and TypeORM CLI/data source.
- Add a todo feature module with:
  - a `Todo` entity containing UUID `id`, required bounded `title`, boolean `completed` defaulting to false, and created/updated timestamps;
  - create and update DTOs with `class-validator` constraints and API-side title trimming;
  - a repository-backed service for ordered listing, creation, partial update, and deletion;
  - a controller exposing `GET /api/todos`, `POST /api/todos`, `PATCH /api/todos/:id`, and `DELETE /api/todos/:id` (returning a no-content response on successful deletion);
  - proper `404` handling for unknown IDs and `400` handling for invalid/empty payloads.
- Add a checked-in initial TypeORM migration that creates the `todos` table, including defaults and timestamps, plus API scripts/data-source configuration to run/revert migrations from the `web/` workspace.
- Add focused Nest tests with a mocked TypeORM repository (or a lightweight test module) covering list ordering/return shape, create, update/toggle, delete, validation/error paths, and missing-record behavior without making the normal unit suite depend on a running database.

### 4. Add PostgreSQL Compose configuration

- Add `web/compose.yaml` containing only a PostgreSQL service based on a pinned supported Alpine PostgreSQL image, with values sourced from the local environment/default substitutions, the host port exposed for Nest, a named persistent volume, and a `pg_isready` health check.
- Keep the service/database/volume names specific to this todo app and avoid modifying the unrelated repository-root Compose file.
- Ensure the example database settings used by Compose and Nest agree, and document that Compose creates the database while the migration command creates the application schema.

### 5. Document local operation

- Add `web/README.md` with prerequisites (Bun and Docker Compose), first-run setup, environment copying, dependency installation, database startup, health inspection, migration, dev startup, URLs, API endpoint summary, tests, lint/build commands, database shutdown, and optional volume reset.
- Include a concise architecture/layout section and explain the browser-visible API environment variable and CORS origin so alternate ports can be configured correctly.
- State explicitly that PostgreSQL data survives container restarts in the named volume and that deleting the volume resets local todos.

## Expected files and areas

The exact generated frontend support files may vary with the researched current template, but the resulting change should be contained in these areas:

- `web/package.json`, `web/bun.lock`, `web/.env.example`, `web/compose.yaml`, `web/README.md`
- `web/apps/frontend/package.json` and generated TanStack Start/Vite/TypeScript/lint/test configuration
- `web/apps/frontend/src/routes/`, root/router setup and generated route tree, `src/lib/todos-api.ts`, todo UI components as useful, styles, and frontend tests
- `web/apps/api/package.json`, Nest/TypeScript/lint/test configuration
- `web/apps/api/src/main.ts`, `app.module.ts`, database configuration/data source, `todos/` entity/DTO/module/controller/service/tests, and `migrations/`

Do not modify the repository-root `compose.yaml`, project factory files, or unrelated applications.

## Verification

Run all commands from `web/` unless noted otherwise, and judge each by exit status:

1. `bun install` — resolves the entire workspace and leaves a reproducible lockfile.
2. `bun run lint` — required configured web lint check; covers both frontend and backend.
3. `bun run test` — focused frontend and API tests pass without requiring an external database.
4. `bun run build` — required configured web build check; builds both TanStack Start and NestJS from a clean source tree.
5. `docker compose config` — validates interpolation and Compose syntax.
6. Copy `.env.example` to `.env`, then run `docker compose up -d` and `docker compose ps`; wait for the PostgreSQL service to become healthy.
7. Run the documented migration command and start the API/frontend. Exercise the complete persistence path through the REST API or browser: create a todo, list it, toggle it complete, restart the API (and optionally the database container without removing its volume), confirm it remains, delete it, and confirm it no longer appears. Also verify invalid create/update payloads and unknown IDs return the documented 4xx responses.
8. Confirm the frontend loads at its documented URL, has no browser console/CORS failures, and visibly handles empty, loading, completed, deletion, and backend-error states.
9. Stop local services with `docker compose down` without deleting the named volume after verification.

The final implementation is complete only when the repository-configured commands exactly invoked as `bun run lint` and `bun run build` from `web/` both pass.