# Systems Dossier Résumé Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the current generic portfolio-style résumé with an independent bilingual systems dossier that is easy to scan, progressively reveals earlier work, and prints as an ink-safe version of the same design.

**Architecture:** Keep the site static and split the résumé into three focused files: semantic bilingual content in `site/resume/index.html`, all résumé presentation and print behavior in `site/resume.css`, and progressive enhancement in `site/resume.js`. Add a dedicated standard-library test module, then remove the résumé compatibility layer from `site/home.css` after the résumé no longer consumes shared styles.

**Tech Stack:** Static HTML, CSS, vanilla JavaScript, nginx, Python `unittest`, Podman for deployment verification

## Global Constraints

- Preserve every existing factual employment date, company, role, education record, contact path, and achievement.
- Keep all five existing Microsoft achievement points visible by default in each language.
- Keep every earlier-role achievement available in its expanded state.
- Preserve complete English and Chinese content.
- Initial language precedence is `localStorage["resume-language"]` → Chinese browser locale → English.
- Preserve the site's `localStorage["theme"]` and `auto → light → dark` cycle.
- Use IBM Plex Mono and IBM Plex Sans; add no font, icon, animation, framework, build, or runtime dependency.
- Use only the approved dark/light palette from the design specification.
- Core content must remain visible without JavaScript.
- Print only the active language, expand every role, and use the ink-safe dossier treatment.
- Do not modify employment claims or rewrite achievements beyond clarity and scanability.
- Do not modify the homepage's content or visual behavior.
- Preserve the user's existing unstaged `.gitignore` change.
- Do not push or deploy until the user explicitly requests it.

## File Structure

- Create `site/resume.js`: résumé-only theme, language, disclosure, print, email-copy, and footer behavior.
- Create `tests/test_resume.py`: dependency-free résumé markup, style, script, accessibility, responsive, and print contracts.
- Modify `site/resume/index.html`: semantic systems-dossier structure, bilingual content, metadata, and asset references.
- Replace `site/resume.css`: self-contained résumé tokens, screen design, responsive behavior, reduced motion, and print layout.
- Modify `site/home.css`: remove the obsolete `html:not(.home-page)` résumé compatibility layer.
- Modify `tests/test_homepage.py`: remove obsolete résumé compatibility tests and assert that homepage CSS remains homepage-only.
- Do not modify `site/style.css` or `site/vendor/primer/`; they remain available to unrelated pages but are no longer loaded by the résumé.

---

### Task 1: Extract Résumé Behavior Into a Dedicated Script

**Files:**
- Create: `site/resume.js`
- Create: `tests/test_resume.py`
- Modify: `site/resume/index.html:34-44,714-943`

**Interfaces:**
- Consumes: current IDs and classes in `site/resume/index.html`, including `#themeToggle`, `#wrap`, `.segmented [data-lang]`, `.rx-role__toggle`, `[data-print]`, `#emailLink`, `#toast`, `#toastMsg`, `#year`, and `#updated`.
- Produces: deferred `/resume.js?v=1` with the current résumé behavior preserved exactly.

- [ ] **Step 1: Write the failing script-extraction tests**

Create `tests/test_resume.py` with the initial contracts:

```python
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESUME_INDEX = ROOT / "site" / "resume" / "index.html"
RESUME_CSS = ROOT / "site" / "resume.css"
RESUME_JS = ROOT / "site" / "resume.js"


class ResumeScriptExtractionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = RESUME_INDEX.read_text(encoding="utf-8")
        cls.js = RESUME_JS.read_text(encoding="utf-8") if RESUME_JS.exists() else ""

    def test_loads_deferred_resume_script(self):
        self.assertIn('<script src="/resume.js?v=1" defer></script>', self.html)

    def test_large_behavior_script_is_not_inline(self):
        self.assertNotIn("/* ---- App-bar hairline on scroll ---- */", self.html)
        self.assertNotIn("function countUp(", self.html)
        self.assertNotIn("function initTimeline(", self.html)

    def test_extracted_script_preserves_current_behavior(self):
        for fragment in (
            "function countUp(",
            "function initTimeline(",
            "window.print()",
            "navigator.clipboard.writeText",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.js)

    def test_preserves_current_theme_contract(self):
        self.assertIn("['auto', 'light', 'dark']", self.js)
        self.assertIn("localStorage.setItem('theme'", self.js)
        self.assertIn("localStorage.removeItem('theme')", self.js)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the new tests and verify the expected failure**

Run:

```bash
python3 -m unittest tests.test_resume.ResumeScriptExtractionTests -v
```

Expected: failures because `site/resume.js` does not exist and the behavior is still inline.

- [ ] **Step 3: Replace the large inline script with a deferred script reference**

Keep the small no-flash head script, but remove the behavior IIFE currently at the bottom of `site/resume/index.html`. Add this immediately before `</body>`:

```html
  <script src="/resume.js?v=1" defer></script>
</body>
```

Do not change the résumé content or stylesheet references in this task.

- [ ] **Step 4: Move the current behavior script without changing logic**

Create `site/resume.js` by moving the complete IIFE currently inside the bottom `<script>` element in `site/resume/index.html` into the new file. Copy from the opening `(function () {` through the closing `})();`, including:

- App-bar `is-stuck` handling.
- Footer metadata.
- Theme cycle and storage.
- Scroll reveals.
- Count-up statistics.
- Role disclosures.
- Career timeline, scrollspy, and keyboard navigation.
- Language toggle.
- Print controls.
- Clipboard and `mailto:` fallback.

The only Task 1 behavior change is that the same script is loaded from `/resume.js?v=1` with `defer`; the JavaScript statements and selectors remain byte-for-byte equivalent to the removed inline IIFE.

- [ ] **Step 5: Run focused and existing regression tests**

Run:

```bash
python3 -m unittest tests.test_resume.ResumeScriptExtractionTests tests.test_homepage -v
node --check site/resume.js
```

Expected: all tests pass and `node --check` exits with status 0.

- [ ] **Step 6: Commit the extraction**

```bash
git add site/resume/index.html site/resume.js tests/test_resume.py
git commit -m "refactor: extract resume interactions" \
  -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>" \
  -m "Copilot-Session: 9e6d184d-77ff-4972-86bb-31358c4d2be8"
