#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
from html import escape
import json
from pathlib import Path
from typing import Callable, Sequence
from urllib.request import Request, urlopen


WIDTH = 1200
HEIGHT = 720
PADDING = 84
OSRM_BASE = "https://router.project-osrm.org/route/v1/driving"

# A future route/geometry change must fail the build loudly rather than
# silently publish a distance label that no longer matches OSRM. 5% comfortably
# covers normal day-to-day OSRM routing variance (observed drift against the
# approved labels is under 0.5% as of 2026-07-13) while still catching a
# genuinely different route.
DEFAULT_TOLERANCE_RATIO = 0.05


@dataclass(frozen=True)
class Place:
    label: str
    lon: float
    lat: float
    is_backup: bool = False


@dataclass(frozen=True)
class RouteSegment:
    start: str
    end: str
    points: tuple[tuple[float, float], ...]
    optional: bool = False


@dataclass(frozen=True)
class RouteResult:
    points: tuple[tuple[float, float], ...]
    distance_km: float


@dataclass(frozen=True)
class Palette:
    name: str
    bg: str
    fg: str
    muted: str
    signal: str
    # Accent for optional/conditional route legs (dashed lines). Not one of
    # the five documented design tokens; chosen to stay in the same amber
    # family while remaining legible against each background, verified with
    # a live browser screenshot rather than a CSS filter guess.
    optional_line: str


LIGHT_PALETTE = Palette(
    name="light",
    bg="#e9e5d9",
    fg="#222a20",
    muted="#596055",
    signal="#53663e",
    optional_line="#a9802f",
)

DARK_PALETTE = Palette(
    name="dark",
    bg="#121610",
    fg="#e7ecdf",
    muted="#87927f",
    signal="#b7cb91",
    optional_line="#d9ac54",
)


PLACES = {
    "yining": Place("伊宁", 81.2747797, 43.9052027),
    "daxigou": Place("大西沟", 80.7729865, 44.3183502),
    "tangbula": Place("唐布拉", 84.2030504, 43.7176595),
    "kuerdening": Place("库尔德宁备用", 82.4680664, 43.4180125, is_backup=True),
}


ROUTES = {
    "route-a.svg": {
        "title": "A / 伊宁双翼基地型",
        "distance_note": "伊宁↔大西沟 79 km · 伊宁↔唐布拉 210–230 km",
        "segments": (
            ("yining", "daxigou", False, 79),
            ("yining", "tangbula", False, 286),
        ),
    },
    "route-b.svg": {
        "title": "B / 东西连续推进型",
        # Both legs are canonically disclosed as ranges, not bare disputed
        # figures (canonical-decisions.md §5): 大西沟→唐布拉 is disputed
        # between this 359 km task baseline and a ~180-200 km independent
        # estimate, resolved to the conservative 300–360 km; 唐布拉→伊宁 is
        # disclosed as 220–290 km, "来源不一". The segment validation values
        # below (359, 286) intentionally stay as the internal OSRM-checked
        # baselines -- only the public label changes.
        "distance_note": "伊宁→大西沟 79 km · 大西沟→唐布拉 300–360 km · 唐布拉→伊宁 220–290 km",
        "segments": (
            ("yining", "daxigou", False, 79),
            ("daxigou", "tangbula", False, 359),
            ("tangbula", "yining", False, 286),
        ),
    },
    "route-c.svg": {
        "title": "C / 唐布拉深住型",
        # The Yining<->Bee Town (伊宁↔唐布拉) movement is never driven as a
        # single 286 km day on this route: it is split across Day 2
        # (outbound) and Day 6 (return), matching #route-comparison's own
        # "无单一长途驾驶日" row and the panel's #route-c-map figcaption
        # ("全程无单一长途驾驶日"). The public label must say so ("分段行驶"),
        # not restate the bare 286 km figure, or the generated map would
        # keep contradicting the panel/comparison-table claim. The segment
        # validation value below (286) intentionally stays as the internal
        # OSRM-checked baseline for the fetched geometry -- only the public
        # label changes.
        "distance_note": "伊宁↔唐布拉 分段行驶 · 大西沟条件支线 79 km",
        "segments": (
            ("yining", "tangbula", False, 286),
            ("yining", "daxigou", True, 79),
        ),
    },
}


