from pathlib import Path
import re
import struct
import unittest


ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "site" / "index.html"
HOME_CSS = ROOT / "site" / "home.css"
HOME_JS = ROOT / "site" / "home.js"
OG_PNG = ROOT / "site" / "og-home.png"
RESUME_INDEX = ROOT / "site" / "resume" / "index.html"
RESUME_JS = ROOT / "site" / "resume.js"


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
        self.assertIn('href="/home.css?v=6"', self.html)
        self.assertNotIn("/vendor/primer/", self.html)
        self.assertNotIn('href="/style.css', self.html)

    def test_homepage_requests_fresh_script_version(self):
        self.assertIn('src="/home.js?v=2"', self.html)

    def test_resume_still_requests_unbumped_home_css_version(self):
        # site/resume/index.html is protected and must not be modified by
        # this fix: it keeps requesting the pre-redesign cache-busting
        # query string. The scoping/compat work in home.css makes that
        # safe by content even though the version tag itself is stale.
        resume_html = RESUME_INDEX.read_text(encoding="utf-8")
        self.assertIn('href="/home.css?v=1"', resume_html)

    def test_command_link_prompts_are_decorative(self):
        command_blocks = re.findall(
            r'<div class="command-links[^"]*"[^>]*>(.*?)</div>',
            self.html,
            flags=re.DOTALL,
        )
        self.assertTrue(command_blocks, "expected at least one command-links block")
        for block in command_blocks:
            anchors = re.findall(r"<a\b[^>]*>(.*?)</a>", block, flags=re.DOTALL)
            self.assertTrue(anchors, "expected command-link anchors in the block")
            for inner in anchors:
                with self.subTest(inner=inner):
                    # The decorative "> " prompt glyph must be wrapped so it
                    # never becomes part of the link's accessible name.
                    self.assertIn('<span aria-hidden="true">&gt;</span>', inner)
                    visible_text = re.sub(
                        r'<span aria-hidden="true">.*?</span>', "", inner, flags=re.DOTALL
                    )
                    self.assertNotIn("&gt;", visible_text)

    def test_html_element_carries_homepage_marker_class(self):
        self.assertRegex(self.html, r'<html\b[^>]*\bclass="home-page"')

    def test_resume_document_is_not_marked_as_home_page(self):
        resume_html = RESUME_INDEX.read_text(encoding="utf-8")
        self.assertNotRegex(resume_html, r'<html\b[^>]*\bclass="home-page"')

    def test_header_nav_includes_linkedin(self):
        nav_match = re.search(
            r'<nav class="system-nav"[^>]*>(.*?)</nav>', self.html, flags=re.DOTALL
        )
        self.assertIsNotNone(nav_match, "expected a .system-nav element")
        nav_html = nav_match.group(1)
        self.assertIn('href="https://www.linkedin.com/in/shunlyu"', nav_html)
        linkedin_match = re.search(
            r'<a href="https://www\.linkedin\.com/in/shunlyu"([^>]*)>LinkedIn</a>',
            nav_html,
        )
        self.assertIsNotNone(
            linkedin_match, "expected a plain-text LinkedIn link in the header nav"
        )
        attrs = linkedin_match.group(1)
        self.assertIn('target="_blank"', attrs)
        self.assertIn('rel="noopener"', attrs)

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

    def test_scopes_global_reset_rules_to_home_page_marker(self):
        required_selectors = (
            "html.home-page {",
            'html.home-page[data-color-mode="light"]',
            'html.home-page[data-color-mode="dark"]',
            "html.home-page body {",
            "html.home-page body::after {",
            "html.home-page *,",
            "html.home-page a {",
            "html.home-page button {",
            "html.home-page :focus-visible {",
            "html.home-page ::selection {",
            "html.home-page main {",
        )
        for selector in required_selectors:
            with self.subTest(selector=selector):
                self.assertIn(selector, self.css)

    def test_reduced_motion_universal_selectors_are_scoped_to_home_page(self):
        reduced_motion_block = re.search(
            r"@media \(prefers-reduced-motion: reduce\)\s*\{(.*?)\n\}",
            self.css,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(
            reduced_motion_block, "expected an @media (prefers-reduced-motion: reduce) block"
        )
        body = reduced_motion_block.group(1)
        self.assertIn("html.home-page {", body)
        self.assertIn("html.home-page *,", body)
        self.assertIn("html.home-page body {", body)
        # These bare, unscoped selectors would leak onto /resume/, which also
        # requests home.css without the homepage marker class.
        self.assertNotRegex(body, r"(?<!\.home-page)\n\s*html\s*\{")
        self.assertNotRegex(body, r"(?<!\.home-page)\n\s*body\s*\{")
        self.assertNotRegex(body, r"\n\s*\*,\n\s*\*::before,\n\s*\*::after\s*\{")

    def test_restores_legacy_type_stack_for_non_home_pages(self):
        token_block = re.search(
            r"html:not\(\.home-page\)\s*\{([^}]*)\}", self.css, flags=re.DOTALL
        )
        self.assertIsNotNone(
            token_block, "expected an html:not(.home-page) compatibility block"
        )
        declarations = token_block.group(1)
        self.assertIn('--font-sans: "Inter"', declarations)
        self.assertIn('--font-mono: "JetBrains Mono"', declarations)

        body_block = re.search(
            r"html:not\(\.home-page\)\s+body\s*\{([^}]*)\}", self.css, flags=re.DOTALL
        )
        self.assertIsNotNone(
            body_block,
            "expected an html:not(.home-page) body compatibility block",
        )
        body_declarations = body_block.group(1)
        self.assertIn('font-feature-settings: "cv11", "ss01"', body_declarations)
        self.assertIn("letter-spacing: -0.005em", body_declarations)

    def test_tablet_breakpoint_collapses_two_column_layout(self):
        tablet_block = re.search(
            r"@media \(max-width: 1024px\)\s*\{(.*?)\n\}", self.css, flags=re.DOTALL
        )
        self.assertIsNotNone(
            tablet_block, "expected an @media (max-width: 1024px) block"
        )
        body = tablet_block.group(1)
        self.assertIn(".intro-shell", body)
        self.assertIn(".console-section", body)
        self.assertIn("grid-template-columns: 1fr", body)
        self.assertIn(".instrument-rail", body)
        self.assertIn("position: static", body)

        mobile_block = re.search(
            r"@media \(max-width: 760px\)\s*\{(.*?)\n\}", self.css, flags=re.DOTALL
        )
        self.assertIsNotNone(mobile_block)
        mobile_body = mobile_block.group(1)
        self.assertIn(".system-nav a:first-child", mobile_body)
        self.assertIn(".fact-list div", mobile_body)
        self.assertIn(".system-footer {", mobile_body)

    def test_intro_title_reveals_with_horizontal_mask(self):
        rule = re.search(
            r"\.js \.intro-title\.boot-item\s*\{([^}]*)\}", self.css, flags=re.DOTALL
        )
        self.assertIsNotNone(
            rule, "expected a dedicated .js .intro-title.boot-item rule"
        )
        name_match = re.search(r"animation(?:-name)?:\s*([\w-]+)", rule.group(1))
        self.assertIsNotNone(name_match, "expected an animation name override")
        keyframe_name = name_match.group(1)
        self.assertNotEqual(
            keyframe_name,
            "boot-in",
            "the name heading must not reuse the shared vertical boot-in mask",
        )

        keyframes = re.search(
            r"@keyframes\s+" + re.escape(keyframe_name) + r"\s*\{(.*?)\n\}",
            self.css,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(keyframes, f"expected @keyframes {keyframe_name}")
        from_block = re.search(r"from\s*\{([^}]*)\}", keyframes.group(1), flags=re.DOTALL)
        self.assertIsNotNone(from_block)
        clip_match = re.search(
            r"clip-path:\s*inset\(([^)]*)\)", from_block.group(1)
        )
        self.assertIsNotNone(clip_match, "expected a clip-path inset() mask")
        top, right, bottom, left = clip_match.group(1).split()
        self.assertEqual(top, "0", "a horizontal mask must not clip the top edge")
        self.assertEqual(bottom, "0", "a horizontal mask must not clip the bottom edge")
        self.assertTrue(
            right != "0" or left != "0",
            "a horizontal mask must clip from the left or right edge",
        )

    def test_system_bar_uses_webkit_backdrop_filter_with_solid_fallback(self):
        supports_block = re.search(
            r"@supports[^{]*backdrop-filter[^{]*\{(.*?)\n\}", self.css, flags=re.DOTALL
        )
        self.assertIsNotNone(
            supports_block, "expected an @supports backdrop-filter feature block"
        )
        body = supports_block.group(1)
        self.assertIn(".system-bar", body)
        self.assertIn("-webkit-backdrop-filter: blur(14px)", body)
        self.assertIn("backdrop-filter: blur(14px)", body)

        base_rule = re.search(r"\n\.system-bar\s*\{([^}]*)\}", self.css, flags=re.DOTALL)
        self.assertIsNotNone(base_rule, "expected a base .system-bar rule")
        self.assertNotIn("backdrop-filter", base_rule.group(1))

    def test_core_content_is_not_hidden_without_enhancement_class(self):
        # Homepage content must never be hidden except behind the
        # `.has-reveal` enhancement class (set by home.js). The only other
        # legitimate hiding gate is the resume-only `html:not(.home-page)
        # .js .reveal` compat rule, driven by resume's own inline no-FOUC
        # script — it can never match the homepage document.
        hidden_reveal_rule = re.search(
            r"(?<!has-reveal )(?<!\.js )\.reveal\s*\{[^}]*opacity\s*:\s*0",
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


class ResumeCompatibilityTests(unittest.TestCase):
    """/resume/ still loads home.css unscoped (as `/home.css?v=1`, without
    the `.home-page` marker class) and its markup + extracted script depend on
    several pre-redesign rules that used to live here unscoped. These tests
    read the actual resume markup and the current home.css to lock in every
    shared contract resume still consumes, restored under `html:not(.home-page)`.
    """

    @classmethod
    def setUpClass(cls):
        cls.css = HOME_CSS.read_text(encoding="utf-8")
        cls.resume_html = RESUME_INDEX.read_text(encoding="utf-8")
        cls.resume_js = RESUME_JS.read_text(encoding="utf-8") if RESUME_JS.exists() else ""

    def test_resume_markup_uses_theme_toggle_icon_per_mode_contract(self):
        # Document the markup contract the CSS below must satisfy: three
        # mode icons inside one .theme-toggle button.
        self.assertRegex(self.resume_html, r'class="theme-toggle"[^>]*>')
        for mode in ("auto", "light", "dark"):
            self.assertIn(f'data-mode="{mode}"', self.resume_html)

    def test_theme_toggle_shows_exactly_one_icon_per_color_mode(self):
        css = self.css
        self.assertRegex(
            css, r'html:not\(\.home-page\)\s+\.theme-toggle\s+\[data-mode\]\s*\{\s*display:\s*none'
        )
        self.assertRegex(
            css,
            r'html:not\(\.home-page\)\s+\.theme-toggle\s+\[data-mode="auto"\]\s*\{\s*display:\s*block',
        )
        self.assertRegex(
            css,
            r'html:not\(\.home-page\)\[data-color-mode="light"\]\s+\.theme-toggle\s+\[data-mode="auto"\]\s*\{\s*display:\s*none',
        )
        self.assertRegex(
            css,
            r'html:not\(\.home-page\)\[data-color-mode="light"\]\s+\.theme-toggle\s+\[data-mode="light"\]\s*\{\s*display:\s*block',
        )
        self.assertRegex(
            css,
            r'html:not\(\.home-page\)\[data-color-mode="dark"\]\s+\.theme-toggle\s+\[data-mode="auto"\]\s*\{\s*display:\s*none',
        )
        self.assertRegex(
            css,
            r'html:not\(\.home-page\)\[data-color-mode="dark"\]\s+\.theme-toggle\s+\[data-mode="dark"\]\s*\{\s*display:\s*block',
        )

    def test_toast_is_shown_has_visible_transform_and_opacity(self):
        base_rule = re.search(
            r"html:not\(\.home-page\)\s+\.toast\s*\{([^}]*)\}", self.css, flags=re.DOTALL
        )
        self.assertIsNotNone(base_rule, "expected a resume-compat .toast base rule")
        self.assertIn("opacity: 0", base_rule.group(1))

        shown_rule = re.search(
            r"html:not\(\.home-page\)\s+\.toast\.is-shown\s*\{([^}]*)\}",
            self.css,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(shown_rule, "expected a resume-compat .toast.is-shown rule")
        declarations = shown_rule.group(1)
        self.assertIn("opacity: 1", declarations)
        self.assertRegex(declarations, r"transform:\s*translate\(-50%,\s*0\)")

        # The resume markup and its extracted script actually use this contract.
        self.assertIn('id="toast"', self.resume_html)
        self.assertIn("toast.classList.add('is-shown')", self.resume_js)

    def test_resume_reveal_hidden_visible_and_variant_contract(self):
        css = self.css
        # `.js` is set directly on <html> by resume's inline no-FOUC script,
        # so the compat selector must be a compound (`html:not(.home-page).js`)
        # rather than a descendant chain — `.js` can never be a *descendant*
        # of `html:not(.home-page)` when it's applied to that same element.
        hidden_rule = re.search(
            r"html:not\(\.home-page\)\.js\s+\.reveal\s*\{([^}]*)\}", css, flags=re.DOTALL
        )
        self.assertIsNotNone(hidden_rule, "expected a resume-compat .js .reveal rule")
        self.assertIn("opacity: 0", hidden_rule.group(1))

        visible_rule = re.search(
            r"html:not\(\.home-page\)\s+\.reveal\.is-visible\s*\{([^}]*)\}",
            css,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(visible_rule, "expected a resume-compat .reveal.is-visible rule")
        self.assertIn("opacity: 1", visible_rule.group(1))

        for variant in ("reveal--left", "reveal--right", "reveal--scale"):
            with self.subTest(variant=variant):
                self.assertRegex(
                    css,
                    r"html:not\(\.home-page\)\.js\s+\." + variant + r"\s*\{",
                )

        # The resume markup and its extracted script actually use this contract.
        self.assertIn('class="rx-summary reveal"', self.resume_html)
        self.assertIn("var reveals = [].slice.call(document.querySelectorAll('.reveal'));", self.resume_js)

    def test_shared_selector_audit_contracts_restored(self):
        # Full intersection audit beyond the three named review findings:
        # footer byline extras, the nav separator, the résumé eyebrow rule,
        # and the tech-stack chip bullet dot all used to live in the
        # unscoped home.css and are genuinely still consumed by /resume/.
        css = self.css
        for selector in (
            "footer__brand",
            "footer__tag",
            "footer__meta",
            "footer__updated",
            "nav__sep",
            "hx-eyebrow",
            "tech-chip",
        ):
            with self.subTest(selector=selector):
                self.assertIn(selector, self.resume_html)
                self.assertRegex(
                    css,
                    r"html:not\(\.home-page\)[^{]*\." + re.escape(selector) + r"\b",
                    f"expected a compat rule restoring .{selector}",
                )

        self.assertRegex(
            css,
            r'html:not\(\.home-page\)\s+\.tech-chip\s+\.dot\s*\{[^}]*width:\s*7px',
        )

    def test_brand_gradient_custom_property_restored_for_resume(self):
        # resume.css reads var(--brand-gradient) directly in six of its own
        # rules (avatar mark, section-title accent bar, gradient stat
        # numbers, timeline dots) — a custom-property dependency, not a
        # class selector, so it doesn't show up in a selector-only audit.
        # Without it, --brand-gradient resolves to nothing and every one of
        # those rules renders blank (invisible avatar, invisible stat
        # numbers via background-clip: text + color: transparent, etc).
        resume_css = (ROOT / "site" / "resume.css").read_text(encoding="utf-8")
        usages = resume_css.count("var(--brand-gradient)")
        self.assertGreaterEqual(usages, 6, "expected resume.css to still reference --brand-gradient")

        token_block = re.search(
            r"html:not\(\.home-page\)\s*\{([^}]*)\}", self.css, flags=re.DOTALL
        )
        self.assertIsNotNone(token_block)
        self.assertRegex(token_block.group(1), r"--brand-gradient:\s*linear-gradient\(")

    def test_homepage_toast_and_reveal_rules_stay_scoped_to_home_page(self):
        css = self.css
        # The new systems-console toast/reveal rules must not leak onto
        # /resume/ as bare, unscoped selectors.
        self.assertNotRegex(css, r"(?<!home-page )(?<!\.js )\n\.toast\s*\{")
        self.assertNotRegex(css, r"(?<!home-page )\n\.toast\.is-visible\s*\{")
        self.assertNotRegex(css, r"(?<!home-page )\n\.has-reveal \.reveal\s*\{")
        self.assertRegex(css, r"html\.home-page \.toast\s*\{")
        self.assertRegex(css, r"html\.home-page \.toast\.is-visible\s*\{")
        self.assertRegex(css, r"html\.home-page \.has-reveal \.reveal\s*\{")


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
        self.assertRegex(html, r'<script src="/home\.js\?v=2" defer></script>')

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


class HomepageAssetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX.read_text(encoding="utf-8")

    def test_references_social_preview(self):
        self.assertIn(
            '<meta property="og:image" content="https://shunlyu.com/og-home.png?v=1">',
            self.html,
        )
        self.assertIn('<meta name="twitter:card" content="summary_large_image">', self.html)
        self.assertIn(
            '<meta name="twitter:image" content="https://shunlyu.com/og-home.png?v=1">',
            self.html,
        )

    def test_social_preview_is_1200_by_630_png(self):
        self.assertTrue(OG_PNG.exists())
        data = OG_PNG.read_bytes()
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
        width, height = struct.unpack(">II", data[16:24])
        self.assertEqual((width, height), (1200, 630))


if __name__ == "__main__":
    unittest.main()
