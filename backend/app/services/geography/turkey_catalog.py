"""
StudyOS Geography EAE — Turkey production catalog.

Authoritative pedagogical catalog for 12 Turkey geography asset packages.
Coordinates are approximate WGS84 centroids used for educational SVG projection.
"""

from __future__ import annotations

import json
import math
import unicodedata
from pathlib import Path
from typing import Any

TURKEY_VIEWPORT = {
    "width": 1000.0,
    "height": 480.0,
    "default_scale": 1.0,
    "max_scale": 12.0,
}

_LON_MIN, _LON_MAX = 25.5, 45.0
_LAT_MIN, _LAT_MAX = 35.8, 42.3

DATA_ROOT = Path(__file__).resolve().parents[4] / "data" / "geography" / "turkey"

REGIONS: list[dict[str, Any]] = [
    {"slug": "marmara", "tr": "Marmara", "en": "Marmara", "lon": 28.5, "lat": 40.8},
    {"slug": "ege", "tr": "Ege", "en": "Aegean", "lon": 28.0, "lat": 38.5},
    {"slug": "akdeniz", "tr": "Akdeniz", "en": "Mediterranean", "lon": 32.5, "lat": 36.8},
    {"slug": "ic_anadolu", "tr": "İç Anadolu", "en": "Central Anatolia", "lon": 33.5, "lat": 39.0},
    {"slug": "karadeniz", "tr": "Karadeniz", "en": "Black Sea", "lon": 35.5, "lat": 41.0},
    {"slug": "dogu_anadolu", "tr": "Doğu Anadolu", "en": "Eastern Anatolia", "lon": 41.0, "lat": 39.5},
    {"slug": "guneydogu_anadolu", "tr": "Güneydoğu Anadolu", "en": "Southeastern Anatolia", "lon": 39.5, "lat": 37.5},
]

# (slug, tr_name, region_slug, lon, lat) — 81 provinces
PROVINCES: list[tuple[str, str, str, float, float]] = [
    ("adana", "Adana", "akdeniz", 35.32, 37.0),
    ("adiyaman", "Adıyaman", "guneydogu_anadolu", 38.28, 37.76),
    ("afyonkarahisar", "Afyonkarahisar", "ege", 30.54, 38.75),
    ("agri", "Ağrı", "dogu_anadolu", 43.05, 39.72),
    ("amasya", "Amasya", "karadeniz", 35.83, 40.65),
    ("ankara", "Ankara", "ic_anadolu", 32.85, 39.93),
    ("antalya", "Antalya", "akdeniz", 30.71, 36.90),
    ("artvin", "Artvin", "karadeniz", 41.82, 41.18),
    ("aydin", "Aydın", "ege", 27.84, 37.84),
    ("balikesir", "Balıkesir", "marmara", 27.88, 39.65),
    ("bilecik", "Bilecik", "marmara", 29.98, 40.14),
    ("bingol", "Bingöl", "dogu_anadolu", 40.50, 38.88),
    ("bitlis", "Bitlis", "dogu_anadolu", 42.11, 38.40),
    ("bolu", "Bolu", "karadeniz", 31.61, 40.73),
    ("burdur", "Burdur", "akdeniz", 30.29, 37.72),
    ("bursa", "Bursa", "marmara", 29.06, 40.19),
    ("canakkale", "Çanakkale", "marmara", 26.41, 40.15),
    ("cankiri", "Çankırı", "ic_anadolu", 33.61, 40.60),
    ("corum", "Çorum", "karadeniz", 34.95, 40.55),
    ("denizli", "Denizli", "ege", 29.09, 37.78),
    ("diyarbakir", "Diyarbakır", "guneydogu_anadolu", 40.23, 37.91),
    ("edirne", "Edirne", "marmara", 26.56, 41.68),
    ("elazig", "Elazığ", "dogu_anadolu", 39.23, 38.67),
    ("erzincan", "Erzincan", "dogu_anadolu", 39.49, 39.75),
    ("erzurum", "Erzurum", "dogu_anadolu", 41.28, 39.90),
    ("eskisehir", "Eskişehir", "ic_anadolu", 30.52, 39.78),
    ("gaziantep", "Gaziantep", "guneydogu_anadolu", 37.38, 37.07),
    ("giresun", "Giresun", "karadeniz", 38.39, 40.91),
    ("gumushane", "Gümüşhane", "karadeniz", 39.48, 40.46),
    ("hakkari", "Hakkâri", "dogu_anadolu", 43.74, 37.57),
    ("hatay", "Hatay", "akdeniz", 36.16, 36.20),
    ("isparta", "Isparta", "akdeniz", 30.56, 37.76),
    ("mersin", "Mersin", "akdeniz", 34.63, 36.80),
    ("istanbul", "İstanbul", "marmara", 28.98, 41.01),
    ("izmir", "İzmir", "ege", 27.14, 38.42),
    ("kars", "Kars", "dogu_anadolu", 43.10, 40.60),
    ("kastamonu", "Kastamonu", "karadeniz", 33.78, 41.39),
    ("kayseri", "Kayseri", "ic_anadolu", 35.49, 38.73),
    ("kirklareli", "Kırklareli", "marmara", 27.23, 41.73),
    ("kirsehir", "Kırşehir", "ic_anadolu", 34.16, 39.15),
    ("kocaeli", "Kocaeli", "marmara", 29.92, 40.85),
    ("konya", "Konya", "ic_anadolu", 32.48, 37.87),
    ("kutahya", "Kütahya", "ege", 29.98, 39.42),
    ("malatya", "Malatya", "dogu_anadolu", 38.31, 38.36),
    ("manisa", "Manisa", "ege", 27.43, 38.62),
    ("kahramanmaras", "Kahramanmaraş", "akdeniz", 36.94, 37.59),
    ("mardin", "Mardin", "guneydogu_anadolu", 40.73, 37.31),
    ("mugla", "Muğla", "ege", 28.37, 37.22),
    ("mus", "Muş", "dogu_anadolu", 41.49, 38.74),
    ("nevsehir", "Nevşehir", "ic_anadolu", 34.71, 38.62),
    ("nigde", "Niğde", "ic_anadolu", 34.68, 37.97),
    ("ordu", "Ordu", "karadeniz", 37.88, 40.98),
    ("rize", "Rize", "karadeniz", 40.52, 41.02),
    ("sakarya", "Sakarya", "marmara", 30.40, 40.76),
    ("samsun", "Samsun", "karadeniz", 36.33, 41.29),
    ("siirt", "Siirt", "guneydogu_anadolu", 41.94, 37.93),
    ("sinop", "Sinop", "karadeniz", 35.15, 42.03),
    ("sivas", "Sivas", "ic_anadolu", 37.02, 39.75),
    ("tekirdag", "Tekirdağ", "marmara", 27.51, 40.98),
    ("tokat", "Tokat", "karadeniz", 36.55, 40.32),
    ("trabzon", "Trabzon", "karadeniz", 39.72, 41.00),
    ("tunceli", "Tunceli", "dogu_anadolu", 39.54, 39.11),
    ("sanliurfa", "Şanlıurfa", "guneydogu_anadolu", 38.79, 37.17),
    ("usak", "Uşak", "ege", 29.41, 38.68),
    ("van", "Van", "dogu_anadolu", 43.34, 38.49),
    ("yozgat", "Yozgat", "ic_anadolu", 34.81, 39.82),
    ("zonguldak", "Zonguldak", "karadeniz", 31.79, 41.46),
    ("aksaray", "Aksaray", "ic_anadolu", 34.03, 38.37),
    ("bayburt", "Bayburt", "karadeniz", 40.23, 40.26),
    ("karaman", "Karaman", "ic_anadolu", 33.22, 37.18),
    ("kirikkale", "Kırıkkale", "ic_anadolu", 33.51, 39.85),
    ("batman", "Batman", "guneydogu_anadolu", 41.13, 37.89),
    ("sirnak", "Şırnak", "guneydogu_anadolu", 42.46, 37.52),
    ("bartin", "Bartın", "karadeniz", 32.34, 41.63),
    ("ardahan", "Ardahan", "dogu_anadolu", 42.70, 41.11),
    ("igdir", "Iğdır", "dogu_anadolu", 44.05, 39.92),
    ("yalova", "Yalova", "marmara", 29.28, 40.65),
    ("karabuk", "Karabük", "karadeniz", 32.63, 41.20),
    ("kilis", "Kilis", "guneydogu_anadolu", 37.12, 36.72),
    ("osmaniye", "Osmaniye", "akdeniz", 36.25, 37.07),
    ("duzce", "Düzce", "karadeniz", 31.16, 40.84),
]



