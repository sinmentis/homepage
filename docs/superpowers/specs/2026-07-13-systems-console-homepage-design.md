# Systems console homepage redesign

**Status:** Approved  
**Date:** 2026-07-13

## Goal

Redesign the homepage as a distinctive personal artifact that reflects a career across embedded systems, Linux, Android, build infrastructure, and cloud engineering.

The interface should feel like a restrained systems console. The visual environment carries the technical theme while the writing remains factual and modest. The result must avoid common AI-generated portfolio patterns without changing the résumé page or adding framework dependencies.

## Current design audit

The current homepage is polished but relies on patterns that now read as generic AI design:

- Purple, blue, and pink gradient text with drifting blurred orbs.
- A centered hero with a status pill, looping typewriter text, two buttons, metrics, and a scroll cue.
- Animated counters, including an abstract `∞ curiosity` metric.
- Three equal expertise cards and a large collection of pill-shaped technology tags.
- Inter as the primary font and rounded bordered cards as the dominant component.
- Decorative motion that creates spectacle but does not explain the content.
- Hidden project and blog sections that increase markup without contributing to the current page.

## Design principles

1. **The interface carries the theme.** Technical atmosphere comes from typography, structure, grid, traces, and motion rather than inflated copy.
2. **Facts replace slogans.** State the current role, previous domains, location, and recurring engineering interests plainly.
3. **Systems breadth is context, not a claim.** The device-to-cloud path appears as a small supporting reference, not the main headline or a repeated four-layer framework.
4. **Motion explains structure.** Cinematic effects reveal relationships and page progression. They do not exist as ambient decoration.
5. **Dark-first, not dark-only.** Dark mode is the flagship expression. Light mode is a coherent warm hardware-datasheet interpretation.
6. **Keep the site simple.** Use static HTML, CSS, and focused vanilla JavaScript with no new runtime or package dependencies.

## Content architecture

### Header

Use a compact status-line header rather than a conventional portfolio navigation bar.

- Retain the name, résumé, GitHub, LinkedIn, and theme control.
- Replace the icon-only theme control with a clear text or compact mode indicator.
- Keep keyboard focus visible and preserve the current system, light, and dark cycle.

### Introduction

Open with a short one-time boot sequence, then settle into:

> Shun Lyu  
> Software engineer working on Azure Kubernetes Service at Microsoft. Previously worked across embedded systems, Linux, Android, and build infrastructure.

Supporting metadata may show Auckland, current focus areas, and direct paths to the résumé and GitHub. Do not use a looping typewriter, availability pill, counters, or abstract self-ratings.

### Work now

Describe current work in two short paragraphs and a compact fact list:

- Cloud-native development and infrastructure automation on Azure Kubernetes Service.
- Reliability, shorter engineering feedback loops, and tools people can trust.
- Earlier work across embedded Linux, Android AOSP, firmware, build systems, and continuous integration and delivery.

This section should read as a calm work note, not a product launch or capability claim.

### Selected notes

Replace expertise cards and the technology tag wall with three plain observations:

- **Reliability:** Making changes observable, reversible, and easier to operate.
- **Tooling:** Removing repetitive steps and shortening the path from change to feedback.
- **Systems:** Following a problem across boundaries instead of stopping at one layer.

The supporting device, Linux, Android, and cloud path appears once in a narrow side rail or small route diagram.

### Links and footer

End with a restrained command surface:

- Résumé
- GitHub
- LinkedIn
- Email

Do not add a generic call-to-action panel or multi-column link farm. Retain copyright and last-updated information.

### Removed content

Remove the current metrics, looping typed roles, gradient identity avatar, equal expertise cards, technology pill wall, and hidden project and blog placeholder sections.

## Visual system

### Typography

- Use **IBM Plex Mono** for display headings, labels, coordinates, and command-style links.
- Use **IBM Plex Sans** for paragraphs and longer explanatory text.
- Use large, tightly tracked monospace headings selectively. Body copy remains proportional and limited to a readable line length.
- Use sentence case for section labels and avoid repeated all-caps headings outside small instrumentation labels.

### Color

Use one muted phosphor-green accent.

| Role | Dark theme | Light theme |
|---|---|---|
| Base | `#121610` | `#E9E5D9` |
| Primary text | `#E7ECDF` | `#222A20` |
| Muted text | `#87927F` | `#596055` |
| Signal accent | `#B7CB91` | `#53663E` |
| Hairline | `#354032` | `#C9C6BA` |

Semantic error and success colors may appear only when required by an actual state. They are not part of the decorative palette.

### Surfaces

