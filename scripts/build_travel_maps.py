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


@dataclass(frozen=True)
class Place:
    label: str
    lon: float
    lat: float


@dataclass(frozen=True)
class RouteSegment:
    start: str
    end: str
    points: tuple[tuple[float, float], ...]
    optional: bool = False


PLACES = {
    "yining": Place("伊宁", 81.2747797, 43.9052027),
    "daxigou": Place("大西沟", 80.7729865, 44.3183502),
    "tangbula": Place("唐布拉", 84.2030504, 43.7176595),
    "kuerdening": Place("库尔德宁备用", 82.4680664, 43.4180125),
}


ROUTES = {
    "route-a.svg": {
        "title": "A / 伊宁双翼基地型",
        "distance_note": "伊宁↔大西沟 79 km · 伊宁↔唐布拉 286 km",
        "segments": (
            ("yining", "daxigou", False),
            ("yining", "tangbula", False),
        ),
    },
    "route-b.svg": {
        "title": "B / 东西连续推进型",
        "distance_note": "伊宁→大西沟 79 km · 大西沟→唐布拉 359 km · 唐布拉→伊宁 286 km",
        "segments": (
            ("yining", "daxigou", False),
            ("daxigou", "tangbula", False),
            ("tangbula", "yining", False),
        ),
    },
    "route-c.svg": {
        "title": "C / 唐布拉深住型",
        "distance_note": "伊宁↔唐布拉 286 km · 大西沟条件支线 79 km",
        "segments": (
            ("yining", "tangbula", False),
            ("yining", "daxigou", True),
        ),
    },
}


def fetch_route(start: Place, end: Place) -> tuple[tuple[float, float], ...]:
    url = (
        f"{OSRM_BASE}/{start.lon},{start.lat};{end.lon},{end.lat}"
        "?overview=full&geometries=geojson"
    )
    request = Request(url, headers={"User-Agent": "shunlyu-travel-map/1.0"})
    with urlopen(request, timeout=45) as response:
        payload = json.load(response)
    if payload.get("code") != "Ok" or not payload.get("routes"):
        raise RuntimeError(f"OSRM route failed for {start.label} -> {end.label}")
    coordinates = payload["routes"][0]["geometry"]["coordinates"]
    if len(coordinates) < 2:
        raise RuntimeError(f"OSRM returned an empty route for {start.label} -> {end.label}")
    return tuple((float(lon), float(lat)) for lon, lat in coordinates)


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
        '<rect width="1200" height="720" rx="22" fill="#e9e5d9"/>',
        '<g stroke="#53663e" stroke-opacity=".12" stroke-width="1">',
    ]
    for x in range(100, 1200, 100):
        lines.append(f'<path d="M{x} 0V720"/>')
    for y in range(100, 720, 100):
        lines.append(f'<path d="M0 {y}H1200"/>')
    lines.append("</g>")
    lines.extend(
        (
            '<text x="44" y="52" font-family="IBM Plex Sans, sans-serif" '
            f'font-size="30" font-weight="600" fill="#222a20">{escape(title)}</text>',
            '<text x="44" y="84" font-family="IBM Plex Mono, monospace" '
            f'font-size="18" fill="#596055">{escape(distance_note)}</text>',
        )
    )

    for segment, points in projected_segments:
        polyline = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
        dash = ' stroke-dasharray="12 10"' if segment.optional else ""
        color = "#a9802f" if segment.optional else "#53663e"
        lines.append(
            f'<polyline points="{polyline}" fill="none" stroke="{color}" '
            f'stroke-width="8" stroke-linecap="round" stroke-linejoin="round"{dash}/>'
        )

    for key, place in places.items():
        x, y = projected_places[key]
        fill = "#87927f" if key == "kuerdening" else "#222a20"
        lines.extend(
            (
                f'<circle cx="{x:.1f}" cy="{y:.1f}" r="9" fill="{fill}" stroke="#e9e5d9" stroke-width="4"/>',
                f'<text x="{x + 14:.1f}" y="{y - 14:.1f}" '
                'font-family="IBM Plex Mono, monospace" font-size="22" '
                f'font-weight="600" fill="#222a20">{escape(place.label)}</text>',
            )
        )

    lines.extend(
        (
            '<text x="44" y="666" font-family="IBM Plex Mono, monospace" '
            'font-size="17" fill="#596055">Route geometry: OpenStreetMap contributors via OSRM</text>',
            "</svg>",
        )
    )
    return "\n".join(lines)


def build_maps(
    output_dir: Path,
    *,
    fetcher: Callable[[Place, Place], tuple[tuple[float, float], ...]] = fetch_route,
) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    cache: dict[tuple[str, str], tuple[tuple[float, float], ...]] = {}
    for filename, route in ROUTES.items():
        segments = []
        for start_key, end_key, optional in route["segments"]:
            cache_key = (start_key, end_key)
            reverse_key = (end_key, start_key)
            if cache_key in cache:
                points = cache[cache_key]
            elif reverse_key in cache:
                points = tuple(reversed(cache[reverse_key]))
            else:
                points = fetcher(PLACES[start_key], PLACES[end_key])
                cache[cache_key] = points
            segments.append(
                RouteSegment(
                    start=start_key,
                    end=end_key,
                    points=points,
                    optional=optional,
                )
            )
        svg = build_svg(
            route["title"],
            PLACES,
            segments,
            route["distance_note"],
        )
        (output_dir / filename).write_text(svg, encoding="utf-8")


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    build_maps(root / "site" / "travel" / "assets")


if __name__ == "__main__":
    main()
