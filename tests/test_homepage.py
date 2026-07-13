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


if __name__ == "__main__":
    unittest.main()