```

---

### Task 2: Build the Standalone Systems Dossier Markup and Visual System

**Files:**
- Modify: `tests/test_resume.py`
- Modify: `site/resume/index.html`
- Replace: `site/resume.css`

**Interfaces:**
- Consumes: `site/resume.js` from Task 1 and the complete existing bilingual factual content.
- Produces: `.resume-page` root marker; `[data-language-panel]`, `[data-language-control]`, `[data-theme-control]`, `[data-theme-label]`, `[data-disclosure]`, `[data-disclosure-control]`, `[data-disclosure-panel]`, `[data-print]`, `[data-email]`, and `[data-toast]` hooks used by Task 3.

- [ ] **Step 1: Add failing markup and visual-system tests**

Append these classes to `tests/test_resume.py`:

```python
class ResumeMarkupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = RESUME_INDEX.read_text(encoding="utf-8")

    def test_uses_standalone_resume_assets(self):
        self.assertIn('class="resume-page"', self.html)
        self.assertIn('href="/resume.css?v=3"', self.html)
        self.assertIn('src="/resume.js?v=1"', self.html)
        for legacy in (
            "/vendor/primer/light.css",
            "/vendor/primer/dark.css",
            "/vendor/primer/primer.css",
            "/style.css",
            "/home.css",
        ):
            with self.subTest(legacy=legacy):
                self.assertNotIn(legacy, self.html)

    def test_loads_approved_fonts_and_social_image(self):
        self.assertIn("IBM+Plex+Mono", self.html)
        self.assertIn("IBM+Plex+Sans", self.html)
        self.assertIn('content="https://shunlyu.com/og-home.png?v=1"', self.html)

    def test_uses_systems_dossier_structure(self):
        for fragment in (
            'class="resume-system-bar"',
            'class="resume-identity"',
            'data-section-index="01"',
            'data-section-index="02"',
            'data-section-index="03"',
            'data-section-index="04"',
            "resume-experience",
            "resume-capabilities",
            "resume-education",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.html)

    def test_keeps_complete_bilingual_panels(self):
        self.assertIn('data-language-panel="en"', self.html)
        self.assertIn('data-language-panel="zh"', self.html)
        self.assertIn("Software Engineer, Azure Kubernetes Service", self.html)
        self.assertIn("软件工程师，Azure Kubernetes Service", self.html)

    def test_current_role_keeps_five_visible_achievements_per_language(self):
        for role_id in ("role-en-microsoft", "role-zh-microsoft"):
            role = re.search(
                rf'<article[^>]+id="{role_id}"[^>]*>(.*?)</article>',
                self.html,
                flags=re.DOTALL,
            )
            self.assertIsNotNone(role)
            self.assertEqual(role.group(1).count("<li>"), 5)
            self.assertNotIn("data-disclosure-control", role.group(1))

    def test_earlier_roles_use_progressive_disclosure(self):
        for role_id in (
            "role-en-crown",
            "role-en-navico",
            "role-en-fp",
            "role-zh-crown",
            "role-zh-navico",
            "role-zh-fp",
        ):
            with self.subTest(role_id=role_id):
                role = re.search(
                    rf'<article[^>]+id="{role_id}"[^>]*>(.*?)</article>',
                    self.html,
                    flags=re.DOTALL,
                )
                self.assertIsNotNone(role)
                self.assertIn("data-disclosure-control", role.group(1))
                self.assertIn("data-disclosure-panel", role.group(1))

    def test_removes_generic_portfolio_patterns(self):
        for fragment in (
            "data-count=",
            "rx-timeline",
            "rx-stat",
            "tech-chip",
            'class="chip"',
            "brand-gradient",
            "rx-header__mark",
        ):
            with self.subTest(fragment=fragment):
                self.assertNotIn(fragment, self.html)


class ResumeStyleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = RESUME_CSS.read_text(encoding="utf-8")

    def test_defines_approved_theme_tokens(self):
        for value in (
            "#121610",
            "#e7ecdf",
            "#87927f",
            "#b7cb91",
            "#354032",
            "#e9e5d9",
            "#222a20",
            "#596055",
            "#53663e",
            "#c9c6ba",
        ):
            with self.subTest(value=value):
                self.assertIn(value, self.css.lower())

    def test_uses_approved_font_roles(self):
        self.assertIn('"IBM Plex Mono"', self.css)
        self.assertIn('"IBM Plex Sans"', self.css)

    def test_uses_indexed_layout_and_plain_capabilities(self):
        self.assertRegex(
            self.css,
            r"\.resume-indexed-section\s*\{[^}]*grid-template-columns:",
        )
        self.assertIn(".resume-capabilities", self.css)
        self.assertNotIn(".tech-chip", self.css)
        self.assertNotIn("--brand-gradient", self.css)

    def test_css_braces_are_balanced(self):
        self.assertEqual(self.css.count("{"), self.css.count("}"))
```

- [ ] **Step 2: Run the new structural tests and verify failure**

Run:

```bash
python3 -m unittest \
  tests.test_resume.ResumeMarkupTests \
  tests.test_resume.ResumeStyleTests -v
```

Expected: failures for legacy stylesheet references, missing dossier structure, old counters/timeline/chips, and missing approved tokens.

- [ ] **Step 3: Replace the document head and system bar**

Update `site/resume/index.html` to use:

```html
<!doctype html>
<html lang="en" class="resume-page" data-color-mode="auto" data-language="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Shun Lyu — Résumé</title>
  <meta name="description" content="Résumé of Shun Lyu, a software engineer working on Azure Kubernetes Service with experience across embedded systems, Linux, Android, build infrastructure, and cloud reliability.">
  <meta name="author" content="Shun Lyu">
  <meta name="theme-color" content="#E9E5D9" media="(prefers-color-scheme: light)">
  <meta name="theme-color" content="#121610" media="(prefers-color-scheme: dark)">

  <meta property="og:type" content="profile">
  <meta property="og:title" content="Shun Lyu — Résumé">
  <meta property="og:description" content="Software engineer working across cloud infrastructure, developer tooling, Linux, Android, and embedded systems.">
  <meta property="og:url" content="https://shunlyu.com/resume/">
  <meta property="og:site_name" content="Shun Lyu">
  <meta property="og:image" content="https://shunlyu.com/og-home.png?v=1">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:image" content="https://shunlyu.com/og-home.png?v=1">

  <link rel="icon" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 32 32'%3E%3Crect width='32' height='32' rx='4' fill='%23121610'/%3E%3Cpath d='M8 10l6 6-6 6M16 22h8' fill='none' stroke='%23b7cb91' stroke-width='2.5'/%3E%3C/svg%3E">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600&display=swap">
  <link rel="stylesheet" href="/resume.css?v=3">

  <script>
    (function () {
      var root = document.documentElement;
      try {
        var theme = localStorage.getItem('theme');
        if (theme === 'light' || theme === 'dark') {
          root.setAttribute('data-color-mode', theme);
        }
      } catch (error) {
        root.setAttribute('data-theme-storage', 'unavailable');
      }

      var language = 'en';
      var savedLanguage = null;
      try {
        savedLanguage = localStorage.getItem('resume-language');
      } catch (error) {
        root.setAttribute('data-language-storage', 'unavailable');
      }
      if (savedLanguage === 'en' || savedLanguage === 'zh') {
        language = savedLanguage;
      } else {
        var browserLanguages = navigator.languages || [navigator.language || 'en'];
        language = browserLanguages.some(function (value) {
          return /^zh(?:-|$)/i.test(value);
        }) ? 'zh' : 'en';
      }
      root.setAttribute('data-language', language);
      root.lang = language === 'zh' ? 'zh' : 'en';
      root.classList.add('resume-init');
    })();
  </script>
</head>
<body id="top">
  <a class="resume-skip-link" href="#resume-main">Skip to content</a>

  <header class="resume-system-bar" id="appbar">
    <a class="resume-home-link" href="/" aria-label="Shun Lyu, home">
      <span aria-hidden="true">&gt;</span> SL / résumé
    </a>
    <nav class="resume-controls" aria-label="Résumé controls">
      <div class="resume-language-control segmented" data-language-control aria-label="Language">
        <button type="button" data-lang="en" aria-pressed="true">EN</button>
        <button type="button" data-lang="zh" aria-pressed="false">中文</button>
      </div>
      <button type="button" data-print>print / PDF</button>
      <button id="themeToggle" type="button" data-theme-control>
        theme:<span data-theme-label>auto</span>
      </button>
    </nav>
  </header>
```

The `#appbar`, `#themeToggle`, `.segmented`, `#wrap`, `.lang-en`, and `.lang-zh` hooks are temporary migration aliases. They keep the extracted Task 1 script functional until Task 3 switches the script to the final data attributes.

- [ ] **Step 4: Rebuild the bilingual dossier content**

Build `resume-main > resume-document` with the English panel first and the Chinese panel second. Inside each panel, use the order identity → profile → experience → capabilities → education.

Use this exact English identity and profile:

