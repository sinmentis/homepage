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


if __name__ == "__main__":
    unittest.main()
