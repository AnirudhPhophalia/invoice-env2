import os
import sys
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Add backend dir to path so imports work
sys.path.insert(0, str(Path(__file__).parent))

from api import services
from api.routes import router


app = FastAPI(title="Invoice & Receipt Processing Platform", version="1.0.0")

frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin, "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def health_check():
    return {"status": "ok", "service": "invoice-platform-backend"}


@app.post("/reset")
def reset_for_validator():
    # Compatibility endpoint for external validator scripts that call /reset.
    return services.reset_environment(batch_size=12)


@app.get("/validate")
def validate_endpoint():
    """
    OpenEnv validation endpoint.
    Runs openenv validate and returns the results.
    """
    try:
        import subprocess
        import sys
        from pathlib import Path

        # Run openenv validate
        result = subprocess.run(
            [sys.executable, "-m", "openenv", "validate"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent,  # Go to repo root
            timeout=30
        )

        return {
            "status": "success" if result.returncode == 0 else "failed",
            "exit_code": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except subprocess.TimeoutExpired:
        return {
            "status": "timeout",
            "error": "Validation timed out after 30 seconds"
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
