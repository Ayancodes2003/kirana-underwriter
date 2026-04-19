from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.analyze import router as analyze_router


app = FastAPI(
    title="Kirana Underwriter MVP",
    version="0.1.0",
    description="Remote cash flow underwriting pipeline for kirana stores.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}
