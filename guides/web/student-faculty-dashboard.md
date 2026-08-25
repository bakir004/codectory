# Student faculty dashboard

The `/` route now provides a responsive, student-facing Campus Compass dashboard with upcoming activities, nearest-due assignments, latest scores, professor and administration announcements, and enrolled courses. All records are typed dummy data in `web/src/features/dashboard/dashboard-data.ts`; there are no APIs, authentication, persistence, or non-student views.

## UI and accessibility

The page uses locally owned shadcn/ui Card, Badge, Avatar, Separator, and Progress primitives, with Lucide icons as decorative supplements. Tailwind CSS v4 is integrated through the Vite plugin and configured through `components.json` and CSS variables. Semantic sections, lists, articles, labeled headings, `time[dateTime]` elements, textual source/status labels, and textual progress values support scanning and assistive technology. The layout changes from a single-column mobile flow to a three-column desktop grid without horizontal overflow. No interactive buttons are rendered, so the project’s rule that every button be red remains applicable without inventing nonfunctional controls.

Assignments are rendered from `sortAssignmentsByDueDate`, which returns a new stable ascending copy and preserves source order for equal timestamps.

## Verification

- `bun run test` — passed (2 focused sorting tests).
- `bun run lint` — passed with existing Fast Refresh export warnings in route files.
- `bun run build` — passed for client and SSR production bundles.

Manual browser inspection was not performed in this change.
