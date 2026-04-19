from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.models.schemas import AnalyzeStoreResponse
from app.services.benchmark_service import benchmark_store
from app.services.detection_service import detect_products
from app.services.estimation_service import estimate_sales_from_features
from app.services.explanation_service import build_explanations
from app.services.feature_service import compute_store_features
from app.services.fraud_service import detect_risk_flags
from app.services.geo_service import get_geo_features
from app.services.loan_service import recommend_loan
from app.utils.image_utils import decode_image_bytes


router = APIRouter()


@router.post("/analyze-store", response_model=AnalyzeStoreResponse)
async def analyze_store(
    images: list[UploadFile] = File(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    geo_radius_meters: int | None = Form(None),
    image_roles: str | None = Form(None),
) -> AnalyzeStoreResponse:
    if len(images) < 3 or len(images) > 5:
        raise HTTPException(status_code=400, detail="Upload between 3 and 5 images.")
    if latitude < -90 or latitude > 90:
        raise HTTPException(status_code=400, detail="latitude must be between -90 and 90.")
    if longitude < -180 or longitude > 180:
        raise HTTPException(status_code=400, detail="longitude must be between -180 and 180.")
    if geo_radius_meters is not None and geo_radius_meters <= 0:
        raise HTTPException(status_code=400, detail="geo_radius_meters must be greater than 0.")

    roles = [role.strip().lower() for role in image_roles.split(",")] if image_roles else []
    if roles and len(roles) != len(images):
        raise HTTPException(status_code=400, detail="image_roles must match the number of uploaded images.")

    image_payloads = []
    for index, upload in enumerate(images):
        content = await upload.read()
        try:
            image = decode_image_bytes(content)
        except ValueError as error:
            raise HTTPException(status_code=400, detail=str(error)) from error
        role = roles[index] if index < len(roles) else "shelf"
        image_payloads.append(
            {
                "filename": upload.filename or f"image_{index + 1}",
                "role": role,
                "image": image,
            }
        )

    detections = []
    shelf_images = [payload for payload in image_payloads if payload["role"] == "shelf"]
    if not shelf_images:
        shelf_images = image_payloads

    for payload in shelf_images:
        image_detections = detect_products(payload["image"])
        detections.append(
            {
                "filename": payload["filename"],
                "role": payload["role"],
                "detections": image_detections,
            }
        )

    detection_count = sum(len(entry["detections"]) for entry in detections)
    features = compute_store_features(shelf_images, detections)
    geo_features = get_geo_features(latitude=latitude, longitude=longitude, radius_meters=geo_radius_meters)
    estimate = estimate_sales_from_features(features, geo_features, detection_count=detection_count)
    risk_flags = detect_risk_flags(features, geo_features, detection_count=detection_count)
    benchmark = benchmark_store(features=features, geo_features=geo_features)
    loan_recommendation = recommend_loan(
        monthly_income_range=estimate["monthly_revenue_range"],
        confidence_score=float(estimate["confidence_score"]),
        risk_flags=risk_flags,
        peer_percentile=int(benchmark["peer_percentile"]),
    )
    explanation = build_explanations(
        features=features,
        geo_features=geo_features,
        risk_flags=risk_flags,
        base_score=float(estimate["base_score"]),
        uncertainty_score=float(estimate["uncertainty_score"]),
        benchmark=benchmark,
        loan_recommendation=loan_recommendation,
    )

    return AnalyzeStoreResponse(
        daily_sales_range=estimate["daily_sales_range"],
        monthly_revenue_range=estimate["monthly_revenue_range"],
        confidence_score=estimate["confidence_score"],
        risk_flags=risk_flags,
        features=features,
        geo_features=geo_features,
        benchmark=benchmark,
        loan_recommendation=loan_recommendation,
        explanation=explanation,
        detections=detections,
        heuristic_tier=estimate["heuristic_tier"],
    )
