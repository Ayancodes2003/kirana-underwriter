# Kirana Underwriter MVP

Phase 1 hackathon backend for remote cash-flow underwriting of kirana stores.

## What it does

- Accepts 3 to 5 uploaded images
- Runs pretrained YOLOv8 detection on shelf images
- Computes shelf density and SKU diversity
- Extracts geo-spatial signals using OpenStreetMap/Overpass (POI, competition, footfall proxy)
- Uses uncertainty-aware fused heuristics to estimate daily sales and monthly revenue ranges
- Adds risk flags and human-readable explanations for decision support
- Adds synthetic peer benchmarking and loan recommendation outputs
- Returns structured JSON

## Run

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Frontend Run

```bash
cd frontend
npm install
npm run dev
```

Optional API host override:

```bash
cp .env.example .env
```

Then set `VITE_API_BASE_URL` in `.env` if your FastAPI server is not running on `http://127.0.0.1:8000`.

## Request

Send a `multipart/form-data` POST request to `/analyze-store` with:

- `images`: 3 to 5 image files
- `latitude`: store latitude (float)
- `longitude`: store longitude (float)
- `geo_radius_meters` optional lookup radius override (int, default from env `GEO_RADIUS_METERS`, fallback 1000)
- `image_roles` optional comma-separated list of roles matching the images, for example:
  - `shelf,counter,storefront`

If roles are omitted, all images are treated as shelf images for detection and feature extraction.

## Response

The response includes revenue ranges plus:

- `features` (shelf density, sku diversity)
- `geo_features` (poi_density, competition_density, footfall_score)
- `risk_flags` (rule-based anomaly/risk indicators)
- `benchmark` (peer_percentile and peer_bucket)
- `loan_recommendation` (eligibility, suggested loan amount, max EMI, decision)
- `explanation` (interpretable reasoning strings)
- detection details and applied heuristic tier

If geo lookup fails, neutral geo defaults are used so estimation still succeeds.
