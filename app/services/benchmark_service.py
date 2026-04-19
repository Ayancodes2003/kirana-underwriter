from __future__ import annotations


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def benchmark_store(features: dict, geo_features: dict) -> dict:
    shelf_density = float(features.get("shelf_density", 0.0))
    sku_diversity = int(features.get("sku_diversity", 0))

    poi_density = float(geo_features.get("poi_density", 0.0))
    competition_density = float(geo_features.get("competition_density", 0.0))
    footfall_score = float(geo_features.get("footfall_score", 0.5))

    shelf_component = _clamp(shelf_density)
    sku_component = _clamp(sku_diversity / 15.0)
    poi_component = _clamp(poi_density / 30.0)
    competition_component = _clamp(competition_density / 20.0)
    footfall_component = _clamp(footfall_score)

    # Synthetic peer score for lightweight benchmark simulation.
    store_score = _clamp(
        0.35 * shelf_component
        + 0.25 * sku_component
        + 0.20 * poi_component
        + 0.20 * footfall_component
        - 0.12 * competition_component
    )

    demand_context = 0.60 * poi_component + 0.40 * footfall_component
    if demand_context < 0.35:
        peer_min, peer_max = 0.15, 0.58
    elif demand_context < 0.65:
        peer_min, peer_max = 0.28, 0.76
    else:
        peer_min, peer_max = 0.42, 0.90

    raw_percentile = ((store_score - peer_min) / (peer_max - peer_min + 1e-6)) * 100.0
    peer_percentile = int(round(max(0.0, min(100.0, raw_percentile))))

    if peer_percentile < 35:
        peer_bucket = "low"
    elif peer_percentile < 70:
        peer_bucket = "average"
    else:
        peer_bucket = "high"

    return {
        "peer_percentile": peer_percentile,
        "peer_bucket": peer_bucket,
    }
