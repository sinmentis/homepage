# Systems Console Homepage Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current AI-styled portfolio homepage with a restrained, cinematic systems-console experience while preserving accurate content, accessibility, theme support, and the existing résumé page.

**Architecture:** The homepage becomes independent from the shared Primer-based résumé styling. `site/index.html` owns semantic content, `site/home.css` owns the dark-first visual system and responsive motion states, and a new `site/home.js` contains small progressive-enhancement initializers. Python standard-library tests protect the static contract without adding dependencies.

**Tech Stack:** Static HTML5, CSS custom properties, vanilla JavaScript, Python 3.12 `unittest`, nginx container serving.

## File structure

| File | Responsibility |
|---|---|
| `site/index.html` | Homepage semantics, accurate copy, metadata, theme prepaint hook, and links. |
| `site/home.css` | Homepage-only tokens, typography, surfaces, layouts, responsive behavior, and motion. |
| `site/home.js` | Theme cycling, entry lifecycle, scroll reveals/progress, email copy fallback, and footer metadata. |
| `site/og-home.svg` | Editable source for the social preview artwork. |
| `site/og-home.png` | 1200×630 social preview referenced by Open Graph and Twitter metadata. |
| `tests/test_homepage.py` | Dependency-free static regression tests for HTML, CSS, JavaScript, and assets. |

## Global constraints

- Do not change `site/resume/index.html`, `site/resume.css`, or the résumé behavior.
- Do not stage or modify the user's existing `.gitignore` change.
- Add no runtime, package, font-rendering, test, or build dependency.
- Use IBM Plex Mono for display/interface text and IBM Plex Sans for prose through the existing Google Fonts approach, with system fallbacks.
- Use dark base `#121610`, dark text `#E7ECDF`, dark muted text `#87927F`, and dark signal accent `#B7CB91`.
- Use light base `#E9E5D9`, light text `#222A20`, light muted text `#596055`, and light signal accent `#53663E`.
- Keep the current `system → light → dark` theme cycle and the existing `localStorage` key `theme`.
- Remove purple-pink gradients, ambient orbs, looping typewriter text, animated counters, generic expertise cards, and technology pill walls.
- Keep the writing factual and modest. The device-to-cloud path is supporting context, not a repeated four-layer claim.
- The entry sequence must finish within 1.4 seconds and never repeat while scrolling.
- Core content must remain visible with JavaScript disabled, `IntersectionObserver` unavailable, or `prefers-reduced-motion: reduce`.
- Clipboard failure must navigate to the `mailto:` link.
- Use Conventional Commits and include the required Copilot trailers.

---

### Task 1: Build the semantic homepage

**Files:**
- Create: `tests/test_homepage.py`
- Replace: `site/index.html`

**Interfaces:**
- Consumes: Existing public routes `/resume/`, `https://github.com/sinmentis`, `https://www.linkedin.com/in/shunlyu`, and `mailto:hello@shunlyu.com`.
- Produces: Stable DOM hooks consumed by Tasks 2 and 3: `[data-theme-control]`, `[data-theme-label]`, `[data-reveal]`, `[data-route]`, `[data-email]`, `[data-toast]`, `[data-toast-message]`, `#year`, and `#updated`.

- [ ] **Step 1: Write failing homepage markup tests**

Create `tests/test_homepage.py` with:

```python
from pathlib import Path
import re
import struct
import unittest


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "site" / "index.html"
HOME_CSS = ROOT / "site" / "home.css"
HOME_JS = ROOT / "site" / "home.js"
OG_PNG = ROOT / "site" / "og-home.png"


class HomepageMarkupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX.read_text(encoding="utf-8")

    def test_uses_system_console_document_structure(self):
        required_fragments = (
            'class="system-bar"',
            'class="intro-shell"',
            'id="work"',
            'id="notes"',
            'class="instrument-rail"',
            'class="command-links"',
            'data-theme-control',
            'data-email',
            'data-toast',
        )
        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.html)

    def test_keeps_copy_factual_and_modest(self):
        self.assertIn(
            "Software engineer working on Azure Kubernetes Service at Microsoft.",
            self.html,
        )
        self.assertIn(
            "Previously worked across embedded systems, Linux, Android, and build infrastructure.",
            self.html,
        )
        self.assertIn("Making changes observable, reversible, and easier to operate.", self.html)

    def test_removes_legacy_ai_portfolio_patterns(self):
        forbidden_fragments = (
            'class="orb',
            'id="typed"',
            'data-count=',
            "Curiosity",
            "focus-cards",
            "stack__chips",
            "brand-gradient",
            "More on the way",
            "coming soon",
        )
        for fragment in forbidden_fragments:
            with self.subTest(fragment=fragment):
                self.assertNotIn(fragment, self.html)

    def test_homepage_owns_its_styles(self):
        self.assertIn('href="/home.css?v=2"', self.html)
        self.assertNotIn("/vendor/primer/", self.html)
        self.assertNotIn('href="/style.css', self.html)

    def test_preserves_accessibility_and_primary_links(self):
        self.assertIn('href="#main-content"', self.html)
        self.assertIn("<main", self.html)
        self.assertIn("<header", self.html)
        self.assertIn("<footer", self.html)
        self.assertIn('href="/resume/"', self.html)
        self.assertIn('href="https://github.com/sinmentis"', self.html)
        self.assertIn('href="https://www.linkedin.com/in/shunlyu"', self.html)
        self.assertIn('href="mailto:hello@shunlyu.com"', self.html)

    def test_uses_approved_fonts(self):
        self.assertIn("family=IBM+Plex+Mono", self.html)
        self.assertIn("family=IBM+Plex+Sans", self.html)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the tests and confirm the current homepage fails**

Run:

```bash
python3 -m unittest tests.test_homepage.HomepageMarkupTests -v
```

Expected: failures for the missing system-console structure, approved copy, independent stylesheet/script, and remaining legacy patterns.

- [ ] **Step 3: Replace `site/index.html` with the approved semantic structure**

Use this complete document:

```html
<!doctype html>
<html lang="en" data-color-mode="auto">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Shun Lyu — Software Engineer</title>
  <meta name="description" content="Software engineer in Auckland working on Azure Kubernetes Service, with experience across embedded systems, Linux, Android, build infrastructure, and cloud reliability.">
  <meta name="author" content="Shun Lyu">
  <meta name="theme-color" content="#E9E5D9" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#121610" media="(prefers-color-scheme: dark)">

  <meta property="og:type" content="website">
  <meta property="og:title" content="Shun Lyu — Software Engineer">
  <meta property="og:description" content="Software engineer working across cloud infrastructure, developer tooling, Linux, Android, and embedded systems.">
  <meta property="og:url" content="https://shunlyu.com/">
  <meta property="og:site_name" content="Shun Lyu">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="Shun Lyu — Software Engineer">
  <meta name="twitter:description" content="Software engineer working across cloud infrastructure, developer tooling, Linux, Android, and embedded systems.">

  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='4' fill='%23121610'/%3E%3Cpath d='M8 10l6 6-6 6M16 22h8' fill='none' stroke='%23b7cb91' stroke-width='2.5' stroke-linecap='square' stroke-linejoin='miter'/%3E%3C/svg%3E">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
  <link rel="stylesheet" href="/home.css?v=2">

  <script>
    (function () {
      var root = document.documentElement;
      root.classList.add('js');
      try {
        var savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'light' || savedTheme === 'dark') {
          root.setAttribute('data-color-mode', savedTheme);
        }
      } catch (error) {
        root.setAttribute('data-theme-storage', 'unavailable');
      }
    })();
  </script>
