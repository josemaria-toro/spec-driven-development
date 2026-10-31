"""The ASGI application: `uvicorn app.main:app`."""

from app.interfaces.api import create_app

app = create_app()
