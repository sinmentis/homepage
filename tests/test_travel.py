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


if __name__ == "__main__":
    unittest.main()