</head>
<body id="top">
  <a class="skip-link" href="#main-content">Skip to content</a>

  <header class="system-bar">
    <div class="system-bar__inner">
      <a class="system-id" href="#top" aria-label="Shun Lyu, home">
        <span class="system-id__prompt" aria-hidden="true">&gt;</span>
        <span>SL / HOME</span>
      </a>

      <nav class="system-nav" aria-label="Primary">
        <a href="#work">Work</a>
        <a href="/resume/">Résumé</a>
        <a href="https://github.com/sinmentis" target="_blank" rel="noopener">GitHub</a>
        <button class="theme-control" type="button" data-theme-control>
          theme:<span data-theme-label>auto</span>
        </button>
      </nav>
    </div>
  </header>

  <main id="main-content">
    <section class="intro-shell" aria-labelledby="intro-title">
      <div class="console-grid" aria-hidden="true"></div>

      <div class="intro-main">
        <p class="console-label boot-item" style="--boot-delay:80ms">Auckland / New Zealand</p>
        <h1 id="intro-title" class="intro-title boot-item" style="--boot-delay:180ms">
          <span aria-hidden="true">&gt;</span> Shun Lyu<span class="cursor-mark" aria-hidden="true">_</span>
        </h1>
        <p class="intro-copy boot-item" style="--boot-delay:320ms">
          Software engineer working on Azure Kubernetes Service at Microsoft.
          Previously worked across embedded systems, Linux, Android, and build infrastructure.
        </p>

        <dl class="intro-status boot-item" style="--boot-delay:460ms">
          <div>
            <dt>focus</dt>
            <dd>reliability · automation · developer tooling</dd>
          </div>
          <div>
            <dt>location</dt>
            <dd>Auckland, New Zealand</dd>
          </div>
        </dl>

        <div class="command-links boot-item" style="--boot-delay:600ms">
          <a href="/resume/">&gt; open /resume</a>
          <a href="https://github.com/sinmentis" target="_blank" rel="noopener">&gt; connect /github</a>
        </div>
      </div>

      <aside class="instrument-rail intro-rail" aria-label="Background">
        <p class="rail-title">Background</p>
        <p>A small route through earlier work.</p>
        <ol class="route-list" data-route>
          <li>device</li>
          <li>linux</li>
          <li>android</li>
          <li aria-current="step">cloud</li>
        </ol>
      </aside>
    </section>

    <section class="console-section" id="work" aria-labelledby="work-title">
      <div class="section-main reveal" data-reveal>
        <p class="console-label">Work / now</p>
        <h2 id="work-title">Building dependable cloud infrastructure.</h2>
        <p>
          I work on cloud-native development and infrastructure automation for Azure Kubernetes
          Service, with an emphasis on reliability and changes that are easier to operate.
        </p>
        <p>
          I tend to gravitate toward build systems, delivery pipelines, and developer tools that
          remove repetitive work and shorten feedback loops.
        </p>

        <dl class="fact-list">
          <div>
            <dt>Current</dt>
            <dd>Azure Kubernetes Service, cloud-native development, and infrastructure automation.</dd>
          </div>
          <div>
            <dt>Interested in</dt>
            <dd>Reliability, observable change, and tools people can trust.</dd>
          </div>
          <div>
            <dt>Earlier work</dt>
            <dd>Embedded Linux, Android AOSP, firmware, build systems, and CI/CD.</dd>
          </div>
        </dl>
      </div>

      <aside class="instrument-rail reveal" data-reveal aria-label="Work context">
        <p class="rail-title">Context</p>
        <p>The work spans boundaries, but the page keeps the claims narrow and specific.</p>
      </aside>
    </section>

    <section class="console-section" id="notes" aria-labelledby="notes-title">
      <div class="section-main reveal" data-reveal>
        <p class="console-label">Selected notes</p>
        <h2 id="notes-title">What I tend to work on.</h2>

        <ol class="note-list">
          <li>
            <span class="note-index">01</span>
            <div>
              <h3>Reliability</h3>
              <p>Making changes observable, reversible, and easier to operate.</p>
            </div>
          </li>
          <li>
            <span class="note-index">02</span>
            <div>
              <h3>Tooling</h3>
              <p>Removing repetitive steps and shortening the path from change to feedback.</p>
            </div>
          </li>
          <li>
            <span class="note-index">03</span>
            <div>
              <h3>Systems</h3>
              <p>Following a problem across boundaries instead of stopping at one layer.</p>
            </div>
          </li>
        </ol>
      </div>

      <aside class="instrument-rail reveal" data-reveal aria-label="Earlier domains">
        <p class="rail-title">Earlier domains</p>
        <p>Firmware, Linux kernel and user space, Android platforms, and build infrastructure.</p>
      </aside>
    </section>

    <section class="closing-section reveal" data-reveal aria-labelledby="continue-title">
      <p class="console-label">Continue</p>
      <h2 id="continue-title">A few useful links.</h2>
      <div class="command-links command-links--large">
        <a href="/resume/">&gt; résumé</a>
        <a href="https://github.com/sinmentis" target="_blank" rel="noopener">&gt; github</a>
        <a href="https://www.linkedin.com/in/shunlyu" target="_blank" rel="noopener">&gt; linkedin</a>
        <a href="mailto:hello@shunlyu.com" data-email="hello@shunlyu.com">&gt; email</a>
      </div>
    </section>
  </main>

  <footer class="system-footer">
    <div>
      <span>© <span id="year">2026</span> Shun Lyu</span>
      <span class="system-footer__muted">Last updated <span id="updated">—</span></span>
    </div>
    <a href="#top">return /top</a>
  </footer>

  <div class="toast" data-toast role="status" aria-live="polite">
    <span data-toast-message>Email copied to clipboard</span>
  </div>

