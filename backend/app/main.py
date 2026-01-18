from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api import endpoints

app = FastAPI(
    title="UIDAI District Intelligence API",
    description="API for accessing UIDAI district-level analytics and risk assessments.",
    version="1.0.0",
)

# CORS Configuration
origins = [
    "http://localhost:3000",  # Next.js Frontend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(endpoints.router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"message": "Welcome to UIDAI District Intelligence API"}
