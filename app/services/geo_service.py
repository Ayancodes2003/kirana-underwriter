from __future__ import annotations

import os
from functools import lru_cache

import requests

OVERPASS_URL = os.getenv("OVERPASS_URL", "https://overpass-api.de/api/interpreter")
DEFAULT_RADIUS_METERS = int(os.getenv("GEO_RADIUS_METERS", "1000"))
ROAD_SCAN_RADIUS_METERS = int(os.getenv("ROAD_SCAN_RADIUS_METERS", "300"))
OVERPASS_TIMEOUT_SECONDS = int(os.getenv("OVERPASS_TIMEOUT_SECONDS", "12"))


def _neutral_geo_features() -> dict:
    return {
        "poi_density": 8,
        "competition_density": 4,
        "footfall_score": 0.5,
        "is_fallback": True,
    }


def _build_poi_query(latitude: float, longitude: float, radius_meters: int) -> str:
    return f"""
    [out:json][timeout:25];
    (
      node(around:{radius_meters},{latitude},{longitude})["shop"];
      way(around:{radius_meters},{latitude},{longitude})["shop"];
      relation(around:{radius_meters},{latitude},{longitude})["shop"];

      node(around:{radius_meters},{latitude},{longitude})["amenity"="school"];
      way(around:{radius_meters},{latitude},{longitude})["amenity"="school"];
      relation(around:{radius_meters},{latitude},{longitude})["amenity"="school"];

      node(around:{radius_meters},{latitude},{longitude})["office"];
      way(around:{radius_meters},{latitude},{longitude})["office"];
      relation(around:{radius_meters},{latitude},{longitude})["office"];

      node(around:{radius_meters},{latitude},{longitude})["public_transport"];
      way(around:{radius_meters},{latitude},{longitude})["public_transport"];
      relation(around:{radius_meters},{latitude},{longitude})["public_transport"];

      node(around:{radius_meters},{latitude},{longitude})["railway"="station"];
      node(around:{radius_meters},{latitude},{longitude})["amenity"="bus_station"];
    );
    out tags center;
    """


def _build_competition_query(latitude: float, longitude: float, radius_meters: int) -> str:
    return f"""
    [out:json][timeout:25];
    (
      node(around:{radius_meters},{latitude},{longitude})["shop"~"^(supermarket|convenience|grocery|general)$"];
      way(around:{radius_meters},{latitude},{longitude})["shop"~"^(supermarket|convenience|grocery|general)$"];
      relation(around:{radius_meters},{latitude},{longitude})["shop"~"^(supermarket|convenience|grocery|general)$"];
    );
    out tags center;
    """


def _build_road_query(latitude: float, longitude: float, radius_meters: int) -> str:
    return f"""
    [out:json][timeout:25];
    (
      way(around:{radius_meters},{latitude},{longitude})["highway"];
    );
    out tags center;
    """


def _run_overpass_query(query: str) -> list[dict]:
    response = requests.post(
        OVERPASS_URL,
        data={"data": query},
        timeout=OVERPASS_TIMEOUT_SECONDS,
    )
    response.raise_for_status()
    payload = response.json()
    return payload.get("elements", [])


def _classify_footfall(road_elements: list[dict]) -> float:
    major_roads = {"motorway", "trunk", "primary", "secondary"}
    residential_roads = {"residential", "living_street", "service", "unclassified"}

    major_count = 0
    residential_count = 0
    for element in road_elements:
        tags = element.get("tags", {})
        highway_type = tags.get("highway", "")
        if highway_type in major_roads:
            major_count += 1
        elif highway_type in residential_roads:
            residential_count += 1

    if major_count >= 2 or (major_count >= 1 and major_count >= residential_count):
        return 0.9
    if major_count >= 1 and residential_count >= 1:
        return 0.6
    if residential_count >= 1:
        return 0.3
    return 0.5


@lru_cache(maxsize=512)
def _get_geo_features_cached(latitude_key: float, longitude_key: float, radius_meters: int) -> dict:
    poi_elements = _run_overpass_query(_build_poi_query(latitude_key, longitude_key, radius_meters))
    competition_elements = _run_overpass_query(_build_competition_query(latitude_key, longitude_key, radius_meters))
    road_elements = _run_overpass_query(_build_road_query(latitude_key, longitude_key, ROAD_SCAN_RADIUS_METERS))

    poi_density = len(poi_elements)
    competition_density = len(competition_elements)
    footfall_score = _classify_footfall(road_elements)

    return {
        "poi_density": poi_density,
        "competition_density": competition_density,
        "footfall_score": footfall_score,
        "is_fallback": False,
    }


def get_geo_features(latitude: float, longitude: float, radius_meters: int | None = None) -> dict:
    resolved_radius = radius_meters or DEFAULT_RADIUS_METERS
    lat_key = round(float(latitude), 4)
    lon_key = round(float(longitude), 4)
    try:
        return _get_geo_features_cached(lat_key, lon_key, int(resolved_radius))
    except Exception:
        return _neutral_geo_features()
