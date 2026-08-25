# Student faculty dashboard and shadcn/ui setup

## What changed

The web app’s `/` route is now a responsive, student-facing Campus Compass dashboard. It displays upcoming activities, assignments in nearest-due-first order, recent scores, professor and administration announcements, and enrolled spring 2026 courses. The records are typed, static dummy data; the change adds no authentication, persistence, APIs, live faculty data, or non-student views.

The dashboard uses local shadcn/ui Card, Badge, Avatar, Separator, and Progress primitives, plus Lucide icons. The page is semantic and responsive: sections use labeled headings and list/article markup, dates use `time[dateTime]`, progress and scores have text equivalents, and the layout moves from one column to three columns on large screens. No buttons or other nonfunctional controls were added, so the project’s red-button rule is not exercised.

## Where it lives

- `web/src/routes/index.tsx` composes the dashboard and renders all five information areas.
- `web/src/features/dashboard/dashboard-data.ts` contains the exported types and dummy records. `sortAssignmentsByDueDate` returns a new stable ascending copy, preserving source order for equal due timestamps.
- `web/src/features/dashboard/dashboard-data.test.ts` covers due-date ordering, input immutability, and equal-date ordering.
- `web/src/components/ui/` contains the local shadcn primitives; `web/src/lib/utils.ts` provides `cn`.
- `web/src/index.css` adds Tailwind CSS v4, shadcn theme tokens, base styles, and light/dark variables. `web/components.json`, `web/tsconfig.app.json`, and `web/vite.config.ts` configure shadcn aliases and Tailwind’s Vite plugin while retaining TanStack Start and port 3000. `web/src/routes/__root.tsx` imports the stylesheet and supplies dashboard metadata.
- `web/package.json` and `web/bun.lock` add the shadcn/Tailwind, Radix, utility, icon, and test dependencies.
- `guides/web/student-faculty-dashboard.md` records the feature, accessibility decisions, non-goals, and verification results. The two `specs/7aed9b5f_student-faculty-dashboard*.md` files contain the accompanying implementation plans.

## Use and verify

From `web/`:

```sh
bun run test
bun run lint
bun run build
```

The recorded results are: two focused sorting tests passed; lint passed with existing Fast Refresh export warnings in route files; and the client and SSR production bundles built successfully. Manual browser inspection was not performed. Run `bun run dev` and open `/` to view the dashboard.
