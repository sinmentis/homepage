# Systems dossier résumé redesign

**Status:** Approved design, pending specification review
**Date:** 2026-07-13

## Goal

Redesign the résumé page as a focused systems dossier that shares the homepage's technical identity while remaining easy for recruiters, engineering managers, and senior engineers to scan.

The redesign should preserve the factual work history, bilingual experience, theme control, contact paths, and print/PDF workflow. It should improve information hierarchy, reduce interaction noise, and remove the generic visual patterns inherited from the previous homepage.

## Audience and reading model

The page serves two reading modes:

1. A recruiter should understand the current role, experience range, location, and core engineering areas within roughly 30 seconds.
2. A technical reader should be able to inspect concrete work, operational impact, technologies, and earlier systems experience without leaving the page.

The design therefore uses progressive density. Current work receives full detail, while earlier roles start with concise summaries and allow expansion.

## Current design audit

The existing résumé is feature-complete but still carries the previous site's generic portfolio language:

- Inter and JetBrains Mono do not match the redesigned homepage typography.
- Blue and purple gradients, radial glow washes, gradient monograms, and pulsing timeline nodes read as decorative rather than informative.
- Animated career counters repeat information already present in the work history.
- A horizontal career timeline duplicates the vertical experience timeline and adds scrollspy complexity.
- Every role is expanded and independently collapsible, which creates more controls than the reading task requires.
- Per-role technology chips and a second skills chip wall repeat the same information.
- Rounded date pills, badges, cards, and icon buttons create a generic component-library appearance.
- The page loads Primer, `style.css`, `home.css`, and `resume.css`, which couples the résumé to homepage compatibility rules.
- A large inline script manages unrelated concerns and makes the page harder to test independently.

The redesign should remove these patterns rather than restyle them.

## Design principles

1. **A résumé first.** The systems theme creates hierarchy but never competes with work history.
2. **Facts over spectacle.** Remove counters, pulse animation, decorative gradients, and duplicated navigation.
3. **Progressive depth.** Keep the current role complete and make earlier detail available without forcing it into the initial scan.
4. **Shared identity, separate module.** Use the homepage palette and typography while keeping résumé styles and behavior independent.
5. **Bilingual by default.** Select the initial language intelligently and keep manual control visible.
6. **Print preserves identity.** Translate the dossier into an ink-safe paper version instead of replacing it with an unrelated traditional template.
7. **Progressive enhancement.** Core content remains available when JavaScript or browser APIs are unavailable.

## Content architecture

### System bar

Use a compact status-line header rather than the current app bar.

It contains:

- A home link labelled `SL / résumé`.
- The active language and manual `EN / 中文` control.
- Print/PDF action.
- Text-based theme state using the existing `auto → light → dark` cycle.

GitHub, LinkedIn, email, and location appear in the identity section rather than being repeated as icon-only navigation.

### Identity

Lead with:

- Name.
- Current role and team.
- A short factual sentence connecting current cloud work with earlier embedded, Linux, Android, and build-infrastructure experience.
- Location.
- Focus areas: reliability, automation, and developer tooling.
- GitHub, LinkedIn, and email.

Do not use a monogram block, status badge, availability message, or animated metric.

### Profile

Replace the current summary and career counters with one short profile section.

The profile should:

- State the experience range without using an animated number.
- Describe the transition from devices and platforms to cloud infrastructure.
- Keep the claims specific and supported by the experience section.
- Use a readable proportional typeface and a constrained line length.

### Experience

Use one chronological experience ledger.

#### Current role

The Microsoft role remains fully visible and contains:

- Role, company, location, and dates.
- All five existing factual achievement points, edited only for clarity and scanability.
- Operational and correctness impact where supported by the existing facts.
- A compact context line for Azure, C#, Python, Kubernetes, and distributed systems.

The current role does not have a collapse control.

#### Earlier roles

Crown Equipment, Navico Group, and Fisher & Paykel initially show:

- Dates.
- Company and role.
- A one- or two-sentence summary covering the role scope and primary work areas represented by the existing bullet points.
- A `details +` disclosure control.

Expanding a role reveals the remaining factual bullet points and a compact technology context line. The interaction uses native button semantics and synchronized `aria-expanded` state.

Every existing factual achievement from an earlier role must remain available in its expanded state.

Remove the separate horizontal career timeline and scrollspy behavior.

### Capabilities

Replace both chip systems with a plain capability matrix:

- Languages.
- Cloud and delivery.
- Platforms.
- Engineering focus.

Each group uses a short heading and comma- or separator-delimited text. Technologies are not interactive and should not look like buttons.

### Education

Keep the two education records in a compact indexed list with year, degree, institution, and existing supporting detail.

### Footer

Use a minimal footer containing:

- Last-updated date.
- Home return path.
- Contact references only where they are not already sufficiently visible.

