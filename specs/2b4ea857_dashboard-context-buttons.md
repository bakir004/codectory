# Plan: Add contextual red buttons to the student dashboard

## Objective

Add clearly visible, contextually placed buttons throughout the existing `/` student dashboard without removing or replacing any dashboard content. The controls are UI-only placeholders in this scope: do not add navigation, handlers, server functions, APIs, persistence, authentication, or dashboard data-model fields.

## Applicable guidance and constraints

- Keep the dashboard in the TanStack Start file route at `web/src/routes/index.tsx`; no router or server changes are needed.
- Every native button must use a red background, accessible contrasting text, and a visible keyboard focus treatment.
- Preserve semantic sections, headings, lists, time metadata, badges, progress text, and the responsive single-column/three-column layout.
- The task explicitly requests buttons while backend actions are out of scope, so render the controls with `type="button"` and no action wiring. Use descriptive visible labels and contextual `aria-label`s where repeated labels need record-specific meaning.
- Do not alter `web/src/features/dashboard/dashboard-data.ts`; button labels and placement do not require data-model changes.
- The required handoff artifact under `adws/adw_data/sessions/2b4ea857/context_handoff/` is an explicit task override of the general rule against editing session runtime records.

## Implementation steps

### 1. Add one reusable, red-only button primitive

Create `web/src/components/ui/button.tsx` following the existing local UI primitive conventions:

- Accept native `ButtonHTMLAttributes<HTMLButtonElement>` and merge caller classes with `cn`.
- Default `type` to `button` so these presentation-only controls cannot accidentally submit a form.
- Give every instance a red base treatment (for example, `bg-red-700` with white text and a darker red hover state), suitable sizing/rounded styling, and disabled styling that remains recognizably red.
- Include explicit `focus-visible` ring/outline utilities with adequate contrast and an offset so keyboard focus remains obvious.
- If size variants are useful for compact row/card actions, allow only sizing/layout variants; do not introduce color variants that could produce a non-red button.

### 2. Place buttons in relevant dashboard contexts

Update `web/src/routes/index.tsx` to import and consistently use the shared `Button`; do not add ad hoc native buttons with divergent styling.

Add controls without deleting or hiding the current header, records, labels, or metadata:

- In the page header, group the existing avatar with a `View profile` button while keeping the greeting and semester summary intact.
- Add compact section-level actions alongside the heading blocks for Upcoming activities (`View calendar`), Latest scores (`View gradebook`), Assignments (`View all assignments`), and Announcements (`View all announcements`).
- Add a compact `Open course` button to each enrolled-course article, using an `aria-label` that includes the course code or title so repeated button text has a unique accessible name.
- Keep controls visually associated with their heading or course card. Adjust header wrappers with wrapping/flex/grid utilities so titles and buttons stack or wrap cleanly on narrow screens and align horizontally when space permits.
- Ensure button placement does not create horizontal overflow and that existing lists, assignment ordering, course progress, and all dashboard cards remain rendered.
- Keep Lucide icons decorative if any are added to controls; button meaning must remain available from text rather than an icon alone.

### 3. Add focused coverage for the shared style contract

Create `web/src/components/ui/button.test.tsx` using Bun’s test API and `react-dom/server` rendering (no new dependency):

- Verify the primitive renders a native button with `type="button"` by default.
- Verify rendered classes include the red background, contrasting text, and visible focus treatment that enforce the repository-wide button rule.
- Verify caller classes can be merged without dropping the required base styling. Avoid tests for click behavior because actions are intentionally out of scope.

Existing assignment sorting tests must continue to pass unchanged.

### 4. Update the dashboard guide/write-up

Update `guides/web/student-faculty-dashboard.md`:

- Replace the obsolete statement that no interactive buttons are rendered.
- Describe the new header, section, and per-course controls, their shared red styling, keyboard focus treatment, responsive placement, and that they are presentation-only in this scoped change.
- State that all prior dashboard content and typed dummy data remain in place and that no backend/data-model behavior was added.
- Refresh the Verification section with the commands actually run and their results, plus the outcome of manual browser inspection if performed; do not claim checks that were not run.

## Verification

From `web/`:

1. Run `bun run test` and confirm both the new button contract tests and existing assignment sorting tests pass.
2. Run `bun run lint` and assess it by exit status; note any pre-existing warnings separately.
3. Run `bun run build` and confirm both client and SSR production builds complete successfully.
4. Manually inspect `/` at narrow mobile and desktop widths:
   - all original activities, scores, assignments, announcements, courses, avatar, and footer remain visible;
   - the new buttons are visibly red with readable contrasting text;
   - section/header/course controls remain contextually aligned without overlap or horizontal scrolling;
   - keyboard Tab navigation reaches each button in logical document order and shows a clear focus indicator;
   - repeated `Open course` controls expose course-specific accessible names;
   - clicking controls causes no backend, persistence, auth, or data mutation side effects, as required by scope.

## Expected files

- Add `web/src/components/ui/button.tsx`.
- Add `web/src/components/ui/button.test.tsx`.
- Modify `web/src/routes/index.tsx`.
- Modify `guides/web/student-faculty-dashboard.md`.
- Leave dashboard data, router setup, backend behavior, and authentication/persistence untouched.
