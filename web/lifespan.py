import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI

from config import get_settings
from ingestion.importer import import_all, log_import_results
from ingestion.seed import ensure_demo_data


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """
    Run startup tasks before serving requests.

    Args:
        _app: FastAPI application instance.

    Yields:
        Control back to the application after startup completes.
    """
    settings = get_settings()
    await asyncio.to_thread(ensure_demo_data, settings)
    if settings.auto_import_on_startup:
        results = await asyncio.to_thread(import_all)
        log_import_results(results)
    yield
