# Plan: Add shadcn/ui Student Faculty Dashboard

## Objective
Replace the starter index page with a polished, responsive student-facing faculty dashboard backed entirely by local dummy data. The dashboard will use locally owned shadcn/ui components and let a student scan upcoming calendar activities, assignments in nearest-due-first order, recent assignment scores, professor and administration announcements, and enrolled courses. Authentication, persistence, backend/API work, live faculty data, and non-student experiences remain out of scope.

## Required documentation research
Before changing dependencies or configuration, use ctx7 to retrieve the latest official shadcn/ui documentation and record the applicable guidance for:

1. Installing shadcn/ui into an existing Vite + React + TypeScript application, including the current Tailwind CSS generation, Vite plugin/configuration, global stylesheet directives, CSS-variable theming, and path-alias requirements.
2. Initializing/configuring `components.json` for the current CLI/schema and adding the exact components selected below with Bun.
3. The current official APIs and accessibility expectations for Card, Badge, Avatar, Separator, Progress, and Button (or the closest current official component set if a named component has changed).
4. Compatibility considerations when applying the Vite instructions to the existing TanStack Start Vite plugin stack; preserve TanStack Start rather than replacing its router/build integration.

Use the researched commands, package names, import patterns, and configuration instead of relying on remembered shadcn/Tailwind setup. Keep the resulting components as source files in this repository rather than adding a prebuilt dashboard package.

## Repository findings and constraints
- `web/` is currently a minimal TanStack Start application. `/` is defined by `web/src/routes/index.tsx`; global document metadata and stylesheet loading belong in `web/src/routes/__root.tsx`; router construction is already correctly isolated in `web/src/router.tsx`.
- `web/vite.config.ts` currently composes `tanstackStart()` and React and already enables `resolve.tsconfigPaths`; shadcn/Tailwind integration must be composed into this file without removing those plugins or changing port 3000.
- There is no existing CSS, component library configuration, test setup, or `web/guides/` directory.
- Follow the web guides: retain file-based routing, use semantic HTML and responsive layouts, preserve obvious keyboard focus, and make every actual `<button>` red with accessible contrasting text in all states. This dashboard needs no server function because all data is dummy client-safe data.
- Do not hand-edit `web/src/routeTree.gen.ts`; allow the normal TanStack tooling/build to regenerate it only if necessary.
- Dependency installation will necessarily update `web/bun.lock`. A normal shadcn initialization may also require `web/components.json`; include that supporting configuration even though the request highlights `web/src`, `web/package.json`, `web/vite.config.ts`, and `web/guides/`.
- Preserve unrelated working-tree changes and do not alter factory/session files other than this requested plan artifact.

## Implementation plan

### 1. Install and configure shadcn/ui from the researched official setup
- From `web/`, apply the current official Bun/shadcn initialization flow in a non-destructive way appropriate for this existing app; do not scaffold a second Vite project.
- Update `web/package.json` and `web/bun.lock` with only the current dependencies/devDependencies actually needed by the selected shadcn components, utility helper, icons, Tailwind integration, and focused Bun tests. Add a `test` script using `bun test` if one does not exist.
- Add/update `web/components.json` with the researched schema, style, global CSS path, CSS-variable setting, icon library, and aliases. Keep generated component aliases aligned with the actual source layout.
- Configure the alias expected by shadcn imports. Prefer the current official approach, but account for this repository’s project-reference TypeScript setup: if an alias must be declared in TypeScript as well as Vite, make the smallest necessary `web/tsconfig.app.json` change and document why. Do not break the existing `tsconfigPaths` resolution.
- Amend `web/vite.config.ts` with the current official Tailwind/shadcn Vite integration while retaining `tanstackStart()`, React, `server.port`, and existing path resolution. Keep plugin order compatible with the researched TanStack Start/shadcn guidance.
- Create the researched global stylesheet (for example `web/src/styles.css`) with the official Tailwind import/directives, shadcn design tokens, dark-token definitions if generated, base border/background rules, and a restrained academic visual theme. Avoid carrying unused template CSS.
- Import the global stylesheet once from `web/src/routes/__root.tsx` in the TanStack Start-supported manner, and update the document title/description from the starter text to student-dashboard metadata.

### 2. Add the local shadcn primitives
- Add the current official implementations under `web/src/components/ui/` for the components the dashboard actually uses: Card, Badge, Avatar, Separator, Progress, and Button, adjusting the list only if ctx7 shows a renamed/replaced official primitive.
- Add `web/src/lib/utils.ts` with the official `cn` class-merging helper and use it from the primitives.
- Keep generated component code close to official output; make only project-required adjustments. In particular, ensure every rendered Button variant has a red background, high-contrast text, readable hover/disabled states, and a visible keyboard focus ring as mandated by `guides/web/style.md`. Do not render neutral or outline `<button>` variants that violate this rule. Links may look secondary but should remain semantic anchors, not disguised buttons.

