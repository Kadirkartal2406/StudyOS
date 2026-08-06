"""
StudyOS Educational Asset Engine (EAE) — Contract Constants
"""

import re
from enum import StrEnum

# URI Pattern: studyos://assets/<domain>/<name>/v<major> (e.g. studyos://assets/geography/turkey_admin/v1)
ASSET_URI_PATTERN = re.compile(
    r"^studyos://assets/[a-z0-9_]+/[a-z0-9_]+/(v[0-9]+|inst_[a-z0-9_]+)$"
)

# Node ID Pattern: <asset_id_prefix>::<layer_type>::<component_identifier>
# e.g. turkey_admin_v1::province::konya
NODE_ID_PATTERN = re.compile(
    r"^[a-z0-9_]+::[a-z0-9_]+::[a-z0-9_]+$"
)

# SemVer Pattern: vX.Y.Z
SEMVER_PATTERN = re.compile(
    r"^v?(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?$"
)


class AssetFormat(StrEnum):
    SVG = "svg"
    PDF = "pdf"
    PNG = "png"
    WEBP = "webp"
    GLTF = "gltf"
    USDZ = "usdz"
    LOTTIE = "lottie"


SUPPORTED_ASSET_FORMATS = tuple(f.value for f in AssetFormat)
DAY_ONE_FORMAT = AssetFormat.SVG

ALLOWED_DOMAINS = (
    "geography",
    "medicine",
    "biology",
    "chemistry",
    "physics",
    "mathematics",
    "history",
    "language",
    "engineering",
    "general",
)

# Geography EAE layer types (middle segment of node IDs)
GEOGRAPHY_LAYER_TYPES = frozenset(
    {
        # admin
        "country",
        "region",
        "subregion",
        "province",
        "province_center",
        # physical
        "mountain",
        "mountain_range",
        "peak",
        "plain",
        "plateau",
        "valley",
        "strait",
        "peninsula",
        "cape",
        "gulf",
        "bay",
        "island",
        # hydrography
        "river",
        "tributary",
        "lake",
        "dam",
        "waterfall",
        "spring",
        "basin",
        # climate / vegetation / agriculture
        "climate_zone",
        "precip_zone",
        "temp_zone",
        "wind_system",
        "forest",
        "maquis",
        "steppe",
        "meadow",
        "endemic_zone",
        "crop_region",
        "irrigation_area",
        "livestock_region",
        # minerals / energy
        "mineral_deposit",
        "hes",
        "res",
        "ges",
        "jes",
        "thermal",
        "nuclear",
        # population / transport / tourism / hazards
        "density_zone",
        "metro_area",
        "major_city",
        "highway",
        "railway",
        "port",
        "airport",
        "unesco",
        "national_park",
        "tourism_center",
        "earthquake_zone",
        "fault",
        "landslide",
        "flood",
        "avalanche",
    }
)

GEOGRAPHY_REQUIRED_ATTRIBUTE_KEYS = frozenset(
    {
        "layer_type",
        "feature_class",
        "confusable_with",
        "qie_aliases",
        "evidence_topic_hints",
    }
)

TURKEY_GEOGRAPHY_PACKAGES = (
    "turkey_admin",
    "turkey_physical",
    "turkey_hydrography",
    "turkey_climate",
    "turkey_vegetation",
    "turkey_agriculture",
    "turkey_minerals",
    "turkey_energy",
    "turkey_population",
    "turkey_transport",
    "turkey_tourism",
    "turkey_hazards",
)
