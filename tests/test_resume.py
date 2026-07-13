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
