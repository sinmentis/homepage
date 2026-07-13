from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
RESUME_INDEX = ROOT / "site" / "resume" / "index.html"
RESUME_CSS = ROOT / "site" / "resume.css"
RESUME_JS = ROOT / "site" / "resume.js"


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

    def test_print_control_guards_missing_print_api(self):
        """initPrintControls must not assume window.print exists.

        The control stays a plain button with no false success state when the
        Print API is unavailable, so the click handler must check
        `typeof window.print === 'function'` before calling it (no broad
        try/catch swallowing the missing-API case).
        """
        init_print_controls = re.search(
            r"function initPrintControls\(\)\s*\{(.*?)\n  \}",
            self.js,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(init_print_controls)
        body = init_print_controls.group(1)
        self.assertIn("typeof window.print === 'function'", body)
        self.assertNotIn("try {", body)


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

    def test_footer_home_link_is_screen_only(self):
        """The footer's return-to-home link is screen navigation, not print content.

        `site/resume.css` hides `.resume-footer-screen-only` under
        `@media print`, so the anchor must carry that class or it prints
        alongside the résumé content.
        """
        footer = re.search(r"<footer[^>]*>(.*?)</footer>", self.html, flags=re.DOTALL)
        self.assertIsNotNone(footer)
        home_link = re.search(
            r'<a\s+([^>]*)href="/"[^>]*>return / home</a>', footer.group(1)
        )
        self.assertIsNotNone(home_link)
        self.assertIn("resume-footer-screen-only", home_link.group(1))

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

    def test_language_panel_visibility_is_root_scoped(self):
        """Task 3 final mechanism: root data-language gates data-language-panel.

        Superseded the Task 2->3 migration-state regression test now that
        resume.js keeps `html[data-language]` in sync on every toggle click
        and the temporary `#wrap[data-lang]` selectors have been removed.
        """
        self.assertIn(
            'html.resume-page[data-language="en"] [data-language-panel="zh"]',
            self.css,
        )
        self.assertIn(
            'html.resume-page[data-language="zh"] [data-language-panel="en"]',
            self.css,
        )
        self.assertNotIn("#wrap[data-lang", self.css)

    def test_identity_reveal_animation_is_disabled_under_reduced_motion(self):
        """Reveal transitions must become immediate for prefers-reduced-motion.

        `.resume-init .resume-identity` runs a 240ms keyframe animation on
        load; a reduced-motion override must neutralize it so the identity
        block does not animate for users who ask for less motion.

        The extraction must stop at the following `@media print` block:
        anchoring the greedy capture to end-of-file (as a prior version of
        this test did) also swallows the print block, since both blocks end
        in `}` and the file's last `}` closes `@media print`, not the
        reduced-motion block.
        """
        reduced_motion_block = re.search(
            r"@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{(.*?)\n\}\s*\n\s*@media print",
            self.css,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(reduced_motion_block)
        block = reduced_motion_block.group(1)
        self.assertIn(".resume-init .resume-identity", block)
        self.assertIn("animation", block)
        self.assertNotIn("@media print", block)


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

    def test_print_resets_dark_screen_color_tokens(self):
        """The dark and auto+dark screen variants set --resume-signal and
        --resume-muted to light-on-dark values via `html.resume-page
        [data-color-mode="dark"]` and `@media (prefers-color-scheme: dark)`.
        Those selectors have higher specificity/later source order than a
        bare `html.resume-page` rule, so the print block must reset the
        tokens on a selector that also matches `[data-color-mode]` (any
        value) to win the cascade in light, dark, and auto modes alike.
        """
        body = self.css_between("@media print")
        self.assertRegex(
            body,
            r"html\.resume-page\[data-color-mode\]\s*\{[^}]*--resume-signal:\s*#24311f",
        )
        self.assertRegex(
            body,
            r"html\.resume-page\[data-color-mode\]\s*\{[^}]*--resume-muted:\s*#3f4a3a",
        )
        self.assertRegex(
            body,
            r"html\.resume-page\[data-color-mode\]\s*\{[^}]*--resume-hairline:\s*#999",
        )


if __name__ == "__main__":
    unittest.main()
