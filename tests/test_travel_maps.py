import re
import unittest
from unittest import mock

from scripts import build_travel_maps as travel_maps_module
from scripts.build_travel_maps import (
    DARK_PALETTE,
    LIGHT_PALETTE,
    ROUTES,
    Place,
    RouteResult,
    RouteSegment,
    build_evidence_panel,
    build_maps,
    build_svg,
    project,
    validate_route_distance,
)


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

    def test_palette_defaults_to_light_and_paints_its_own_colors(self):
        places = {"yining": Place("伊宁", 81.2, 43.9)}
        svg = build_svg("A / test", places, [])
        self.assertIn(f'fill="{LIGHT_PALETTE.bg}"', svg)
        self.assertNotIn(DARK_PALETTE.bg, svg)

    def test_dark_palette_paints_dark_colors_not_light_ones(self):
        places = {"yining": Place("伊宁", 81.2, 43.9)}
        svg = build_svg("A / test", places, [], palette=DARK_PALETTE)
        self.assertIn(f'fill="{DARK_PALETTE.bg}"', svg)
        self.assertIn(DARK_PALETTE.fg, svg)
        self.assertIn(DARK_PALETTE.signal, svg)
        self.assertNotIn(LIGHT_PALETTE.bg, svg)
        self.assertNotIn(LIGHT_PALETTE.fg, svg)

    def test_light_and_dark_palettes_match_travel_css_tokens(self):
        # Pins the generator's palettes to the exact tokens documented in the
        # design spec / travel.css so the two can't silently drift apart.
        self.assertEqual(LIGHT_PALETTE.bg, "#e9e5d9")
        self.assertEqual(LIGHT_PALETTE.fg, "#222a20")
        self.assertEqual(LIGHT_PALETTE.muted, "#596055")
        self.assertEqual(LIGHT_PALETTE.signal, "#53663e")
        self.assertEqual(DARK_PALETTE.bg, "#121610")
        self.assertEqual(DARK_PALETTE.fg, "#e7ecdf")
        self.assertEqual(DARK_PALETTE.muted, "#87927f")
        self.assertEqual(DARK_PALETTE.signal, "#b7cb91")

    def test_backup_marker_color_is_driven_by_place_field_not_dict_key(self):
        # A place keyed "kuerdening" but NOT marked as backup must get the
        # primary marker color; a place under any other key marked backup
        # must get the muted marker color. This proves the choice is driven
        # by the semantic `is_backup` field, not a string comparison on key.
        places = {
            "kuerdening": Place("库尔德宁", 82.0, 43.4, is_backup=False),
            "some_other_key": Place("替代地点", 81.0, 44.0, is_backup=True),
        }
        svg = build_svg("test", places, [])
        self.assertIn(f'fill="{LIGHT_PALETTE.fg}" stroke="{LIGHT_PALETTE.bg}"', svg)
        self.assertIn(f'fill="{LIGHT_PALETTE.muted}" stroke="{LIGHT_PALETTE.bg}"', svg)


class TravelPlaceTests(unittest.TestCase):
    def test_place_defaults_to_not_backup(self):
        self.assertFalse(Place("伊宁", 81.2, 43.9).is_backup)

    def test_place_can_be_marked_backup(self):
        self.assertTrue(Place("库尔德宁", 82.0, 43.4, is_backup=True).is_backup)


class TravelEvidencePanelTests(unittest.TestCase):
    def test_evidence_panel_uses_light_palette_colors_and_required_text(self):
        svg = build_evidence_panel(LIGHT_PALETTE)
        self.assertIn(f'fill="{LIGHT_PALETTE.bg}"', svg)
        self.assertIn("未找到许可明确的近期实景图", svg)
        self.assertIn("不使用其他地点照片代替", svg)
        self.assertNotIn(DARK_PALETTE.bg, svg)

    def test_evidence_panel_uses_dark_palette_colors_and_required_text(self):
        svg = build_evidence_panel(DARK_PALETTE)
        self.assertIn(f'fill="{DARK_PALETTE.bg}"', svg)
        self.assertIn("未找到许可明确的近期实景图", svg)
        self.assertIn("不使用其他地点照片代替", svg)
        self.assertNotIn(LIGHT_PALETTE.bg, svg)


