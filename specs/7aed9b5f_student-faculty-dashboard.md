# Plan: Add a shadcn/ui Student Faculty Dashboard

## Objective

Replace the starter `/` page with a responsive, student-facing faculty dashboard backed only by typed dummy data. The page must make upcoming calendar activities, assignments ordered by nearest due date, recent assignment scores, professor and administration announcements, and enrolled courses easy to scan. Use locally owned shadcn/ui primitives and preserve the existing TanStack Start architecture. Authentication, persistence, backend/API integration, live data, and non-student views remain out of scope.

## Required current-documentation research

Before installing or configuring anything, use ctx7 to retrieve the latest official shadcn/ui documentation rather than relying on remembered commands. Research and apply:

1. The current setup for adding shadcn/ui to an existing React + TypeScript + Vite application, including the supported Tailwind CSS version, Vite plugin/configuration, global CSS directives/imports, CSS-variable theming, and source alias setup.
2. The current `components.json` schema and Bun-compatible CLI commands for initialization and adding the selected primitives.
3. The official current implementations/APIs and dependencies for Card, Badge, Avatar, Separator, and Progress; include Button only if the delivered dashboard has a genuine interactive action.
4. How that Vite setup should be composed with an existing TanStack Start Vite plugin stack. Do not replace or disable TanStack Start routing/build integration.

Use the exact current package names, config shape, CLI invocation, and generated component patterns returned by the official docs. Keep component source in the repository; do not add a dashboard template or prebuilt page package.

## Repository constraints and guide decisions

- The app is a minimal TanStack Start project. Keep `/` in `web/src/routes/index.tsx`, root document concerns in `web/src/routes/__root.tsx`, router setup in `web/src/router.tsx`, and TanStack Start integration in `web/vite.config.ts`.
- Preserve Vite port `3000`, React integration, `tanstackStart()`, and existing TypeScript path-resolution behavior while adding the researched shadcn/Tailwind setup.
- There is currently no app stylesheet, shadcn configuration, component library, or test script. Tailwind/shadcn dependencies are also absent from `web/bun.lock`.
- Follow `guides/web/style.md`: semantic and responsive markup is required, and every actual `<button>` must have a red background, accessible contrasting text, and a clearly visible keyboard focus state. Prefer omitting decorative/nonfunctional controls; if a shadcn Button is genuinely used, ensure every rendered variant obeys this project-specific rule.
- Keep all dummy data client-safe; no server functions are needed.
- Do not hand-edit generated `web/src/routeTree.gen.ts`.
- Package installation will update `web/bun.lock`. The official setup is also expected to require `web/components.json` and may require minimal alias changes in `web/tsconfig.app.json` and/or `web/tsconfig.json`; include these necessary supporting files even though the requested primary areas are `web/src`, `web/package.json`, `web/vite.config.ts`, and `guides/web/`.
- The engineer explicitly requires this handoff plan under `adws/adw_data/sessions/...`; that direct request overrides the factory guide’s general prohibition on editing session runtime records. No implementation should otherwise alter runtime records.

## Implementation steps

### 1. Install and configure shadcn/ui

- From `web/`, use the researched current shadcn CLI flow in-place; do not scaffold another application.
- Update `web/package.json` and `web/bun.lock` only with dependencies/devDependencies needed by the researched Tailwind/shadcn setup, selected primitives, class-merging utility, and any icons actually rendered. Add a `test` script using Bun’s test runner for the focused data test below.
- Create `web/components.json` using the current official schema. Point its stylesheet and component/lib aliases at the actual `web/src` locations and select CSS variables/icon configuration consistently with the implementation.
- Add the documented `@/*` (or current shadcn-required) source alias in the smallest set of TypeScript/Vite configuration files needed for the application, tests, and CLI to agree. Preserve the repository’s existing project-reference and `resolve.tsconfigPaths` setup.
- Update `web/vite.config.ts` to compose the current official Tailwind Vite integration with `tanstackStart()` and React. Retain the current server port and path resolution, and use the plugin ordering supported by the researched docs.
- Add a single global stylesheet under `web/src/` using the current official Tailwind import/directives and shadcn theme tokens. Apply a restrained academic visual theme, sensible base typography/backgrounds, responsive defaults, and accessible focus/contrast styles without retaining unused starter CSS.
- Import that stylesheet once through `web/src/routes/__root.tsx` using the supported TanStack Start pattern. Replace starter title metadata and add a concise dashboard description.

### 2. Add local shadcn/ui primitives

- Add the current official source implementations under `web/src/components/ui/` for the primitives actually used: Card, Badge, Avatar, Separator, and Progress are the intended baseline. Add Button only if the page implements a useful real action; do not add unused primitives.
- Add `web/src/lib/utils.ts` with the current official `cn` helper required by generated primitives.
- Keep generated source close to official output, making only configuration/import or project-style adjustments that are necessary. If Button is included, make its available/rendered variants red with high-contrast text, clear hover/disabled treatment, and a visible `focus-visible` indicator. Do not use neutral or outline `<button>` styling that violates the guide.

