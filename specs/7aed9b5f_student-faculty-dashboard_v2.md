# Plan: Add a shadcn/ui Student Faculty Dashboard

## Objective

Replace the starter `/` page with a responsive student-facing faculty dashboard backed entirely by typed dummy data. Students must be able to scan upcoming calendar activities, assignments ordered by nearest due date, latest assignment scores, recent professor and administration announcements, and enrolled courses. Preserve TanStack Start, use locally owned shadcn/ui components, and exclude authentication, persistence, APIs, live faculty data, and non-student views.

## Researched implementation basis

Context7 research against the latest official `/shadcn-ui/ui` documentation is complete in `adws/adw_data/sessions/7aed9b5f/context_handoff/research.md`. Apply these findings directly; no additional external research is needed:

- Use Tailwind CSS v4 through `tailwindcss` and `@tailwindcss/vite`, with the Tailwind plugin before `tanstackStart()` and React in `web/vite.config.ts`.
- Use the current shadcn CSS-variable setup with `@import "tailwindcss"`, `@import "tw-animate-css"`, the current shadcn Tailwind stylesheet import when generated/required, `@theme inline`, base tokens, and base-layer styles.
- Use a New York-style, non-RSC, TypeScript `web/components.json` with CSS variables, Lucide icons, `src/index.css`, and `@/components`, `@/components/ui`, and `@/lib/utils` aliases.
- Use Bun-compatible shadcn CLI commands (`bunx shadcn@latest ...`) and the current official source for Card, Badge, Avatar, Separator, and Progress. The components use the `cn` helper built from `clsx` and `tailwind-merge`; Badge uses `class-variance-authority`; icons use `lucide-react`.
- Required setup packages identified by research are `@tailwindcss/vite`, `tailwindcss`, `tw-animate-css`, `clsx`, `tailwind-merge`, `class-variance-authority`, and `lucide-react`, plus component-specific Radix packages selected by the current CLI. Do not add Button unless the final design has a genuine interactive action.

## Repository constraints and guide decisions

- Keep `/` as a TanStack Start file route in `web/src/routes/index.tsx`, root document concerns in `web/src/routes/__root.tsx`, router creation in `web/src/router.tsx`, and Vite/TanStack integration in `web/vite.config.ts`.
- Preserve Vite port `3000`, `resolve.tsconfigPaths`, `tanstackStart()`, and React integration. There is no server-only behavior, so do not add server functions.
- Do not hand-edit generated `web/src/routeTree.gen.ts`.
- Follow `guides/web/style.md`: use semantic HTML and responsive layouts. Every rendered `<button>` must be red with contrasting accessible text and an obvious keyboard focus indicator. The simple read-only dashboard needs no button, so avoid decorative or nonfunctional controls rather than inventing actions.
- Dependency installation necessarily updates `web/bun.lock`. The researched setup also requires `web/components.json` and source-alias configuration in the relevant TypeScript project file(s); these are necessary supporting files even though the prompt highlights `web/src`, `web/package.json`, `web/vite.config.ts`, and `guides/web/`.
- The requested handoff artifact under `adws/adw_data/sessions/...` explicitly overrides the general prohibition in `guides/adws/style.md` on editing session runtime records. Do not otherwise change factory/runtime records.

## Implementation plan

### 1. Configure shadcn/ui and Tailwind CSS v4

- From `web/`, initialize shadcn in the existing application rather than scaffolding another Vite project. Use the researched New York/non-RSC/TypeScript/CSS-variable/Lucide choices.
- Add `web/components.json` with the official schema URL, `src/index.css`, empty Tailwind config for v4, and aliases matching the actual source layout.
- Add the researched packages to the correct dependency sections of `web/package.json`, let Bun update `web/bun.lock`, and avoid packages for unused components. Add a `test` script that runs `bun test`.
- Configure `@/*` to resolve to `web/src/*` in the TypeScript configuration read by both the shadcn CLI and app compiler. Because this repo uses project references, apply the smallest compatible alias change to `web/tsconfig.json` and/or `web/tsconfig.app.json`; keep `resolve.tsconfigPaths: true` rather than introducing a duplicate hard-coded Vite alias unless required by the researched setup.
- Update `web/vite.config.ts` to import `@tailwindcss/vite` and use `plugins: [tailwindcss(), tanstackStart(), react()]`, retaining the current port and path-resolution settings.
- Create `web/src/index.css` with the researched Tailwind v4/shadcn imports, `@custom-variant dark`, `@theme inline` mappings, complete light/dark CSS variables required by the generated primitives, and base border/background/foreground styles. Adjust tokens toward a restrained academic look while maintaining accessible contrast.
- Import `web/src/index.css` once from `web/src/routes/__root.tsx`. Replace the starter page title with student-dashboard metadata and add a concise description meta tag.

### 2. Add the local shadcn primitives