def project_lon_lat(lon: float, lat: float) -> tuple[float, float]:
    x = (lon - _LON_MIN) / (_LON_MAX - _LON_MIN) * TURKEY_VIEWPORT["width"]
    y = (1.0 - (lat - _LAT_MIN) / (_LAT_MAX - _LAT_MIN)) * TURKEY_VIEWPORT["height"]
    return round(x, 2), round(y, 2)


def rect_path(cx: float, cy: float, w: float, h: float) -> str:
    x0, y0 = cx - w / 2, cy - h / 2
    x1, y1 = cx + w / 2, cy + h / 2
    return f"M{x0:.2f} {y0:.2f} L{x1:.2f} {y0:.2f} L{x1:.2f} {y1:.2f} L{x0:.2f} {y1:.2f} Z"


def line_path(points: list[tuple[float, float]]) -> str:
    if not points:
        return ""
    parts = [f"M{points[0][0]:.2f} {points[0][1]:.2f}"]
    for x, y in points[1:]:
        parts.append(f"L{x:.2f} {y:.2f}")
    return " ".join(parts)


def circle_path(cx: float, cy: float, r: float = 6.0) -> str:
    k = 0.5522847498 * r
    return (
        f"M{cx - r:.2f} {cy:.2f} "
        f"C{cx - r:.2f} {cy - k:.2f} {cx - k:.2f} {cy - r:.2f} {cx:.2f} {cy - r:.2f} "
        f"C{cx + k:.2f} {cy - r:.2f} {cx + r:.2f} {cy - k:.2f} {cx + r:.2f} {cy:.2f} "
        f"C{cx + r:.2f} {cy + k:.2f} {cx + k:.2f} {cy + r:.2f} {cx:.2f} {cy + r:.2f} "
        f"C{cx - k:.2f} {cy + r:.2f} {cx - r:.2f} {cy + k:.2f} {cx - r:.2f} {cy:.2f} Z"
    )


def bbox_wh(cx: float, cy: float, w: float, h: float) -> list[float]:
    return [round(cx - w / 2, 2), round(cy - h / 2, 2), round(cx + w / 2, 2), round(cy + h / 2, 2)]


# ── GeoJSON → SVG polygon helpers ───────────────────────────────────────────

def _normalize_slug(name: str) -> str:
    """Convert a Turkish province name to a URL/ID-safe ASCII slug."""
    replacements = {
        "ç": "c", "Ç": "c",
        "ğ": "g", "Ğ": "g",
        "ı": "i", "İ": "i",
        "ö": "o", "Ö": "o",
        "ş": "s", "Ş": "s",
        "ü": "u", "Ü": "u",
    }
    for src, dst in replacements.items():
        name = name.replace(src, dst)
    # Strip remaining non-ASCII via NFD decomposition
    nfd = unicodedata.normalize("NFD", name)
    ascii_str = "".join(c for c in nfd if unicodedata.category(c) != "Mn")
    return ascii_str.lower().strip().replace(" ", "_").replace("-", "_")


def _douglas_peucker(
    points: list[tuple[float, float]], tolerance: float
) -> list[tuple[float, float]]:
    """Ramer-Douglas-Peucker simplification for polygon/polyline point lists."""
    if len(points) < 3:
        return points
    # Find the point furthest from the line between start and end
    start, end = points[0], points[-1]
    dx = end[0] - start[0]
    dy = end[1] - start[1]
    length = math.hypot(dx, dy)
    max_dist = 0.0
    max_idx = 0
    for i in range(1, len(points) - 1):
        if length == 0:
            dist = math.hypot(points[i][0] - start[0], points[i][1] - start[1])
        else:
            dist = abs(dx * (start[1] - points[i][1]) - (start[0] - points[i][0]) * dy) / length
        if dist > max_dist:
            max_dist = dist
            max_idx = i
    if max_dist <= tolerance:
        return [start, end]
    left = _douglas_peucker(points[:max_idx + 1], tolerance)
    right = _douglas_peucker(points[max_idx:], tolerance)
    return left[:-1] + right


def _geojson_ring_to_svg_path(ring: list[list[float]], tolerance_deg: float = 0.008) -> str:
    """Convert a GeoJSON coordinate ring [[lon, lat], ...] to SVG path string."""
    # Project all points to SVG space
    projected = [project_lon_lat(pt[0], pt[1]) for pt in ring]
    # Simplify
    simplified = _douglas_peucker(projected, tolerance_deg * 20)  # deg→SVG units ~20x
    if len(simplified) < 3:
        return ""
    parts = [f"M{simplified[0][0]:.2f} {simplified[0][1]:.2f}"]
    for x, y in simplified[1:]:
        parts.append(f"L{x:.2f} {y:.2f}")
    parts.append("Z")
    return " ".join(parts)


def geojson_to_svg_path(geometry: dict[str, Any], tolerance_deg: float = 0.008) -> str:
    """Convert a GeoJSON geometry (Polygon or MultiPolygon) to an SVG path string."""
    geo_type = geometry.get("type", "")
    coords = geometry.get("coordinates", [])
    parts: list[str] = []

    if geo_type == "Polygon":
        # coords = [outer_ring, *inner_rings] — use outer ring only
        if coords:
            p = _geojson_ring_to_svg_path(coords[0], tolerance_deg)
            if p:
                parts.append(p)
    elif geo_type == "MultiPolygon":
        # coords = [[outer_ring, *holes], ...] — pick largest polygon by coord count
        best_ring: list[list[float]] = []
        for polygon in coords:
            if polygon and len(polygon[0]) > len(best_ring):
                best_ring = polygon[0]
        # Also include other significant polygons (area > 10% of best)
        threshold = max(3, int(len(best_ring) * 0.1))
        for polygon in coords:
            if polygon and len(polygon[0]) >= threshold:
                p = _geojson_ring_to_svg_path(polygon[0], tolerance_deg)
                if p:
                    parts.append(p)
    return " ".join(parts)


def _bbox_from_path_d(path_d: str) -> list[float]:
    """Extract bounding box [xmin, ymin, xmax, ymax] from SVG path data string."""
    import re
    nums = list(map(float, re.findall(r"[-+]?(?:\d*\.\d+|\d+)", path_d)))
    if len(nums) < 4:
        return [0.0, 0.0, 0.0, 0.0]
    xs = nums[0::2]
    ys = nums[1::2]
    return [round(min(xs), 2), round(min(ys), 2), round(max(xs), 2), round(max(ys), 2)]


def load_province_geojson() -> dict[str, dict[str, Any]]:
    """
    Load Turkey province boundaries from the GeoJSON source file.
    Returns a dict mapping normalized slug → geometry dict.
    Falls back to empty dict if file not found (builder uses rect_path as fallback).
    """
    geo_file = DATA_ROOT / "sources" / "tr-provinces.geojson"
    if not geo_file.exists():
        return {}
    data = json.loads(geo_file.read_text(encoding="utf-8"))
    result: dict[str, dict[str, Any]] = {}
    for feature in data.get("features", []):
        props = feature.get("properties", {})
        name = props.get("name") or props.get("NAME") or ""
        if not name:
            continue
        slug = _normalize_slug(name)
        result[slug] = feature["geometry"]
    # Known slug aliases where GeoJSON name differs from catalog slug
    _SLUG_ALIASES: dict[str, str] = {
        "afyon": "afyonkarahisar",  # GeoJSON uses short form
    }
    for geo_slug, catalog_slug in _SLUG_ALIASES.items():
        if geo_slug in result and catalog_slug not in result:
            result[catalog_slug] = result[geo_slug]
    return result