### 3. Create deterministic typed dummy data and sorting behavior

- Add `web/src/features/dashboard/dashboard-data.ts` (and colocated types if useful) with realistic local records for:
  - upcoming calendar activities: ISO date/time, display details, category, and optional location;
  - assignments: identifier, course, ISO due timestamp, and status;
  - latest scores: assignment/course, earned and possible points or percentage, and graded date;
  - announcements: title/excerpt, timestamp, author, and an explicit professor or administration source type, with at least one of each;
  - enrolled courses: code, title, professor, meeting details, and optional labeled progress/accent metadata.
- Export a pure `sortAssignmentsByDueDate` helper. It must return a new nearest-to-farthest array, leave its input unchanged, and use a documented deterministic tie behavior (stable source order is acceptable).
- Render the assignment section from that helper rather than relying on manually ordered JSX. Keep every record local and static; add no fetch, loader, storage, server function, authentication placeholder, or fake API abstraction.

### 4. Build the dashboard UI

- Replace the placeholder `Home` content in `web/src/routes/index.tsx` while preserving `createFileRoute('/')`. Keep the route composition-focused by extracting meaningful section components under `web/src/features/dashboard/` when the page becomes substantial.
- Build a semantic dashboard shell with a student/university identity header, logical heading hierarchy, `<main>` and labeled `<section>` elements, list/article markup for repeated records, and `<time dateTime>` for dates.
- Include all required sections in a scannable responsive layout:
  - **Upcoming activities** in chronological order with date/time, type, and location where present;
  - **Assignments** visibly ordered by nearest due timestamp, with course, due information, and status badges;
  - **Latest scores** with assignment/course and an unambiguous textual score;
  - **Latest announcements** with recent professor and administration entries whose source is explicit, not color-only;
  - **Enrolled courses** with course code/name, professor, and meeting information, plus progress only when accompanied by a text value.
- Use shadcn Cards for grouping and a deliberate mix of Badge, Avatar, Separator, and Progress where appropriate so the page clearly uses the installed component system rather than recreating equivalents ad hoc.
- Icons must be supplemental: hide decorative icons from assistive technology, and label any icon that uniquely conveys information.
- Make the page one-column at narrow widths and a balanced multi-column grid at larger widths, with no horizontal overflow, readable contrast, and touch-friendly spacing. Avoid nonfunctional menus, filters, links, or “view all” buttons. If navigation links are added, keep them semantic anchors rather than buttons.

### 5. Add a focused behavior test

- Add `web/src/features/dashboard/dashboard-data.test.ts` using `bun:test`.
- Cover ascending due-date ordering from deliberately unsorted input, non-mutation of the source array, and deterministic handling of equal due dates.
- Keep this pure-data test free of DOM/browser dependencies; a heavyweight component test framework is not warranted for this static dashboard.

### 6. Document the feature in the requested guide area

- Add `guides/web/student-faculty-dashboard.md` (or an equally specific unused filename) rather than creating a separate `web/guides/` tree.
- Describe the delivered user-visible sections, the fact that all records are dummy/local, the selected shadcn primitives and current setup approach, the source and sorting behavior of assignment data, responsive/accessibility choices, and the project-specific red-button rule.
- State the non-goals: authentication, persistence, backend APIs, live faculty data, and non-student views.
- Record the exact automated and manual verification actually performed and its outcomes; do not claim commands or browser checks that were not run.

## Verification

Run from `web/` and judge every command by exit status:

1. `bun run test` — the focused due-date sort, immutability, and tie-behavior tests pass.
2. `bun run lint` — all route, feature, data, test, utility, and local component source passes Oxlint.
3. `bun run build` — TanStack Start/Vite production compilation succeeds, proving the CSS integration, aliases, SSR rendering, and component imports resolve.
4. Start `bun run dev` and inspect `/` at narrow mobile and wide desktop widths. Confirm all five required information areas appear, assignments are visibly nearest-due-first, both announcement source types are present, content reflows without clipping/overflow, and there are no runtime or hydration errors.
5. Keyboard-check all interactive elements for a visible focus indicator. Inspect every rendered `<button>` (if any) in default, hover, focus, and disabled states to verify it remains red with contrasting text.
6. Inspect semantic structure and accessible names: heading order, section labels, list markup, machine-readable times, textual progress/score equivalents, and non-color-only status/source labels.
7. Review the final diff to ensure it contains no API/auth/persistence/live-data work, no non-student views, no manual change to `routeTree.gen.ts`, no unrelated changes, and an accurate `guides/web/student-faculty-dashboard.md` verification record.