Remove the duplicate monogram and decorative location phrase.

## Bilingual behavior

Retain complete English and Chinese content.

Initial language selection uses this precedence:

1. A valid language explicitly saved by the visitor.
2. Browser language beginning with `zh`.
3. English.

Manual language selection remains available at all times and persists under `localStorage["resume-language"]`. Changing language updates the document's `lang` attribute.

Only the active language participates in visual layout, accessibility traversal, and printing. The inactive language must use the HTML `hidden` state or an equivalent accessible mechanism rather than visual-only hiding.

If local storage is unavailable, language selection still works for the current page view without persistence.

## Visual system

### Direction

Use the approved **systems dossier** direction.

The page should feel like a carefully indexed engineering record, not a terminal emulator. Technical character comes from section numbering, hairlines, grid alignment, metadata labels, and restrained route references.

### Typography

- Use IBM Plex Mono for the name, section indices, dates, metadata labels, controls, and compact context lines.
- Use IBM Plex Sans for summaries, work details, and longer reading.
- Use tightly tracked display type selectively.
- Keep body text within approximately 65 characters per line.
- Use tabular figures for dates and numerical metadata.
- Use sentence case for content headings and uppercase only for small instrumentation labels where useful.

### Color

Share the homepage palette:

| Role | Dark theme | Light theme |
|---|---|---|
| Base | `#121610` | `#E9E5D9` |
| Primary text | `#E7ECDF` | `#222A20` |
| Muted text | `#87927F` | `#596055` |
| Signal accent | `#B7CB91` | `#53663E` |
| Hairline | `#354032` | `#C9C6BA` |

Use the signal accent for active controls, section indices, focus treatment, the current-role rule, and limited state indication.

Do not use blue/purple gradients, bright glow, multiple decorative accents, or generic black drop shadows.

### Surfaces

- Keep the page on one continuous background.
- Use subtle grid texture and low-opacity grain without reducing text contrast.
- Use section rules, indentation, and spacing instead of card elevation.
- Avoid uniformly rounded containers and pill-shaped metadata.
- Do not place every role or capability group inside a bordered card.

### Responsive behavior

Desktop uses an indexed two-column section structure:

- Narrow section index or route column.
- Main reading column.

On smaller screens:

- Section indices move above their content.
- Identity metadata becomes a single stack.
- Experience metadata wraps without horizontal scrolling.
- Capability groups become one column.
- Disclosure controls retain at least a 44-pixel touch target.

The mobile layout remains ordinary document flow with no sticky timeline or horizontal career scroller.

## Interaction and motion

### Theme

Preserve the site's `auto → light → dark` theme cycle and `localStorage["theme"]` contract.

The control should display text rather than rely on three sun, moon, and monitor icons.

### Experience disclosures

- Only earlier roles are collapsible.
- Summary content remains visible when collapsed.
- Detail content is visible by default without JavaScript.
- JavaScript adds disclosure behavior after initialization.
- Print always expands every role in the active language.

### Entry and scrolling

The résumé should be readable immediately.

- Do not use a boot sequence.
- Do not animate numbers.
- Do not pulse the current-role marker.
- Do not use experience scrollspy.
- The identity and top metadata run one 240-millisecond opacity and transform transition after first paint; no section uses scroll-triggered reveal.
- Disclosure transitions should finish within approximately 260 milliseconds.
- Hover and pressed states use no more than one pixel of movement.

Under `prefers-reduced-motion: reduce`, reveal and disclosure transitions become immediate.

## Print and PDF

Print the active language using an ink-safe translation of the systems dossier.

The print version preserves:

- IBM Plex typography where available.
- Section numbers and indexed layout.
- The current-role accent rule.
- Capability grouping.
- The same content hierarchy as the web page.

The print version changes:

- Dark surfaces to white or warm paper.
- Signal green to a printer-safe dark green or solid ink where necessary.
- Grid texture to minimal or none.
- Interactive controls to hidden.
- Collapsed details to fully expanded.
- Links to readable text without browser-only hover treatment.

Avoid full-bleed dark backgrounds and do not depend on background-graphics printing being enabled.

Use page-break rules to keep headings with following content. Keep an experience entry together unless the entry itself is taller than the remaining printable page area.

## Technical architecture

### Files

- `site/resume/index.html`: semantic bilingual résumé content and minimal no-flash initialization.
- `site/resume.css`: self-contained résumé tokens, themes, layouts, components, responsive rules, reduced-motion handling, and print styles.
- `site/resume.js`: theme, language, disclosures, print, email-copy behavior, and footer metadata.
- `tests/test_resume.py`: dedicated dependency-free résumé regression tests.

Reuse the existing branded `/og-home.png?v=1` social image rather than adding a second résumé-specific asset.

### Independence from legacy styles

The redesigned résumé must stop loading:

