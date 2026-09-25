from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.connection import Base, engine
from app.models.complaint import Complaint
from app.routers.complaint import router as complaint_router

from app.routers.ai import router as ai_router


Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="AIVOA Customer Complaint Management System",
    description="AI-powered pharmaceutical customer complaint management system",
    version="1.0.0",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins = [
        "http://localhost:5173",
        "https://complaint-system-sepia-xi.vercel.app/",
    ]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(complaint_router)
app.include_router(ai_router)


@app.get("/")
def root():
    return {
        "message": "AIVOA Complaint Management API is running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }
