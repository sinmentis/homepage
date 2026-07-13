import unittest

from scripts.build_travel_maps import Place, RouteSegment, build_svg, project


class TravelMapProjectionTests(unittest.TestCase):
    def test_project_keeps_points_inside_canvas_and_inverts_latitude(self):
        points = [(80.0, 43.0), (84.0, 45.0)]
        mapped = project(points, width=1200, height=720, padding=80)
        self.assertEqual(len(mapped), 2)
        for x, y in mapped:
            self.assertGreaterEqual(x, 80)
            self.assertLessEqual(x, 1120)
            self.assertGreaterEqual(y, 80)
            self.assertLessEqual(y, 640)
        self.assertGreater(mapped[0][1], mapped[1][1])


class TravelMapSvgTests(unittest.TestCase):
    def test_svg_contains_route_places_and_attribution(self):
        places = {
            "yining": Place("伊宁", 81.2, 43.9),
            "daxigou": Place("大西沟", 80.7, 44.3),
        }
        segments = [
            RouteSegment(
                start="yining",
                end="daxigou",
                points=((81.2, 43.9), (81.0, 44.1), (80.7, 44.3)),
                optional=False,
            )
        ]
        svg = build_svg(
            "A / 伊宁双翼",
            places,
            segments,
            "伊宁↔大西沟 79 km",
        )
        self.assertIn("<svg", svg)
        self.assertIn("伊宁", svg)
        self.assertIn("大西沟", svg)
        self.assertIn("79 km", svg)
        self.assertIn("OpenStreetMap contributors via OSRM", svg)
        self.assertNotIn('stroke-dasharray="12 10"', svg)

    def test_optional_segment_is_dashed(self):
        places = {
            "yining": Place("伊宁", 81.2, 43.9),
            "daxigou": Place("大西沟", 80.7, 44.3),
        }
        segments = [
            RouteSegment(
                start="yining",
                end="daxigou",
                points=((81.2, 43.9), (80.7, 44.3)),
                optional=True,
            )
        ]
        svg = build_svg("C / 唐布拉深住", places, segments)
        self.assertIn('stroke-dasharray="12 10"', svg)


if __name__ == "__main__":
    unittest.main()