class TravelDistanceValidationTests(unittest.TestCase):
    def test_accepts_distance_within_tolerance(self):
        # Should not raise: 82 km actual vs 79 km approved is well inside the
        # default tolerance.
        validate_route_distance("yining -> daxigou", approved_km=79, actual_km=82)

    def test_rejects_distance_outside_tolerance(self):
        with self.assertRaises(ValueError) as ctx:
            validate_route_distance("yining -> daxigou", approved_km=79, actual_km=120)
        message = str(ctx.exception)
        self.assertIn("79", message)
        self.assertIn("120", message)

    def test_tolerance_ratio_is_configurable(self):
        # 90 km actual vs 79 km approved is a ~14% drift: rejected at the
        # tight 5% default, accepted with an explicit, wider ratio.
        with self.assertRaises(ValueError):
            validate_route_distance("yining -> daxigou", approved_km=79, actual_km=90)
        validate_route_distance(
            "yining -> daxigou", approved_km=79, actual_km=90, tolerance_ratio=0.2
        )


class TravelBuildMapsTests(unittest.TestCase):
    def _stub_fetcher(self, distances):
        def fetcher(start, end):
            key = (start.label, end.label)
            return RouteResult(
                points=((start.lon, start.lat), (end.lon, end.lat)),
                distance_km=distances[key],
            )

        return fetcher

    def test_build_maps_writes_light_and_dark_variants_for_every_route(self):
        import tempfile
        from pathlib import Path

        distances = {
            ("伊宁", "大西沟"): 79.0,
            ("伊宁", "唐布拉"): 286.0,
            ("大西沟", "唐布拉"): 359.0,
        }
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            build_maps(output_dir, fetcher=self._stub_fetcher(distances))
            expected_files = (
                "route-a.svg",
                "route-a-dark.svg",
                "route-b.svg",
                "route-b-dark.svg",
                "route-c.svg",
                "route-c-dark.svg",
                "daxigou-evidence.svg",
                "daxigou-evidence-dark.svg",
            )
            for name in expected_files:
                with self.subTest(name=name):
                    self.assertTrue((output_dir / name).exists())
            light = (output_dir / "route-a.svg").read_text(encoding="utf-8")
            dark = (output_dir / "route-a-dark.svg").read_text(encoding="utf-8")
            self.assertIn(LIGHT_PALETTE.bg, light)
            self.assertIn(DARK_PALETTE.bg, dark)
            self.assertNotIn(DARK_PALETTE.bg, light)
            self.assertNotIn(LIGHT_PALETTE.bg, dark)

    def test_build_maps_raises_and_writes_nothing_when_distance_drifts(self):
        import tempfile
        from pathlib import Path

        # yining->daxigou is approved at 79 km; feed back a wildly different
        # distance so a future route/geometry change fails loudly instead of
        # silently publishing mismatched geometry and text.
        distances = {
            ("伊宁", "大西沟"): 400.0,
            ("伊宁", "唐布拉"): 286.0,
            ("大西沟", "唐布拉"): 359.0,
        }
        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp)
            with self.assertRaises(ValueError):
                build_maps(output_dir, fetcher=self._stub_fetcher(distances))
            self.assertEqual(list(output_dir.iterdir()), [])


