# Frontend Guide

## Architecture

- Keep UI code in a feature-oriented structure rather than one large component tree.
- Separate presentation components from data access, server state, and domain logic.
- Keep routes thin: route modules compose screens; reusable behavior belongs in components or hooks.
- Use TanStack Router/Start conventions consistently and keep browser-only code out of server modules.
- Model API boundaries explicitly with typed request and response shapes.
- Keep shared state minimal; prefer local state for local concerns and query/server state for remote data.

## Code style

- Use TypeScript with strict typing; avoid `any` and unsafe casts unless there is a documented reason.
- Prefer small, composable functional components and named exports.
- Use clear names that describe intent; avoid abbreviations and boolean names without an `is`, `has`, or `can` prefix.
- Keep JSX declarative and move non-trivial transformations into named functions.
- Follow the formatter and linter configuration. Do not introduce competing formatting conventions.
- Keep imports organized and remove unused code, dead styles, and console debugging before completion.

## Documentation

- Document non-obvious architectural decisions near the relevant module or in the project README.
- Public components and hooks should have concise usage notes when their behavior is not self-evident.
- README instructions must include prerequisites, install commands, development commands, and production/build commands.
- Keep documentation task-oriented and verify commands whenever setup changes.

## Testing

- Test user-visible behavior and important data flows rather than implementation details.
- Cover loading, empty, success, and error states for remote data.
- Add focused tests for non-trivial hooks, transformations, validation, and accessibility-sensitive interactions.
- Prefer deterministic tests with isolated fixtures; do not depend on live external services.
- Run lint, type checks, tests, and the production build before declaring frontend work complete.
