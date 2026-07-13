from pathlib import Path
import re
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
        self.assertIn('href="/travel/travel.css?v=1"', self.html)
        self.assertIn('src="/travel/travel.js?v=1"', self.html)
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
if __name__ == "__main__":
    unittest.main()
