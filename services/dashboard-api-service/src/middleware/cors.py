"""
CORS Middleware Configuration
VELOX Trading Platform
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


def setup_cors(app: FastAPI, allowed_origins: list[str]) -> None:
    """
    Configure CORS middleware for FastAPI application
    
    Args:
        app: FastAPI application instance
        allowed_origins: List of allowed origins (e.g., ["http://localhost:3000"])
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"]
    )
