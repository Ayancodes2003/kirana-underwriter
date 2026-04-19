from __future__ import annotations


def build_explanations(
    features: dict,
    geo_features: dict,
    risk_flags: list[str],
    base_score: float,
    uncertainty_score: float,
    benchmark: dict | None = None,
    loan_recommendation: dict | None = None,
) -> list[str]:
    explanations: list[str] = []

    shelf_density = float(features.get("shelf_density", 0.0))
    sku_diversity = int(features.get("sku_diversity", 0))
    poi_density = float(geo_features.get("poi_density", 0.0))
    competition_density = float(geo_features.get("competition_density", 0.0))
    footfall_score = float(geo_features.get("footfall_score", 0.5))
    geo_fallback = bool(geo_features.get("is_fallback", False))

    if shelf_density >= 0.25:
        explanations.append("High shelf density indicates strong inventory availability.")
    elif shelf_density <= 0.10:
        explanations.append("Low shelf density suggests constrained on-shelf inventory.")

    if sku_diversity >= 8:
        explanations.append("Strong SKU diversity suggests broader customer coverage.")
    elif sku_diversity <= 3:
        explanations.append("Limited SKU diversity may cap potential daily throughput.")

    if poi_density >= 12:
        explanations.append("High POI density near the store indicates stronger demand potential.")
    elif poi_density <= 4:
        explanations.append("Lower surrounding POI density indicates weaker walk-in demand support.")

    if competition_density >= 12:
        explanations.append("High nearby competition may reduce customer share and margins.")

    if footfall_score >= 0.8:
        explanations.append("Road connectivity suggests high footfall and stronger conversion opportunity.")
    elif footfall_score <= 0.35:
        explanations.append("Lower road footfall proxy may limit demand conversion.")

    if geo_fallback:
        explanations.append("Geo lookup fallback values were used, which increases model uncertainty.")

    flag_to_reason = {
        "inventory_footfall_mismatch": "Inventory level appears high versus low footfall, indicating a consistency risk.",
        "inventory_competition_mismatch": "Inventory is high in a dense competition zone, which may indicate overestimation risk.",
        "low_visibility": "Low detection visibility in uploaded images increases uncertainty.",
        "over_optimized_shelf": "Extremely dense shelf appearance can indicate staged stocking behavior.",
    }
    for flag in risk_flags:
        reason = flag_to_reason.get(flag)
        if reason:
            explanations.append(reason)

    explanations.append(
        f"Composite base score is {base_score:.2f} with uncertainty {uncertainty_score:.2f}."
    )

    if benchmark:
        peer_percentile = int(benchmark.get("peer_percentile", 0))
        peer_bucket = str(benchmark.get("peer_bucket", "average"))
        explanations.append(
            f"Peer benchmark places this store at percentile {peer_percentile} in the {peer_bucket} bucket."
        )

    if loan_recommendation:
        decision = str(loan_recommendation.get("decision", "manual_review"))
        max_emi = int(loan_recommendation.get("max_emi", 0))
        explanations.append(
            f"Loan decision is {decision} with a conservative EMI cap near {max_emi} per month."
        )

    return explanations