def geo_attrs(
    layer_type: str,
    feature_class: str,
    *,
    confusable: list[str] | None = None,
    aliases: list[str] | None = None,
    hints: list[str] | None = None,
    region_codes: list[str] | None = None,
    province_codes: list[str] | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "layer_type": layer_type,
        "feature_class": feature_class,
        "confusable_with": confusable or [],
        "qie_aliases": aliases or [],
        "evidence_topic_hints": hints or [],
    }
    if region_codes is not None:
        out["region_codes"] = region_codes
    if province_codes is not None:
        out["province_codes"] = province_codes
    if extra:
        out.update(extra)
    return out


def nid(prefix: str, layer: str, slug: str) -> str:
    return f"{prefix}::{layer}::{slug}"


def make_node(
    node_id: str,
    tr: str,
    en: str,
    bbox: list[float],
    attrs: dict[str, Any],
    path_d: str,
) -> dict[str, Any]:
    return {
        "id": node_id,
        "name": {"tr": tr, "en": en},
        "bounding_box": bbox,
        "attributes": attrs,
        "path_d": path_d,
    }


# Confusable pairs (bidirectional pedagogical distractors)
CONFUSABLE_PAIRS: list[tuple[str, str]] = [
    ("turkey_hydro_v1::river::kizilirmak", "turkey_hydro_v1::river::sakarya"),
    ("turkey_hydro_v1::river::ergene", "turkey_hydro_v1::river::gediz"),
    ("turkey_hydro_v1::river::yesilirmak", "turkey_hydro_v1::river::kizilirmak"),
    ("turkey_hydro_v1::lake::van", "turkey_hydro_v1::lake::tuz"),
    ("turkey_minerals_v1::mineral_deposit::bor_eskisehir", "turkey_minerals_v1::mineral_deposit::komur_zonguldak"),
    ("turkey_minerals_v1::mineral_deposit::bakir_murgul", "turkey_minerals_v1::mineral_deposit::krom_elazig"),
    ("turkey_admin_v1::province::konya", "turkey_admin_v1::province::ankara"),
    ("turkey_admin_v1::province::izmir", "turkey_admin_v1::province::antalya"),
    ("turkey_admin_v1::region::ege", "turkey_admin_v1::region::marmara"),
    ("turkey_climate_v1::climate_zone::karadeniz", "turkey_climate_v1::climate_zone::akdeniz"),
    ("turkey_physical_v1::plain::gediz", "turkey_physical_v1::plain::buyuk_menderes"),
    ("turkey_hazards_v1::fault::kuzey_anadolu", "turkey_hazards_v1::fault::dogu_anadolu"),
]


def confusable_map() -> dict[str, list[str]]:
    m: dict[str, list[str]] = {}
    for a, b in CONFUSABLE_PAIRS:
        m.setdefault(a, []).append(b)
        m.setdefault(b, []).append(a)
    return m


def adjacency_catalog() -> dict[str, Any]:
    """Province → region membership (full adjacency edges generated lightly)."""
    by_region: dict[str, list[str]] = {}
    for slug, _name, region, _lo, _la in PROVINCES:
        by_region.setdefault(region, []).append(slug)
    neighbors: dict[str, list[str]] = {}
    for region, members in by_region.items():
        for slug in members:
            others = [m for m in members if m != slug][:6]
            neighbors[slug] = others
    return {"region_membership": by_region, "province_neighbors": neighbors}


def build_admin_package(cmap: dict[str, list[str]]) -> dict[str, Any]:
    prefix = "turkey_admin_v1"
    layers: list[dict[str, Any]] = []

    # country
    cx, cy = project_lon_lat(35.0, 39.0)
    country = make_node(
        nid(prefix, "country", "turkiye"),
        "Türkiye",
        "Turkey",
        bbox_wh(cx, cy, 900, 400),
        geo_attrs("country", "sovereign_state", aliases=["Türkiye", "Turkey"], hints=["turkiye_cografyasi"]),
        rect_path(cx, cy, 900, 400),
    )
    layers.append({"id": "country", "z_index": 0, "min_lod": 0.5, "nodes": [country]})

    # regions
    region_nodes = []
    for r in REGIONS:
        x, y = project_lon_lat(r["lon"], r["lat"])
        node_id = nid(prefix, "region", r["slug"])
        region_nodes.append(
            make_node(
                node_id,
                r["tr"],
                r["en"],
                bbox_wh(x, y, 160, 100),
                geo_attrs(
                    "region",
                    "geographic_region",
                    confusable=cmap.get(node_id, []),
                    aliases=[r["tr"], f"{r['tr']} Bölgesi"],
                    hints=["bolgeler"],
                    region_codes=[r["slug"]],
                ),
                rect_path(x, y, 160, 100),
            )
        )
    layers.append({"id": "regions", "z_index": 1, "min_lod": 0.8, "nodes": region_nodes})

    # subregions (pedagogical samples)
    subregions = [
        ("trakya", "Trakya", "Thrace", "marmara", 26.8, 41.3),
        ("canakkale_bogazi_cevre", "Çanakkale Boğazı Çevresi", "Dardanelles Area", "marmara", 26.4, 40.2),
        ("ic_bati_anadolu", "İç Batı Anadolu", "Inner West Anatolia", "ege", 29.5, 38.8),
        ("toroslar", "Toroslar", "Taurus Belt", "akdeniz", 33.0, 37.0),
        ("orta_karadeniz", "Orta Karadeniz", "Central Black Sea", "karadeniz", 36.5, 41.0),
        ("yukari_firat", "Yukarı Fırat", "Upper Euphrates", "dogu_anadolu", 39.5, 39.2),
        ("gap_bolgesi", "GAP Bölgesi", "GAP Region", "guneydogu_anadolu", 39.5, 37.4),
    ]
    sub_nodes = []
    for slug, tr, en, region, lon, lat in subregions:
        x, y = project_lon_lat(lon, lat)
        node_id = nid(prefix, "subregion", slug)
        sub_nodes.append(
            make_node(
                node_id,
                tr,
                en,
                bbox_wh(x, y, 90, 55),
                geo_attrs(
                    "subregion",
                    "geographic_subregion",
                    aliases=[tr],
                    hints=["alt_bolgeler"],
                    region_codes=[region],
                ),
                rect_path(x, y, 90, 55),
            )
        )
    # LOD fix: subregions visible after slight zoom
    layers.append({"id": "subregions", "z_index": 2, "min_lod": 1.2, "nodes": sub_nodes})

    # provinces — use real GeoJSON boundaries when available
    province_geojson = load_province_geojson()
    prov_nodes = []
    center_nodes = []
    for slug, name, region, lon, lat in PROVINCES:
        cx, cy = project_lon_lat(lon, lat)
        node_id = nid(prefix, "province", slug)
        conf = cmap.get(node_id, [])
        # confusable nearby province by region
        if not conf:
            peers = [p for p in PROVINCES if p[2] == region and p[0] != slug]
            if peers:
                conf = [nid(prefix, "province", peers[0][0])]

        # Prefer GeoJSON polygon; fall back to rect if not found
        geo = province_geojson.get(slug)
        if geo:
            path_d = geojson_to_svg_path(geo, tolerance_deg=0.008)
            prov_bbox = _bbox_from_path_d(path_d) if path_d else bbox_wh(cx, cy, 28, 22)
        else:
            path_d = rect_path(cx, cy, 28, 22)
            prov_bbox = bbox_wh(cx, cy, 28, 22)

        prov_nodes.append(
            make_node(
                node_id,
                name,
                name,
                prov_bbox,
                geo_attrs(
                    "province",
                    "admin_province",
                    confusable=conf,
                    aliases=[name, f"{name} ili"],
                    hints=["iller", "turkiye_idari"],
                    region_codes=[region],
                    province_codes=[slug],
                    extra={"capital": True},
                ),
                path_d,
            )
        )
        c_id = nid(prefix, "province_center", f"{slug}_merkez")
        center_nodes.append(
            make_node(
                c_id,
                f"{name} Merkezi",
                f"{name} Center",
                bbox_wh(cx, cy, 10, 10),
                geo_attrs(
                    "province_center",
                    "admin_center",
                    aliases=[f"{name} merkez"],
                    hints=["il_merkezleri"],
                    region_codes=[region],
                    province_codes=[slug],
                ),
                circle_path(cx, cy, 4),
            )
        )
    # LOD fix: provinces visible at default scale=1.0, centers appear on zoom
    layers.append({"id": "provinces", "z_index": 3, "min_lod": 0.8, "nodes": prov_nodes})
    layers.append({"id": "province_centers", "z_index": 4, "min_lod": 2.0, "nodes": center_nodes})

    return _package(
        "turkey_admin",
        prefix,
        {"tr": "Türkiye İdari Haritası", "en": "Turkey Administrative Map"},
        ["cografya", "turkiye", "idari", "iller", "bolgeler"],
        layers,
    )


