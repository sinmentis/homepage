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
            'class="instrument-rail',
            'class="command-links',
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

    def test_entry_lifecycle_states_drive_grid_and_scanline_power_on(self):
        def animation_from(selector):
            rule = re.search(
                re.escape(selector) + r"\s*\{([^}]*)\}",
                self.css,
                flags=re.DOTALL,
            )
            self.assertIsNotNone(rule, f"expected rule for {selector}")
            match = re.search(
                r"animation:\s*([\w-]+)\s+([\d.]+)(m?s)",
                rule.group(1),
            )
            self.assertIsNotNone(
                match, f"expected animation shorthand on {selector}"
            )
            name, value, unit = match.groups()
            duration_ms = float(value) * (1 if unit == "ms" else 1000)
            return name, duration_ms

        grid_keyframe, grid_duration_ms = animation_from(
            ".entry-running .console-grid"
        )
        self.assertLessEqual(grid_duration_ms, 1400)
        self.assertRegex(self.css, rf"@keyframes\s+{re.escape(grid_keyframe)}\s*\{{")

        scanline_keyframe, scanline_duration_ms = animation_from(
            ".entry-running body::after"
        )
        self.assertLessEqual(scanline_duration_ms, 1400)
        self.assertRegex(
            self.css, rf"@keyframes\s+{re.escape(scanline_keyframe)}\s*\{{"
        )

        complete_grid = re.search(
            r"\.entry-complete\s+\.console-grid\s*\{([^}]*)\}",
            self.css,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(complete_grid, "expected .entry-complete .console-grid rule")
        self.assertIn("opacity: 1", complete_grid.group(1))

        complete_scanline = re.search(
            r"\.entry-complete\s+body::after\s*\{([^}]*)\}",
            self.css,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(
            complete_scanline, "expected .entry-complete body::after rule"
        )
        self.assertIn("opacity: 0.035", complete_scanline.group(1))

        self.assertNotRegex(
            self.css,
            r"\.entry-(running|complete)[^{]*\{[^}]*pointer-events:\s*auto",
        )


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


if __name__ == "__main__":
    unittest.main()