def validate_route_distance(
    label: str,
    approved_km: float,
    actual_km: float,
    tolerance_ratio: float = DEFAULT_TOLERANCE_RATIO,
) -> None:
    """Raise ValueError if `actual_km` drifts from `approved_km` beyond
    `tolerance_ratio`. Used to keep the approved, rounded planning labels
    honest against the OSRM-reported distance actually used to draw each
    route, instead of letting the two silently diverge."""
    tolerance_km = approved_km * tolerance_ratio
    diff_km = abs(actual_km - approved_km)
    if diff_km > tolerance_km:
        raise ValueError(
            f"{label}: OSRM-reported distance {actual_km:.1f} km differs from "
            f"the approved planning label {approved_km:.0f} km by {diff_km:.1f} km, "
            f"exceeding the {tolerance_km:.1f} km ({tolerance_ratio:.0%}) tolerance"
        )


def fetch_route(start: Place, end: Place) -> RouteResult:
    url = (
        f"{OSRM_BASE}/{start.lon},{start.lat};{end.lon},{end.lat}"
        "?overview=full&geometries=geojson"
    )
    request = Request(url, headers={"User-Agent": "shunlyu-travel-map/1.0"})
    with urlopen(request, timeout=45) as response:
        payload = json.load(response)
    if payload.get("code") != "Ok" or not payload.get("routes"):
        raise RuntimeError(f"OSRM route failed for {start.label} -> {end.label}")
    route = payload["routes"][0]
    coordinates = route["geometry"]["coordinates"]
    if len(coordinates) < 2:
        raise RuntimeError(f"OSRM returned an empty route for {start.label} -> {end.label}")
    points = tuple((float(lon), float(lat)) for lon, lat in coordinates)
    return RouteResult(points=points, distance_km=float(route["distance"]) / 1000.0)


def project(
    points: Sequence[tuple[float, float]],
    *,
    width: int = WIDTH,
    height: int = HEIGHT,
    padding: int = PADDING,
) -> tuple[tuple[float, float], ...]:
    if not points:
        raise ValueError("at least one point is required")
    lons = [point[0] for point in points]
    lats = [point[1] for point in points]
    min_lon, max_lon = min(lons), max(lons)
    min_lat, max_lat = min(lats), max(lats)
    lon_span = max(max_lon - min_lon, 0.000001)
    lat_span = max(max_lat - min_lat, 0.000001)
    usable_width = width - (padding * 2)
    usable_height = height - (padding * 2)
    scale = min(usable_width / lon_span, usable_height / lat_span)
    drawn_width = lon_span * scale
    drawn_height = lat_span * scale
    x_offset = padding + ((usable_width - drawn_width) / 2)
    y_offset = padding + ((usable_height - drawn_height) / 2)
    return tuple(
        (
            x_offset + ((lon - min_lon) * scale),
            height - (y_offset + ((lat - min_lat) * scale)),
        )
        for lon, lat in points
    )


def build_svg(
    title: str,
    places: dict[str, Place],
    segments: Sequence[RouteSegment],
    distance_note: str = "",
    palette: Palette = LIGHT_PALETTE,
) -> str:
    all_points = [point for segment in segments for point in segment.points]
    all_points.extend((place.lon, place.lat) for place in places.values())
    projected = project(all_points)
    point_iter = iter(projected)

    projected_segments = []
    for segment in segments:
        segment_points = tuple(next(point_iter) for _ in segment.points)
        projected_segments.append((segment, segment_points))
    projected_places = {
        key: next(point_iter)
        for key in places
    }

    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 720" role="img">',
        f"<title>{escape(title)}</title>",
        f'<rect width="1200" height="720" rx="22" fill="{palette.bg}"/>',
        f'<g stroke="{palette.signal}" stroke-opacity=".12" stroke-width="1">',
    ]
    for x in range(100, 1200, 100):
        lines.append(f'<path d="M{x} 0V720"/>')
    for y in range(100, 720, 100):
        lines.append(f'<path d="M0 {y}H1200"/>')
    lines.append("</g>")
    lines.extend(
        (
            '<text x="44" y="52" font-family="IBM Plex Sans, sans-serif" '
            f'font-size="30" font-weight="600" fill="{palette.fg}">{escape(title)}</text>',
            '<text x="44" y="84" font-family="IBM Plex Mono, monospace" '
            f'font-size="18" fill="{palette.muted}">{escape(distance_note)}</text>',
        )
    )

    for segment, points in projected_segments:
        polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        dash = ' stroke-dasharray="12 10"' if segment.optional else ""
        color = palette.optional_line if segment.optional else palette.signal
        lines.append(
            f'<polyline points="{polyline}" fill="none" stroke="{color}" '
            f'stroke-width="8" stroke-linecap="round" stroke-linejoin="round"{dash}/>'
        )

    for key, place in places.items():
        x, y = projected_places[key]
        fill = palette.muted if place.is_backup else palette.fg
        lines.extend(
            (
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="{fill}" stroke="{palette.bg}" stroke-width="4"/>',
                f'<text x="{x + 14:.1f}" y="{y - 14:.1f}" '
                'font-family="IBM Plex Mono, monospace" font-size="22" '
                f'font-weight="600" fill="{palette.fg}">{escape(place.label)}</text>',
            )
        )

    lines.extend(
        (
            '<text x="44" y="666" font-family="IBM Plex Mono, monospace" '
            f'font-size="17" fill="{palette.muted}">Route geometry: OpenStreetMap contributors via OSRM</text>',
            "</svg>",
        )
    )
    return "\n".join(lines)