def build_physical_package(cmap: dict[str, list[str]]) -> dict[str, Any]:
    prefix = "turkey_physical_v1"
    features = [
        ("mountain_range", "toroslar", "Toroslar", "Taurus Mountains", 33.0, 37.0, 200, 40),
        ("mountain_range", "kuzey_anadolu_daglari", "Kuzey Anadolu Dağları", "Northern Anatolian Mts", 36.0, 41.0, 280, 30),
        ("mountain", "agri_dagi", "Ağrı Dağı", "Mount Ararat", 44.3, 39.7, 30, 30),
        ("peak", "agri_zirve", "Ağrı Zirvesi", "Ararat Peak", 44.3, 39.7, 12, 12),
        ("plain", "gediz", "Gediz Ovası", "Gediz Plain", 27.5, 38.6, 50, 30),
        ("plain", "buyuk_menderes", "Büyük Menderes Ovası", "Buyuk Menderes Plain", 27.8, 37.8, 55, 28),
        ("plain", "cukurova", "Çukurova", "Cukurova Plain", 35.3, 36.9, 70, 35),
        ("plateau", "anadolu_platosu", "Anadolu Platosu", "Anatolian Plateau", 33.5, 39.0, 180, 100),
        ("valley", "firat_vadisi", "Fırat Vadisi", "Euphrates Valley", 39.0, 38.5, 40, 80),
        ("strait", "istanbul_bogazi", "İstanbul Boğazı", "Bosphorus", 29.05, 41.1, 18, 40),
        ("strait", "canakkale_bogazi", "Çanakkale Boğazı", "Dardanelles", 26.4, 40.2, 18, 35),
        ("peninsula", "gelibolu", "Gelibolu Yarımadası", "Gallipoli Peninsula", 26.4, 40.35, 25, 40),
        ("cape", "baba_burnu", "Baba Burnu", "Cape Baba", 26.05, 39.48, 12, 12),
        ("gulf", "izmir_korfezi", "İzmir Körfezi", "Gulf of Izmir", 26.9, 38.45, 40, 25),
        ("bay", "antalya_korfezi", "Antalya Körfezi", "Gulf of Antalya", 30.7, 36.7, 45, 25),
        ("island", "gokceada", "Gökçeada", "Gokceada", 25.9, 40.2, 18, 14),
        ("island", "bozcaada", "Bozcaada", "Bozcaada", 26.04, 39.83, 14, 12),
    ]
    by_layer: dict[str, list] = {}
    for layer, slug, tr, en, lon, lat, w, h in features:
        x, y = project_lon_lat(lon, lat)
        node_id = nid(prefix, layer, slug)
        node = make_node(
            node_id,
            tr,
            en,
            bbox_wh(x, y, w, h),
            geo_attrs(
                layer,
                layer,
                confusable=cmap.get(node_id, []),
                aliases=[tr],
                hints=["fiziki_cografya"],
            ),
            rect_path(x, y, w, h) if layer != "peak" else circle_path(x, y, 5),
        )
        by_layer.setdefault(layer, []).append(node)
    layers = [
        {"id": k, "z_index": i, "min_lod": 1.0 if k != "peak" else 2.0, "nodes": v}
        for i, (k, v) in enumerate(by_layer.items())
    ]
    return _package(
        "turkey_physical",
        prefix,
        {"tr": "Türkiye Fiziki Haritası", "en": "Turkey Physical Map"},
        ["cografya", "fiziki", "daglar", "ovalar"],
        layers,
    )


def build_hydro_package(cmap: dict[str, list[str]]) -> dict[str, Any]:
    prefix = "turkey_hydro_v1"
    rivers = [
        ("kizilirmak", "Kızılırmak", "Kizilirmak", [(34.0, 41.2), (34.5, 40.5), (35.0, 39.5), (36.0, 39.0), (36.5, 41.3)]),
        ("sakarya", "Sakarya", "Sakarya", [(30.5, 39.5), (30.6, 40.2), (30.4, 40.8), (30.3, 41.1)]),
        ("yesilirmak", "Yeşilırmak", "Yesilirmak", [(36.5, 40.0), (36.4, 40.5), (36.3, 41.2)]),
        ("firat", "Fırat", "Euphrates", [(39.5, 39.5), (39.2, 38.5), (38.8, 37.5), (38.5, 37.0)]),
        ("dicle", "Dicle", "Tigris", [(41.0, 38.5), (40.8, 37.8), (40.5, 37.2)]),
        ("gediz", "Gediz", "Gediz", [(28.5, 38.7), (27.8, 38.6), (27.2, 38.6)]),
        ("buyuk_menderes", "Büyük Menderes", "Buyuk Menderes", [(29.0, 37.9), (28.2, 37.8), (27.4, 37.6)]),
        ("ergene", "Ergene", "Ergene", [(26.8, 41.2), (27.2, 41.1), (27.6, 41.0)]),
        ("seyhan", "Seyhan", "Seyhan", [(35.3, 38.0), (35.3, 37.5), (35.3, 36.8)]),
        ("ceyhan", "Ceyhan", "Ceyhan", [(36.0, 37.8), (35.8, 37.2), (35.5, 36.8)]),
    ]
    lakes = [
        ("van", "Van Gölü", "Lake Van", 43.3, 38.6, 45, 30),
        ("tuz", "Tuz Gölü", "Lake Tuz", 33.4, 38.7, 40, 28),
        ("beysehir", "Beyşehir Gölü", "Lake Beysehir", 31.5, 37.7, 28, 22),
        ("egirdir", "Eğirdir Gölü", "Lake Egirdir", 30.85, 37.85, 22, 30),
    ]
    dams = [
        ("ataturk", "Atatürk Barajı", "Ataturk Dam", 38.5, 37.5, True),
        ("keban", "Keban Barajı", "Keban Dam", 38.8, 38.8, True),
        ("karakaya", "Karakaya Barajı", "Karakaya Dam", 39.0, 38.4, True),
        ("hirfanli", "Hirfanlı Barajı", "Hirfanli Dam", 33.7, 39.2, False),
    ]
    basins = [
        ("kizilirmak_havzasi", "Kızılırmak Havzası", "Kizilirmak Basin", 35.0, 40.0),
        ("firat_dicle_havzasi", "Fırat-Dicle Havzası", "Euphrates-Tigris Basin", 40.0, 38.0),
        ("marmara_havzasi", "Marmara Havzası", "Marmara Basin", 28.5, 40.8),
    ]

    river_nodes = []
    for slug, tr, en, coords in rivers:
        pts = [project_lon_lat(lo, la) for lo, la in coords]
        xs = [p[0] for p in pts]
        ys = [p[1] for p in pts]
        node_id = nid(prefix, "river", slug)
        river_nodes.append(
            make_node(
                node_id,
                tr,
                en,
                [min(xs) - 4, min(ys) - 4, max(xs) + 4, max(ys) + 4],
                geo_attrs(
                    "river",
                    "river",
                    confusable=cmap.get(node_id, []),
                    aliases=[tr, f"{tr} Nehri"],
                    hints=["akarsular", "hidrografya"],
                ),
                line_path(pts),
            )
        )
    # tributaries
    trib = make_node(
        nid(prefix, "tributary", "delice"),
        "Delice",
        "Delice",
        bbox_wh(*project_lon_lat(34.5, 40.0), 40, 20),
        geo_attrs("tributary", "tributary", aliases=["Delice"], hints=["kollar"], province_codes=["yozgat"]),
        line_path([project_lon_lat(34.2, 39.8), project_lon_lat(34.8, 40.2)]),
    )

    lake_nodes = []
    for slug, tr, en, lon, lat, w, h in lakes:
        x, y = project_lon_lat(lon, lat)
        node_id = nid(prefix, "lake", slug)
        lake_nodes.append(
            make_node(
                node_id,
                tr,
                en,
                bbox_wh(x, y, w, h),
                geo_attrs(
                    "lake",
                    "lake",
                    confusable=cmap.get(node_id, []),
                    aliases=[tr],
                    hints=["goller"],
                ),
                rect_path(x, y, w, h),
            )
        )

    dam_nodes = []
    for slug, tr, en, lon, lat, gap in dams:
        x, y = project_lon_lat(lon, lat)
        node_id = nid(prefix, "dam", slug)
        dam_nodes.append(
            make_node(
                node_id,
                tr,
                en,
                bbox_wh(x, y, 16, 16),
                geo_attrs(
                    "dam",
                    "dam",
                    aliases=[tr],
                    hints=["barajlar", "gap"] if gap else ["barajlar"],
                    extra={"gap_project": gap},
                ),
                circle_path(x, y, 7),
            )
        )

    waterfall = make_node(
        nid(prefix, "waterfall", "dudeniz"),
        "Düden Şelalesi",
        "Duden Falls",
        bbox_wh(*project_lon_lat(30.7, 36.9), 12, 12),
        geo_attrs("waterfall", "waterfall", aliases=["Düden"], hints=["selaleler"]),
        circle_path(*project_lon_lat(30.7, 36.9), 5),
    )
    spring = make_node(
        nid(prefix, "spring", "kirkgoz"),
        "Kırkgöz Kaynakları",
        "Kirkgöz Springs",
        bbox_wh(*project_lon_lat(30.6, 37.1), 12, 12),
        geo_attrs("spring", "spring", aliases=["Kırkgöz"], hints=["kaynaklar"]),
        circle_path(*project_lon_lat(30.6, 37.1), 5),
    )

    basin_nodes = []
    for slug, tr, en, lon, lat in basins:
        x, y = project_lon_lat(lon, lat)
        basin_nodes.append(
            make_node(
                nid(prefix, "basin", slug),
                tr,
                en,
                bbox_wh(x, y, 120, 80),
                geo_attrs("basin", "drainage_basin", aliases=[tr], hints=["havzalar"]),
                rect_path(x, y, 120, 80),
            )
        )

    layers = [
        {"id": "basins", "z_index": 0, "min_lod": 0.8, "nodes": basin_nodes},
        {"id": "rivers", "z_index": 1, "min_lod": 1.0, "nodes": river_nodes},
        {"id": "tributaries", "z_index": 2, "min_lod": 1.8, "nodes": [trib]},
        {"id": "lakes", "z_index": 3, "min_lod": 1.0, "nodes": lake_nodes},
        {"id": "dams", "z_index": 4, "min_lod": 1.5, "nodes": dam_nodes},
        {"id": "waterfalls", "z_index": 5, "min_lod": 2.0, "nodes": [waterfall]},
        {"id": "springs", "z_index": 6, "min_lod": 2.0, "nodes": [spring]},
    ]
    return _package(
        "turkey_hydrography",
        prefix,
        {"tr": "Türkiye Hidrografya Haritası", "en": "Turkey Hydrography Map"},
        ["cografya", "hidrografya", "nehirler", "goller", "barajlar"],
        layers,
    )