```html
<main id="resume-main" class="resume-main">
  <article class="resume-document" id="wrap" data-lang="en">
    <div class="lang-en" data-language-panel="en">
      <header class="resume-identity">
        <div>
          <p class="resume-label">Auckland / New Zealand</p>
          <h1>Shun Lyu</h1>
          <p class="resume-role-line">Software Engineer, Azure Kubernetes Service <span>@ Microsoft</span></p>
          <p class="resume-intro">Software engineer working on Azure Kubernetes Service, with earlier work across embedded systems, Linux, Android, and build infrastructure.</p>
        </div>
        <dl class="resume-identity-meta">
          <div><dt>focus</dt><dd>reliability / automation / developer tooling</dd></div>
          <div><dt>location</dt><dd>Auckland, New Zealand</dd></div>
          <div><dt>links</dt><dd><a href="https://github.com/sinmentis">GitHub</a> / <a href="https://www.linkedin.com/in/shunlyu">LinkedIn</a> / <a id="emailLink" href="mailto:hello@shunlyu.com" data-email="hello@shunlyu.com">email</a></dd></div>
        </dl>
      </header>

      <section class="resume-indexed-section" data-section-index="01" aria-labelledby="profile-en">
        <div class="resume-section-index"><span>01</span>Profile</div>
        <div class="resume-section-body">
          <h2 id="profile-en">Systems work, from devices to cloud infrastructure.</h2>
          <p>Software Engineer with 7+ years across embedded systems, Linux platforms, developer tooling, and cloud infrastructure. Currently on the Azure Kubernetes Service team at Microsoft, working on resource APIs and control-plane reliability for production Kubernetes clusters.</p>
        </div>
      </section>
```

Insert the English experience section from Step 5, followed by:

```html
      <section class="resume-indexed-section" data-section-index="03" aria-labelledby="capabilities-en">
        <div class="resume-section-index"><span>03</span>Capabilities</div>
        <div class="resume-section-body">
          <h2 id="capabilities-en">Technical context</h2>
          <div class="resume-capabilities">
            <div><h3>Languages</h3><p>C, C++, C#, Python, Java, Bash</p></div>
            <div><h3>Cloud and delivery</h3><p>Azure, Kubernetes, Docker, CI/CD, GitHub Actions, Jenkins</p></div>
            <div><h3>Platforms</h3><p>Linux kernel and user space, Android AOSP, embedded Linux, .NET MAUI, ARM</p></div>
            <div><h3>Engineering focus</h3><p>System reliability, infrastructure automation, developer tooling, build systems</p></div>
          </div>
        </div>
      </section>

      <section class="resume-indexed-section" data-section-index="04" aria-labelledby="education-en">
        <div class="resume-section-index"><span>04</span>Education</div>
        <div class="resume-section-body resume-education">
          <h2 id="education-en">Education</h2>
          <div class="resume-education-item"><time>2025</time><p><strong>Master of Fintech and Investment Management</strong><br>Lincoln University, New Zealand</p></div>
          <div class="resume-education-item"><time>2019</time><p><strong>BE (Hons), Computer Engineering</strong><br>University of Canterbury, New Zealand · minors: Communication &amp; Network Engineering</p></div>
        </div>
      </section>
    </div>
```

Use this exact Chinese identity and profile:

```html
    <div class="lang-zh" data-language-panel="zh">
      <header class="resume-identity">
        <div>
          <p class="resume-label">新西兰 / 奥克兰</p>
          <h1>Shun Lyu</h1>
          <p class="resume-role-line">软件工程师，Azure Kubernetes Service <span>@ Microsoft</span></p>
          <p class="resume-intro">目前从事 Azure Kubernetes Service 开发，此前经历涵盖嵌入式系统、Linux、Android 与构建基础设施。</p>
        </div>
        <dl class="resume-identity-meta">
          <div><dt>方向</dt><dd>可靠性 / 自动化 / 开发者工具</dd></div>
          <div><dt>地点</dt><dd>新西兰，奥克兰</dd></div>
          <div><dt>链接</dt><dd><a href="https://github.com/sinmentis">GitHub</a> / <a href="https://www.linkedin.com/in/shunlyu">LinkedIn</a> / <a href="mailto:hello@shunlyu.com" data-email="hello@shunlyu.com">邮箱</a></dd></div>
        </dl>
      </header>

      <section class="resume-indexed-section" data-section-index="01" aria-labelledby="profile-zh">
        <div class="resume-section-index"><span>01</span>概述</div>
        <div class="resume-section-body">
          <h2 id="profile-zh">从设备系统到云基础设施。</h2>
          <p>拥有 7 年以上经验的软件工程师，经历涵盖嵌入式系统、Linux 平台、开发者工具和云基础设施。目前在微软 Azure Kubernetes Service 团队，负责资源 API 与生产级 Kubernetes 集群控制面的可靠性。</p>
        </div>
      </section>
```

Insert the Chinese experience section from Step 5, followed by:

```html
      <section class="resume-indexed-section" data-section-index="03" aria-labelledby="capabilities-zh">
        <div class="resume-section-index"><span>03</span>技能</div>
        <div class="resume-section-body">
          <h2 id="capabilities-zh">技术背景</h2>
          <div class="resume-capabilities">
            <div><h3>编程语言</h3><p>C、C++、C#、Python、Java、Bash</p></div>
            <div><h3>云与交付</h3><p>Azure、Kubernetes、Docker、CI/CD、GitHub Actions、Jenkins</p></div>
            <div><h3>平台</h3><p>Linux 内核与用户态、Android AOSP、嵌入式 Linux、.NET MAUI、ARM</p></div>
            <div><h3>工程方向</h3><p>系统可靠性、基础设施自动化、开发者工具、构建系统</p></div>
          </div>
        </div>
      </section>

      <section class="resume-indexed-section" data-section-index="04" aria-labelledby="education-zh">
        <div class="resume-section-index"><span>04</span>教育</div>
        <div class="resume-section-body resume-education">
          <h2 id="education-zh">教育</h2>
          <div class="resume-education-item"><time>2025</time><p><strong>金融科技与投资管理硕士</strong><br>林肯大学，新西兰</p></div>
          <div class="resume-education-item"><time>2019</time><p><strong>工程荣誉学士，计算机工程</strong><br>坎特伯雷大学，新西兰 · 辅修：通信与网络工程</p></div>
        </div>
      </section>
    </div>
  </article>
</main>
```

Finish the document with:

```html
  <footer class="resume-footer">
    <span>© <span id="year">2026</span> Shun Lyu · updated <span id="updated">—</span></span>
    <a href="/">return / home</a>
  </footer>

  <div class="resume-toast" id="toast" data-toast role="status" aria-live="polite">
    <span id="toastMsg" data-toast-message>Email copied to clipboard</span>
  </div>

  <script src="/resume.js?v=1" defer></script>
</body>
</html>
```

- [ ] **Step 5: Convert experience entries to current and progressive role patterns**

Use this exact current-role shell in English and retain the existing five English `<li>` strings unchanged:

```html
<article class="resume-role resume-role--current rx-role" id="role-en-microsoft">
  <header class="resume-role-header">
    <div>
      <h3>Software Engineer, Azure Kubernetes Service</h3>
      <p>Microsoft · Auckland, New Zealand</p>
    </div>
    <time>Apr 2026 — Present</time>
  </header>
  <ul class="resume-achievements">
    <li>Designed and shipped a new Azure resource API for managing custom VM image specifications on Kubernetes clusters end to end — API contract, access control, and CRUD semantics — then implemented and reviewed 15+ production changes from design through rollout.</li>
    <li>Hardened cluster reliability by fixing a background reconciliation bug that could overwrite live node metadata, a deadlock in the resource-deletion path, and image-reuse logic that failed to recover from broken image builds, eliminating a class of state corruption in production.</li>
    <li>Added safety guardrails for a feature in preview by blocking unsupported VM configurations (e.g., confidential computing VMs) and scoping validation to the specific resource being changed, removing false-positive failures on unrelated resources.</li>
    <li>Improved a list API's performance and correctness at scale with a targeted database index and batched, fallback-safe metadata merging, and documented inheritance and pagination edge cases for the team.</li>
    <li>Led cross-team integration to exclude a subset of managed resources from an automated patching pipeline and preserve feature state across automatic upgrades, then took ownership of the related validation code.</li>
  </ul>
  <p class="resume-context"><span>context /</span> Azure · C# · Python · Kubernetes · CI/CD · Distributed Systems</p>
</article>
```

Use the corresponding Chinese shell and move all five existing Chinese Microsoft `<li>` strings unchanged:

```html
<article class="resume-role resume-role--current rx-role" id="role-zh-microsoft">
  <header class="resume-role-header">
    <div>
      <h3>软件工程师，Azure Kubernetes Service</h3>
      <p>Microsoft · 新西兰，奥克兰</p>
    </div>
    <time>2026.4 — 至今</time>
  </header>
  <ul class="resume-achievements">
    <li>为 Kubernetes 集群上的自定义 VM 镜像规格设计并交付了一个全新的 Azure 资源 API——从 API 契约、访问控制到增删改查语义均由本人主导设计，并在此基础上实现和评审了 15+ 个生产环境变更，覆盖从设计到上线的全过程。</li>
    <li>通过修复后台协调（reconciliation）逻辑中可能覆盖存活节点元数据的缺陷、资源删除路径中的死锁问题，以及镜像复用逻辑在镜像构建失败后无法正常恢复的问题，消除了生产集群中的状态损坏隐患，提升了平台可靠性。</li>
    <li>为预览阶段的新功能构建安全防护机制——阻止其在不支持的 VM 配置（如机密计算 VM）上启用，并将校验逻辑收窄到仅针对被修改的具体资源，避免了对无关资源的误报。</li>
    <li>通过增加针对性的数据库索引和带降级兜底的批量元数据合并，提升了某个大规模 list API 的性能与正确性，并为团队梳理文档记录了继承规则与分页边界情况。</li>
    <li>主导跨团队协作，将一部分受管资源从自动化补丁流水线中排除，并确保某功能的状态在自动升级过程中正确保留；此后成为相关校验代码的负责人。</li>
  </ul>
  <p class="resume-context"><span>技术背景 /</span> Azure · C# · Python · Kubernetes · CI/CD · 分布式系统</p>
</article>
```

Use this exact earlier-role pattern:

```html
<article class="resume-role rx-role" id="role-en-crown" data-disclosure>
  <header class="resume-role-header">
    <div>
      <h3>Software Engineer</h3>
      <p>Crown Equipment Corporation · Robotics Technology Centre · Auckland</p>
    </div>
    <time>Jun 2024 — Mar 2026</time>
  </header>
  <p class="resume-role-summary">Build infrastructure, CI/CD, static analysis, performance measurement, and Android development workflows.</p>
  <button
    class="resume-disclosure-control rx-role__toggle"
    type="button"
    aria-expanded="true"
    aria-controls="details-en-crown"
    data-disclosure-control
    data-open-label="details +"
    data-close-label="details −"
  >details −</button>
  <div id="details-en-crown" class="resume-role-details" data-disclosure-panel>
    <div class="resume-role-details-inner">
      <ul class="resume-achievements">
        <li>Led adoption of the C#/.NET ecosystem across internal Android projects, pioneering MAUI/Android optimizations and automated build flows.</li>
        <li>Designed and maintained CI/CD pipelines (GitHub Actions, Jenkins) for multi-platform C++ and C# applications, including containerized Android builds.</li>
        <li>Automated dependency management, package publishing, and test orchestration, removing manual steps from the release process.</li>
        <li>Built static-analysis and performance-measurement frameworks across C++, C#, and Python to catch regressions before release.</li>
      </ul>
      <p class="resume-context"><span>context /</span> C# · .NET · C++ · Python · GitHub Actions · Jenkins · Linux · Android</p>
    </div>
  </div>
</article>
```

Use these exact summaries for the remaining roles:

| ID | Summary |
|---|---|
| `role-en-navico` | `ARM Linux platforms, kernel and bootloader debugging, containerized toolchains, and integration automation.` |
| `role-en-fp` | `Connected appliances, embedded Linux, bare-metal firmware, Qt, and reproducible development environments.` |
| `role-zh-crown` | `构建基础设施、CI/CD、静态分析、性能度量与 Android 开发流程。` |
| `role-zh-navico` | `ARM Linux 平台、内核与 bootloader 调试、容器化工具链和集成自动化。` |
| `role-zh-fp` | `联网家电、嵌入式 Linux、裸机固件、Qt 与可复现开发环境。` |

For each of these five roles:

- Keep the existing company, role, location, and date.
- Move every existing achievement `<li>` into `data-disclosure-panel`.
- Wrap each panel's achievements and context line in `.resume-role-details-inner`.
- Include the temporary `rx-role` class on the article and `rx-role__toggle` class on the disclosure button.
- Set the source `aria-expanded="true"` and show the close label so no-JavaScript and Task 2 behavior match the visible detail content.
- Use IDs `details-en-navico`, `details-en-fp`, `details-zh-crown`, `details-zh-navico`, and `details-zh-fp`.
- Use `details +` / `details −` in English and `详情 +` / `详情 −` in Chinese.
- Keep one compact `resume-context` line using the technologies already associated with the role.

- [ ] **Step 6: Replace `site/resume.css` with the standalone dossier foundation**

Start the file with the complete theme and base contracts:

```css
html.resume-page {
  color-scheme: light;
  --resume-bg: #e9e5d9;
  --resume-fg: #222a20;
  --resume-muted: #596055;
  --resume-signal: #53663e;
  --resume-hairline: #c9c6ba;
  --resume-grid: rgba(83, 102, 62, 0.055);
  --resume-panel: rgba(255, 255, 255, 0.18);
  --resume-focus: 0 0 0 3px rgba(83, 102, 62, 0.34);
  --resume-mono: "IBM Plex Mono", ui-monospace, SFMono-Regular, Menlo, Consolas, monospace;
  --resume-sans: "IBM Plex Sans", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  --resume-container: 72rem;
  --resume-bar-height: 3.5rem;
  --resume-ease: cubic-bezier(0.22, 1, 0.36, 1);
  background: var(--resume-bg);
  scroll-behavior: smooth;
}

@media (prefers-color-scheme: dark) {
  html.resume-page {
    color-scheme: dark;
    --resume-bg: #121610;
    --resume-fg: #e7ecdf;
    --resume-muted: #87927f;
    --resume-signal: #b7cb91;
    --resume-hairline: #354032;
    --resume-grid: rgba(183, 203, 145, 0.045);
    --resume-panel: rgba(20, 27, 18, 0.72);
    --resume-focus: 0 0 0 3px rgba(183, 203, 145, 0.3);
  }
}

html.resume-page[data-color-mode="light"] {
  color-scheme: light;
  --resume-bg: #e9e5d9;
  --resume-fg: #222a20;
  --resume-muted: #596055;
  --resume-signal: #53663e;
  --resume-hairline: #c9c6ba;
  --resume-grid: rgba(83, 102, 62, 0.055);
  --resume-panel: rgba(255, 255, 255, 0.18);
  --resume-focus: 0 0 0 3px rgba(83, 102, 62, 0.34);
}

html.resume-page[data-color-mode="dark"] {
  color-scheme: dark;
  --resume-bg: #121610;
  --resume-fg: #e7ecdf;
  --resume-muted: #87927f;
  --resume-signal: #b7cb91;
  --resume-hairline: #354032;
  --resume-grid: rgba(183, 203, 145, 0.045);
  --resume-panel: rgba(20, 27, 18, 0.72);
  --resume-focus: 0 0 0 3px rgba(183, 203, 145, 0.3);
}

html.resume-page *,
html.resume-page *::before,
html.resume-page *::after {
  box-sizing: border-box;
}

html.resume-page body {
  margin: 0;
  color: var(--resume-fg);
  background:
    linear-gradient(var(--resume-grid) 1px, transparent 1px),
    linear-gradient(90deg, var(--resume-grid) 1px, transparent 1px),
    var(--resume-bg);
  background-size: 48px 48px;
  font-family: var(--resume-sans);
  line-height: 1.6;
  text-rendering: optimizeLegibility;
}

html.resume-page a {
  color: inherit;
  text-underline-offset: 0.22em;
}

html.resume-page button {
  color: inherit;
  font: inherit;
}

html.resume-page :focus-visible {
  outline: 0;
  box-shadow: var(--resume-focus);
}

[hidden] {
  display: none !important;
}

html.resume-page[data-language="en"] [data-language-panel="zh"],
html.resume-page[data-language="zh"] [data-language-panel="en"],
#wrap[data-lang="en"] .lang-zh,
#wrap[data-lang="zh"] .lang-en {
  display: none;
}

.rx-role.is-collapsed .resume-role-details {
  display: none;
}
```

