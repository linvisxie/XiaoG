"""Convenient production-like entry point used by run_windows.bat."""
import uvicorn

from backend.config import settings

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host=settings.runtime.host, port=settings.runtime.port, reload=False)