def build_evidence_panel(palette: Palette = LIGHT_PALETTE) -> str:
    """Original evidence-gap graphic for Daxigou, redrawn per palette so the
    dark variant uses real theme-correct colors instead of a CSS filter."""
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 760" role="img">',
        "<title>大西沟影像证据说明</title>",
        f'<rect width="1200" height="760" rx="24" fill="{palette.bg}"/>',
        f'<g stroke="{palette.signal}" stroke-opacity=".12">',
        '<path d="M0 120H1200M0 240H1200M0 360H1200M0 480H1200M0 600H1200"/>',
        '<path d="M180 0V760M360 0V760M540 0V760M720 0V760M900 0V760M1080 0V760"/>',
        "</g>",
        f'<path d="M190 510c130-210 250-260 365-90 120-230 250-270 455 55" fill="none" stroke="{palette.signal}" stroke-width="12" stroke-linecap="round"/>',
        f'<circle cx="550" cy="250" r="42" fill="none" stroke="{palette.signal}" stroke-width="10"/>',
        f'<text x="110" y="120" font-family="IBM Plex Mono, monospace" font-size="30" fill="{palette.muted}">DAXIGOU / EVIDENCE GAP</text>',
        f'<text x="110" y="620" font-family="IBM Plex Sans, sans-serif" font-size="42" font-weight="600" fill="{palette.fg}">未找到许可明确的近期实景图</text>',
        f'<text x="110" y="680" font-family="IBM Plex Sans, sans-serif" font-size="27" fill="{palette.muted}">不使用其他地点照片代替。秋色在出发前复核。</text>',
        "</svg>",
    ]
    return "\n".join(lines)


def build_maps(
    output_dir: Path,
    *,
    fetcher: Callable[[Place, Place], RouteResult] = fetch_route,
    tolerance_ratio: float = DEFAULT_TOLERANCE_RATIO,
) -> None:
    cache: dict[tuple[str, str], RouteResult] = {}
    routes_segments: dict[str, list[RouteSegment]] = {}

    # Fetch and validate every segment of every route BEFORE writing any
    # file, so a distance drift beyond tolerance fails the whole build
    # loudly instead of silently publishing a partially mismatched set of
    # assets.
    for filename, route in ROUTES.items():
        segments = []
        for start_key, end_key, optional, expected_km in route["segments"]:
            cache_key = (start_key, end_key)
            reverse_key = (end_key, start_key)
            if cache_key in cache:
                result = cache[cache_key]
                points = result.points
            elif reverse_key in cache:
                result = cache[reverse_key]
                points = tuple(reversed(result.points))
            else:
                result = fetcher(PLACES[start_key], PLACES[end_key])
                cache[cache_key] = result
                points = result.points
            validate_route_distance(
                f"{filename}: {PLACES[start_key].label} -> {PLACES[end_key].label}",
                expected_km,
                result.distance_km,
                tolerance_ratio,
            )
            segments.append(
                RouteSegment(
                    start=start_key,
                    end=end_key,
                    points=points,
                    optional=optional,
                )
            )
        routes_segments[filename] = segments

    output_dir.mkdir(parents=True, exist_ok=True)
    for filename, route in ROUTES.items():
        segments = routes_segments[filename]
        for palette in (LIGHT_PALETTE, DARK_PALETTE):
            svg = build_svg(
                route["title"],
                PLACES,
                segments,
                route["distance_note"],
                palette,
            )
            name = filename if palette is LIGHT_PALETTE else filename.replace(".svg", "-dark.svg")
            (output_dir / name).write_text(svg, encoding="utf-8")

    for palette in (LIGHT_PALETTE, DARK_PALETTE):
        name = "daxigou-evidence.svg" if palette is LIGHT_PALETTE else "daxigou-evidence-dark.svg"
        (output_dir / name).write_text(build_evidence_panel(palette), encoding="utf-8")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    build_maps(root / "site" / "travel" / "assets")


if __name__ == "__main__":
    main()