</body>
</html>
```

- [ ] **Step 4: Run the markup tests**

Run:

```bash
python3 -m unittest tests.test_homepage.HomepageMarkupTests -v
```

Expected: all six markup tests pass and the page has no missing local asset request.

- [ ] **Step 5: Verify the static document is served**

Run:

```bash
python3 -m http.server 4173 --bind 127.0.0.1 --directory site
```

In a second shell:

```bash
curl --fail --silent --show-error http://127.0.0.1:4173/ | grep -F "Building dependable cloud infrastructure."
```

Expected: the heading is printed and `curl` exits with status 0. Stop the server with its exact process ID after the check.

- [ ] **Step 6: Commit the semantic homepage**

```bash
git add site/index.html tests/test_homepage.py
git commit -m "feat: rebuild homepage content structure" \
  -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>" \
  -m "Copilot-Session: 9e6d184d-77ff-4972-86bb-31358c4d2be8"
```

---

### Task 2: Implement the dark-first visual system

**Files:**
- Modify: `tests/test_homepage.py`
- Replace: `site/home.css`

**Interfaces:**
- Consumes: The class names and data attributes created in Task 1.
- Produces: Theme variables controlled by `html[data-color-mode]`, visible static content, responsive single-column behavior, boot animations, `.has-reveal`, and `.is-visible` presentation states consumed by Task 3.

- [ ] **Step 1: Add failing CSS contract tests**

Insert this class above the `if __name__ == "__main__":` block in `tests/test_homepage.py`:

```python
class HomepageStyleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = HOME_CSS.read_text(encoding="utf-8")

    def test_defines_approved_theme_tokens(self):
        required_tokens = (
            "--page-bg: #e9e5d9",
            "--page-fg: #222a20",
            "--page-muted: #596055",
            "--signal: #53663e",
            "--page-bg: #121610",
            "--page-fg: #e7ecdf",
            "--page-muted: #87927f",
            "--signal: #b7cb91",
        )
        lower_css = self.css.lower()
        for token in required_tokens:
            with self.subTest(token=token):
                self.assertIn(token, lower_css)

    def test_uses_approved_font_roles(self):
        self.assertIn('--font-interface: "IBM Plex Mono"', self.css)
        self.assertIn('--font-prose: "IBM Plex Sans"', self.css)

    def test_supports_reduced_motion_and_mobile_layout(self):
        self.assertIn("@media (prefers-reduced-motion: reduce)", self.css)
        self.assertIn("@media (max-width: 760px)", self.css)
        self.assertIn(".instrument-rail", self.css)
        self.assertIn("position: sticky", self.css)

    def test_core_content_is_not_hidden_without_enhancement_class(self):
        hidden_reveal_rule = re.search(
            r"(?<!has-reveal )\.reveal\s*\{[^}]*opacity\s*:\s*0",
            self.css,
            flags=re.DOTALL,
        )
        self.assertIsNone(hidden_reveal_rule)
        self.assertIn(".has-reveal .reveal", self.css)

    def test_css_braces_are_balanced(self):
        self.assertEqual(self.css.count("{"), self.css.count("}"))
```

- [ ] **Step 2: Run the CSS tests and confirm failure**

Run:

```bash
python3 -m unittest tests.test_homepage.HomepageStyleTests -v
```

Expected: failures because the existing CSS still contains the gradient/orb system and lacks the approved tokens.

- [ ] **Step 3: Replace `site/home.css`**

Use this complete stylesheet:

```css
:root {
  color-scheme: light;
  --page-bg: #e9e5d9;
  --page-fg: #222a20;
  --page-muted: #596055;
  --signal: #53663e;
  --hairline: #c9c6ba;
  --panel-bg: rgba(255, 255, 255, 0.16);
  --grid-line: rgba(65, 79, 58, 0.08);
  --focus-ring: 0 0 0 3px rgba(83, 102, 62, 0.34);
  --font-interface: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  --font-prose: "IBM Plex Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --container: 74rem;
  --bar-height: 3.5rem;
  --page-progress: 0%;
  --grid-offset: 0px;
  --ease-out: cubic-bezier(0.22, 1, 0.36, 1);
}

@media (prefers-color-scheme: dark) {
  :root {
    color-scheme: dark;
    --page-bg: #121610;
    --page-fg: #e7ecdf;
    --page-muted: #87927f;
    --signal: #b7cb91;
    --hairline: #354032;
    --panel-bg: rgba(20, 27, 18, 0.72);
    --grid-line: rgba(183, 203, 145, 0.045);
    --focus-ring: 0 0 0 3px rgba(183, 203, 145, 0.3);
  }
}