- `/vendor/primer/light.css`
- `/vendor/primer/dark.css`
- `/vendor/primer/primer.css`
- `/style.css`
- `/home.css`

`resume.css` should contain only the tokens and components the résumé needs. This removes the non-home compatibility layer that was previously required in `home.css`.

Homepage behavior must remain unchanged.

### JavaScript boundaries

`resume.js` should expose small internal initializers:

- `initThemeControl`
- `initLanguageControl`
- `initExperienceDisclosures`
- `initPrintControls`
- `initEmailCopy`
- `initFooterMetadata`

Each initializer should be independent and leave core content usable when its required browser API is unavailable.

The small head script sets only the classes and attributes needed to avoid a theme or language flash. All interaction logic belongs in `resume.js`.

## State and data flow

### Theme

1. Read the existing `theme` value before paint.
2. Apply `light` or `dark` only when valid; otherwise use `auto`.
3. The control cycles through `auto`, `light`, and `dark`.
4. Save explicit values and remove the key for `auto`.

### Language

1. Read a valid saved résumé language.
2. Otherwise inspect `navigator.language` and `navigator.languages`.
3. Choose Chinese for a Chinese browser locale; otherwise choose English.
4. Update the active content, control state, and root `lang` attribute.
5. Persist manual changes when storage is available.

### Disclosures

1. The HTML ships with all details readable.
2. JavaScript marks the document as disclosure-enhanced.
3. Earlier role controls update `aria-expanded`, visual state, and detail visibility.
4. Print styles override all collapsed states.

## Error handling and progressive enhancement

- If theme storage fails, continue with system theme and allow non-persistent control changes.
- If language storage fails, infer the initial language and allow non-persistent manual changes.
- If browser locale APIs are unavailable, default to English.
- If clipboard access fails, follow the email `mailto:` link.
- If disclosure initialization fails, leave all role details visible.
- If printing is unavailable, the control remains a normal button with no false success state.
- Do not use broad catches that hide unrelated failures.

## Accessibility

- Preserve a visible-on-focus skip link.
- Use semantic `header`, `nav`, `main`, `article`, `section`, and `footer` landmarks.
- Maintain logical source order independent of the indexed visual grid.
- Keep visible focus indicators in both themes.
- Use buttons for theme, language, print, and disclosure actions.
- Keep disclosure controls synchronized with `aria-expanded` and `aria-controls`.
- Update the document language when the active résumé language changes.
- Remove inactive language content from the accessibility tree.
- Ensure color is not the only indicator of current state.
- Maintain WCAG AA contrast for body text and controls.
- On coarse-pointer devices, keep theme, language, print, and disclosure controls at least 44 by 44 CSS pixels.

## Validation

### Automated

Add dependency-free tests covering:

- Semantic résumé landmarks and core content in both languages.
- Dedicated stylesheet and deferred script references.
- Removal of Primer, `style.css`, and `home.css` dependencies.
- Approved IBM Plex font loading.
- Absence of animated counters, duplicated career timeline, pulse animation, and skills chip walls.
- Locale selection precedence and manual persistence contracts.
- Existing theme cycle and storage key.
- Progressive disclosure semantics and no-JavaScript visibility.
- Print expansion, active-language behavior, and ink-safe styling.
- Reduced-motion behavior.
- Social metadata, contact links, and favicon.
- CSS syntax invariants and JavaScript syntax.
- Homepage regression contracts affected by removing résumé compatibility styles.

### Browser

Validate:

- Desktop, tablet, and narrow mobile layouts.
- English and Chinese initial selection and manual switching.
- Dark, light, and automatic themes.
- Keyboard navigation and focus order.
- Current role readability and earlier-role disclosures.
- JavaScript-disabled content.
- Reduced-motion behavior.
- Print preview for both languages.
- No horizontal overflow.
- No browser console errors or missing assets.
- Homepage visual and behavioral regression check.

## Out of scope

- Changing employment dates, claims, or factual achievements without separate content review.
- Adding a framework, build system, animation library, icon library, or runtime dependency.
- Generating a separately hosted PDF file.
- Adding analytics, contact forms, or recruiter tracking.
- Redesigning the homepage again.

## Acceptance criteria

- The résumé visually belongs to the same site as the systems-console homepage without copying its cinematic homepage choreography.
- Recruiters can identify current role, experience range, location, and core skills quickly.
- Technical readers can inspect full current-role details and expand earlier experience.
- The page no longer uses blue/purple gradients, animated counters, pulse animation, duplicated timelines, or technology pill walls.
- English and Chinese selection works through browser locale, manual control, and persistence.
- Print preserves the dossier hierarchy in an ink-safe light treatment.
- The résumé no longer depends on Primer, `style.css`, or `home.css`.
- Core content remains usable without JavaScript.
- Homepage behavior and styling remain unchanged.