def _zone_package(
    uri_name: str,
    prefix: str,
    title: dict[str, str],
    tags: list[str],
    layer_type: str,
    zones: list[tuple[str, str, str, float, float, float, float]],
    cmap: dict[str, list[str]],
    hint: str,
) -> dict[str, Any]:
    nodes = []
    for slug, tr, en, lon, lat, w, h in zones:
        x, y = project_lon_lat(lon, lat)
        node_id = nid(prefix, layer_type, slug)
        nodes.append(
            make_node(
                node_id,
                tr,
                en,
                bbox_wh(x, y, w, h),
                geo_attrs(
                    layer_type,
                    layer_type,
                    confusable=cmap.get(node_id, []),
                    aliases=[tr],
                    hints=[hint],
                ),
                rect_path(x, y, w, h),
            )
        )
    return _package(
        uri_name,
        prefix,
        title,
        tags,
        [{"id": layer_type + "s", "z_index": 0, "min_lod": 0.8, "nodes": nodes}],
    )


def build_climate_package(cmap: dict[str, list[str]]) -> dict[str, Any]:
    prefix = "turkey_climate_v1"
    climate = [
        ("karadeniz", "Karadeniz İklimi", "Black Sea Climate", 36.0, 41.0, 220, 60),
        ("akdeniz", "Akdeniz İklimi", "Mediterranean Climate", 32.0, 36.9, 260, 55),
        ("karasal", "Karasal İklim", "Continental Climate", 34.0, 39.2, 280, 120),
        ("marmara_gecis", "Marmara Geçiş İklimi", "Marmara Transitional", 28.5, 40.8, 120, 70),
    ]
    precip = [
        ("yuksek_yagis_karadeniz", "Yüksek Yağış — Karadeniz", "High Precip Black Sea", 39.0, 41.0, 160, 40),
        ("dusuk_yagis_ic_anadolu", "Düşük Yağış — İç Anadolu", "Low Precip Central", 33.5, 39.0, 160, 90),
    ]
    temp = [
        ("sicak_akdeniz", "Sıcak — Akdeniz", "Warm Mediterranean", 32.0, 36.9, 200, 45),
        ("soguk_dogu", "Soğuk — Doğu Anadolu", "Cold East", 41.0, 39.5, 160, 90),
    ]
    wind = [
        ("poyraz", "Poyraz", "Poyraz Wind", 29.0, 41.0, 60, 40),
        ("lodos", "Lodos", "Lodos Wind", 28.0, 39.0, 60, 40),
    ]
    layers = []
    for layer_type, items, z, lod in [
        ("climate_zone", climate, 0, 0.8),
        ("precip_zone", precip, 1, 1.2),
        ("temp_zone", temp, 2, 1.2),
        ("wind_system", wind, 3, 1.5),
    ]:
        nodes = []
        for slug, tr, en, lon, lat, w, h in items:
            x, y = project_lon_lat(lon, lat)
            node_id = nid(prefix, layer_type, slug)
            nodes.append(
                make_node(
                    node_id,
                    tr,
                    en,
                    bbox_wh(x, y, w, h),
                    geo_attrs(
                        layer_type,
                        layer_type,
                        confusable=cmap.get(node_id, []),
                        aliases=[tr],
                        hints=["iklim"],
                    ),
                    rect_path(x, y, w, h),
                )
            )
        layers.append({"id": layer_type + "s", "z_index": z, "min_lod": lod, "nodes": nodes})
    return _package(
        "turkey_climate",
        prefix,
        {"tr": "Türkiye İklim Haritası", "en": "Turkey Climate Map"},
        ["cografya", "iklim", "yagis"],
        layers,
    )


def build_vegetation_package(cmap: dict[str, list[str]]) -> dict[str, Any]:
    zones = [
        ("forest", "karadeniz_ormani", "Karadeniz Ormanları", "Black Sea Forests", 37.0, 41.0, 200, 50),
        ("maquis", "akdeniz_maki", "Akdeniz Makisi", "Mediterranean Maquis", 32.0, 36.9, 220, 45),
        ("steppe", "ic_anadolu_bozkir", "İç Anadolu Bozkırı", "Central Anatolian Steppe", 33.5, 39.0, 200, 100),
        ("meadow", "yayla_cayirlari", "Yayla Çayırları", "Alpine Meadows", 41.0, 40.5, 100, 50),
        ("endemic_zone", "toros_endemik", "Toros Endemik Bölgesi", "Taurus Endemic Zone", 33.0, 37.0, 120, 40),
    ]
    by_layer: dict[str, list] = {}
    prefix = "turkey_vegetation_v1"
    for layer, slug, tr, en, lon, lat, w, h in zones:
        x, y = project_lon_lat(lon, lat)
        node_id = nid(prefix, layer, slug)
        by_layer.setdefault(layer, []).append(
            make_node(
                node_id,
                tr,
                en,
                bbox_wh(x, y, w, h),
                geo_attrs(layer, layer, confusable=cmap.get(node_id, []), aliases=[tr], hints=["bitki_ortusu"]),
                rect_path(x, y, w, h),
            )
        )
    layers = [{"id": k, "z_index": i, "min_lod": 0.9, "nodes": v} for i, (k, v) in enumerate(by_layer.items())]
    return _package(
        "turkey_vegetation",
        prefix,
        {"tr": "Türkiye Bitki Örtüsü", "en": "Turkey Vegetation"},
        ["cografya", "bitki", "orman"],
        layers,
    )