[data-color-mode="light"] {
  color-scheme: light;
  --page-bg: #e9e5d9;
  --page-fg: #222a20;
  --page-muted: #596055;
  --signal: #53663e;
  --hairline: #c9c6ba;
  --panel-bg: rgba(255, 255, 255, 0.16);
  --grid-line: rgba(65, 79, 58, 0.08);
  --focus-ring: 0 0 0 3px rgba(83, 102, 62, 0.34);
}

[data-color-mode="dark"] {
  color-scheme: dark;
  --page-bg: #121610;
  --page-fg: #e7ecdf;
  --page-muted: #87927f;
  --signal: #b7cb91;
  --hairline: #354032;
  --panel-bg: rgba(20, 27, 18, 0.72);
  --grid-line: rgba(183, 203, 145, 0.045);
  --focus-ring: 0 0 0 3px rgba(183, 203, 145, 0.3);
}

*,
*::before,
*::after {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
  background: var(--page-bg);
}

body {
  margin: 0;
  min-height: 100vh;
  color: var(--page-fg);
  background:
    linear-gradient(var(--grid-line) 1px, transparent 1px),
    linear-gradient(90deg, var(--grid-line) 1px, transparent 1px),
    var(--page-bg);
  background-position: 0 var(--grid-offset);
  background-size: 42px 42px;
  font-family: var(--font-prose);
  font-size: 1rem;
  line-height: 1.65;
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
}

body::after {
  content: "";
  position: fixed;
  inset: 0;
  z-index: 100;
  pointer-events: none;
  opacity: 0.035;
  background: repeating-linear-gradient(
    0deg,
    transparent 0 3px,
    currentColor 4px
  );
}

a {
  color: inherit;
  text-decoration: none;
}

a,
button {
  -webkit-tap-highlight-color: transparent;
}

button {
  font: inherit;
}

:focus-visible {
  outline: none;
  box-shadow: var(--focus-ring);
}

::selection {
  color: var(--page-bg);
  background: var(--signal);
}

.skip-link {
  position: fixed;
  left: 1rem;
  top: 0.75rem;
  z-index: 200;
  padding: 0.5rem 0.75rem;
  color: var(--page-bg);
  background: var(--signal);
  font-family: var(--font-interface);
  font-size: 0.75rem;
  transform: translateY(-160%);
}

.skip-link:focus {
  transform: translateY(0);
}

.system-bar {
  position: sticky;
  top: 0;
  z-index: 50;
  min-height: var(--bar-height);
  border-bottom: 1px solid var(--hairline);
  background: color-mix(in srgb, var(--page-bg) 88%, transparent);
  backdrop-filter: blur(14px);
}

.system-bar::after {
  content: "";
  position: absolute;
  left: 0;
  bottom: -1px;
  width: var(--page-progress);
  height: 1px;
  background: var(--signal);
}

