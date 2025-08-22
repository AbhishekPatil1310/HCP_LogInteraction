#
# Main entry point for the FastAPI application.
# This file initializes the application, sets up middleware,
# ensures database tables are created, and registers API routes.
#

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import interaction
from db import create_tables

# --- FastAPI App Initialization ---
app = FastAPI(
    title="HCP Interaction Logger API",
    description="A backend API for logging interactions with Healthcare Professionals (HCPs).",
    version="1.0.0",
)

# --- Middleware Setup ---
# CORS (Cross-Origin Resource Sharing) is enabled to allow requests
# from any frontend client. Adjust allow_origins for production.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # Allows all domains (frontend can connect)
    allow_credentials=True,
    allow_methods=["*"],      # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],      # Allows all headers
)

# --- Application Startup ---
@app.on_event("startup")
async def startup_event():
    """Run on application startup: ensure database tables exist."""
    create_tables()

# --- Routers Registration ---
# Mounts the interaction router under `/api`
app.include_router(interaction.router, prefix="/api", tags=["interaction"])

# --- Development Server Entry Point ---
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",   # Exposes API on all network interfaces
        port=8000,
        reload=True,      # Auto-reload on file changes (useful for development)
    )