def build_agriculture_package(cmap: dict[str, list[str]]) -> dict[str, Any]:
    prefix = "turkey_agriculture_v1"
    items = [
        ("crop_region", "bugday_ic_anadolu", "Buğday — İç Anadolu", "Wheat Central Anatolia", 33.5, 39.0, 160, 90),
        ("crop_region", "pamuk_cukurova", "Pamuk — Çukurova", "Cotton Cukurova", 35.3, 36.9, 70, 35),
        ("crop_region", "findik_karadeniz", "Fındık — Karadeniz", "Hazelnut Black Sea", 38.0, 41.0, 160, 40),
        ("crop_region", "cay_dogu_karadeniz", "Çay — Doğu Karadeniz", "Tea East Black Sea", 40.5, 41.0, 80, 35),
        ("irrigation_area", "gap_sulama", "GAP Sulama Alanları", "GAP Irrigation", 39.5, 37.4, 140, 70),
        ("livestock_region", "koyunculuk_ic_anadolu", "Koyunculuk — İç Anadolu", "Sheep Central", 34.0, 39.0, 140, 80),
        ("livestock_region", "buyukbas_marmara", "Büyükbaş — Marmara", "Cattle Marmara", 28.5, 40.8, 100, 60),
    ]
    by_layer: dict[str, list] = {}
    for layer, slug, tr, en, lon, lat, w, h in items:
        x, y = project_lon_lat(lon, lat)
        node_id = nid(prefix, layer, slug)
        by_layer.setdefault(layer, []).append(
            make_node(
                node_id,
                tr,
                en,
                bbox_wh(x, y, w, h),
                geo_attrs(layer, layer, confusable=cmap.get(node_id, []), aliases=[tr], hints=["tarim"]),
                rect_path(x, y, w, h),
            )
        )
    layers = [{"id": k, "z_index": i, "min_lod": 1.0, "nodes": v} for i, (k, v) in enumerate(by_layer.items())]
    return _package(
        "turkey_agriculture",
        prefix,
        {"tr": "Türkiye Tarım Haritası", "en": "Turkey Agriculture Map"},
        ["cografya", "tarim", "hayvancilik"],
        layers,
    )


def build_minerals_package(cmap: dict[str, list[str]]) -> dict[str, Any]:
    prefix = "turkey_minerals_v1"
    deposits = [
        ("bor_eskisehir", "Bor — Eskişehir", "Boron Eskisehir", 30.5, 39.8, "eskisehir"),
        ("bor_kutahya", "Bor — Kütahya", "Boron Kutahya", 29.9, 39.4, "kutahya"),
        ("komur_zonguldak", "Kömür — Zonguldak", "Coal Zonguldak", 31.8, 41.5, "zonguldak"),
        ("demir_divrigi", "Demir — Divriği", "Iron Divrigi", 37.9, 39.4, "sivas"),
        ("bakir_murgul", "Bakır — Murgul", "Copper Murgul", 41.6, 41.3, "artvin"),
        ("krom_elazig", "Krom — Elazığ", "Chrome Elazig", 39.2, 38.7, "elazig"),
        ("petrol_batman", "Petrol — Batman", "Oil Batman", 41.1, 37.9, "batman"),
        ("dogalgaz_trakya", "Doğalgaz — Trakya", "Natural Gas Thrace", 27.0, 41.3, "kirklareli"),
        ("altin_bergama", "Altın — Bergama", "Gold Bergama", 27.2, 39.1, "izmir"),
        ("gumus_gumushane", "Gümüş — Gümüşhane", "Silver Gumushane", 39.5, 40.5, "gumushane"),
        ("mermer_afyon", "Mermer — Afyon", "Marble Afyon", 30.5, 38.8, "afyonkarahisar"),
        ("pomza_nevsehir", "Pomza — Nevşehir", "Pumice Nevsehir", 34.7, 38.6, "nevsehir"),
    ]
    nodes = []
    for slug, tr, en, lon, lat, prov in deposits:
        x, y = project_lon_lat(lon, lat)
        node_id = nid(prefix, "mineral_deposit", slug)
        nodes.append(
            make_node(
                node_id,
                tr,
                en,
                bbox_wh(x, y, 14, 14),
                geo_attrs(
                    "mineral_deposit",
                    "mineral_deposit",
                    confusable=cmap.get(node_id, []),
                    aliases=[tr.split(" — ")[0], tr],
                    hints=["madenler"],
                    province_codes=[prov],
                ),
                circle_path(x, y, 6),
            )
        )
    return _package(
        "turkey_minerals",
        prefix,
        {"tr": "Türkiye Maden Haritası", "en": "Turkey Minerals Map"},
        ["cografya", "madenler", "bor", "komur"],
        [{"id": "mineral_deposits", "z_index": 0, "min_lod": 1.0, "nodes": nodes}],
    )


def build_energy_package(cmap: dict[str, list[str]]) -> dict[str, Any]:
    prefix = "turkey_energy_v1"
    plants = [
        ("hes", "ataturk_hes", "Atatürk HES", "Ataturk HEP", 38.5, 37.5),
        ("hes", "keban_hes", "Keban HES", "Keban HEP", 38.8, 38.8),
        ("res", "canakkale_res", "Çanakkale RES", "Canakkale Wind", 26.5, 40.1),
        ("res", "izmir_res", "İzmir RES", "Izmir Wind", 27.0, 38.5),
        ("ges", "karapinar_ges", "Karapınar GES", "Karapinar Solar", 33.6, 37.7),
        ("jes", "buyuk_menderes_jes", "Büyük Menderes JES", "Buyuk Menderes Geo", 28.5, 37.9),
        ("thermal", " Soma_termik", "Soma Termik", "Soma Thermal", 27.6, 39.2),
        ("nuclear", "akkuyu_nukleer", "Akkuyu Nükleer", "Akkuyu Nuclear", 33.5, 36.1),
    ]
    # fix thermal slug
    plants = [
        ("hes", "ataturk_hes", "Atatürk HES", "Ataturk HEP", 38.5, 37.5),
        ("hes", "keban_hes", "Keban HES", "Keban HEP", 38.8, 38.8),
        ("res", "canakkale_res", "Çanakkale RES", "Canakkale Wind", 26.5, 40.1),
        ("res", "izmir_res", "İzmir RES", "Izmir Wind", 27.0, 38.5),
        ("ges", "karapinar_ges", "Karapınar GES", "Karapinar Solar", 33.6, 37.7),
        ("jes", "buyuk_menderes_jes", "Büyük Menderes JES", "Buyuk Menderes Geo", 28.5, 37.9),
        ("thermal", "soma_termik", "Soma Termik", "Soma Thermal", 27.6, 39.2),
        ("nuclear", "akkuyu_nukleer", "Akkuyu Nükleer", "Akkuyu Nuclear", 33.5, 36.1),
    ]
    by_layer: dict[str, list] = {}
    for layer, slug, tr, en, lon, lat in plants:
        x, y = project_lon_lat(lon, lat)
        node_id = nid(prefix, layer, slug)
        by_layer.setdefault(layer, []).append(
            make_node(
                node_id,
                tr,
                en,
                bbox_wh(x, y, 14, 14),
                geo_attrs(layer, layer, confusable=cmap.get(node_id, []), aliases=[tr], hints=["enerji"]),
                circle_path(x, y, 6),
            )
        )
    layers = [{"id": k, "z_index": i, "min_lod": 1.2, "nodes": v} for i, (k, v) in enumerate(by_layer.items())]
    return _package(
        "turkey_energy",
        prefix,
        {"tr": "Türkiye Enerji Haritası", "en": "Turkey Energy Map"},
        ["cografya", "enerji", "hes", "res", "ges"],
        layers,
    )