- Use fine hairlines, subtle technical grids, restrained scan-line texture, and low-opacity grain.
- Avoid blurred color orbs, glass cards, bright gradients, generic drop shadows, and uniformly rounded containers.
- Keep most content on one continuous surface. Use borders and spacing to create hierarchy instead of card elevation.

### Iconography

Use text labels and simple custom inline SVG marks where necessary. Keep stroke width consistent. Avoid adding an icon library.

Update the favicon and social preview to match the new dark base and signal accent.

## Motion

### Entry sequence

Run a short boot-style reveal once on page load:

1. The technical grid fades in.
2. The name reveals through a horizontal mask.
3. Two or three status lines settle into place.
4. The page becomes fully interactive.

The sequence must be brief and must not repeat.

### Scroll behavior

- Use CSS sticky positioning for limited panel overlap and section handoff.
- Use `IntersectionObserver` for entry states.
- Use a passive scroll listener with `requestAnimationFrame` only where continuous progress is required for a trace or mask.
- Draw thin SVG routes or traces when related content enters the viewport.
- Avoid parallax objects, looping shimmer, counters, bobbing arrows, and continuous typewriter effects.

### Interaction

- Links use underline travel, a small position change, and signal-color focus treatment.
- Pressed states move by approximately one pixel.
- Theme changes should transition color variables without animating layout.

### Reduced motion

When `prefers-reduced-motion: reduce` is active:

- Skip the boot sequence.
- Disable sticky scene choreography and trace drawing.
- Show every section immediately in normal document order.
- Keep only essential focus and pressed-state feedback.

## Responsive behavior

- Desktop uses a content area with a narrow instrumentation rail.
- Tablet collapses the rail beneath its related content.
- Mobile becomes a straightforward single column with no pinned scenes.
- Preserve readable text sizes and avoid horizontal overflow from long monospace labels.
- Use `min-height: 100dvh` only where a full-screen introduction is needed.

## Technical architecture

### Files

- `site/index.html`: semantic homepage structure and content.
- `site/home.css`: homepage tokens, layouts, theme surfaces, responsive rules, and motion states.
- `site/home.js`: homepage-specific theme, entry, scroll, footer date, and email-copy behavior.
- `site/style.css`: change only shared tokens or components that must remain consistent across the homepage and résumé.
- `site/og-home.png`: branded social preview matching the new visual system.

The résumé HTML and résumé-specific styling remain functionally unchanged.

### JavaScript boundaries

`site/home.js` should contain small independent initializers:

- `initThemeControl`
- `initEntrySequence`
- `initScrollScenes`
- `initEmailCopy`
- `initFooterMetadata`

Each initializer must leave the document usable when its required browser API is unavailable.

### State flow

- The document provides meaningful content before JavaScript runs.
- CSS controls theme presentation through `data-color-mode`.
- The theme control reads and writes the existing `localStorage` value.
- Observers add presentation-only state classes.
- Scroll progress updates CSS custom properties through a throttled animation frame.
- Email copy reports success through the existing live-region toast and falls back to `mailto:` when clipboard access fails.

## Error handling and progressive enhancement

- Do not hide core content by default and wait for JavaScript to reveal it.
- If `IntersectionObserver` is unavailable, render all sections in their final visible state.
- If continuous scroll logic fails, sticky sections remain readable in document order.
- If `localStorage` is unavailable, continue using the system theme without blocking rendering.
- If clipboard access fails, navigate to the email link.
- Avoid broad catch blocks that convert failures into success states.

## Accessibility

- Preserve the skip link and semantic landmarks.
- Keep visible focus indicators for every interactive element.
- Maintain sufficient contrast in both themes.
- Do not communicate meaning through color alone.
- Keep decorative grids, traces, and status marks hidden from assistive technology.
- Preserve logical reading order regardless of sticky visual positioning.
- Use clear accessible names for theme, social, résumé, and email controls.

## Validation

Validate the finished homepage with the repository's existing static-site workflow:

- Desktop and mobile layouts.
- System, light, and dark themes.
- Keyboard-only navigation and focus order.
- `prefers-reduced-motion`.
- JavaScript disabled.
- Clipboard success and fallback behavior.
- No horizontal overflow.
- No browser console errors or missing network assets.
- Résumé page regression check.
- Metadata, favicon, and social preview URLs.

## Acceptance criteria

- The homepage no longer uses purple-pink gradients, ambient orbs, looping typed text, animated counters, generic expertise cards, or technology pill walls.
- The page reads as a personal systems-console artifact without overstating the career story.
- Current work and previous domains remain accurate and easy to find.
- Dark and light themes both feel intentionally designed.
- Cinematic motion has a clear structural purpose and fully degrades under reduced motion or unavailable browser APIs.
- The homepage remains fast, accessible, dependency-light, and independent from the résumé page.
