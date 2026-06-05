from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import uvicorn
import logging
from contextlib import asynccontextmanager

from app.api import analyze, report, chatbot, dashboard, websocket_manager
from app.ml.model_loader import load_all_models
from app.utils.firebase import init_firebase

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 Starting Scam Detection System...")
    init_firebase()
    load_all_models()
    logger.info("✅ All models and services loaded successfully")
    yield
    logger.info("🛑 Shutting down...")


app = FastAPI(
    title="ScamShield AI - Scam Detection System",
    description="AI-powered real-time scam detection across SMS, Email, Voice, and URLs",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze.router, prefix="/api/v1/analyze", tags=["Analysis"])
app.include_router(report.router, prefix="/api/v1/report", tags=["Reporting"])
app.include_router(chatbot.router, prefix="/api/v1/chatbot", tags=["Chatbot"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(websocket_manager.router, prefix="/ws", tags=["WebSocket"])


@app.get("/")
async def root():
    return {
        "service": "ScamShield AI",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "analyze_text": "/api/v1/analyze/text",
            "analyze_url": "/api/v1/analyze/url",
            "analyze_voice": "/api/v1/analyze/voice",
            "analyze_email": "/api/v1/analyze/email",
            "chatbot": "/api/v1/chatbot/ask",
            "dashboard": "/api/v1/dashboard/stats",
            "report": "/api/v1/report/scam",
            "websocket": "/ws/alerts"
        }
    }


@app.get("/health")
async def health():
    return {"status": "healthy", "message": "ScamShield AI is running"}


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