Add the primary dossier layout:

```css
.resume-system-bar {
  position: sticky;
  top: 0;
  z-index: 20;
  min-height: var(--resume-bar-height);
  padding: 0.75rem max(1rem, calc((100vw - var(--resume-container)) / 2));
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  color: var(--resume-muted);
  background: color-mix(in srgb, var(--resume-bg) 90%, transparent);
  border-bottom: 1px solid var(--resume-hairline);
  font-family: var(--resume-mono);
  font-size: 0.72rem;
}

.resume-main {
  width: min(100%, var(--resume-container));
  margin-inline: auto;
  padding: clamp(3rem, 7vw, 6rem) clamp(1rem, 3vw, 2rem);
}

.resume-identity {
  display: grid;
  grid-template-columns: minmax(0, 1.6fr) minmax(16rem, 0.4fr);
  gap: clamp(2rem, 6vw, 5rem);
  align-items: end;
  padding-bottom: clamp(2rem, 5vw, 3.5rem);
  border-bottom: 1px solid var(--resume-hairline);
}

.resume-identity h1 {
  margin: 0;
  font-family: var(--resume-mono);
  font-size: clamp(3.5rem, 10vw, 7.5rem);
  font-weight: 600;
  letter-spacing: -0.07em;
  line-height: 0.88;
  text-wrap: balance;
}

.resume-intro,
.resume-section-body > p,
.resume-role-summary,
.resume-achievements {
  max-width: 65ch;
}

.resume-indexed-section {
  display: grid;
  grid-template-columns: minmax(7rem, 0.24fr) minmax(0, 1fr);
  gap: clamp(1.5rem, 4vw, 3rem);
  padding-block: clamp(3rem, 7vw, 5rem);
  border-bottom: 1px solid var(--resume-hairline);
}

.resume-section-index {
  color: var(--resume-muted);
  font-family: var(--resume-mono);
  font-size: 0.7rem;
  line-height: 1.7;
  text-transform: uppercase;
}

.resume-section-index span {
  display: block;
  margin-bottom: 0.6rem;
  color: var(--resume-signal);
  font-weight: 600;
}

.resume-section-body h2 {
  margin: 0 0 1.25rem;
  font-family: var(--resume-mono);
  font-size: clamp(1.45rem, 3vw, 2.25rem);
  letter-spacing: -0.04em;
  line-height: 1.1;
  text-wrap: balance;
}
```

Add role and capability rules:

```css
.resume-role {
  padding: 0 0 2rem 1.25rem;
  border-left: 1px solid var(--resume-hairline);
}

.resume-role + .resume-role {
  padding-top: 2rem;
  border-top: 1px solid var(--resume-hairline);
}

.resume-role--current {
  border-left: 2px solid var(--resume-signal);
}

.resume-role-header {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  gap: 1rem;
  align-items: start;
}

.resume-role-header h3 {
  margin: 0;
  font-family: var(--resume-mono);
  font-size: 1rem;
  line-height: 1.35;
}

.resume-role-header p,
.resume-role-header time,
.resume-context {
  color: var(--resume-muted);
  font-family: var(--resume-mono);
  font-size: 0.7rem;
}

.resume-achievements {
  margin: 1rem 0;
  padding: 0;
  list-style: none;
}

.resume-achievements li {
  position: relative;
  margin: 0.7rem 0;
  padding-left: 1.3rem;
}

.resume-achievements li::before {
  content: ">";
  position: absolute;
  left: 0;
  color: var(--resume-signal);
  font-family: var(--resume-mono);
}

.resume-disclosure-control {
  min-height: 2.75rem;
  margin-top: 0.5rem;
  padding: 0;
  color: var(--resume-signal);
  background: transparent;
  border: 0;
  font-family: var(--resume-mono);
  font-size: 0.72rem;
  cursor: pointer;
}

.resume-role-details {
  padding-top: 0.25rem;
}

.resume-capabilities {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1.5rem 2rem;
}

.resume-capabilities > div {
  padding-top: 0.9rem;
  border-top: 1px solid var(--resume-hairline);
}

.resume-capabilities h3 {
  margin: 0 0 0.4rem;
  font-family: var(--resume-mono);
  font-size: 0.75rem;
}

.resume-capabilities p {
  margin: 0;
  color: var(--resume-muted);
}
```

Add:

```css
.resume-skip-link {
  position: fixed;
  top: 0.75rem;
  left: 0.75rem;
  z-index: 50;
  padding: 0.6rem 0.8rem;
  color: var(--resume-bg);
  background: var(--resume-signal);
  font-family: var(--resume-mono);
  transform: translateY(-180%);
}

.resume-skip-link:focus {
  transform: translateY(0);
}

.resume-home-link,
.resume-controls,
.resume-language-control {
  display: flex;
  align-items: center;
}

.resume-home-link {
  gap: 0.45rem;
  color: var(--resume-fg);
  font-weight: 600;
  text-decoration: none;
}

.resume-home-link span {
  color: var(--resume-signal);
}

.resume-controls {
  gap: 1rem;
}

.resume-language-control {
  gap: 0.2rem;
}

.resume-controls button {
  min-height: 2.25rem;
  padding: 0 0.35rem;
  color: var(--resume-muted);
  background: transparent;
  border: 0;
  font-family: var(--resume-mono);
  font-size: 0.7rem;
  cursor: pointer;
}

.resume-controls button:hover,
.resume-controls button[aria-pressed="true"] {
  color: var(--resume-signal);
}

.resume-controls button:active,
.resume-home-link:active {
  transform: translateY(1px);
}

.resume-label {
  margin: 0 0 1rem;
  color: var(--resume-signal);
  font-family: var(--resume-mono);
  font-size: 0.7rem;
}

.resume-role-line {
  margin: 1rem 0 0;
  font-family: var(--resume-mono);
  font-size: clamp(0.9rem, 2vw, 1.1rem);
}

.resume-role-line span {
  color: var(--resume-signal);
}

.resume-intro {
  margin: 1rem 0 0;
  color: var(--resume-muted);
}

.resume-identity-meta {
  margin: 0;
}

.resume-identity-meta div {
  display: grid;
  grid-template-columns: 4.5rem 1fr;
  gap: 0.75rem;
  padding-block: 0.7rem;
  border-top: 1px solid var(--resume-hairline);
}

.resume-identity-meta dt,
.resume-identity-meta dd {
  margin: 0;
  font-family: var(--resume-mono);
  font-size: 0.7rem;
}

.resume-identity-meta dt {
  color: var(--resume-muted);
}

.resume-education-item {
  display: grid;
  grid-template-columns: 5rem 1fr;
  gap: 1rem;
  padding-block: 1rem;
  border-top: 1px solid var(--resume-hairline);
}

.resume-education-item time {
  color: var(--resume-muted);
  font-family: var(--resume-mono);
  font-size: 0.72rem;
}

.resume-education-item p {
  margin: 0;
}

.resume-footer {
  width: min(100%, var(--resume-container));
  margin-inline: auto;
  padding: 1.25rem clamp(1rem, 3vw, 2rem);
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  color: var(--resume-muted);
  border-top: 1px solid var(--resume-hairline);
  font-family: var(--resume-mono);
  font-size: 0.68rem;
}

.resume-toast {
  position: fixed;
  left: 50%;
  bottom: 1.5rem;
  z-index: 40;
  padding: 0.65rem 0.9rem;
  color: var(--resume-bg);
  background: var(--resume-signal);
  font-family: var(--resume-mono);
  font-size: 0.72rem;
  opacity: 0;
  transform: translate(-50%, 120%);
  transition: opacity 180ms var(--resume-ease), transform 240ms var(--resume-ease);
}

.resume-toast.is-shown,
.resume-toast.is-visible {
  opacity: 1;
  transform: translate(-50%, 0);
}
```

