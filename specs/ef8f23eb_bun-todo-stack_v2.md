# Plan: Bun TanStack Start Todo Stack

## Objective

Build a self-contained todo application under `web/` with:

- a Bun-managed React frontend using TanStack Start and its Vite plugin;
- a NestJS REST API;
- PostgreSQL persistence supplied by a local Docker Compose service;
- workspace-level lint, build, test, migration, and development commands.

The todo scope is limited to listing, creating, completing/reopening, and deleting items. Do not add authentication, deployment infrastructure, or unrelated todo features. The required repository checks run from `web/` and must pass exactly as `bun run lint` and `bun run build`.

## Researched conventions to apply

Use the completed official-documentation research in `adws/adw_data/sessions/ef8f23eb/context_handoff/research.md` as the bootstrap reference:

- Configure Vite with `tanstackStart()` from `@tanstack/react-start/plugin/vite` **before** `viteReact()`.
- Export `getRouter()` from `src/router.tsx`, construct the router from generated `src/routeTree.gen.ts`, and enable scroll restoration.
- Build the document shell with `createRootRoute`, `HeadContent`, `Outlet`, and `Scripts` in `src/routes/__root.tsx`.
- Let the TanStack Vite integration generate the file-based route tree from `src/routes/` and keep that generated file in the form expected by the current toolchain.
- Use Bun’s native workspace filtering/workspace execution for root scripts rather than introducing another package manager.
- Bootstrap Nest through `NestFactory.create(AppModule)`, with the global API prefix, CORS, validation, and port configured before listening.

The research provides enough current external guidance; implementation should not pause for another research phase. If installed package behavior exposes a small mismatch with the documented examples, retain the current official package conventions and note the adjustment in `web/README.md`.

## Architecture and assumptions

- Create a private Bun workspace rooted at `web/` with `apps/frontend` and `apps/api` packages.
- Run the frontend on port `3000`, the API on port `3001`, and PostgreSQL on host port `5432` by default, while allowing environment overrides.
- Run application processes on the host with Bun; Compose contains only PostgreSQL.
- Use Nest’s TypeORM integration with the `pg` driver and an explicit checked-in migration. Keep `synchronize: false`.
- Store shared local configuration in `web/.env`; commit only `web/.env.example`. Point Vite and Nest/TypeORM explicitly at the workspace-root environment file so commands behave consistently when workspace scripts execute from package directories.
- Use a browser-facing `VITE_API_URL` defaulting to `http://localhost:3001`, and restrict API CORS to `FRONTEND_ORIGIN`, defaulting to `http://localhost:3000`.
- Commit `web/bun.lock`; do not create npm, Yarn, or pnpm lockfiles.

## Implementation plan

### 1. Create the Bun workspace and shared commands

- Add `web/package.json` with `private: true`, `apps/*` workspaces, the active Bun package-manager version, and root scripts for:
  - parallel frontend/API development via Bun workspace filtering;
  - individual frontend and API development;
  - sequential or fail-propagating workspace lint and build operations;
  - workspace tests;
  - API migration run/revert operations.
- Give the two workspace packages distinct names and ensure each defines `dev`, `lint`, `build`, and `test` so root commands do not silently skip required work.
- Add `web/.env.example` with aligned Compose and application defaults: PostgreSQL database, user, password, host port, `DATABASE_URL`, API port, frontend origin, and public API URL.
- Install once with Bun from `web/` and commit the resulting `bun.lock`.

### 2. Bootstrap the TanStack Start frontend

- Create `web/apps/frontend` from the researched TanStack Start build-from-scratch/current starter conventions, using React, TypeScript, Vite, `@tanstack/react-start`, and `@tanstack/react-router` under Bun.
- Add the canonical Vite, TypeScript, lint, and test configuration. In `vite.config.ts`:
  - set the development port to `3000`;
  - set `envDir` to the workspace root if needed for `web/.env`;
  - order `tanstackStart()` before `viteReact()`.
- Add the required TanStack Start shell:
  - `src/router.tsx` exporting `getRouter()` around the generated route tree;
  - `src/routes/__root.tsx` containing document metadata, stylesheet linkage/import, `HeadContent`, `Outlet`, and `Scripts`;
  - `src/routes/index.tsx` as the only product route;
  - generated `src/routeTree.gen.ts` produced by the TanStack tooling rather than hand-maintained route declarations.
- Remove starter demos and sample assets. Set the page title and metadata for the todo app.

### 3. Implement the todo frontend

- Add a typed API client such as `src/lib/todos-api.ts` with a `Todo` contract and methods for:
  - `GET /api/todos`;
  - `POST /api/todos`;
  - `PATCH /api/todos/:id`;
  - `DELETE /api/todos/:id`.
- Read `VITE_API_URL` with a local API fallback. Parse successful JSON consistently and convert non-2xx responses into useful errors for the UI.
- Build the index route/component to:
  - load todos on mount;
  - create from a trimmed, required title;
  - toggle an item’s `completed` value;
  - delete an item;
  - update displayed state from API responses rather than pretending persistence succeeded.
