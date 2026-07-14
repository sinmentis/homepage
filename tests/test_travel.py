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

ROUTES = {
    "route-a": ("2026.09.12–09.18", "¥26,300–46,900"),
    "route-b": ("2026.09.12–09.18", "¥25,150–30,300"),
    "route-c": ("2026.09.10–09.16", "¥24,862–40,772"),
}


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
        for element in ("<header", "<main", "<section", "<footer"):
            with self.subTest(element=element):
                self.assertIn(element, self.html)
        self.assertIn('href="#main-content"', self.html)

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

    def test_page_uses_current_css_and_js_versions(self):
        # travel.css bumps v=5 -> v=6 for the print-mode dark-token fix
        # (Cloudflare caches by full URL including querystring, so a stale
        # cached asset would otherwise keep serving the old, print-unsafe
        # dark-mode CSS indefinitely). travel.js is untouched, so its query
        # param stays v=4. Content-image coverage returns once route panels
        # exist (Task 2+); the neutral comparison shell has no <img> tags of
        # its own yet.
        self.assertIn('href="/travel/travel.css?v=6"', self.html)
        self.assertIn('src="/travel/travel.js?v=4"', self.html)

    def test_social_preview_uses_current_cache_buster(self):
        preview_url = "https://shunlyu.com/travel/assets/og-travel.png?v=3"
        self.assertIn(f'<meta property="og:image" content="{preview_url}">', self.html)
        self.assertIn(f'<meta name="twitter:image" content="{preview_url}">', self.html)

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

    def test_page_opens_with_neutral_dense_comparison(self):
        self.assertIn("三套完整行程", self.html)
        self.assertIn('id="route-comparison"', self.html)
        self.assertIn('class="comparison-shell"', self.html)
        self.assertIn('id="comparison-title" tabindex="-1"', self.html)
        self.assertIn('class="route-comparison-wrap"', self.html)
        self.assertIn('class="route-comparison"', self.html)
        self.assertNotIn("推荐 / 最稳", self.html)
        self.assertNotIn("目前推荐 A", self.html)
        self.assertNotIn('aria-selected="true"', self.html)
        for label in ("班表已核对", "候选", "价格待确认", "条件项", "下单前复核"):
            self.assertIn(label, self.html)

    def test_three_equal_route_choices_exist(self):
        choices = re.findall(r'data-route-choice="(route-[abc])"', self.html)
        self.assertEqual(choices, ["route-a", "route-b", "route-c"])
        for route_id, (dates, budget) in ROUTES.items():
            with self.subTest(route=route_id):
                self.assertIn(f'href="#{route_id}-panel"', self.html)
                self.assertIn(dates, self.html)
                self.assertIn(budget, self.html)

    def test_route_b_date_disclosure_is_in_comparison_row(self):
        row = re.search(
            r'<tr[^>]*data-route-row="route-b"[^>]*>(.*?)</tr>',
            self.html,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(row)
        self.assertIn(
            "个人行程 9/11 晚–9/18；新疆共同行程 9/12–9/18，7 天 6 晚",
            row.group(1),
        )

    def test_compact_tabs_start_unselected(self):
        tabs = re.findall(r'<button\b[^>]*data-route-tab="route-[abc]"[^>]*>', self.html)
        self.assertEqual(len(tabs), 3)
        for tab in tabs:
            self.assertIn('aria-selected="false"', tab)
            self.assertIn('tabindex="-1"', tab)

    def test_stale_single_route_values_are_removed(self):
        for fragment in (
            "2026.09.11–09.17",
            "周三 / 周五",
            "08:00</td><td>11:40",
            "11 小时 35 分",
        ):
            self.assertNotIn(fragment, self.html)

    def route_panel(self, route_id):
        match = re.search(
            rf'<section\s+class="route-panel"\s+id="{route_id}-panel"\s+'
            rf'data-route-panel="{route_id}"\s+role="tabpanel"\s+'
            rf'aria-labelledby="{route_id}-tab">(.*?)</section>\s*<!-- /{route_id} -->',
            self.html,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match, route_id)
        return match.group(1)

    def route_section(self, route_id, section_name):
        panel = self.route_panel(route_id)
        match = re.search(
            rf'<section\s+class="route-{section_name}"\s+'
            rf'aria-labelledby="{route_id}-{section_name}-title">(.*?)'
            rf'</section>\s*<!-- /{route_id}-{section_name} -->',
            panel,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match, f"{route_id} {section_name}")
        block = match.group(1)
        self.assertIn(f'id="{route_id}-{section_name}-title"', block)
        self.assertTrue(re.sub(r"<[^>]+>", "", block).strip())
        return block

    def assert_complete_route(self, route_id):
        panel = self.route_panel(route_id)
        section_names = (
            "status", "flight", "transfer", "car", "map", "itinerary",
            "stays", "food", "budget", "booking", "fallbacks", "sources",
        )
        sections = {
            section_name: self.route_section(route_id, section_name)
            for section_name in section_names
        }
        positions = [
            panel.index(f'class="route-{section_name}"')
            for section_name in section_names
        ]
        self.assertEqual(positions, sorted(positions), f"{route_id} section order")
        section_fields = {
            "status": ("研究更新时间：2026-07-14", "候选", "尚未预订"),
            "flight": ("去程", "返程", "价格待确认", "下单前复核"),
            "transfer": ("接驳", "时间", "备选"),
            "car": ("取车", "还车", "驾驶者", "保险"),
            "map": ("距离", f"{route_id}.svg", f"{route_id}-dark.svg"),
            "stays": ("两间房", "主选", "备选", "可取消"),
            "food": ("早餐", "午餐", "晚餐", "清淡"),
            "budget": ("地面", "交通", "总计"),
            "booking": ("预订截止", "取消"),
            "fallbacks": ("天气", "路况", "库存", "疲劳"),
            "sources": ("href=\"https://", "班表已核对", "候选", "下单前复核"),
        }
        for section_name, required_fragments in section_fields.items():
            for fragment in required_fragments:
                self.assertIn(fragment, sections[section_name])
        for day in range(1, 8):
            article = re.search(
                rf'<article\s+class="itinerary-day"\s+id="{route_id}-day-{day}"\s+'
                rf'data-day="{day}">(.*?)</article>',
                sections["itinerary"],
                flags=re.DOTALL,
            )
            self.assertIsNotNone(article, f"{route_id} day {day}")
            for label in ("时间", "餐食", "驾驶", "体力", "备选"):
                self.assertIn(label, article.group(1))
        dates, budget = ROUTES[route_id]
        for fragment in (
            dates,
            budget,
            "可取消",
            "预订截止",
            "下单前复核",
        ):
            self.assertIn(fragment, panel)
        for forbidden_reference in ("同 A", "同 B", "同 C", "见上方", "共用前述"):
            self.assertNotIn(forbidden_reference, panel)

    def test_route_a_is_complete_and_canonical(self):
        self.assert_complete_route("route-a")
        panel = self.route_panel("route-a")
        for fragment in (
            "GS7607", "周二、周四、周六",
            "6 小时 14 分计划间隔", "约 5–5.5 小时可用时间",
            "西安住宿一晚", "约 210–230 公里 / 3–3.5 小时",
            "每日西安—伊宁航线走廊", "具体航班号与时刻下单前复核",
            "¥26,300–46,900", "route-a.svg", "route-a-dark.svg",
        ):
            self.assertIn(fragment, panel)
        self.assertNotRegex(
            panel,
            r"3U50(?:39|40)[\s\S]{0,300}班表已核对",
            "unconfirmed 3U times must not be labeled as verified",
        )

    def test_route_b_is_complete_and_canonical(self):
        self.assert_complete_route("route-b")
        panel = self.route_panel("route-b")
        for fragment in (
            "MU6903", "CZ6823", "GS7607", "约 20 分钟",
            "商务出行者个人行程为 9 月 11 日晚至 9 月 18 日",
            "约 300–360 公里 / 4–7 小时",
            "不进入仙女湖高海拔段",
            "¥25,150–30,300", "route-b.svg", "route-b-dark.svg",
        ):
            self.assertIn(fragment, panel)
        self.assertNotIn("骑马上山", panel)
        self.assertNotIn("延长至仙女湖", panel)


class TravelAssetTests(unittest.TestCase):
    def test_route_maps_are_static_svg_files_with_distance_labels(self):
        expected = {
            "route-a.svg": ("79 km", "210–230 km"),
            "route-a-dark.svg": ("79 km", "210–230 km"),
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
        # Route A's Yining↔Bee Town leg is canonically 210–230 km / 3–3.5h
        # (canonical-decisions.md); the old page's stale 286 km figure must
        # not reappear in either theme variant.
        for name in ("route-a.svg", "route-a-dark.svg"):
            with self.subTest(name=name):
                svg = (ASSETS / name).read_text(encoding="utf-8")
                self.assertNotIn(
                    "286 km", svg,
                    f"{name} must not contain the stale 286 km distance label",
                )

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

    def test_grid_cards_can_shrink_below_their_table_min_content(self):
        # `.flight-grid`/`.stay-grid`/`.booking-grid` size their two columns
        # with `minmax(0, 1fr)`, but a grid *item*'s own default min-width is
        # `auto`, which resolves to its content's min-content size unless the
        # item itself opts out. A `.flight-card` containing a wide table
        # (`min-width: 38rem`+) blows out its 1fr track regardless of the
        # container's minmax(0, ...) unless the card explicitly sets
        # `min-width: 0`, which is what actually lets `.matrix-wrap`'s
        # `overflow-x: auto` take effect instead of stretching the whole
        # page. Confirmed via a live 375px measurement: without this rule,
        # `document.documentElement.scrollWidth` still exceeded the
        # viewport even after wrapping the table in `.matrix-wrap`.
        match = re.search(
            r"html\.travel-page \.flight-card,\s*\n"
            r"html\.travel-page \.stay-card,\s*\n"
            r"html\.travel-page \.booking-card \{([^}]*)\}",
            self.css,
        )
        self.assertIsNotNone(
            match,
            "expected the shared `.flight-card, .stay-card, .booking-card` padding rule",
        )
        self.assertIn("min-width: 0", match.group(1))

    def test_print_layout_keeps_itinerary_and_hides_sticky_navigation(self):
        print_block = self.css.split("@media print {", 1)[1]
        self.assertIn(".day-nav", print_block)
        self.assertIn("display: none", print_block)
        self.assertIn(".itinerary-day", print_block)
        self.assertIn("break-inside: avoid", print_block)

    def test_print_itinerary_day_switches_to_block_to_avoid_chromium_fragmentation(self):
        # `break-inside: avoid` is not reliably honored by Chromium when the
        # element itself is `display: grid` (a documented fragmentation
        # limitation). The print-only `.itinerary-day` rule must drop the
        # grid layout in favor of `display: block` so each day card can no
        # longer split across a page boundary; `grid-template-columns` alone
        # is not sufficient defense against that pagination bug.
        print_block = self.css.split("@media print {", 1)[1]
        solo_rules = re.findall(
            r"html\.travel-page \.itinerary-day \{([^}]*)\}", print_block
        )
        self.assertTrue(
            solo_rules, "expected a standalone `.itinerary-day` rule under @media print"
        )
        solo_rule = solo_rules[-1]
        self.assertIn("display: block", solo_rule)
        self.assertNotIn("grid-template-columns", solo_rule)

    def test_print_sticky_bars_get_defensive_static_positioning(self):
        # `display: none` alone has been observed to be insufficient to keep
        # `position: sticky` elements from re-rendering mid-page during
        # Chromium's print pagination once an ancestor fragments across a
        # page break. Add `position: static !important` as defense-in-depth
        # alongside `display: none` for the two sticky bars.
        print_block = self.css.split("@media print {", 1)[1]
        match = re.search(
            r"html\.travel-page \.travel-bar,\s*\n\s*html\.travel-page \.day-nav\s*\{([^}]*)\}",
            print_block,
        )
        self.assertIsNotNone(
            match, "expected a combined `.travel-bar, .day-nav` rule under @media print"
        )
        rule = match.group(1)
        self.assertIn("display: none", rule)
        self.assertIn("position: static !important", rule)

    def test_print_hides_skip_link_with_defensive_static_positioning(self):
        # `.skip-link` is `position: fixed`, parked off-canvas (top: -5rem)
        # until keyboard focus -- architecturally identical to the
        # `.travel-bar`/`.day-nav` sticky bars above, which needed both
        # `display: none` *and* `position: static !important` because
        # `display: none` alone did not stop Chromium from re-rendering a
        # fixed-position element mid-page once print pagination fragments an
        # ancestor. Confirmed via a rasterized print PDF: without this rule,
        # the "跳到正文" skip-link pill appeared on 12 of 13 printed pages.
        print_block = self.css.split("@media print {", 1)[1]
        match = re.search(
            r"html\.travel-page \.skip-link\s*\{([^}]*)\}",
            print_block,
        )
        self.assertIsNotNone(
            match, "expected a `.skip-link` rule under @media print"
        )
        rule = match.group(1)
        self.assertIn("display: none", rule)
        self.assertIn("position: static !important", rule)

    def test_print_flight_tables_render_without_horizontal_clipping(self):
        # `.matrix-wrap` keeps `overflow-x: auto` for screen so a wide table
        # scrolls inside its card instead of overlapping its sibling.
        # `overflow: auto` has no interactive affordance in a paginated,
        # static medium though -- content beyond the clip rectangle is
        # simply never rendered onto the printed page at all. Print must
        # relax the clip (`overflow-x: visible`), drop the table's explicit
        # `min-width` floor so it can size to the printed page instead of
        # its screen minimum, and give each flight card the full container
        # width (single column) so all six columns -- including 抵达
        # (arrival) and 备注 (remarks) -- have room to lay out without
        # being clipped or overlapping.
        print_block = self.css.split("@media print {", 1)[1]

        grid_match = re.search(
            r"html\.travel-page \.flight-grid\s*\{([^}]*)\}", print_block
        )
        self.assertIsNotNone(
            grid_match, "expected a `.flight-grid` rule under @media print"
        )
        self.assertIn("grid-template-columns: 1fr", grid_match.group(1))

        wrap_match = re.search(
            r"html\.travel-page \.flight-card \.matrix-wrap\s*\{([^}]*)\}",
            print_block,
        )
        self.assertIsNotNone(
            wrap_match,
            "expected a `.flight-card .matrix-wrap` rule under @media print",
        )
        self.assertIn("overflow-x: visible", wrap_match.group(1))

        table_match = re.search(
            r"html\.travel-page \.flight-card table\s*\{([^}]*)\}", print_block
        )
        self.assertIsNotNone(
            table_match, "expected a `.flight-card table` rule under @media print"
        )
        self.assertIn("min-width: 0", table_match.group(1))

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

    def test_print_forces_light_background_on_html_not_just_body(self):
        # The print rule that hardcodes a white/black page background only
        # ever targeted `html.travel-page body`, never `html.travel-page`
        # itself. `html.travel-page` still carries `background:
        # var(--page-bg)` from the base rule, which is the dark token while
        # explicit dark mode or OS-driven auto-dark is active, so the
        # printed page showed a dark bar/margin around the (correctly
        # forced-white) body. Both the html element and the body must be
        # explicitly forced light for print.
        print_block = self.css.split("@media print {", 1)[1]
        match = re.search(
            r"html\.travel-page,\s*\n\s*html\.travel-page body \{([^}]*)\}",
            print_block,
        )
        self.assertIsNotNone(
            match,
            "expected a combined `html.travel-page, html.travel-page body` "
            "rule under @media print forcing a light background",
        )
        self.assertIn("background: #fff", match.group(1))
        self.assertIn("color: #000", match.group(1))

    def test_print_forces_light_theme_tokens_regardless_of_dark_mode(self):
        # Explicit dark mode (`data-color-mode="dark"`) and the OS/browser
        # `prefers-color-scheme: dark` default both set `--page-bg`,
        # `--page-fg`, `--page-muted`, `--signal`, `--hairline`, and
        # `--panel-bg` to their dark values via selectors with equal or
        # higher specificity than a plain print reset would have, so a
        # real printed page picked up the dark `--panel-bg` on every
        # flight/stay/booking/itinerary-day card and washed-out muted/
        # signal text -- not just a dark html/body background. Print must
        # force every themed token back to its light value with
        # `!important` so cards, hairline borders, and muted/signal text
        # stay ink-safe no matter which theme was active on screen.
        print_block = self.css.split("@media print {", 1)[1]
        match = re.search(r"html\.travel-page \{([^}]*)\}", print_block)
        self.assertIsNotNone(
            match,
            "expected a bare `html.travel-page` token-reset rule under "
            "@media print",
        )
        rule = match.group(1)
        for declaration in (
            "color-scheme: light",
            "--page-bg: #ffffff",
            "--page-fg: #222a20",
            "--page-muted: #596055",
            "--signal: #53663e",
            "--hairline: #c9c6ba",
            "--panel-bg: rgba(255, 255, 255, 0.16)",
        ):
            with self.subTest(declaration=declaration):
                self.assertIn(declaration, rule)
                self.assertIn(f"{declaration} !important", rule)


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