Do not introduce gradients, pills, generic card shadows, or a second accent.

- [ ] **Step 7: Run structural tests and inspect the diff**

Run:

```bash
python3 -m unittest \
  tests.test_resume.ResumeMarkupTests \
  tests.test_resume.ResumeStyleTests -v
git diff --check
```

Expected: all Task 2 tests pass and `git diff --check` reports no errors.

- [ ] **Step 8: Commit the systems dossier structure**

```bash
git add site/resume/index.html site/resume.css tests/test_resume.py
git commit -m "feat: redesign resume as systems dossier" \
  -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>" \
  -m "Copilot-Session: 9e6d184d-77ff-4972-86bb-31358c4d2be8"
```

---

### Task 3: Implement Locale Selection and Progressive Disclosure

**Files:**
- Modify: `tests/test_resume.py`
- Replace: `site/resume.js`
- Modify: `site/resume/index.html`
- Modify: `site/resume.css`

**Interfaces:**
- Consumes: Task 2's data attributes and semantic controls.
- Produces: `data-language`, `data-color-mode`, `has-disclosures`, per-panel `hidden`, per-control `aria-pressed`, per-disclosure `aria-expanded`, and toast `is-visible` state.

- [ ] **Step 1: Replace the extraction tests with failing final-script behavior tests**

Replace `ResumeScriptExtractionTests` with:

```python
class ResumeScriptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = RESUME_INDEX.read_text(encoding="utf-8")
        cls.js = RESUME_JS.read_text(encoding="utf-8")

    def test_loads_deferred_resume_script(self):
        self.assertIn('<script src="/resume.js?v=1" defer></script>', self.html)

    def test_large_behavior_script_is_not_inline(self):
        self.assertNotIn("function countUp(", self.html)
        self.assertNotIn("function initTimeline(", self.html)

    def test_defines_only_final_initializers(self):
        for name in (
            "initThemeControl",
            "initLanguageControl",
            "initExperienceDisclosures",
            "initPrintControls",
            "initEmailCopy",
            "initFooterMetadata",
        ):
            with self.subTest(name=name):
                self.assertRegex(self.js, rf"function\s+{name}\s*\(")
        for legacy in ("countUp", "initTimeline", "initLegacyPresentation", "IntersectionObserver"):
            with self.subTest(legacy=legacy):
                self.assertNotIn(legacy, self.js)

    def test_language_precedence_and_persistence_are_explicit(self):
        self.assertIn("localStorage.getItem('resume-language')", self.html)
        self.assertIn("navigator.languages", self.html)
        self.assertIn("navigator.language", self.html)
        self.assertIn("localStorage.setItem('resume-language'", self.js)
        self.assertIn("root.lang = language === 'zh' ? 'zh' : 'en'", self.js)

    def test_inactive_language_is_removed_from_accessibility_tree(self):
        self.assertIn("panel.hidden = panelLanguage !== language", self.js)

    def test_disclosures_are_progressive_enhancements(self):
        self.assertNotRegex(self.html, r"data-disclosure-panel[^>]*\shidden")
        self.assertIn("root.classList.add('has-disclosures')", self.js)
        self.assertIn("panel.hidden = false", self.js)
        self.assertIn("panel.hidden = true", self.js)
        self.assertIn("panel.setAttribute('data-open', 'true')", self.js)
        self.assertIn("panel.removeAttribute('data-open')", self.js)
        self.assertIn("button.setAttribute('aria-expanded'", self.js)

    def test_print_expands_details_without_javascript_state_loss(self):
        self.assertIn("window.addEventListener('beforeprint'", self.js)
        self.assertIn("window.addEventListener('afterprint'", self.js)

    def test_clipboard_failure_uses_mailto(self):
        self.assertIn("navigator.clipboard.writeText", self.js)
        self.assertIn("window.location.href = link.getAttribute('href')", self.js)
```

- [ ] **Step 2: Run the script tests and verify failure**

Run:

```bash
python3 -m unittest tests.test_resume.ResumeScriptTests -v
```

Expected: failures because the script still contains legacy presentation behavior and does not use the final data-attribute contracts.

- [ ] **Step 3: Replace `site/resume.js` with the final focused implementation**

Use:

```javascript
(function () {
  'use strict';

  var root = document.documentElement;
  var themeOrder = ['auto', 'light', 'dark'];
  var reduceMotion = window.matchMedia
    && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  function setTheme(mode, persist) {
    root.setAttribute('data-color-mode', mode);
    var label = document.querySelector('[data-theme-label]');
    if (label) label.textContent = mode;
    var control = document.querySelector('[data-theme-control]');
    if (control) {
      control.setAttribute(
        'aria-label',
        'Theme: ' + (mode === 'auto' ? 'system' : mode) + ' — activate to change'
      );
    }
    if (!persist) return;
    try {
      if (mode === 'auto') localStorage.removeItem('theme');
      else localStorage.setItem('theme', mode);
    } catch (error) {
      root.setAttribute('data-theme-storage', 'unavailable');
    }
  }

  function initThemeControl() {
    var control = document.querySelector('[data-theme-control]');
    if (!control) return;
    setTheme(root.getAttribute('data-color-mode') || 'auto', false);
    control.addEventListener('click', function () {
      var current = root.getAttribute('data-color-mode') || 'auto';
      setTheme(themeOrder[(themeOrder.indexOf(current) + 1) % themeOrder.length], true);
    });
  }

  function setLanguage(language, persist) {
    root.setAttribute('data-language', language);
    root.lang = language === 'zh' ? 'zh' : 'en';
    [].slice.call(document.querySelectorAll('[data-language-panel]')).forEach(function (panel) {
      var panelLanguage = panel.getAttribute('data-language-panel');
      panel.hidden = panelLanguage !== language;
    });
    [].slice.call(document.querySelectorAll('[data-language-control] [data-lang]')).forEach(function (button) {
      button.setAttribute(
        'aria-pressed',
        button.getAttribute('data-lang') === language ? 'true' : 'false'
      );
    });
    if (!persist) return;
    try {
      localStorage.setItem('resume-language', language);
    } catch (error) {
      root.setAttribute('data-language-storage', 'unavailable');
    }
  }

  function initLanguageControl() {
    var initialLanguage = root.getAttribute('data-language') === 'zh' ? 'zh' : 'en';
    setLanguage(initialLanguage, false);
    [].slice.call(document.querySelectorAll('[data-language-control] [data-lang]')).forEach(function (button) {
      button.addEventListener('click', function () {
        setLanguage(button.getAttribute('data-lang') === 'zh' ? 'zh' : 'en', true);
      });
    });
  }

  function setDisclosure(button, panel, open, immediate) {
    button.setAttribute('aria-expanded', open ? 'true' : 'false');
    button.textContent = open
      ? button.getAttribute('data-close-label')
      : button.getAttribute('data-open-label');
    if (open) {
      panel.hidden = false;
      panel.setAttribute('data-transition-state', 'opening');
      if (immediate || reduceMotion) {
        panel.setAttribute('data-open', 'true');
        panel.removeAttribute('data-transition-state');
        return;
      }
      requestAnimationFrame(function () {
        panel.setAttribute('data-open', 'true');
        panel.removeAttribute('data-transition-state');
      });
      return;
    }

    panel.removeAttribute('data-open');
    panel.setAttribute('data-transition-state', 'closing');
    if (immediate || reduceMotion) {
      panel.hidden = true;
      panel.removeAttribute('data-transition-state');
      return;
    }

    function finishClose(event) {
      if (event.target !== panel) return;
      panel.removeEventListener('transitionend', finishClose);
      if (panel.getAttribute('data-transition-state') === 'closing') {
        panel.hidden = true;
        panel.removeAttribute('data-transition-state');
      }
    }
    panel.addEventListener('transitionend', finishClose);
  }

  function initExperienceDisclosures() {
    var disclosures = [].slice.call(document.querySelectorAll('[data-disclosure]'));
    if (!disclosures.length) return;
    root.classList.add('has-disclosures');
    disclosures.forEach(function (disclosure) {
      var button = disclosure.querySelector('[data-disclosure-control]');
      var panel = disclosure.querySelector('[data-disclosure-panel]');
      if (!button || !panel) return;
      setDisclosure(button, panel, false, true);
      button.addEventListener('click', function () {
        setDisclosure(
          button,
          panel,
          button.getAttribute('aria-expanded') !== 'true',
          false
        );
      });
    });
  }

  function initPrintControls() {
    var printButtons = [].slice.call(document.querySelectorAll('[data-print]'));
    var disclosures = [].slice.call(document.querySelectorAll('[data-disclosure]'));
    var previousStates = [];

    printButtons.forEach(function (button) {
      button.addEventListener('click', function () {
        window.print();
      });
    });

    window.addEventListener('beforeprint', function () {
      previousStates = disclosures.map(function (disclosure) {
        var button = disclosure.querySelector('[data-disclosure-control]');
        var panel = disclosure.querySelector('[data-disclosure-panel]');
        var open = button && button.getAttribute('aria-expanded') === 'true';
        if (button && panel) setDisclosure(button, panel, true, true);
        return { button: button, panel: panel, open: open };
      });
    });

    window.addEventListener('afterprint', function () {
      previousStates.forEach(function (state) {
        if (state.button && state.panel) {
          setDisclosure(state.button, state.panel, state.open, true);
        }
      });
    });
  }

  function initEmailCopy() {
    var links = [].slice.call(document.querySelectorAll('[data-email]'));
    var toast = document.querySelector('[data-toast]');
    var message = toast && toast.querySelector('[data-toast-message]');
    var timer;

    links.forEach(function (link) {
      link.addEventListener('click', function (event) {
        if (!navigator.clipboard || !navigator.clipboard.writeText) return;
        event.preventDefault();
        navigator.clipboard.writeText(link.getAttribute('data-email')).then(function () {
          if (!toast || !message) return;
          message.textContent = root.lang === 'zh' ? '邮箱已复制' : 'Email copied to clipboard';
          toast.classList.add('is-visible');
          clearTimeout(timer);
          timer = setTimeout(function () {
            toast.classList.remove('is-visible');
          }, 2200);
        }).catch(function () {
          window.location.href = link.getAttribute('href');
        });
      });
    });
  }

  function initFooterMetadata() {
    var year = document.getElementById('year');
    var updated = document.getElementById('updated');
    if (year) year.textContent = new Date().getFullYear();
    if (!updated) return;
    var date = new Date(document.lastModified);
    updated.textContent = Number.isNaN(date.getTime())
      ? String(new Date().getFullYear())
      : date.toLocaleDateString(root.lang === 'zh' ? 'zh-CN' : 'en-NZ', {
          year: 'numeric',
          month: 'short',
          day: 'numeric'
        });
  }

  initThemeControl();
  initLanguageControl();
  initExperienceDisclosures();
  initPrintControls();
  initEmailCopy();
  initFooterMetadata();
})();
```