- Include explicit initial-loading, empty, mutation-pending, and recoverable error states. Disable only relevant controls while requests are pending and make the form, checkbox/toggle, delete control, status messages, and labels accessible by keyboard and assistive technology.
- Add a compact responsive stylesheet with clear focus states and a visible completed-item treatment. Do not add filtering, due dates, categories, drag-and-drop, global state tooling, or additional routes.
- Add frontend tests with the starter-compatible Vitest/Testing Library setup. Mock the API boundary and cover initial list/empty rendering, title validation and create, toggle, delete, and a request failure.

### 4. Implement the NestJS API

- Create `web/apps/api` as a Bun-runnable NestJS TypeScript package with `nest-cli.json`, build/test TypeScript configuration, lint configuration, and package scripts.
- In `src/main.ts`:
  - create `AppModule` with `NestFactory`;
  - set the global prefix to `api`;
  - enable CORS only for the configured frontend origin;
  - install a global `ValidationPipe` with `whitelist`, `transform`, and rejection of unexpected fields as appropriate;
  - listen on the configured API port, default `3001`.
- Configure `@nestjs/config`, `@nestjs/typeorm`, TypeORM, and `pg` in `AppModule`. Resolve `web/.env` predictably from both development and CLI contexts, validate required database settings, register entities/migrations explicitly, and keep schema synchronization disabled.
- Add a reusable TypeORM CLI `DataSource` that consumes the same configuration as Nest. Ensure compiled and source migration paths work for the documented migration commands.

### 5. Add the todo persistence and REST feature

- Create a `todos` feature module with:
  - a `Todo` entity using UUID `id`, bounded non-empty `title`, `completed` defaulting to `false`, and created/updated timestamps;
  - create/update DTOs using `class-validator` and `class-transformer`, including server-side title trimming;
  - a repository-backed service;
  - a REST controller.
- Implement these contracts:
  - `GET /api/todos` returns all todos in a stable newest-first order;
  - `POST /api/todos` validates and persists a new incomplete todo, returning it;
  - `PATCH /api/todos/:id` accepts title and/or completed, rejects an empty update, persists it, and returns the updated todo;
  - `DELETE /api/todos/:id` deletes an existing todo and returns HTTP 204.
- Return HTTP 404 for unknown IDs and HTTP 400 for malformed UUIDs, blank/oversized titles, unknown fields, and empty update bodies.
- Add an initial migration under the API package that creates the `todos` table, defaults, and timestamps, with a correct down migration.
- Add focused Nest unit/controller tests using a mocked repository or test provider. Cover creation, ordered listing, update/toggle, deletion, invalid input behavior at the controller boundary, and missing records without requiring PostgreSQL for the normal test command.

### 6. Add PostgreSQL Compose support

- Add `web/compose.yaml` with one PostgreSQL service using a pinned supported Alpine image.
- Supply database name/user/password and host-port interpolation from `web/.env`, mount a todo-specific named volume, and add a `pg_isready` health check.
- Do not modify or depend on the unrelated repository-root `compose.yaml`.
- Keep Compose values and `DATABASE_URL` defaults synchronized. Compose creates the database/container only; the migration command creates the application schema.

### 7. Document the application

- Add `web/README.md` covering:
  - architecture and directory layout;
  - Bun and Docker Compose prerequisites;
  - copying `.env.example`, installing dependencies, starting PostgreSQL, checking health, running migrations, and starting both apps;
  - frontend/API URLs and endpoint payloads;
  - test, lint, build, and migration commands;
  - CORS and public API URL configuration;
  - stopping containers and optionally resetting the named volume.
- Explain that the named volume preserves todos across normal container restarts and that removing it intentionally resets local data.

## Expected change surface

Keep changes under the requested application scope:

- `web/package.json`, `web/bun.lock`, `web/.env.example`, `web/compose.yaml`, `web/README.md`
- `web/apps/frontend/package.json`, Vite/TypeScript/lint/test configuration, TanStack router/root/index route and generated route tree, API client, styles, and tests
- `web/apps/api/package.json`, Nest/TypeScript/lint/test configuration, bootstrap/root module, database/data-source configuration, todo entity/DTO/module/service/controller/tests, and migration

Do not alter the repository-root Compose configuration, factory code, `projects.yaml`, or unrelated projects.

## Verification

Run these from `web/` and use command exit status as the result:

1. `bun install` — installs both workspace packages and leaves the committed Bun lockfile current.
2. `bun run lint` — required repository web lint check; verifies frontend and API.
3. `bun run test` — runs focused frontend and API tests without an external database.
4. `bun run build` — required repository web build check; builds TanStack Start and NestJS.
5. `docker compose config` — validates Compose syntax and interpolation.
6. Copy `.env.example` to ignored `.env`, run `docker compose up -d`, and wait until `docker compose ps` reports PostgreSQL healthy.
7. Run the documented migration command, then start both applications with the root development command.
8. Exercise the full path in the browser or through the API: create a todo, list it, toggle it complete, restart the API and PostgreSQL container without removing the volume, verify the todo remains, delete it, and verify it is gone.
9. Verify blank/invalid requests and unknown IDs return the intended 4xx statuses; verify the browser has no CORS or console errors and displays loading, empty, completed, delete, and backend-error states.
10. Stop PostgreSQL with `docker compose down` without removing its volume.

Completion requires the end-to-end persistence check and successful execution of the exact configured checks `bun run lint` and `bun run build` from `web/`.