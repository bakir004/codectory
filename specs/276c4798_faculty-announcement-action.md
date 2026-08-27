# Plan: Add the faculty announcement creation action

## Objective

Make the existing PostgreSQL-backed announcement creation flow a prominent, role-aware dashboard action labeled **Create announcement**. Faculty dashboard viewers can open the existing creation dialog from the Announcements header and save a new announcement; student viewers do not receive that action.

## Scope and constraints

- Limit implementation changes to `web/`.
- Preserve the existing TanStack Start `/` file route, announcement dialog/form, validation, server function, repository insert, loader invalidation, and PostgreSQL schema. The requested label, header placement, dialog behavior, and persistence path already exist and should be reused rather than duplicated.
- Introduce an explicit typed dashboard-viewer role in the web UI and pass it into the Announcements feature. Because this project currently has no authentication/session system and authentication remains out of scope, this change is UI role gating, not a security authorization boundary; do not invent credentials, cookies, middleware, or a second persistence mechanism.
- Keep every rendered button red with contrasting text and an obvious keyboard focus indicator. Preserve semantic headings, dialogs, labels, inline errors, pending states, responsive layout, and focus behavior.
- Do not alter announcement edit/delete behavior beyond any refactoring needed to isolate the create-action visibility.

## Implementation steps

### 1. Model and test the create-action role policy

Add `web/src/features/announcements/permissions.ts` with:

- a narrow exported dashboard role type covering `student` and `faculty`;
- a small pure predicate that returns true only for the faculty role when deciding whether to expose announcement creation.

Add `web/src/features/announcements/permissions.test.ts` using Bun's test API. Assert that faculty is allowed and student is denied. Keep this policy independent of React and PostgreSQL so both branches are deterministic and focused.

### 2. Make the existing Announcements create control role-aware

Update `web/src/features/announcements/announcement-controls.tsx`:

- accept the typed viewer role as an `Announcements` prop and derive create permission through the shared predicate;
- render the existing red **Create announcement** button prominently beside the Announcements title/description only for faculty;
- retain its current click behavior: clear edit state and open the existing `Dialog` in creation mode;
- keep the existing `AnnouncementForm` submission path through `addAnnouncement`, `router.invalidate()`, close-on-success behavior, validation, saving/error feedback, and red dialog buttons unchanged;
- adjust the empty-state copy by role so students are not instructed to use a hidden creation action, while faculty still receives a useful creation prompt;
- keep the header responsive (allow title/action wrapping or stacking at narrow widths) and preserve the `announcements-heading` association.

Do not add a second form, dialog, server function, repository method, or database table. The existing `addAnnouncement` → `createAnnouncement` PostgreSQL flow is the required persistence implementation.

### 3. Supply the dashboard's viewer role at the route boundary

Update `web/src/routes/index.tsx` to define the current demo dashboard viewer's typed role at the route/component boundary and pass it to `Announcements`.

- Keep the default `/` experience as the existing student-facing dashboard, so the create action is absent for the student viewer.
- Provide the faculty dashboard mode through a validated TanStack Router search value (for example, `?role=faculty`), defaulting invalid or omitted values to `student`; use the role only to choose the dashboard view and create-action visibility.
- Reflect the selected view in the footer text so manual verification makes the active role unambiguous, without changing dashboard data, announcement records, or server APIs.
- Do not present this demo role selector as authentication or authorization. Do not add a role-toggle button (which would itself create an unspecified dashboard action).

If route search validation is factored into a pure helper, place it with dashboard data and add focused student/default/faculty cases to `web/src/features/dashboard/dashboard-data.test.ts`; otherwise keep the validation narrow and type-safe in the route.

### 4. Update the web write-up

Update `web/README.md` to describe:

- the faculty-only **Create announcement** action in the Announcements header;
- reuse of the accessible creation dialog and existing validated PostgreSQL create path;
- the student view's lack of the create action and role-appropriate empty state;
- that role selection is a demo UI context and not authentication/authorization;
- the checks actually run and their outcomes, including whether manual browser and live PostgreSQL verification were performed.

Do not claim verification that was not executed.

## Verification

Run from `web/` and judge each command by its exit status:

1. `bun run test` — the new faculty/student permission tests, any search-role tests, announcement validation tests, and assignment sorting tests pass.
2. `bun run lint` — lint succeeds.
3. `bun run build` — the TanStack Start client and server production build succeeds.

Manually inspect the running `/` dashboard at narrow and desktop widths:

- with the default/ student view, the Announcements header and records remain visible but **Create announcement** is absent, and an empty list does not tell students to create one;
- with the faculty role search value, a prominent red **Create announcement** button appears in the Announcements header with a visible keyboard focus indicator;
- activating it by mouse and keyboard opens the existing creation dialog, labels and validation remain accessible, Cancel closes it, and narrow layouts do not overflow;
- if a local PostgreSQL service and migrated database are available, submit a valid announcement and confirm it persists, the dialog closes, and the refreshed list shows the new record; otherwise record that live persistence was not manually exercised.

## Expected files

- Add `web/src/features/announcements/permissions.ts`.
- Add `web/src/features/announcements/permissions.test.ts`.
- Modify `web/src/features/announcements/announcement-controls.tsx`.
- Modify `web/src/routes/index.tsx`.
- Optionally modify `web/src/features/dashboard/dashboard-data.test.ts` only if route-role parsing is extracted for focused testing.
- Modify `web/README.md`.

No implementation files outside `web/` are part of the work. The session plan and its required spec copy are workflow artifacts only.