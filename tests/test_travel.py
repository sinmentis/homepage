from pathlib import Path
import re
import struct
import unittest


ROOT = Path(__file__).resolve().parents[1]
TRAVEL_DIR = ROOT / "site" / "travel"
INDEX = TRAVEL_DIR / "index.html"
CSS = TRAVEL_DIR / "travel.css"
JS = TRAVEL_DIR / "travel.js"
HOME_INDEX = ROOT / "site" / "index.html"
ASSETS = TRAVEL_DIR / "assets"


class TravelPageContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = INDEX.read_text(encoding="utf-8") if INDEX.exists() else ""

    def test_travel_page_files_exist(self):
        self.assertTrue(INDEX.exists())
        self.assertTrue(CSS.exists())
        self.assertTrue(JS.exists())

    def test_page_is_unlisted_and_noindex(self):
        self.assertIn('<meta name="robots" content="noindex, nofollow">', self.html)
        home_html = HOME_INDEX.read_text(encoding="utf-8")
        self.assertNotIn('href="/travel/', home_html)

    def test_page_carries_travel_marker_and_semantic_structure(self):
        self.assertRegex(self.html, r'<html\b[^>]*\bclass="travel-page"')
        for element in ("<header", "<main", "<section", "<article", "<footer"):
            with self.subTest(element=element):
                self.assertIn(element, self.html)
        self.assertIn('href="#main-content"', self.html)

    def test_all_three_route_options_are_present_and_pending(self):
        required = (
            'data-route-id="route-a"',
            'data-route-id="route-b"',
            'data-route-id="route-c"',
            "伊宁双翼基地型",
            "东西连续推进型",
            "唐布拉深住型",
            "路线待决定",
        )
        for fragment in required:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.html)

    def test_required_places_and_backup_are_present(self):
        for place in ("伊宁", "大西沟", "唐布拉", "库尔德宁"):
            with self.subTest(place=place):
                self.assertIn(place, self.html)

    def test_private_planning_details_are_absent(self):
        forbidden = (
            "青岛",
            "西安",
            "商务",
            "航班",
            "机票",
            "身份证",
            "30000",
            "30,000",
            "酒店预订",
            "订单号",
            "电话号码",
        )
        for fragment in forbidden:
            with self.subTest(fragment=fragment):
                self.assertNotIn(fragment, self.html)

    def test_page_uses_local_css_js_and_local_content_images(self):
        # travel.css stays at v=4 (unchanged by this fix). travel.js bumps
        # v=2 -> v=3: this fix's image-error race patch (see
        # TravelScriptTests.test_image_failure_state_also_catches_already_settled_eager_images)
        # changes travel.js content, so it needs its own cache-bust
        # (Cloudflare caches by full URL including querystring; see
        # final-print-fix-report.md's "?v=3 poisoning" note for travel.css —
        # that incident was for the CSS asset's own ?v=3, an unrelated
        # cache key from this JS asset's ?v=3, which has never been
        # requested).
        self.assertIn('href="/travel/travel.css?v=4"', self.html)
        self.assertIn('src="/travel/travel.js?v=3"', self.html)
        image_sources = re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', self.html)
        self.assertTrue(image_sources)
        for source in image_sources:
            with self.subTest(source=source):
                self.assertTrue(source.startswith("/travel/assets/"))

    def test_route_content_remains_in_html_without_javascript(self):
        for route_id in ("route-a", "route-b", "route-c"):
            article = re.search(
                rf'<article\b[^>]*data-route-id="{route_id}"[^>]*>(.*?)</article>',
                self.html,
                flags=re.DOTALL,
            )
            self.assertIsNotNone(article)
            self.assertIn("<ol", article.group(1))
            self.assertIn("真实代价", article.group(1))
            self.assertIn('class="distance-note"', article.group(1))
            for score in ("风景", "人流", "驾驶", "住宿", "天气"):
                with self.subTest(route_id=route_id, score=score):
                    self.assertIn(f"<dt>{score}</dt>", article.group(1))

    def test_external_sources_and_navigation_links_are_safe(self):
        self.assertIn('href="https://www.amap.com/"', self.html)
        self.assertIn('href="https://map.baidu.com/"', self.html)
        external_links = re.findall(
            r'<a\b[^>]*href="https://(?!shunlyu\.com)[^"]+"[^>]*>',
            self.html,
        )
        self.assertTrue(external_links)
        for link in external_links:
            with self.subTest(link=link):
                self.assertIn('target="_blank"', link)
                self.assertIn('rel="noopener noreferrer"', link)

    def test_route_map_ships_both_light_and_dark_variants(self):
        # Both palettes must ship in the markup so CSS alone (no JS
        # required) can select the theme-correct image for auto/light/dark.
        figure = re.search(
            r'<figure class="route-map">(.*?)</figure>', self.html, flags=re.DOTALL
        )
        self.assertIsNotNone(figure)
        block = figure.group(1)
        self.assertIn('src="/travel/assets/route-a.svg"', block)
        self.assertIn('src="/travel/assets/route-a-dark.svg"', block)
        self.assertIn('data-theme-variant="light"', block)
        self.assertIn('data-theme-variant="dark"', block)
        self.assertEqual(len(re.findall(r"<img\b", block)), 2)

    def test_daxigou_evidence_ships_both_light_and_dark_variants(self):
        figure = re.search(
            r"<figure>\s*<img[^>]*daxigou-evidence(.*?)</figure>",
            self.html,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(figure)
        block = figure.group(0)
        self.assertIn('src="/travel/assets/daxigou-evidence.svg"', block)
        self.assertIn('src="/travel/assets/daxigou-evidence-dark.svg"', block)
        self.assertIn('data-theme-variant="light"', block)
        self.assertIn('data-theme-variant="dark"', block)
        self.assertEqual(len(re.findall(r"<img\b", block)), 2)

    def test_evidence_grid_images_load_eagerly(self):
        # Evidence images (including both Daxigou theme variants) must not
        # be lazy-loaded: Chromium does not force-load off-screen lazy
        # images for print, so a user printing without first scrolling
        # would otherwise get blank evidence boxes.
        grid = re.search(
            r'<div class="evidence-grid">(.*?)</div>\s*<p class="source-note">',
            self.html,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(grid)
        block = grid.group(1)
        images = re.findall(r"<img\b[^>]*>", block)
        self.assertEqual(len(images), 5)
        for image in images:
            with self.subTest(image=image):
                self.assertNotIn('loading="lazy"', image)

    def test_decision_matrix_headers_have_scope_attributes(self):
        table = re.search(r"<table>(.*?)</table>", self.html, flags=re.DOTALL)
        self.assertIsNotNone(table)
        block = table.group(1)
        self.assertEqual(len(re.findall(r'<th scope="col">', block)), 5)
        self.assertEqual(len(re.findall(r'<th scope="row">', block)), 3)

class TravelAssetTests(unittest.TestCase):
    def test_route_maps_are_static_svg_files_with_distance_labels(self):
        expected = {
            "route-a.svg": ("79 km", "286 km"),
            "route-b.svg": ("79 km", "359 km", "286 km"),
            "route-c.svg": ("286 km", "79 km"),
        }
        for name, labels in expected.items():
            with self.subTest(name=name):
                svg = (ASSETS / name).read_text(encoding="utf-8")
                self.assertIn("<svg", svg)
                self.assertIn("OpenStreetMap contributors via OSRM", svg)
                for label in labels:
                    self.assertIn(label, svg)

    def test_social_preview_is_png_with_expected_dimensions(self):
        preview = ASSETS / "og-travel.png"
        self.assertTrue(preview.exists())
        data = preview.read_bytes()
        self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
        width, height = struct.unpack(">II", data[16:24])
        self.assertEqual((width, height), (1200, 630))

    def test_destination_images_are_local_webp_files(self):
        for name in ("tangbula.webp", "yining-ili-river.webp", "kuerdening.webp"):
            with self.subTest(name=name):
                data = (ASSETS / name).read_bytes()
                self.assertEqual(data[:4], b"RIFF")
                self.assertEqual(data[8:12], b"WEBP")

    def test_daxigou_uses_an_explicit_evidence_panel(self):
        panel = (ASSETS / "daxigou-evidence.svg").read_text(encoding="utf-8")
        self.assertIn("未找到许可明确的近期实景图", panel)
        self.assertIn("不使用其他地点照片代替", panel)

    def test_route_maps_and_daxigou_evidence_have_real_dark_variants(self):
        # Each generated light asset must have a corresponding, distinctly
        # colored dark asset (not a CSS filter) so auto/light/dark all
        # render the theme-correct palette.
        pairs = (
            ("route-a.svg", "route-a-dark.svg"),
            ("route-b.svg", "route-b-dark.svg"),
            ("route-c.svg", "route-c-dark.svg"),
            ("daxigou-evidence.svg", "daxigou-evidence-dark.svg"),
        )
        for light_name, dark_name in pairs:
            with self.subTest(light=light_name, dark=dark_name):
                light = (ASSETS / light_name).read_text(encoding="utf-8")
                dark = (ASSETS / dark_name).read_text(encoding="utf-8")
                self.assertIn("<svg", dark)
                self.assertIn("#e9e5d9", light)
                self.assertNotIn("#e9e5d9", dark)
                self.assertIn("#121610", dark)
                self.assertNotIn("#121610", light)

    def test_attribution_records_exact_licences(self):
        credits = (ASSETS / "ATTRIBUTION.md").read_text(encoding="utf-8")
        required = (
            "lwtt93",
            "CC BY 2.0",
            "Charlie Qi",
            "CC BY-SA 4.0",
            "George Lu",
            "OpenStreetMap contributors via OSRM",
        )
        for fragment in required:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, credits)

    def test_attribution_states_yining_derivative_stays_cc_by_sa(self):
        credits = (ASSETS / "ATTRIBUTION.md").read_text(encoding="utf-8")
        yining_section = credits.split("## Yining", 1)[1].split("## ", 1)[0]
        self.assertIn("remains licensed under CC BY-SA 4.0", yining_section)


class TravelStyleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = CSS.read_text(encoding="utf-8") if CSS.exists() else ""

    def test_styles_are_scoped_to_travel_page(self):
        required = (
            "html.travel-page {",
            "html.travel-page[data-color-mode=\"light\"]",
            "html.travel-page[data-color-mode=\"dark\"]",
            "html.travel-page body {",
            "html.travel-page .route-controls",
            "html.travel-page .evidence-grid",
        )
        for selector in required:
            with self.subTest(selector=selector):
                self.assertIn(selector, self.css)

    def test_uses_current_homepage_tokens(self):
        for token in (
            "--page-bg: #e9e5d9",
            "--page-fg: #222a20",
            "--page-muted: #596055",
            "--signal: #53663e",
            "--page-bg: #121610",
            "--page-fg: #e7ecdf",
            "--signal: #b7cb91",
            '--font-interface: "IBM Plex Mono"',
            '--font-prose: "IBM Plex Sans"',
        ):
            with self.subTest(token=token):
                self.assertIn(token, self.css)

    def test_supports_mobile_print_and_reduced_motion(self):
        self.assertIn("@media (max-width: 760px)", self.css)
        self.assertIn("@media (prefers-reduced-motion: reduce)", self.css)
        self.assertIn("@media print", self.css)

    def test_avoids_gradients_and_decorative_shadows(self):
        self.assertNotIn("linear-gradient", self.css)
        self.assertNotIn("radial-gradient", self.css)
        self.assertNotIn("drop-shadow", self.css)
        self.assertEqual(self.css.count("box-shadow:"), 1)
        self.assertIn("box-shadow: var(--focus-ring)", self.css)

    def test_image_failed_state_overrides_evidence_grid_object_fit(self):
        # `.image-failed` must out-specificity `html.travel-page .evidence-grid
        # img` (which sets object-fit: cover) so the broken-image fallback is
        # not cropped/hidden for sighted users once an evidence photo errors.
        self.assertIn(
            "html.travel-page .evidence-grid img.image-failed", self.css
        )
        self.assertNotIn("html.travel-page .image-failed {", self.css)

    def test_image_failed_note_is_styled_and_visible(self):
        self.assertIn(
            "html.travel-page .evidence-grid .image-failed-note", self.css
        )

    def test_theme_variant_images_are_selected_without_javascript(self):
        # Dark variants hide by default, then reveal via the same
        # auto/light/dark contract as the page's own color tokens, purely
        # through CSS attribute selectors (no script execution needed).
        self.assertIn('img[data-theme-variant="dark"]', self.css)
        self.assertIn(
            'html.travel-page[data-color-mode="auto"] img[data-theme-variant="dark"]',
            self.css,
        )
        self.assertIn(
            'html.travel-page[data-color-mode="auto"] img[data-theme-variant="light"]',
            self.css,
        )
        self.assertIn(
            'html.travel-page[data-color-mode="dark"] img[data-theme-variant="light"]',
            self.css,
        )
        self.assertIn(
            'html.travel-page[data-color-mode="dark"] img[data-theme-variant="dark"]',
            self.css,
        )
        # The auto-mode branch must live inside the OS dark-scheme media
        # query, otherwise it would apply regardless of OS preference.
        auto_index = self.css.index(
            'html.travel-page[data-color-mode="auto"] img[data-theme-variant="dark"]'
        )
        media_index = self.css.rfind("@media (prefers-color-scheme: dark)", 0, auto_index)
        self.assertNotEqual(media_index, -1)

    def test_print_media_forces_light_theme_variant_images(self):
        # The dark SVGs bake a near-black background directly into the
        # image, so printing them (explicit dark mode, or auto while the OS
        # is in dark mode) would put a large ink-wasting dark rectangle on
        # an otherwise ink-safe printed page. Print must always show the
        # light variant and hide the dark one, regardless of the on-screen
        # theme selection, so `!important` is required to out-rank the
        # screen-only `data-color-mode`/`prefers-color-scheme` rules above.
        self.assertIn("@media print", self.css)
        print_block = self.css.split("@media print {", 1)[1]
        self.assertIn('img[data-theme-variant="dark"]', print_block)
        self.assertIn('img[data-theme-variant="light"]', print_block)
        dark_index = print_block.index('img[data-theme-variant="dark"]')
        light_index = print_block.index('img[data-theme-variant="light"]')
        dark_rule = print_block[dark_index : print_block.index("}", dark_index)]
        light_rule = print_block[light_index : print_block.index("}", light_index)]
        self.assertIn("display: none !important", dark_rule)
        self.assertIn("display: block !important", light_rule)


class TravelScriptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.js = JS.read_text(encoding="utf-8") if JS.exists() else ""

    def test_defines_small_initializers(self):
        for name in ("initThemeControl", "initRouteControls", "initImageFailureState"):
            with self.subTest(name=name):
                self.assertRegex(self.js, rf"function\s+{name}\s*\(")

    def test_route_map_assets_and_captions_are_explicit(self):
        for fragment in (
            "/travel/assets/route-a.svg",
            "/travel/assets/route-b.svg",
            "/travel/assets/route-c.svg",
            "/travel/assets/route-a-dark.svg",
            "/travel/assets/route-b-dark.svg",
            "/travel/assets/route-c-dark.svg",
            "路线 A 把长途拆开",
            "大西沟到唐布拉约 359 公里",
            "大西沟只在秋色确认后增加",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.js)

    def test_route_switch_updates_both_light_and_dark_map_images(self):
        # Route switching must keep both theme-variant <img> elements in
        # sync, since CSS (not JS) decides which one is visible.
        self.assertIn('data-theme-variant="light"', self.js)
        self.assertIn('data-theme-variant="dark"', self.js)
        self.assertIn("darkSrc", self.js)

    def test_preserves_theme_storage_contract(self):
        self.assertIn("['auto', 'light', 'dark']", self.js)
        self.assertIn("localStorage.setItem('theme'", self.js)
        self.assertIn("localStorage.removeItem('theme')", self.js)

    def test_supports_keyboard_route_navigation(self):
        self.assertIn("ArrowRight", self.js)
        self.assertIn("ArrowLeft", self.js)
        self.assertIn("Home", self.js)
        self.assertIn("End", self.js)

    def test_image_failure_state_is_visible_to_sighted_users(self):
        # Browsers do not reliably paint alt text inside a broken <img>
        # (verified in Chromium), so the failure must also surface as a
        # normal, non-replaced DOM node that always paints.
        self.assertIn("image-failed-note", self.js)
        self.assertIn("figure.querySelector('figcaption')", self.js)

    def test_image_failure_state_also_catches_already_settled_eager_images(self):
        # Evidence images load eagerly now (no `loading="lazy"`), so a fast
        # same-origin failure can resolve before this deferred script
        # attaches its 'error' listener. The handler must also detect an
        # image that already finished failing by the time it runs.
        self.assertIn("image.complete", self.js)
        self.assertIn("naturalWidth === 0", self.js)


if __name__ == "__main__":
    unittest.main()