class TravelBuildMapsReverseCacheTests(unittest.TestCase):
    def test_reverse_leg_reuses_single_fetch_and_reverses_point_order(self):
        # Isolate the cache/reverse-cache branch in build_maps() (it checks
        # `cache_key` then `reverse_key` before calling the fetcher) from the
        # production route data, by patching the module-level PLACES/ROUTES
        # for the duration of this test only. No production code changes.
        import tempfile
        from pathlib import Path

        places = {
            "alpha": Place("Alpha", 10.0, 20.0),
            "beta": Place("Beta", 30.0, 40.0),
        }
        routes = {
            "route-forward.svg": {
                "title": "Forward",
                "distance_note": "",
                "segments": (("alpha", "beta", False, 100),),
            },
            "route-reverse.svg": {
                "title": "Reverse",
                "distance_note": "",
                "segments": (("beta", "alpha", False, 100),),
            },
        }
        calls = []

        def fetcher(start, end):
            calls.append((start.label, end.label))
            return RouteResult(
                points=((10.0, 20.0), (20.0, 30.0), (30.0, 40.0)),
                distance_km=100.0,
            )

        with mock.patch.object(travel_maps_module, "PLACES", places), mock.patch.object(
            travel_maps_module, "ROUTES", routes
        ):
            with tempfile.TemporaryDirectory() as tmp:
                output_dir = Path(tmp)
                build_maps(output_dir, fetcher=fetcher)
                forward_svg = (output_dir / "route-forward.svg").read_text(encoding="utf-8")
                reverse_svg = (output_dir / "route-reverse.svg").read_text(encoding="utf-8")

        # One-direction fetch reuse + single fetch for the reverse pair: the
        # reverse leg (beta -> alpha) must never trigger its own fetcher
        # call; it has to reuse the alpha -> beta result already in cache.
        self.assertEqual(calls, [("Alpha", "Beta")])

        # Reversed point order/output behavior: alpha and beta are the only
        # two places, so both routes project over an identical bounding box
        # and render with the same scale/offset. The reverse route's
        # polyline must therefore be the exact reverse of the forward
        # route's polyline, not a re-fetch of the opposite direction.
        forward_points = re.search(r'<polyline points="([^"]+)"', forward_svg).group(1).split(" ")
        reverse_points = re.search(r'<polyline points="([^"]+)"', reverse_svg).group(1).split(" ")
        self.assertEqual(reverse_points, list(reversed(forward_points)))


class TravelRouteADistanceNoteTests(unittest.TestCase):
    def test_route_a_distance_note_is_canonical_not_stale(self):
        # Route A's Yining<->Bee Town (唐布拉) leg is canonically 210-230 km
        # (canonical-decisions.md). The generator's public distance_note for
        # route-a.svg must reflect that range, not the stale 286 km figure,
        # or regenerating the asset would reintroduce the reviewed defect.
        distance_note = ROUTES["route-a.svg"]["distance_note"]
        self.assertIn("210–230 km", distance_note)
        self.assertNotIn("286 km", distance_note)


class TravelRouteBDistanceNoteTests(unittest.TestCase):
    def test_route_b_distance_note_is_canonical_not_stale(self):
        # Route B's Qingshuihe/Huocheng->Bee Town (大西沟→唐布拉) leg is
        # disputed between a 359 km task baseline and a ~180-200 km
        # independent estimate; canonical-decisions.md resolves this as the
        # conservative 300-360 km range, matching the panel's own
        # "约 300–360 公里 / 4–7 小时" Day 3 copy. The Bee Town->Yining
        # return leg (唐布拉→伊宁) is likewise disclosed in the panel as
        # "约 220–290 公里，来源不一，下单前复核" rather than a bare 286 km.
        # The generator's public distance_note for route-b.svg must reflect
        # both ranges, not the bare, disputed 359 km / 286 km figures, or
        # regenerating the asset would reintroduce the reviewed defect. The
        # internal segment validation values (359, 286 km) that check the
        # fetched OSRM geometry are a separate concern and stay unchanged.
        distance_note = ROUTES["route-b.svg"]["distance_note"]
        self.assertIn("79 km", distance_note)
        self.assertIn("300–360 km", distance_note)
        self.assertIn("220–290 km", distance_note)
        self.assertNotIn("359 km", distance_note)
        self.assertNotIn("286 km", distance_note)

        segments_by_leg = {
            (start, end): expected_km
            for start, end, _optional, expected_km in ROUTES["route-b.svg"]["segments"]
        }
        # The internal OSRM validation values must remain the disputed
        # baseline figures (359, 286) -- only the public label changes.
        self.assertEqual(segments_by_leg[("daxigou", "tangbula")], 359)
        self.assertEqual(segments_by_leg[("tangbula", "yining")], 286)


if __name__ == "__main__":
    unittest.main()
