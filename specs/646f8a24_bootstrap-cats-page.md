# Plan: Apply Bootstrap CSS to the Cats Page

## Objective
Load Bootstrap CSS 5.3.3 on the existing cats page and use its responsive layout and component classes while preserving all current copy, semantics, cat-message behavior, and the page’s warm custom theme. Do not add Bootstrap JavaScript or any new content/functionality.

## Files in scope
- Modify `cats-page/index.html`.
- Modify `cats-page/styles.css`.
- Review but do not change `cats-page/script.js`; its existing selectors and message-cycling behavior already work with CSS-only Bootstrap integration.
- Do not modify unrelated files.

## Implementation steps

### 1. Load Bootstrap and apply it to the existing markup (`cats-page/index.html`)
- Add the Bootstrap 5.3.3 minified CSS `<link>` from jsDelivr in `<head>`, including the official integrity hash and `crossorigin="anonymous"` attributes:
  - URL: `https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css`
  - Integrity: `sha384-QWTKZyjpPEjISv5WaRU9OFeRpok6YctnYmDr5pNlyT2bRjXh0JMhjY6hW+ALEwIH`
- Keep `styles.css` after the Bootstrap link so the existing cat-specific palette and intentional theme overrides win in the cascade.
- Do not add Bootstrap’s JavaScript bundle; no Bootstrap JavaScript component is needed.
- Layer Bootstrap classes onto the existing semantic elements rather than replacing their content:
  - Use a Bootstrap `container` for the hero content and main/footer width constraints, plus spacing/alignment utilities where they replace equivalent custom spacing.
  - Convert the facts layout to a Bootstrap `row` with gutters and responsive columns. Add non-semantic column wrappers as needed so each existing `article` can remain a proper Bootstrap `card` with full-height behavior; keep all three facts and their order unchanged.
  - Apply Bootstrap card structure/classes to the existing fact-card content without changing text or heading hierarchy.
  - Apply Bootstrap spacing/text-alignment utilities to the existing message panel where appropriate.
  - Add Bootstrap button component classes (including `btn` and `btn-primary`, with the existing size/shape represented by Bootstrap classes where practical) to the existing message button.
  - Use Bootstrap footer spacing/alignment utilities while retaining the existing footer copy.
- Preserve `id="message-button"`, `id="message-output"`, `aria-controls`, `role="status"`, `aria-live="polite"`, section labels, and all other interaction/accessibility hooks verbatim.
- Keep the existing deferred `script.js` reference unchanged.

### 2. Reconcile custom styling with Bootstrap (`cats-page/styles.css`)
- Retain the custom CSS variables, cream/peach/coral color theme, typography, hero presentation, card visual accents, message-panel treatment, output styling, and reduced-motion/focus accommodations.
- Remove or revise rules that would fight the newly added Bootstrap layout/components:
  - Let Bootstrap’s container and grid classes own the page width, facts columns, gutters, and responsive one-column-to-three-column transition instead of the current custom `facts__grid` grid and its mobile override.
  - Adapt fact-card selectors to the Bootstrap card markup so padding is applied at the correct card/body level and full-height cards remain visually consistent.
  - Replace broad element-level button sizing/component rules with targeted theme overrides for `#message-button`/its Bootstrap button classes. Prefer Bootstrap’s button custom properties/state styling so normal, hover, active, and focus states retain the coral theme without duplicating the whole component implementation.
  - Remove redundant width, spacing, or alignment declarations where Bootstrap utilities now provide them, while retaining custom declarations Bootstrap does not represent (such as fluid headline sizing and the cat medallion).
- Ensure custom selectors still work with the final class structure and do not override Bootstrap’s responsive column widths accidentally.
- Keep the mobile hero adjustment and reduced-motion behavior if they remain necessary after the markup changes.

### 3. Preserve message behavior (`cats-page/script.js`)
- Make no behavioral or content changes. The existing defensive element lookup, click listener, message order, output update, and index wraparound remain the source of truth.
- Do not introduce Bootstrap JavaScript APIs, dependencies, new handlers, or renamed selectors.

## Verification
- Inspect the final `<head>` and confirm Bootstrap 5.3.3 CSS is loaded before `styles.css`, with the expected integrity/crossorigin attributes, and that no Bootstrap JavaScript was added.
- Confirm the page visibly uses Bootstrap classes for its container/grid, cards, and button rather than merely loading the stylesheet.
- Open or serve `cats-page/index.html` in a browser with network access and verify:
  - Bootstrap CSS loads successfully from the CDN.
  - The facts display as three equal-height columns at Bootstrap medium-and-wider widths and stack cleanly on narrow screens, with no overflow or doubled/incorrect gutters.
  - The hero, facts, message panel, button, and footer retain the existing warm theme and readable spacing.
  - Keyboard focus remains visible and hover/active button states remain legible.
- Click `#message-button` repeatedly and confirm `#message-output` shows the four existing messages in order and wraps to the first message after the fourth click. Also confirm the status element and `aria-controls` relationship remain intact.
- Review the diff to ensure no page copy, message strings, user-facing behavior, or unrelated files changed; `cats-page/script.js` should have no diff.
