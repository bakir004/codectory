# Architecture

- Use TanStack Start file-based routes in `src/routes/`.
- Keep router setup in `src/router.tsx` and Vite/TanStack Start integration in `vite.config.ts`.
- Prefer TanStack Start server functions for server-only behavior; do not put server-only code directly in route components.