- [ ] **Step 4: Remove the temporary Task 2 migration aliases**

In `site/resume/index.html`:

- Remove `id="appbar"` from `.resume-system-bar`.
- Remove `id="themeToggle"` from `[data-theme-control]`.
- Remove the `segmented` class from `[data-language-control]`.
- Remove `id="wrap"` and `data-lang="en"` from `.resume-document`.
- Remove `lang-en` and `lang-zh` from the language panels.
- Remove `rx-role` from every role.
- Remove `rx-role__toggle` from every disclosure control.

In `site/resume.css`, replace the four-selector language block with:

```css
html.resume-page[data-language="en"] [data-language-panel="zh"],
html.resume-page[data-language="zh"] [data-language-panel="en"] {
  display: none;
}
```

Delete the temporary collapse rule:

```css
.rx-role.is-collapsed .resume-role-details {
  display: none;
}
```

- [ ] **Step 5: Add disclosure and identity motion styles**

Add:

```css
.resume-init .resume-identity {
  animation: resume-enter 240ms var(--resume-ease) both;
}

@keyframes resume-enter {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

.has-disclosures .resume-role-details {
  display: grid;
  grid-template-rows: 0fr;
  opacity: 0;
  transition:
    grid-template-rows 260ms var(--resume-ease),
    opacity 220ms var(--resume-ease);
}

.has-disclosures .resume-role-details-inner {
  min-height: 0;
  overflow: hidden;
}

.has-disclosures .resume-role-details[data-open="true"] {
  grid-template-rows: 1fr;
  opacity: 1;
}

.has-disclosures .resume-role-details[hidden] {
  display: none !important;
}

.resume-disclosure-control:hover {
  transform: translateY(-1px);
}

.resume-disclosure-control:active {
  transform: translateY(1px);
}

.resume-toast.is-visible {
  opacity: 1;
  transform: translate(-50%, 0);
}
```

Replace the Task 2 selector `.resume-toast.is-shown, .resume-toast.is-visible` with the final `.resume-toast.is-visible` selector above.

- [ ] **Step 6: Run script, style, and full résumé tests**

Run:

```bash
python3 -m unittest tests.test_resume -v
node --check site/resume.js
```

Expected: all résumé tests pass and JavaScript syntax is valid.

- [ ] **Step 7: Commit the progressive behavior**

```bash
git add site/resume/index.html site/resume.js site/resume.css tests/test_resume.py
git commit -m "feat: add resume locale and disclosure behavior" \
  -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>" \
  -m "Copilot-Session: 9e6d184d-77ff-4972-86bb-31358c4d2be8"
```

---

### Task 4: Finish Responsive Print, Remove Legacy Coupling, and Verify

**Files:**
- Modify: `tests/test_resume.py`
- Modify: `site/resume.css`
- Modify: `site/home.css:58-279,974-1005`
- Modify: `tests/test_homepage.py:12,71-77,102-104,188-227,304-316,378-531`

**Interfaces:**
- Consumes: final résumé HTML/CSS/JS from Tasks 2 and 3.
- Produces: self-contained screen, mobile, reduced-motion, and print behavior; homepage-only `home.css`; complete regression evidence.

- [ ] **Step 1: Add failing responsive, print, and isolation tests**

Append to `tests/test_resume.py`:

```python
class ResumeResponsiveAndPrintTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = RESUME_CSS.read_text(encoding="utf-8")

    def css_between(self, start, end=None):
        self.assertIn(start, self.css)
        body = self.css.split(start, 1)[1]
        if end is not None:
            self.assertIn(end, body)
            body = body.split(end, 1)[0]
        return body

    def test_mobile_layout_becomes_single_column(self):
        mobile = self.css_between(
            "@media (max-width: 760px)",
            "@media (pointer: coarse)",
        )
        self.assertIn(".resume-identity", mobile)
        self.assertIn(".resume-indexed-section", mobile)
        self.assertIn("grid-template-columns: 1fr", mobile)
        self.assertIn(".resume-capabilities", mobile)

    def test_coarse_pointer_controls_reach_44_pixels(self):
        coarse = self.css_between(
            "@media (pointer: coarse)",
            "@media (prefers-reduced-motion: reduce)",
        )
        self.assertIn("min-height: 44px", coarse)
        self.assertIn("min-width: 44px", coarse)

    def test_reduced_motion_disables_entry_and_transitions(self):
        reduced = self.css_between(
            "@media (prefers-reduced-motion: reduce)",
            "@media print",
        )
        self.assertIn("animation: none", reduced)
        self.assertIn("transition: none", reduced)

    def test_print_is_ink_safe_and_expands_details(self):
        body = self.css_between("@media print")
        self.assertIn("background: #fff", body)
        self.assertIn("color: #000", body)
        self.assertIn("[data-disclosure-panel]", body)
        self.assertIn("display: block !important", body)
        self.assertIn("[data-language-panel][hidden]", body)
        self.assertIn("display: none !important", body)
        self.assertIn(".resume-system-bar", body)
        self.assertIn("display: none !important", body)

    def test_print_keeps_role_entries_together(self):
        body = self.css_between("@media print")
        self.assertRegex(body, r"\.resume-role\s*\{[^}]*break-inside:\s*avoid")
```