- Use `bunx shadcn@latest add card badge avatar separator progress` from `web/` (or the equivalent single current CLI invocation) to add official local source under `web/src/components/ui/`.
- Add/retain `web/src/lib/utils.ts` with the researched `cn(...inputs)` implementation using `clsx` and `tailwind-merge`.
- Keep generated primitives close to official output and do not add unused Button source. If implementation needs an actual button after all, add the official Button and then modify every available/rendered button variant so it has a red background, accessible contrasting text, clear hover/disabled treatment, and a visible `focus-visible` ring.

### 3. Model local dummy data and explicit assignment ordering

- Add `web/src/features/dashboard/dashboard-data.ts` with exported TypeScript types and realistic static records for:
  - upcoming activities with stable identifiers, ISO date/time, title, category, and optional location;
  - assignments with course identity, ISO due timestamp, and submission status;
  - recently scored assignments with course, earned/possible points or percentage, and graded date;
  - announcements with author, timestamp, excerpt, and an explicit `professor` or `administration` source type, including at least one of each;
  - enrolled courses with code, title, professor, meeting details, and labeled progress where useful.
- Export a pure `sortAssignmentsByDueDate` helper that returns a new array sorted ascending by due timestamp. It must not mutate its input and must preserve source order for equal dates (or use another documented deterministic tie-breaker).
- Render assignments from this helper, not from manually preordered JSX. Keep all data static and local; add no fetches, loaders, server functions, storage, authentication placeholders, or fake service layers.

### 4. Build the responsive dashboard route

- Replace the placeholder in `web/src/routes/index.tsx` while preserving `createFileRoute('/')`. Keep the route focused on composition; extract substantial sections into focused files under `web/src/features/dashboard/` such as `dashboard-header.tsx`, `upcoming-activities.tsx`, `assignments-list.tsx`, `scores-list.tsx`, `announcements-list.tsx`, and `courses-grid.tsx` as warranted.
- Build a semantic shell with a student/university identity header, logical heading order, `<main>`, labeled `<section>` elements, list/article markup for repeated records, and `<time dateTime>` elements for dates.
- Include the five acceptance areas:
  - **Upcoming activities:** multiple chronologically displayed calendar items with date/time, category, and location where present.
  - **Assignments:** nearest-due-first output from the sorting helper, with course, due details, and text/status badges.
  - **Latest scores:** recent graded work with course and unambiguous score text.
  - **Latest announcements:** recent entries from professors and administration with author/source type shown in text, not color alone.
  - **Enrolled courses:** course code/name, professor, meeting details, and any progress value in both visual and textual form.
- Use shadcn Card for section/course grouping and an intentional mix of Badge, Avatar, Separator, and Progress so the page visibly uses the installed component system rather than ad hoc equivalents.
- Use Lucide icons only as supplemental decoration. Hide decorative icons from assistive technology; give meaningful icons an accessible name when surrounding text does not already provide it.
- Use a single-column flow on small screens and a balanced multi-column grid on wider screens, with no horizontal overflow, readable spacing/contrast, and touch-friendly targets. Do not add fake navigation, filters, “view all” controls, or other nonfunctional interactions.

### 5. Add focused tests

- Add `web/src/features/dashboard/dashboard-data.test.ts` using `bun:test`.
- Test that deliberately unsorted assignments become ascending nearest-due-first output, the original input array remains unchanged, and equal due dates follow the documented deterministic ordering.
- Keep the test pure and DOM-free; no browser test framework is needed for this static feature.

### 6. Document the delivered feature

- Add `guides/web/student-faculty-dashboard.md` (the requested guide area, not a new `web/guides/` tree).
- Describe the user-visible dashboard sections, local/dummy nature of the data, selected shadcn components, Tailwind v4/Vite setup, assignment sorting source and behavior, responsive/semantic/accessibility decisions, and the all-buttons-red project rule.
- State the non-goals: authentication, persistence, live faculty data, backend APIs, and non-student views.
- Record exact automated and manual verification actually performed and its outcomes. Do not claim checks that were not run.

## Verification

Run commands from `web/` and judge each by exit status:

1. `bun run test` — sorting, immutability, and equal-date tests pass.
2. `bun run lint` — route, feature components, data, tests, utilities, and generated local UI primitives pass Oxlint.
3. `bun run build` — TanStack Start/Vite production compilation succeeds, proving CSS integration, aliases, SSR-safe rendering, and component imports.
4. Run `bun run dev` and inspect `/` at narrow mobile and wide desktop widths. Confirm all five required content areas are present, assignments display nearest due date first, both announcement source types appear, and cards reflow without clipping or horizontal scrolling.
5. Check the browser console for runtime/hydration errors and keyboard-check every interactive element. If any `<button>` exists, verify its default, hover, focus, and disabled states remain red with contrasting text and a visible focus indicator.
6. Inspect heading hierarchy, section labels, list semantics, `dateTime` values, text alternatives for scores/progress, and source/status labels that do not rely on color.
7. Review the final diff for accurate guide documentation, no API/auth/persistence/live-data or non-student work, no manual `routeTree.gen.ts` edit, and no unrelated changes.
