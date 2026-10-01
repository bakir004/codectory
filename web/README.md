# Todo app

A small full-stack todo app managed as a Bun workspace:

- `apps/frontend` — React, TanStack Start, TanStack Router, and Vite
- `apps/api` — NestJS REST API, TypeORM, and PostgreSQL persistence
- `compose.yaml` — PostgreSQL only (the app processes run with Bun)

## Prerequisites

Install Bun and Docker with the Docker Compose plugin. From this directory:

```sh
cp .env.example .env
bun install
docker compose up -d
bun run migration:run
bun run dev
```

The frontend is at <http://localhost:3000> and the API is at
<http://localhost:3001/api/todos>. PostgreSQL health can be checked with
`docker compose ps`.

## Configuration

`.env.example` contains matching defaults for Compose and the applications.
`DATABASE_URL` controls the API connection, `API_PORT` controls the API,
`FRONTEND_ORIGIN` controls CORS, and `VITE_API_URL` is the browser-facing API
URL. The named `todo-postgres-data` volume preserves todos across normal
container restarts. Use `docker compose down -v` only when you intentionally
want to reset local data.

## API

- `GET /api/todos` — list todos, newest first
- `POST /api/todos` — create with `{ "title": "Buy coffee" }`
- `PATCH /api/todos/:id` — update `{ "title": "..." }` and/or `{ "completed": true }`
- `DELETE /api/todos/:id` — delete a todo (204)

Requests are validated and unexpected fields, blank titles, malformed UUIDs, and
unknown todo IDs are rejected with a 4xx response.

## Commands

Run both applications with `bun run dev`, or use `bun run dev:frontend` and
`bun run dev:api` separately. The required deterministic quality checks are:

```sh
bun run format:check
bun run lint
bun run typecheck
bun run test
bun run build
```

`bun run format` writes Biome formatting changes; `format:check` verifies
formatting without modifying files. These five non-mutating checks cover both
applications where applicable. Production output is created by `bun run build`.

Database migrations can be run with:

```sh
bun run migration:run
bun run migration:revert
```

Stop PostgreSQL with `docker compose down`; this leaves the named volume intact.
