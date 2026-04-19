from __future__ import annotations


def _round_thousand(value: float) -> int:
    return int(round(value / 1000.0) * 1000)


def recommend_loan(
    monthly_income_range: list[int],
    confidence_score: float,
    risk_flags: list[str],
    peer_percentile: int,
) -> dict:
    lower_income = max(0, int(monthly_income_range[0])) if monthly_income_range else 0
    max_emi = _round_thousand(lower_income * 0.30)

    severe_flags = {
        "inventory_footfall_mismatch",
        "inventory_competition_mismatch",
        "over_optimized_shelf",
    }
    has_severe_flag = any(flag in severe_flags for flag in risk_flags)

    if confidence_score < 0.45 or has_severe_flag:
        decision = "manual_review"
        eligible = False
        multiplier = 0.0
    elif confidence_score < 0.70 or len(risk_flags) >= 2 or peer_percentile < 40:
        decision = "approve_with_limit"
        eligible = True
        multiplier = 3.0 + max(0.0, (peer_percentile - 20) / 100.0)
    else:
        decision = "approve"
        eligible = True
        multiplier = 4.5 + min(1.5, (peer_percentile / 100.0))

    recommended_loan_amount = _round_thousand(lower_income * multiplier)
    if not eligible:
        recommended_loan_amount = 0

    return {
        "eligible": eligible,
        "recommended_loan_amount": recommended_loan_amount,
        "max_emi": max_emi,
        "decision": decision,
    }