### 3. Model deterministic dummy dashboard data and ordering
- Add a typed local data module such as `web/src/features/dashboard/dashboard-data.ts` containing realistic but clearly dummy records for:
  - upcoming calendar activities with date/time, title, category, and optional location;
  - assignments with course, due timestamp/label, submission status, and identifiers;
  - latest scored assignments with score/total or percentage and course;
  - announcements from both professors and administration, with author/role, timestamp label, category, and excerpt;
  - enrolled courses with code, name, professor, meeting information, progress, and visual accent metadata.
- Export a small pure `sortAssignmentsByDueDate` helper that returns a new nearest-to-farthest array and does not mutate source data. Feed the assignment section from this helper rather than manually arranging JSX, making the “nearest due date” requirement explicit and testable.
- Keep all information static and local. Do not add fetches, loaders, server functions, storage, authentication placeholders, or controls that imply those systems exist.

### 4. Build the dashboard route and composed sections
- Replace the placeholder in `web/src/routes/index.tsx` with the `/` dashboard route, keeping TanStack Start’s `createFileRoute('/')` convention.
- Split substantial UI into focused files under `web/src/features/dashboard/` (for example shell/header, overview, activity/assignment lists, scores/announcements, and courses) so the route remains composition-focused. Use the local shadcn primitives throughout rather than one-off equivalents.
- Build a semantic dashboard shell with a compact university/student identity header and responsive main content. Use headings in a logical hierarchy, `<main>`, `<section>`, lists/articles, `<time dateTime>` where dates are represented, and descriptive labels rather than relying on color or icons alone.
- Include all acceptance content above the fold or in an easily scannable responsive flow:
  - an “Upcoming” calendar card with multiple chronologically presented activities;
  - an “Assignments” card populated through nearest-due-first sorting and clear due/status badges;
  - a “Latest scores” summary with recent graded items and accessible score text;
  - “Announcements” containing recent items from at least one professor and university administration, visibly identifying the source type;
  - an “Enrolled courses” area with course identity, professor/meeting details, and optional labeled progress bars.
- Use shadcn Cards for grouping, Badges for statuses/categories, Avatar for student/author identity, Separator for list structure, Progress only with an accompanying text value, and a Button only for a small useful static affordance if warranted. Do not add nonfunctional navigation menus, filters, or “view all” controls merely for decoration.
- Use Lucide icons only as supplemental decoration; hide decorative icons from assistive technology or provide accessible names where an icon conveys unique information.
- Make the layout adapt cleanly from one column on phones to a balanced multi-column dashboard on wider screens, with no horizontal overflow, sufficiently large touch targets, readable contrast, and visible `:focus-visible` styling. Red is the required button color, not necessarily the dominant page color.

### 5. Add focused behavior tests
- Add a Bun test such as `web/src/features/dashboard/dashboard-data.test.ts` for `sortAssignmentsByDueDate`.
- Verify unsorted dates become ascending nearest-due-first order, input data is not mutated, and equal due dates remain deterministic (preserve source order or use a documented stable tie-breaker).
- Keep the test free of browser/DOM dependencies unless the current setup already provides them; this change does not need a heavyweight UI test framework for a static composition.

### 6. Document the delivered dashboard
- Create `web/guides/student-dashboard.md` and record:
  - the user-visible dashboard sections and that their data is dummy/local;
  - the shadcn/ui components used and the researched setup/configuration approach;
  - the location of dashboard data and the due-date ordering behavior;
  - responsive/accessibility decisions, including the project-specific all-buttons-red rule;
  - explicit non-goals (auth, persistence, APIs/live data, and non-student views);
  - exact automated and manual verification performed, with outcomes filled in after execution.
- Do not replace the factory-provided guides; this is a feature write-up inside the requested `web/guides/` location.

## Verification
Run all commands from `web/` and judge success by exit status:

1. `bun run test` — focused ordering tests pass.
2. `bun run lint` — Oxlint reports no violations in route, data, tests, or generated/local component code.
3. `bun run build` — TanStack Start/Vite completes production compilation, proving CSS, aliases, SSR-safe rendering, and component imports resolve.
4. Run the app with `bun run dev` and inspect `/` at narrow mobile and wide desktop widths:
   - every required section and dummy content type is present;
   - assignments visibly run from earliest to latest due date;
   - announcements include both professor and administration sources;
   - cards reflow without clipping or horizontal scrolling;
   - heading/list/time semantics are sensible and progress has text equivalents;
   - keyboard traversal has visible focus, and every rendered `<button>` is red with contrasting text in default, hover, focus, and disabled states.
5. Check the browser console for hydration/runtime errors and inspect the final diff to ensure there are no fetch/API/auth/persistence additions, no manual edits to generated route-tree output, and no unrelated file changes.