.system-bar__inner {
  width: min(100%, var(--container));
  min-height: var(--bar-height);
  margin-inline: auto;
  padding-inline: clamp(1rem, 3vw, 2rem);
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.system-id,
.system-nav,
.theme-control,
.console-label,
.intro-status,
.route-list,
.note-index,
.system-footer {
  font-family: var(--font-interface);
}

.system-id {
  display: inline-flex;
  align-items: center;
  gap: 0.55rem;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.05em;
}

.system-id__prompt {
  color: var(--signal);
}

.system-nav {
  display: flex;
  align-items: center;
  gap: clamp(0.55rem, 2vw, 1.35rem);
  font-size: 0.72rem;
}

.system-nav a,
.theme-control,
.command-links a,
.system-footer a {
  position: relative;
  padding-block: 0.25rem;
}

.system-nav a::after,
.theme-control::after,
.command-links a::after,
.system-footer a::after {
  content: "";
  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;
  height: 1px;
  background: var(--signal);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 220ms var(--ease-out);
}

.system-nav a:hover,
.theme-control:hover,
.command-links a:hover,
.system-footer a:hover {
  color: var(--signal);
  transform: translateY(-1px);
}

.system-nav a:hover::after,
.theme-control:hover::after,
.command-links a:hover::after,
.system-footer a:hover::after {
  transform: scaleX(1);
}

.system-nav a:active,
.theme-control:active,
.command-links a:active,
.system-footer a:active {
  transform: translateY(1px);
}

.theme-control {
  padding-inline: 0;
  color: var(--page-muted);
  background: transparent;
  border: 0;
  cursor: pointer;
}

main {
  width: min(100%, var(--container));
  margin-inline: auto;
  padding-inline: clamp(1rem, 3vw, 2rem);
}

.intro-shell,
.console-section {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 15rem;
  gap: clamp(2rem, 5vw, 5rem);
}

.intro-shell {
  position: relative;
  min-height: calc(100dvh - var(--bar-height));
  align-items: center;
  padding-block: clamp(4rem, 10vw, 8rem);
  border-bottom: 1px solid var(--hairline);
  overflow: hidden;
}

.console-grid {
  position: absolute;
  inset: 0;
  pointer-events: none;
  background: radial-gradient(
    circle at 32% 34%,
    color-mix(in srgb, var(--signal) 9%, transparent),
    transparent 34%
  );
}

.intro-main,
.section-main {
  position: relative;
  z-index: 1;
  max-width: 46rem;
}

.console-label {
  margin: 0 0 1.5rem;
  color: var(--signal);
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.09em;
  text-transform: uppercase;
}

.intro-title,
.section-main h2,
.closing-section h2 {
  margin: 0;
  font-family: var(--font-interface);
  font-weight: 600;
  letter-spacing: -0.065em;
  text-wrap: balance;
}

.intro-title {
  max-width: 11ch;
  font-size: clamp(3.25rem, 9vw, 7.8rem);
  line-height: 0.9;
}

.intro-title > span:first-child,
.cursor-mark {
  color: var(--signal);
}

.intro-copy {
  max-width: 42rem;
  margin: 2rem 0 0;
  color: var(--page-muted);
  font-size: clamp(1.05rem, 2vw, 1.3rem);
  line-height: 1.65;
  text-wrap: pretty;
}

.intro-status {
  display: grid;
  gap: 0.6rem;
  margin: 2rem 0 0;
  font-size: 0.76rem;
}

.intro-status div {
  display: grid;
  grid-template-columns: 5rem 1fr;
  gap: 1rem;
}

.intro-status dt {
  color: var(--signal);
}

.intro-status dd {
  margin: 0;
  color: var(--page-muted);
}

.command-links {
  display: flex;
  flex-wrap: wrap;
  gap: 0.8rem 2rem;
  margin-top: 2.25rem;
  font-family: var(--font-interface);
  font-size: 0.8rem;
  font-weight: 600;
}

.command-links a {
  color: var(--signal);
}

.instrument-rail {
  position: sticky;
  top: calc(var(--bar-height) + 2rem);
  align-self: start;
  padding: 1.25rem 0 1.25rem 1.25rem;
  border-left: 1px solid var(--hairline);
  color: var(--page-muted);
  font-size: 0.78rem;
}

.intro-rail {
  top: calc(var(--bar-height) + 8rem);
}

.rail-title {
  margin: 0 0 0.8rem;
  color: var(--signal);
  font-family: var(--font-interface);
  font-size: 0.68rem;
  font-weight: 600;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.instrument-rail p {
  margin: 0;
}

.route-list {
  position: relative;
  display: grid;
  gap: 0.9rem;
  margin: 1.4rem 0 0;
  padding: 0;
  list-style: none;
  font-size: 0.68rem;
  text-transform: uppercase;
}

.route-list::before {
  content: "";
  position: absolute;
  left: 3px;
  top: 0.45rem;
  bottom: 0.45rem;
  width: 1px;
  background: var(--hairline);
  transform: scaleY(0);
  transform-origin: top;
  transition: transform 900ms var(--ease-out);
}

.route-list.is-visible::before {
  transform: scaleY(1);
}

.route-list li {
  position: relative;
  padding-left: 1.1rem;
}

.route-list li::before {
  content: "";
  position: absolute;
  left: 0;
  top: 0.4rem;
  width: 7px;
  height: 7px;
  border: 1px solid var(--page-muted);
  background: var(--page-bg);
}

.route-list li[aria-current="step"] {
  color: var(--signal);
}

.route-list li[aria-current="step"]::before {
  border-color: var(--signal);
  background: var(--signal);
}

.console-section {
  min-height: 82dvh;
  align-items: start;
  padding-block: clamp(5rem, 12vw, 10rem);
  border-bottom: 1px solid var(--hairline);
}

.section-main h2,
.closing-section h2 {
  max-width: 16ch;
  font-size: clamp(2.35rem, 6vw, 5.4rem);
  line-height: 0.98;
}

.section-main > p:not(.console-label) {
  max-width: 42rem;
  margin: 1.6rem 0 0;
  color: var(--page-muted);
  font-size: clamp(1rem, 1.4vw, 1.12rem);
}

.fact-list {
  margin: 3rem 0 0;
  border-top: 1px solid var(--hairline);
}

.fact-list div {
  display: grid;
  grid-template-columns: 8rem minmax(0, 1fr);
  gap: 2rem;
  padding-block: 1.2rem;
  border-bottom: 1px solid var(--hairline);
}

.fact-list dt {
  color: var(--signal);
  font-family: var(--font-interface);
  font-size: 0.7rem;
  text-transform: uppercase;
}

.fact-list dd {
  margin: 0;
  color: var(--page-muted);
}

.note-list {
  margin: 3rem 0 0;
  padding: 0;
  border-top: 1px solid var(--hairline);
  list-style: none;
}

.note-list li {
  display: grid;
  grid-template-columns: 3rem minmax(0, 1fr);
  gap: 1.5rem;
  padding-block: 1.6rem;
  border-bottom: 1px solid var(--hairline);
}

.note-index {
  color: var(--signal);
  font-size: 0.7rem;
}

.note-list h3 {
  margin: 0;
  font-family: var(--font-interface);
  font-size: 1rem;
  font-weight: 600;
}

.note-list p {
  max-width: 38rem;
  margin: 0.45rem 0 0;
  color: var(--page-muted);
}

.closing-section {
  min-height: 62dvh;
  padding-block: clamp(5rem, 12vw, 10rem);
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.command-links--large {
  gap: 1rem 2.5rem;
  margin-top: 3rem;
  font-size: clamp(0.9rem, 1.5vw, 1.15rem);
}

.system-footer {
  width: min(100%, var(--container));
  margin-inline: auto;
  padding: 1.5rem clamp(1rem, 3vw, 2rem);
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  border-top: 1px solid var(--hairline);
  color: var(--page-muted);
  font-size: 0.68rem;
}

.system-footer > div {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem 1.2rem;
}

.system-footer__muted {
  opacity: 0.8;
}

.toast {
  position: fixed;
  left: 50%;
  bottom: 1.5rem;
  z-index: 80;
  padding: 0.65rem 0.9rem;
  color: var(--page-bg);
  background: var(--signal);
  font-family: var(--font-interface);
  font-size: 0.72rem;
  opacity: 0;
  transform: translate(-50%, 140%);
  transition:
    opacity 220ms var(--ease-out),
    transform 320ms var(--ease-out);
}

.toast.is-visible {
  opacity: 1;
  transform: translate(-50%, 0);
}

.js .boot-item {
  animation: boot-in 560ms var(--ease-out) both;
  animation-delay: var(--boot-delay, 0ms);
}

@keyframes boot-in {
  from {
    opacity: 0;
    transform: translateY(18px);
    clip-path: inset(0 0 100% 0);
  }
  to {
    opacity: 1;
    transform: none;
    clip-path: inset(0);
  }
}

.reveal {
  opacity: 1;
  transform: none;
}

.has-reveal .reveal {
  opacity: 0;
  transform: translateY(34px);
  transition:
    opacity 720ms var(--ease-out),
    transform 900ms var(--ease-out);
}

.has-reveal .reveal.is-visible {
  opacity: 1;
  transform: none;
}

@media (max-width: 760px) {
  body {
    background-size: 30px 30px;
  }

  .system-bar__inner {
    align-items: flex-start;
    padding-block: 0.85rem;
  }

  .system-nav {
    justify-content: flex-end;
    flex-wrap: wrap;
  }

  .system-nav a:first-child {
    display: none;
  }

  .intro-shell,
  .console-section {
    grid-template-columns: 1fr;
    gap: 2.5rem;
  }

  .intro-shell {
    min-height: auto;
    padding-block: 5rem;
  }

  .intro-title {
    font-size: clamp(3.1rem, 18vw, 5rem);
  }

  .instrument-rail,
  .intro-rail {
    position: static;
    padding: 1.25rem 0 0;
    border-top: 1px solid var(--hairline);
    border-left: 0;
  }

  .console-section {
    min-height: auto;
    padding-block: 5.5rem;
  }

  .fact-list div {
    grid-template-columns: 1fr;
    gap: 0.45rem;
  }

  .system-footer {
    align-items: flex-start;
    flex-direction: column;
  }
}

@media (prefers-reduced-motion: reduce) {
  html {
    scroll-behavior: auto;
  }

  *,
  *::before,
  *::after {
    animation-duration: 0.001ms !important;
    animation-delay: 0ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.001ms !important;
  }

  body {
    background-position: 0 0;
  }

  .instrument-rail {
    position: static;
  }

  .has-reveal .reveal {
    opacity: 1;
    transform: none;
  }

  .route-list::before {
    transform: scaleY(1);
  }
}
```

- [ ] **Step 4: Run markup and CSS tests**

Run:

```bash
python3 -m unittest tests.test_homepage.HomepageMarkupTests tests.test_homepage.HomepageStyleTests -v
```

Expected: all markup and style tests pass.

- [ ] **Step 5: Check responsive static rendering**

Serve `site/` on port 4173 and inspect:

- `1440×1000`
- `1024×768`
- `390×844`

At each width, confirm:

- No horizontal overflow.
- The instrumentation rail is sticky only above 760px.
- Body paragraphs remain below roughly 65 characters per line.
- Light and dark modes have coherent surfaces and visible focus rings.
- Content is visible before `site/home.js` exists.

- [ ] **Step 6: Commit the visual system**

```bash
git add site/home.css tests/test_homepage.py
git commit -m "feat: add systems console visual system" \
  -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>" \
  -m "Copilot-Session: 9e6d184d-77ff-4972-86bb-31358c4d2be8"
```

---

### Task 3: Add progressive interactions and cinematic motion

**Files:**
- Modify: `site/index.html`
- Modify: `tests/test_homepage.py`
- Create: `site/home.js`

**Interfaces:**
- Consumes: DOM hooks from Task 1 and presentation states from Task 2.
- Produces: `initThemeControl()`, `initEntrySequence()`, `initScrollScenes()`, `initEmailCopy()`, and `initFooterMetadata()`. No function may make core content depend on successful JavaScript execution.

- [ ] **Step 1: Add failing JavaScript contract tests**

Insert this class above the `if __name__ == "__main__":` block in `tests/test_homepage.py`:

```python
class HomepageScriptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.js = HOME_JS.read_text(encoding="utf-8") if HOME_JS.exists() else ""

    def test_defines_small_initializers(self):
        for name in (
            "initThemeControl",
            "initEntrySequence",
            "initScrollScenes",
            "initEmailCopy",
            "initFooterMetadata",
        ):
            with self.subTest(name=name):
                self.assertRegex(self.js, rf"function\s+{name}\s*\(")

    def test_loads_deferred_homepage_script(self):
        html = INDEX.read_text(encoding="utf-8")
        self.assertRegex(html, r'<script src="/home\.js\?v=1" defer></script>')

    def test_keeps_progressive_enhancement_guards(self):
        required_fragments = (
            "prefers-reduced-motion: reduce",
            "IntersectionObserver",
            "requestAnimationFrame",
            "navigator.clipboard",
            "window.location.assign",
        )
        for fragment in required_fragments:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.js)

    def test_preserves_theme_cycle_and_storage_key(self):
        self.assertIn("['auto', 'light', 'dark']", self.js)
        self.assertIn("localStorage.setItem('theme'", self.js)
        self.assertIn("localStorage.removeItem('theme')", self.js)

    def test_does_not_use_legacy_animation_behaviors(self):
        for fragment in ("data-count", "typed.textContent", "setInterval("):
            with self.subTest(fragment=fragment):
                self.assertNotIn(fragment, self.js)
```

- [ ] **Step 2: Run the script tests and confirm failure**

Run:

```bash
python3 -m unittest tests.test_homepage.HomepageScriptTests -v
```

Expected: failures because `site/home.js` and its deferred script tag do not exist.

- [ ] **Step 3: Link and create `site/home.js`**

Add this line immediately before `</body>` in `site/index.html`:

```html
  <script src="/home.js?v=1" defer></script>
```

Use this complete script:

```javascript
(function () {
  'use strict';

  var root = document.documentElement;
  var reduceMotion = window.matchMedia &&
    window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var toastTimer;

  function initThemeControl() {
    var control = document.querySelector('[data-theme-control]');
    var label = document.querySelector('[data-theme-label]');
    var order = ['auto', 'light', 'dark'];

    if (!control || !label) return;

    function currentMode() {
      var mode = root.getAttribute('data-color-mode');
      return order.indexOf(mode) === -1 ? 'auto' : mode;
    }

    function render(mode) {
      label.textContent = mode;
      control.setAttribute('aria-label', 'Theme: ' + mode + '. Activate to change.');
    }

    render(currentMode());

    control.addEventListener('click', function () {
      var mode = currentMode();
      var next = order[(order.indexOf(mode) + 1) % order.length];
      root.setAttribute('data-color-mode', next);

      try {
        if (next === 'auto') {
          localStorage.removeItem('theme');
        } else {
          localStorage.setItem('theme', next);
        }
      } catch (error) {
        root.setAttribute('data-theme-storage', 'unavailable');
      }

      render(next);
    });
  }

  function initEntrySequence() {
    if (reduceMotion) {
      root.classList.add('entry-complete');
      return;
    }

    root.classList.add('entry-running');
    window.setTimeout(function () {
      root.classList.remove('entry-running');
      root.classList.add('entry-complete');
    }, 1400);
  }

  function initScrollScenes() {
    var reveals = Array.prototype.slice.call(
      document.querySelectorAll('[data-reveal]')
    );
    var route = document.querySelector('[data-route]');

    if (!reduceMotion && 'IntersectionObserver' in window && reveals.length) {
      root.classList.add('has-reveal');

      var observer = new IntersectionObserver(function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        });
      }, {
        threshold: 0.16,
        rootMargin: '0px 0px -10% 0px'
      });

      reveals.forEach(function (element) {
        observer.observe(element);
      });
    }

    if (route) {
      if (reduceMotion || !('IntersectionObserver' in window)) {
        route.classList.add('is-visible');
      } else {
        var routeObserver = new IntersectionObserver(function (entries) {
          entries.forEach(function (entry) {
            if (!entry.isIntersecting) return;
            entry.target.classList.add('is-visible');
            routeObserver.unobserve(entry.target);
          });
        }, { threshold: 0.4 });
        routeObserver.observe(route);
      }
    }

    if (reduceMotion || !window.requestAnimationFrame) return;

    var framePending = false;

    function updateProgress() {
      var scrollable = document.documentElement.scrollHeight - window.innerHeight;
      var progress = scrollable > 0 ? window.scrollY / scrollable : 0;
      var clamped = Math.max(0, Math.min(1, progress));
      root.style.setProperty('--page-progress', (clamped * 100) + '%');
      root.style.setProperty('--grid-offset', (-clamped * 120) + 'px');
      framePending = false;
    }

    function requestProgressUpdate() {
      if (framePending) return;
      framePending = true;
      window.requestAnimationFrame(updateProgress);
    }

    updateProgress();
    window.addEventListener('scroll', requestProgressUpdate, { passive: true });
    window.addEventListener('resize', requestProgressUpdate);
  }

  function showToast(message) {
    var toast = document.querySelector('[data-toast]');
    var toastMessage = document.querySelector('[data-toast-message]');

    if (!toast || !toastMessage) return;

    toastMessage.textContent = message;
    toast.classList.add('is-visible');
    window.clearTimeout(toastTimer);
    toastTimer = window.setTimeout(function () {
      toast.classList.remove('is-visible');
    }, 2200);
  }

  function initEmailCopy() {
    var emailLink = document.querySelector('[data-email]');
    if (!emailLink) return;

    emailLink.addEventListener('click', function (event) {
      if (!navigator.clipboard || !navigator.clipboard.writeText) return;

      event.preventDefault();
      navigator.clipboard.writeText(emailLink.getAttribute('data-email'))
        .then(function () {
          showToast('Email copied to clipboard');
        })
        .catch(function () {
          window.location.assign(emailLink.getAttribute('href'));
        });
    });
  }

  function initFooterMetadata() {
    var year = document.getElementById('year');
    var updated = document.getElementById('updated');

    if (year) {
      year.textContent = String(new Date().getFullYear());
    }

    if (updated) {
      var modified = new Date(document.lastModified);
      if (Number.isNaN(modified.getTime())) {
        updated.textContent = 'unknown';
      } else {
        updated.textContent = modified.toLocaleDateString('en-NZ', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        });
      }
    }
  }

  initThemeControl();
  initEntrySequence();
  initScrollScenes();
  initEmailCopy();
  initFooterMetadata();
})();
```

- [ ] **Step 4: Run all source tests**

Run:

```bash
python3 -m unittest tests.test_homepage -v
```

Expected: all markup, style, and script tests pass.

- [ ] **Step 5: Verify browser behavior**

Serve `site/` locally, then use a browser to verify:

1. Theme control cycles `auto → light → dark → auto`.
2. Reload preserves explicit light or dark mode.
3. The boot sequence finishes within 1.4 seconds and does not restart while scrolling.
4. Scroll reveals run once and the route line draws once.
5. The top progress line follows scroll without console errors.
6. Keyboard focus is visible on every link and the theme button.
7. Email click copies on a secure browser context; forced clipboard rejection navigates to `mailto:hello@shunlyu.com`.
8. With reduced motion enabled, content is immediately visible, rails are not sticky, and the route line is already drawn.
9. With JavaScript disabled, every content section remains visible and all ordinary links work.

- [ ] **Step 6: Commit the homepage interactions**

```bash
git add site/index.html site/home.js tests/test_homepage.py
git commit -m "feat: add progressive homepage interactions" \
  -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>" \
  -m "Copilot-Session: 9e6d184d-77ff-4972-86bb-31358c4d2be8"
