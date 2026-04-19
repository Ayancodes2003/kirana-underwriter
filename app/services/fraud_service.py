from __future__ import annotations


def detect_risk_flags(features: dict, geo_features: dict, detection_count: int) -> list[str]:
    flags: list[str] = []

    shelf_density = float(features.get("shelf_density", 0.0))
    footfall_score = float(geo_features.get("footfall_score", 0.5))
    competition_density = float(geo_features.get("competition_density", 0.0))

    if shelf_density >= 0.55 and footfall_score <= 0.35:
        flags.append("inventory_footfall_mismatch")

    if shelf_density >= 0.60 and competition_density >= 12:
        flags.append("inventory_competition_mismatch")

    if detection_count < 4:
        flags.append("low_visibility")

    if shelf_density > 0.90:
        flags.append("over_optimized_shelf")

    return flags
