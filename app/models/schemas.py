from pydantic import BaseModel, Field


class DetectionBox(BaseModel):
    label: str
    class_id: int
    confidence: float
    bbox: list[float] = Field(min_length=4, max_length=4)
    area: float


class ImageDetections(BaseModel):
    filename: str
    role: str
    detections: list[DetectionBox]


class StoreFeatures(BaseModel):
    shelf_density: float
    sku_diversity: int


class GeoFeatures(BaseModel):
    poi_density: float
    competition_density: float
    footfall_score: float


class BenchmarkResult(BaseModel):
    peer_percentile: int
    peer_bucket: str


class LoanRecommendation(BaseModel):
    eligible: bool
    recommended_loan_amount: int
    max_emi: int
    decision: str


class AnalyzeStoreResponse(BaseModel):
    daily_sales_range: list[int]
    monthly_revenue_range: list[int]
    confidence_score: float
    risk_flags: list[str]
    features: StoreFeatures
    geo_features: GeoFeatures
    benchmark: BenchmarkResult
    loan_recommendation: LoanRecommendation
    explanation: list[str]
    detections: list[ImageDetections]
    heuristic_tier: str
