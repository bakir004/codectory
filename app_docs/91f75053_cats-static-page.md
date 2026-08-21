# Cats Static Page

## What changed

Added a dependency-free, responsive cat-themed webpage under `cats-page/`. It has a welcoming “Cozy Cat Corner” hero, three cat-fact cards, and a small interactive message button that cycles through four local messages. The page uses semantic sections, accessible labels/status output, visible keyboard focus styling, and a mobile breakpoint that stacks the fact cards.

## Files

- `cats-page/index.html` — HTML structure, hero, facts, interactive controls, and links to the local CSS and deferred JavaScript.
- `cats-page/styles.css` — Warm color palette, responsive layout, card/button styling, focus state, and reduced-motion handling. It uses no external assets or fonts.
- `cats-page/script.js` — Cycles through a local array of cat messages when the button is clicked and updates the live output element.
- `specs/91f75053_cats-static-page.md` — Implementation plan and verification checklist for the page.

## Use and verification

Open `cats-page/index.html` directly in a browser, or serve the repository with any static file server. Confirm the hero and three fact cards render, resize to a single-column fact layout below the mobile breakpoint, and that keyboard focus is visible on the button. Click “Show me a cat message” repeatedly to verify the displayed message changes and wraps back to the first message after the fourth.
