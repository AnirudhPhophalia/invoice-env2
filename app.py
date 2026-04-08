# app.py - HF Spaces entry point
"""
HF Spaces entry point for the Invoice Processing Environment.
This file should be at the repository root for HF Spaces to find it.
"""

from backend.main import app

# Export the FastAPI app for HF Spaces
__all__ = ["app"]