```

---

### Task 4: Add social artwork and complete integration validation

**Files:**
- Modify: `site/index.html`
- Modify: `tests/test_homepage.py`
- Create: `site/og-home.svg`
- Create: `site/og-home.png`

**Interfaces:**
- Consumes: The approved visual tokens and homepage metadata from Tasks 1 and 2.
- Produces: Public `https://shunlyu.com/og-home.png` Open Graph image and final validated homepage.

- [ ] **Step 1: Add failing social asset tests**

Insert this class above the `if __name__ == "__main__":` block in `tests/test_homepage.py`:

```python
class HomepageAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX.read_text(encoding="utf-8")

    def test_references_social_preview(self):
        self.assertIn(
            '<meta property="og:image" content="https://shunlyu.com/og-home.png">',
            self.html,
        )
        self.assertIn('<meta name="twitter:card" content="summary_large_image">', self.html)
        self.assertIn(
            '<meta name="twitter:image" content="https://shunlyu.com/og-home.png">',
            self.html,
        )

    def test_social_preview_is_1200_by_630_png(self):
        self.assertTrue(OG_PNG.exists())
        data = OG_PNG.read_bytes()
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
        width, height = struct.unpack(">II", data[16:24])
        self.assertEqual((width, height), (1200, 630))
```

- [ ] **Step 2: Run the asset tests and confirm failure**