Add this homepage isolation test to `HomepageStyleTests` in `tests/test_homepage.py`:

```python
def test_home_css_has_no_non_home_compatibility_layer(self):
    self.assertNotIn("html:not(.home-page)", self.css)
```

- [ ] **Step 2: Run the new tests and verify failure**

Run:

```bash
python3 -m unittest \
  tests.test_resume.ResumeResponsiveAndPrintTests \
  tests.test_homepage.HomepageStyleTests.test_home_css_has_no_non_home_compatibility_layer -v
```

Expected: failures because final responsive/print rules are incomplete and `home.css` still contains résumé compatibility selectors.

- [ ] **Step 3: Add responsive and coarse-pointer rules**

Add:

```css
@media (max-width: 760px) {
  html.resume-page body {
    background-size: 30px 30px;
  }

  .resume-system-bar {
    position: static;
    align-items: flex-start;
    flex-direction: column;
  }

  .resume-controls {
    width: 100%;
    justify-content: space-between;
    flex-wrap: wrap;
  }

  .resume-identity,
  .resume-indexed-section {
    grid-template-columns: 1fr;
  }

  .resume-indexed-section {
    gap: 1rem;
    padding-block: 3.5rem;
  }

  .resume-section-index {
    display: flex;
    gap: 0.75rem;
    align-items: baseline;
  }

  .resume-section-index span {
    display: inline;
  }

  .resume-role-header {
    grid-template-columns: 1fr;
  }

  .resume-capabilities {
    grid-template-columns: 1fr;
  }

  .resume-education-item {
    grid-template-columns: 4rem 1fr;
  }
}

@media (pointer: coarse) {
  .resume-controls button,
  .resume-language-control button,
  .resume-disclosure-control {
    min-width: 44px;
    min-height: 44px;
  }
}

@media (prefers-reduced-motion: reduce) {
  html.resume-page {
    scroll-behavior: auto;
  }

  .resume-init .resume-identity {
    animation: none;
  }

  .has-disclosures .resume-role-details,
  .resume-disclosure-control,
  .resume-toast {
    transition: none;
  }
}
```

- [ ] **Step 4: Add the ink-safe print translation**

Add:

```css
@media print {
  @page {
    margin: 13mm 13mm 16mm;
  }

  html.resume-page,
  html.resume-page body {
    color: #000 !important;
    background: #fff !important;
  }

  .resume-system-bar,
  .resume-skip-link,
  .resume-disclosure-control,
  .resume-toast,
  .resume-footer-screen-only {
    display: none !important;
  }

  .resume-main {
    width: 100%;
    padding: 0;
  }

  [data-language-panel][hidden] {
    display: none !important;
  }

  [data-disclosure-panel] {
    display: block !important;
  }

  .resume-role-details-inner {
    overflow: visible !important;
  }

  .resume-identity {
    animation: none !important;
    grid-template-columns: 1fr 15rem;
    gap: 10mm;
    padding-bottom: 7mm;
    border-bottom: 1.5pt solid #24311f;
  }

  .resume-identity h1 {
    font-size: 34pt;
    color: #000;
  }

  .resume-indexed-section {
    grid-template-columns: 24mm 1fr;
    gap: 7mm;
    padding-block: 7mm;
    border-bottom: 0.5pt solid #aaa;
  }

  .resume-section-index span,
  .resume-context span {
    color: #24311f !important;
  }

  .resume-role {
    break-inside: avoid;
    border-left-color: #aaa;
  }

  .resume-role--current {
    border-left-color: #24311f;
  }

  .resume-achievements li::before {
    color: #24311f;
  }

  .resume-capabilities > div,
  .resume-education-item {
    break-inside: avoid;
    border-color: #aaa;
  }

  a {
    color: #000 !important;
    text-decoration: none !important;
  }
}
```

Check print preview with backgrounds disabled. The hierarchy and current-role rule must remain visible.

- [ ] **Step 5: Remove obsolete résumé compatibility from `home.css`**

Delete:

- The complete `html:not(.home-page)` token and body blocks at the top.
- Theme-toggle compatibility rules.
- Legacy résumé reveal rules.
- Footer, toast, nav separator, eyebrow, and tech-chip compatibility rules.
- The `html:not(.home-page).js .reveal` reduced-motion rule.

After deletion, every selector in `site/home.css` must either start with `html.home-page`, be a homepage class used by `site/index.html`, or be an `@keyframes`/media wrapper around homepage rules.

- [ ] **Step 6: Remove obsolete résumé compatibility tests**

In `tests/test_homepage.py`:

- Remove `RESUME_INDEX`.
- Remove `test_resume_still_requests_unbumped_home_css_version`.
- Remove `test_resume_document_is_not_marked_as_home_page`.
- Remove `test_restores_legacy_type_stack_for_non_home_pages`.
- Update comments in `test_reduced_motion_universal_selectors_are_scoped_to_home_page` and `test_core_content_is_not_hidden_without_enhancement_class` so they no longer describe the old résumé dependency.
- Delete the entire `ResumeCompatibilityTests` class.
- Keep the new `test_home_css_has_no_non_home_compatibility_layer`.

- [ ] **Step 7: Run the complete static verification**

Run:

```bash
python3 -m unittest tests.test_homepage tests.test_resume -v
node --check site/home.js
node --check site/resume.js
git diff --check
```

Expected:

- All homepage and résumé tests pass.
- Both JavaScript syntax checks exit with status 0.
- `git diff --check` reports no whitespace errors.

- [ ] **Step 8: Verify routes and assets through a local nginx-equivalent static server**

Start a temporary server:

```bash
python3 -m http.server 4173 --directory site
```

Verify:

```bash
curl -fsS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:4173/
curl -fsS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:4173/resume/
curl -fsS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:4173/resume.css?v=3
curl -fsS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:4173/resume.js?v=1
curl -fsS -o /dev/null -w '%{http_code}\n' http://127.0.0.1:4173/og-home.png?v=1
```

Expected: five `200` responses.

Stop the server by its exact process ID after browser validation.

- [ ] **Step 9: Perform browser and print validation**

Use Playwright against `http://127.0.0.1:4173/resume/`:

1. Desktop viewport `1440 × 900`: verify the indexed two-column dossier, five visible Microsoft bullets, earlier summaries, and no horizontal overflow.
2. Mobile viewport `390 × 844`: verify one-column sections, wrapping system controls, 44-pixel controls, and no horizontal overflow.
3. Set browser locale to `zh-CN` with cleared storage: verify Chinese is selected automatically and `<html lang="zh">`.
4. Select English manually, reload, and verify `localStorage["resume-language"]` keeps English.
5. Cycle `auto → light → dark → auto` and verify `localStorage["theme"]`.
6. Expand and collapse each earlier role in both languages; verify `aria-expanded`, button label, panel visibility, and keyboard activation.
7. Disable JavaScript and reload: verify English content and every role detail remain visible.
8. Emulate `prefers-reduced-motion: reduce`: verify no identity animation or disclosure transition.
9. Open print preview in English and Chinese: verify only the active language prints, every role is expanded, controls are hidden, and the paper treatment remains legible without background graphics.
10. Verify the browser console has no errors or warnings and the network log has no missing assets.
11. Re-open the homepage and verify its dark/light themes, entry sequence, navigation, email copy, and responsive layout remain unchanged.

- [ ] **Step 10: Commit the final responsive and isolation work**

```bash
git add \
  site/resume/index.html \
  site/resume.css \
  site/resume.js \
  site/home.css \
  tests/test_resume.py \
  tests/test_homepage.py
git commit -m "fix: finish resume print and style isolation" \
  -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>" \
  -m "Copilot-Session: 9e6d184d-77ff-4972-86bb-31358c4d2be8"
```

The implementation branch is ready for review after this commit. Do not push or rebuild the production container until the user explicitly requests deployment.
