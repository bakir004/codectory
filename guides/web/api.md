# API Guide

## Architecture

- Organize the NestJS backend by domain or feature; keep controllers, services, and persistence concerns separated.
- Controllers handle transport concerns only: parsing input, applying validation, and mapping responses.
- Services contain application and domain behavior; repositories or data-access modules contain database interaction.
- Define DTOs for external input and output. Do not expose ORM entities directly as an accidental API contract.
- Validate all external input at the boundary and return consistent HTTP status codes and error shapes.
- Keep configuration environment-based and never commit credentials or machine-specific settings.
- Database migrations and schema changes must be explicit, reviewable, and safe to run from a clean database.

## Code style

- Use strict TypeScript and prefer explicit return types for public methods and service boundaries.
- Use NestJS dependency injection rather than manually constructing providers.
- Keep methods focused and short; extract named helpers when logic has a distinct purpose.
- Use consistent naming: nouns for resources, verbs for actions, and predictable pluralization in routes.
- Avoid hidden side effects, broad exception catches, and duplicated validation rules.
- Keep linting, formatting, and import conventions consistent with the repository configuration.

## Documentation

- Document each resource's purpose, routes, request shape, response shape, and error behavior.
- Keep the API README accurate for environment variables, database setup, migrations, development, and test commands.
- Record architectural decisions and intentional trade-offs in concise decision notes when they affect future work.
- Update API documentation in the same change as route or contract changes.

## Testing

- Unit-test domain and service behavior, including validation and failure paths.
- Add controller or integration tests for important HTTP contracts, status codes, and response shapes.
- Exercise database-backed behavior against an isolated test database or deterministic test container.
- Test authorization and input validation at the boundary when those concerns exist.
- Avoid tests that depend on shared developer databases, network services, clock timing, or test order.
- Run lint, type checks, migrations/schema validation, unit tests, integration tests, and a production build before declaring backend work complete.