Run:

```bash
python3 -m unittest tests.test_homepage.HomepageAssetTests -v
```

Expected: failures because the metadata and PNG do not exist.

- [ ] **Step 3: Add the social metadata**

In `site/index.html`, replace:

```html
  <meta name="twitter:card" content="summary">
```

with:

```html
  <meta property="og:image" content="https://shunlyu.com/og-home.png">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta property="og:image:alt" content="Shun Lyu, software engineer, shown in a restrained systems-console design.">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="https://shunlyu.com/og-home.png">
  <meta name="twitter:image:alt" content="Shun Lyu, software engineer, shown in a restrained systems-console design.">
```

- [ ] **Step 4: Create the editable social artwork**

Create `site/og-home.svg`:

```svg
<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">
  <rect width="1200" height="630" fill="#121610"/>
  <g stroke="#b7cb91" stroke-opacity=".08">
    <path d="M0 70H1200M0 140H1200M0 210H1200M0 280H1200M0 350H1200M0 420H1200M0 490H1200M0 560H1200"/>
    <path d="M70 0V630M140 0V630M210 0V630M280 0V630M350 0V630M420 0V630M490 0V630M560 0V630M630 0V630M700 0V630M770 0V630M840 0V630M910 0V630M980 0V630M1050 0V630M1120 0V630"/>
  </g>
  <text x="76" y="84" fill="#87927f" font-family="IBM Plex Mono, monospace" font-size="20" font-weight="600" letter-spacing="2">AUCKLAND / NEW ZEALAND</text>
  <text x="76" y="270" fill="#b7cb91" font-family="IBM Plex Mono, monospace" font-size="86" font-weight="600">&gt;</text>
  <text x="154" y="270" fill="#e7ecdf" font-family="IBM Plex Mono, monospace" font-size="86" font-weight="600" letter-spacing="-6">Shun Lyu</text>
  <text x="76" y="342" fill="#87927f" font-family="IBM Plex Sans, sans-serif" font-size="30">Software engineer working across cloud infrastructure,</text>
  <text x="76" y="386" fill="#87927f" font-family="IBM Plex Sans, sans-serif" font-size="30">developer tooling, Linux, Android, and embedded systems.</text>
  <line x1="76" y1="492" x2="1124" y2="492" stroke="#354032"/>
  <text x="76" y="548" fill="#b7cb91" font-family="IBM Plex Mono, monospace" font-size="20">reliability · automation · developer tooling</text>
  <text x="1124" y="548" fill="#87927f" text-anchor="end" font-family="IBM Plex Mono, monospace" font-size="20">SHUNLYU.COM</text>
</svg>
```

