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

    def test_page_publishes_dated_candidate_itinerary(self):
        required = (
            "2026.09.11–09.17",
            "7 天 6 晚",
            "候选行程",
            "尚未预订",
            "任何拿到链接的人都能查看",
            "9 月 18 日 01:20",
        )
        for fragment in required:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.html)

    def test_concrete_flight_schedule_candidates_are_present(self):
        required = (
            "MU2413",
            "GS7607",
            "3U5040",
            "MF3200",
            "9H8387",
            "G56652",
            "11 小时 35 分",
            "5 小时 05 分",
            "班表已核对",
            "价格待确认",
        )
        for fragment in required:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.html)

    def test_all_seven_days_remain_in_static_html(self):
        for day in range(1, 8):
            with self.subTest(day=day):
                self.assertIn(f'id="day-{day}"', self.html)
                self.assertIn(f'data-day="{day}"', self.html)
        self.assertIn("无新增住宿夜", self.html)

    def test_booking_components_are_present(self):
        required = (
            "伊宁希尔顿欢朋酒店",
            "尼勒克蜂巢印象民宿",
            "一嗨租车",
            "两间房",
            "大众探岳",
            "巴彦岱一绝烤包子",
            "特丰抓饭",
            "地面预算",
            "总预算",
            "2026 年 7 月 20 日",
            "2026 年 9 月 8 日",
        )
        for fragment in required:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.html)

    def test_fallbacks_cover_fragile_decisions(self):
        required = (
            "航班备选动作",
            "伊宁天缘国际酒店",
            "伊宁广仁郡亚朵酒店",
            "独库唐布拉野奢度假酒店",
            "携程租车 / 神州租车",
            "馕、酸奶、水果、坚果和饮用水",
        )
        for fragment in required:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.html)

    def test_public_page_excludes_personal_and_transactional_data(self):
        forbidden = (
            "身份证号",
            "订单号",
            "票号",
            "房间号",
            "手机号",
            "电话号码",
            "联系人姓名",
            "商务对象",
            "会面地址",
            "已出票",
            "已预订成功",
        )
        for fragment in forbidden:
            with self.subTest(fragment=fragment):
                self.assertNotIn(fragment, self.html)

    def test_static_supporting_route_map_remains(self):
        figure = re.search(
            r'<figure class="route-map">(.*?)</figure>',
            self.html,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(figure)
        block = figure.group(1)
        self.assertIn('src="/travel/assets/route-a.svg"', block)
        self.assertIn('src="/travel/assets/route-a-dark.svg"', block)
        self.assertNotIn("data-route-control", self.html)

    def test_flight_and_budget_tables_have_scoped_headers(self):
        tables = re.findall(r"<table>(.*?)</table>", self.html, flags=re.DOTALL)
        self.assertGreaterEqual(len(tables), 2)
        for table in tables:
            with self.subTest(table=table[:80]):
                self.assertIn('scope="col"', table)

    def test_day_navigation_targets_all_days(self):
        for day in range(1, 8):
            with self.subTest(day=day):
                self.assertIn(f'href="#day-{day}"', self.html)

    def test_dynamic_information_is_labeled_with_research_date(self):
        required = (
            "研究更新时间：2026-07-14",
            "不是 9 月精确日期库存",
            "下单前复核",
            "可取消条款待确认",
        )
        for fragment in required:
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.html)

    def test_required_places_and_backup_are_present(self):
        for place in ("伊宁", "大西沟", "唐布拉", "库尔德宁"):
            with self.subTest(place=place):
                self.assertIn(place, self.html)

    def test_page_uses_local_css_js_and_local_content_images(self):
        # travel.css bumps v=4 -> v=5 and travel.js bumps v=3 -> v=4: this
        # task's markup change (route-decision panels replaced by the dated
        # itinerary) needs matching style/script updates in Tasks 3 and 4,
        # so both cache-busting query params move together even though the
        # CSS/JS file contents are untouched here (Cloudflare caches by full
        # URL including querystring, so a stale cached asset would otherwise
        # keep serving the old route-decision styling/behavior).
        self.assertIn('href="/travel/travel.css?v=5"', self.html)
        self.assertIn('src="/travel/travel.js?v=4"', self.html)
        image_sources = re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', self.html)
        self.assertTrue(image_sources)
        for source in image_sources:
            with self.subTest(source=source):
                self.assertTrue(source.startswith("/travel/assets/"))

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

    def test_supporting_route_map_ships_both_light_and_dark_variants(self):
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
            'html.travel-page[data-color-mode="light"]',
            'html.travel-page[data-color-mode="dark"]',
            "html.travel-page body {",
            "html.travel-page .status-grid",
            "html.travel-page .flight-grid",
            "html.travel-page .itinerary-day",
            "html.travel-page .day-nav",
            "html.travel-page .budget-wrap",
            "html.travel-page .evidence-grid",
        )
        for selector in required:
            with self.subTest(selector=selector):
                self.assertIn(selector, self.css)

    def test_mobile_layout_converts_dense_grids_to_single_column(self):
        mobile = self.css.split("@media (max-width: 760px) {", 1)[1]
        for selector in (
            ".status-grid",
            ".flight-grid",
            ".stay-grid",
            ".booking-grid",
        ):
            with self.subTest(selector=selector):
                self.assertIn(selector, mobile)

    def test_print_layout_keeps_itinerary_and_hides_sticky_navigation(self):
        print_block = self.css.split("@media print {", 1)[1]
        self.assertIn(".day-nav", print_block)
        self.assertIn("display: none", print_block)
        self.assertIn(".itinerary-day", print_block)
        self.assertIn("break-inside: avoid", print_block)

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

    def test_defines_only_required_initializers(self):
        for name in ("initThemeControl", "initImageFailureState"):
            with self.subTest(name=name):
                self.assertRegex(self.js, rf"function\s+{name}\s*\(")
        self.assertNotIn("initRouteControls", self.js)
        self.assertNotIn("routeMaps", self.js)

    def test_script_does_not_hide_itinerary_content(self):
        self.assertNotIn("data-day", self.js)
        self.assertNotIn("display = 'none'", self.js)

    def test_preserves_theme_storage_contract(self):
        self.assertIn("['auto', 'light', 'dark']", self.js)
        self.assertIn("localStorage.setItem('theme'", self.js)
        self.assertIn("localStorage.removeItem('theme')", self.js)

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
