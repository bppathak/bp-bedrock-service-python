import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import auth, events, forms, health, queue, submissions

import logging
import sys

logging.basicConfig(
    level=logging.DEBUG, #Set to DEBUG to see debug messages
    format='%(asctime)s-%(levelname)s-%(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)     # Output to console
    ]
)

def create_app() -> FastAPI:
    app = FastAPI(title="BP Bedrock Submission Service")

    cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[origin.strip() for origin in cors_origins.split(",") if origin.strip()],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(forms.router)
    app.include_router(submissions.router)
    app.include_router(events.router)
    app.include_router(queue.router)
    return app


app = create_app()