def build_population_package(cmap: dict[str, list[str]]) -> dict[str, Any]:
    prefix = "turkey_population_v1"
    items = [
        ("density_zone", "yogun_marmara", "Yoğun Nüfus — Marmara", "Dense Marmara", 28.8, 40.9, 100, 70),
        ("density_zone", "seyrek_dogu", "Seyrek Nüfus — Doğu", "Sparse East", 41.5, 39.5, 140, 90),
        ("metro_area", "istanbul_metro", "İstanbul Metropol", "Istanbul Metro", 28.98, 41.01, 50, 35),
        ("metro_area", "ankara_metro", "Ankara Metropol", "Ankara Metro", 32.85, 39.93, 40, 30),
        ("major_city", "izmir_kent", "İzmir", "Izmir", 27.14, 38.42, 16, 16),
        ("major_city", "bursa_kent", "Bursa", "Bursa", 29.06, 40.19, 16, 16),
        ("major_city", "antalya_kent", "Antalya", "Antalya", 30.71, 36.90, 16, 16),
    ]
    by_layer: dict[str, list] = {}
    for layer, slug, tr, en, lon, lat, w, h in items:
        x, y = project_lon_lat(lon, lat)
        node_id = nid(prefix, layer, slug)
        by_layer.setdefault(layer, []).append(
            make_node(
                node_id,
                tr,
                en,
                bbox_wh(x, y, w, h),
                geo_attrs(layer, layer, confusable=cmap.get(node_id, []), aliases=[tr], hints=["nufus"]),
                rect_path(x, y, w, h) if layer != "major_city" else circle_path(x, y, 6),
            )
        )
    layers = [{"id": k, "z_index": i, "min_lod": 1.0, "nodes": v} for i, (k, v) in enumerate(by_layer.items())]
    return _package(
        "turkey_population",
        prefix,
        {"tr": "Türkiye Nüfus Haritası", "en": "Turkey Population Map"},
        ["cografya", "nufus", "metropol"],
        layers,
    )


def build_transport_package(cmap: dict[str, list[str]]) -> dict[str, Any]:
    prefix = "turkey_transport_v1"
    highways = [
        ("o4", "O-4 Anadolu Otoyolu", "O-4 Anatolian Highway", [(29.0, 40.8), (30.5, 40.7), (32.5, 39.9)]),
        ("o3", "O-3 Avrupa Otoyolu", "O-3 European Highway", [(26.6, 41.5), (28.5, 41.0)]),
    ]
    railways = [
        ("ankara_istanbul_demiryolu", "Ankara–İstanbul Demiryolu", "Ankara-Istanbul Rail", [(28.98, 41.01), (30.5, 40.5), (32.85, 39.93)]),
    ]
    ports = [
        ("haydarpasa", "Haydarpaşa Limanı", "Haydarpasa Port", 29.02, 41.00),
        ("mersin_liman", "Mersin Limanı", "Mersin Port", 34.64, 36.80),
        ("izmir_liman", "İzmir Limanı", "Izmir Port", 27.14, 38.42),
    ]
    airports = [
        ("ist", "İstanbul Havalimanı", "Istanbul Airport", 28.75, 41.27),
        ("esb", "Esenboğa", "Esenboga Airport", 33.0, 40.13),
        ("ayt", "Antalya Havalimanı", "Antalya Airport", 30.79, 36.90),
    ]
    layers = []
    hw_nodes = []
    for slug, tr, en, coords in highways:
        pts = [project_lon_lat(a, b) for a, b in coords]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        node_id = nid(prefix, "highway", slug)
        hw_nodes.append(
            make_node(
                node_id,
                tr,
                en,
                [min(xs) - 3, min(ys) - 3, max(xs) + 3, max(ys) + 3],
                geo_attrs("highway", "highway", aliases=[tr], hints=["ulasim"]),
                line_path(pts),
            )
        )
    layers.append({"id": "highways", "z_index": 0, "min_lod": 1.0, "nodes": hw_nodes})

    rail_nodes = []
    for slug, tr, en, coords in railways:
        pts = [project_lon_lat(a, b) for a, b in coords]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        rail_nodes.append(
            make_node(
                nid(prefix, "railway", slug),
                tr,
                en,
                [min(xs) - 3, min(ys) - 3, max(xs) + 3, max(ys) + 3],
                geo_attrs("railway", "railway", aliases=[tr], hints=["ulasim"]),
                line_path(pts),
            )
        )
    layers.append({"id": "railways", "z_index": 1, "min_lod": 1.2, "nodes": rail_nodes})

    port_nodes = []
    for slug, tr, en, lon, lat in ports:
        x, y = project_lon_lat(lon, lat)
        port_nodes.append(
            make_node(
                nid(prefix, "port", slug),
                tr,
                en,
                bbox_wh(x, y, 12, 12),
                geo_attrs("port", "port", aliases=[tr], hints=["ulasim", "limanlar"]),
                circle_path(x, y, 5),
            )
        )
    layers.append({"id": "ports", "z_index": 2, "min_lod": 1.5, "nodes": port_nodes})

    ap_nodes = []
    for slug, tr, en, lon, lat in airports:
        x, y = project_lon_lat(lon, lat)
        ap_nodes.append(
            make_node(
                nid(prefix, "airport", slug),
                tr,
                en,
                bbox_wh(x, y, 12, 12),
                geo_attrs("airport", "airport", aliases=[tr], hints=["ulasim", "havalimanlari"]),
                circle_path(x, y, 5),
            )
        )
    layers.append({"id": "airports", "z_index": 3, "min_lod": 1.5, "nodes": ap_nodes})

    return _package(
        "turkey_transport",
        prefix,
        {"tr": "Türkiye Ulaşım Haritası", "en": "Turkey Transport Map"},
        ["cografya", "ulasim", "otoyol", "liman"],
        layers,
    )


def build_tourism_package(cmap: dict[str, list[str]]) -> dict[str, Any]:
    prefix = "turkey_tourism_v1"
    items = [
        ("unesco", "cappadocia", "Kapadokya", "Cappadocia", 34.8, 38.6),
        ("unesco", "pamukkale", "Pamukkale", "Pamukkale", 29.1, 37.9),
        ("unesco", "troy", "Troya", "Troy", 26.2, 39.96),
        ("unesco", "gobeklitepe", "Göbeklitepe", "Gobekli Tepe", 38.92, 37.22),
        ("national_park", "uludag", "Uludağ Milli Parkı", "Uludag NP", 29.15, 40.07),
        ("national_park", "kazdagi", "Kazdağı Milli Parkı", "Kazdag NP", 26.8, 39.7),
        ("tourism_center", "antalya_turizm", "Antalya Turizm Merkezi", "Antalya Tourism", 30.71, 36.90),
        ("tourism_center", "bodrum", "Bodrum", "Bodrum", 27.43, 37.03),
    ]
    by_layer: dict[str, list] = {}
    for layer, slug, tr, en, lon, lat in items:
        x, y = project_lon_lat(lon, lat)
        node_id = nid(prefix, layer, slug)
        by_layer.setdefault(layer, []).append(
            make_node(
                node_id,
                tr,
                en,
                bbox_wh(x, y, 14, 14),
                geo_attrs(layer, layer, confusable=cmap.get(node_id, []), aliases=[tr], hints=["turizm"]),
                circle_path(x, y, 6),
            )
        )
    layers = [{"id": k, "z_index": i, "min_lod": 1.2, "nodes": v} for i, (k, v) in enumerate(by_layer.items())]
    return _package(
        "turkey_tourism",
        prefix,
        {"tr": "Türkiye Turizm Haritası", "en": "Turkey Tourism Map"},
        ["cografya", "turizm", "unesco"],
        layers,
    )


def build_hazards_package(cmap: dict[str, list[str]]) -> dict[str, Any]:
    prefix = "turkey_hazards_v1"
    faults = [
        ("kuzey_anadolu", "Kuzey Anadolu Fay Hattı", "North Anatolian Fault", [(27.0, 40.7), (30.0, 40.8), (33.0, 40.9), (36.0, 40.7), (40.0, 40.5)]),
        ("dogu_anadolu", "Doğu Anadolu Fay Hattı", "East Anatolian Fault", [(36.5, 37.5), (38.0, 38.0), (40.0, 38.8), (41.5, 39.5)]),
    ]
    eq_zones = [
        ("birinci_derece", "1. Derece Deprem Bölgesi", "Highest Seismic Zone", 29.0, 40.8, 160, 70),
        ("dogu_yuksek_risk", "Doğu Yüksek Risk", "East High Risk", 40.5, 39.0, 140, 90),
    ]
    other = [
        ("landslide", "karadeniz_heyelan", "Karadeniz Heyelan Bölgesi", "Black Sea Landslide", 38.0, 41.0, 120, 40),
        ("flood", "cakurova_sel", "Çukurova Sel Riski", "Cukurova Flood", 35.3, 36.9, 70, 35),
        ("avalanche", "dogu_cig", "Doğu Anadolu Çığ Bölgesi", "East Avalanche", 41.5, 39.8, 100, 60),
    ]
    layers = []
    fault_nodes = []
    for slug, tr, en, coords in faults:
        pts = [project_lon_lat(a, b) for a, b in coords]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        node_id = nid(prefix, "fault", slug)
        fault_nodes.append(
            make_node(
                node_id,
                tr,
                en,
                [min(xs) - 4, min(ys) - 4, max(xs) + 4, max(ys) + 4],
                geo_attrs(
                    "fault",
                    "fault",
                    confusable=cmap.get(node_id, []),
                    aliases=[tr, "KAF" if "kuzey" in slug else "DAF"],
                    hints=["afet", "deprem", "fay"],
                ),
                line_path(pts),
            )
        )
    layers.append({"id": "faults", "z_index": 0, "min_lod": 1.0, "nodes": fault_nodes})

    eq_nodes = []
    for slug, tr, en, lon, lat, w, h in eq_zones:
        x, y = project_lon_lat(lon, lat)
        eq_nodes.append(
            make_node(
                nid(prefix, "earthquake_zone", slug),
                tr,
                en,
                bbox_wh(x, y, w, h),
                geo_attrs("earthquake_zone", "earthquake_zone", aliases=[tr], hints=["afet", "deprem"]),
                rect_path(x, y, w, h),
            )
        )
    layers.append({"id": "earthquake_zones", "z_index": 1, "min_lod": 0.9, "nodes": eq_nodes})

    by_layer: dict[str, list] = {}
    for layer, slug, tr, en, lon, lat, w, h in other:
        x, y = project_lon_lat(lon, lat)
        by_layer.setdefault(layer, []).append(
            make_node(
                nid(prefix, layer, slug),
                tr,
                en,
                bbox_wh(x, y, w, h),
                geo_attrs(layer, layer, aliases=[tr], hints=["afet"]),
                rect_path(x, y, w, h),
            )
        )
    for i, (k, v) in enumerate(by_layer.items(), start=2):
        layers.append({"id": k + "s", "z_index": i, "min_lod": 1.2, "nodes": v})

    return _package(
        "turkey_hazards",
        prefix,
        {"tr": "Türkiye Afet Haritası", "en": "Turkey Hazard Map"},
        ["cografya", "afet", "deprem", "fay"],
        layers,
    )


def _package(
    uri_name: str,
    prefix: str,
    title: dict[str, str],
    tags: list[str],
    layers_with_paths: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build manifest + svg from layers that include path_d on nodes."""
    manifest_layers = []
    svg_parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {TURKEY_VIEWPORT["width"]} {TURKEY_VIEWPORT["height"]}">',
        '<rect width="100%" height="100%" fill="#F8FAFC"/>',
    ]
    for layer in layers_with_paths:
        m_nodes = []
        for node in layer["nodes"]:
            path_d = node.pop("path_d")
            svg_parts.append(
                f'<path id="{node["id"]}" d="{path_d}" fill="#CBD5E1" stroke="#334155" stroke-width="1.2"/>'
            )
            m_nodes.append(node)
        manifest_layers.append(
            {
                "id": layer["id"],
                "z_index": layer["z_index"],
                "min_lod": layer["min_lod"],
                "nodes": m_nodes,
            }
        )
    svg_parts.append("</svg>")
    return {
        "uri_name": uri_name,
        "prefix": prefix,
        "manifest": {
            "schema_version": "1.0",
            "asset_id": f"studyos://assets/geography/{uri_name}/v1",
            "version": "1.0.0",
            "domain": "geography",
            "format": "svg",
            "title": title,
            "viewport": TURKEY_VIEWPORT,
            "layers": manifest_layers,
            "tags": tags,
            "license_type": "studyos_core",
            "tenant_id": None,
        },
        "svg": "\n".join(svg_parts),
    }


def build_all_package_specs() -> list[dict[str, Any]]:
    cmap = confusable_map()
    return [
        build_admin_package(cmap),
        build_physical_package(cmap),
        build_hydro_package(cmap),
        build_climate_package(cmap),
        build_vegetation_package(cmap),
        build_agriculture_package(cmap),
        build_minerals_package(cmap),
        build_energy_package(cmap),
        build_population_package(cmap),
        build_transport_package(cmap),
        build_tourism_package(cmap),
        build_hazards_package(cmap),
    ]


def write_ontology_files(root: Path | None = None) -> Path:
    root = root or DATA_ROOT
    ontology = root / "ontology"
    ontology.mkdir(parents=True, exist_ok=True)

    packages = build_all_package_specs()
    catalog: list[dict[str, Any]] = []
    for pkg in packages:
        for layer in pkg["manifest"]["layers"]:
            for node in layer["nodes"]:
                catalog.append(
                    {
                        "asset_id": pkg["manifest"]["asset_id"],
                        "node_id": node["id"],
                        "name": node["name"],
                        "layer_type": node["attributes"]["layer_type"],
                        "attributes": node["attributes"],
                    }
                )

    (ontology / "node_catalog.json").write_text(
        json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (ontology / "adjacency.json").write_text(
        json.dumps(adjacency_catalog(), ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (ontology / "confusable_pairs.json").write_text(
        json.dumps(
            [{"a": a, "b": b} for a, b in CONFUSABLE_PAIRS],
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    cross_links = {
        "province_to_minerals": {
            "eskisehir": ["turkey_minerals_v1::mineral_deposit::bor_eskisehir"],
            "zonguldak": ["turkey_minerals_v1::mineral_deposit::komur_zonguldak"],
            "batman": ["turkey_minerals_v1::mineral_deposit::petrol_batman"],
        },
        "river_to_basin": {
            "turkey_hydro_v1::river::kizilirmak": ["turkey_hydro_v1::basin::kizilirmak_havzasi"],
            "turkey_hydro_v1::river::firat": ["turkey_hydro_v1::basin::firat_dicle_havzasi"],
        },
        "fault_to_provinces": {
            "turkey_hazards_v1::fault::kuzey_anadolu": ["sakarya", "kocaeli", "duzce", "bolu", "erzincan"],
        },
    }
    (ontology / "cross_links.json").write_text(
        json.dumps(cross_links, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (root / "sources" / "LICENSE.txt").parent.mkdir(parents=True, exist_ok=True)
    (root / "sources" / "LICENSE.txt").write_text(
        "StudyOS educational geometries derived from approximate public centroids.\n"
        "Pedagogical simplification for StudyOS EAE. License: studyos_core.\n",
        encoding="utf-8",
    )
    return ontology


def load_ontology_bundle() -> dict[str, Any]:
    ontology = DATA_ROOT / "ontology"
    return {
        "node_catalog": json.loads((ontology / "node_catalog.json").read_text(encoding="utf-8")),
        "adjacency": json.loads((ontology / "adjacency.json").read_text(encoding="utf-8")),
        "confusable_pairs": json.loads((ontology / "confusable_pairs.json").read_text(encoding="utf-8")),
        "cross_links": json.loads((ontology / "cross_links.json").read_text(encoding="utf-8")),
    }
