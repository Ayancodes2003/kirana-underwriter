from __future__ import annotations


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _base_daily_range_from_score(score: float) -> tuple[list[int], str]:
    if score >= 0.62:
        return [13000, 32000], "high"
    if score >= 0.38:
        return [5500, 13000], "medium"
    return [1500, 5000], "low"


def _apply_uncertainty_to_range(base_range: list[int], uncertainty_score: float) -> list[int]:
    lower, upper = base_range
    midpoint = (lower + upper) / 2.0
    half_width = (upper - lower) / 2.0

    # Low uncertainty tightens the range slightly, high uncertainty widens it.
    width_factor = 0.80 + (1.40 * uncertainty_score)
    adjusted_half_width = half_width * width_factor

    adjusted_lower = max(0, int(round(midpoint - adjusted_half_width)))
    adjusted_upper = int(round(midpoint + adjusted_half_width))
    if adjusted_upper <= adjusted_lower:
        adjusted_upper = adjusted_lower + 500
    return [adjusted_lower, adjusted_upper]


def _compute_uncertainty_score(
    shelf_density: float,
    poi_density: float,
    competition_density: float,
    detection_count: int,
    geo_fallback: bool,
) -> float:
    uncertainty = 0.20

    if detection_count < 5:
        uncertainty += 0.25
    elif detection_count < 12:
        uncertainty += 0.12

    if shelf_density <= 0.05 or shelf_density >= 0.85:
        uncertainty += 0.15

    if geo_fallback:
        uncertainty += 0.20

    if competition_density >= 12 and shelf_density >= 0.60:
        uncertainty += 0.15

    # Reduce uncertainty when visual and geo signals are consistent.
    if shelf_density >= 0.20 and poi_density >= 10 and 2 <= competition_density <= 10:
        uncertainty -= 0.12

    return _clamp(uncertainty)


def estimate_sales_from_features(features: dict, geo_features: dict, detection_count: int) -> dict:
    shelf_density = float(features.get("shelf_density", 0.0))
    sku_diversity = int(features.get("sku_diversity", 0))

    poi_density = float(geo_features.get("poi_density", 0.0))
    competition_density = float(geo_features.get("competition_density", 0.0))
    footfall_score = float(geo_features.get("footfall_score", 0.5))
    geo_fallback = bool(geo_features.get("is_fallback", False))

    shelf_component = _clamp(shelf_density)
    sku_component = _clamp(sku_diversity / 15.0)
    poi_component = _clamp(poi_density / 30.0)
    competition_component = _clamp(competition_density / 20.0)
    footfall_component = _clamp(footfall_score)

    score = (
        0.30 * shelf_component
        + 0.25 * sku_component
        + 0.20 * poi_component
        + 0.20 * footfall_component
        - 0.15 * competition_component
    )
    base_score = _clamp(score)

    uncertainty_score = _compute_uncertainty_score(
        shelf_density=shelf_density,
        poi_density=poi_density,
        competition_density=competition_density,
        detection_count=detection_count,
        geo_fallback=geo_fallback,
    )
    confidence_score = round(_clamp(1.0 - uncertainty_score), 4)

    base_daily_range, heuristic_tier = _base_daily_range_from_score(base_score)
    daily_sales_range = _apply_uncertainty_to_range(base_daily_range, uncertainty_score)

    monthly_revenue_range = [daily_sales_range[0] * 26, daily_sales_range[1] * 30]

    return {
        "daily_sales_range": daily_sales_range,
        "monthly_revenue_range": monthly_revenue_range,
        "confidence_score": confidence_score,
        "heuristic_tier": heuristic_tier,
        "base_score": round(base_score, 4),
        "uncertainty_score": round(uncertainty_score, 4),
    }