- [ ] **Step 5: Render `site/og-home.png` without adding a dependency**

1. Start the existing static server:

```bash
python3 -m http.server 4173 --bind 127.0.0.1 --directory site
```

2. Use the Playwright browser tool:
   - Navigate to `http://127.0.0.1:4173/og-home.svg`.
   - Resize the viewport to `1200×630`.
   - Capture a PNG screenshot at CSS scale to `site/og-home.png`.
   - Confirm the screenshot contains only the SVG with no browser margin.

3. Stop the server with its exact process ID.

- [ ] **Step 6: Run the complete test suite**

Run:

```bash
python3 -m unittest tests.test_homepage -v
```

Expected: all tests pass, including the 1200×630 PNG signature and dimension check.

- [ ] **Step 7: Run the final visual and behavior matrix**

With the local server running, check:

| View | Required result |
|---|---|
| 1440×1000 dark | Flagship dark design, sticky rails, no card grid, no clipped heading. |
| 1440×1000 light | Warm datasheet surface, readable muted text, same hierarchy as dark. |
| 390×844 dark | One column, static rails, no horizontal overflow, reachable theme control. |
| 390×844 light | Same content order and contrast, no desktop sticky behavior. |
| Reduced motion | No entry delay, sticky rails disabled, all content immediately visible. |
| JavaScript disabled | All sections and links visible; only enhanced theme/motion/copy behavior is absent. |
| Keyboard only | Skip link works; focus order follows document order; every control has a visible ring. |
| `/resume/` | Existing résumé layout, theme toggle, language control, and print behavior remain unchanged. |

Also verify:

```bash
curl --fail --silent --show-error http://127.0.0.1:4173/ >/dev/null
curl --fail --silent --show-error http://127.0.0.1:4173/resume/ >/dev/null
curl --fail --silent --show-error http://127.0.0.1:4173/og-home.png >/dev/null
git diff --exit-code HEAD -- site/resume/index.html site/resume.css site/style.css
```

Expected: all commands exit with status 0, and the browser console contains no errors or missing asset requests.

- [ ] **Step 8: Commit the social preview and final regression coverage**

```bash
git add site/index.html site/og-home.svg site/og-home.png tests/test_homepage.py
git commit -m "feat: add homepage social preview" \
  -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>" \
  -m "Copilot-Session: 9e6d184d-77ff-4972-86bb-31358c4d2be8"
```

- [ ] **Step 9: Confirm the final branch state**

Run:

```bash
python3 -m unittest tests.test_homepage -v
git status --short
git --no-pager log -4 --oneline
```

Expected:

- All homepage tests pass.
- `git status --short` is clean in an isolated worktree, or shows only the user's pre-existing `.gitignore` modification in the current worktree.
- The latest four commits are the semantic structure, visual system, interactions, and social preview commits.
