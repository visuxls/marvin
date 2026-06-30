from fastapi import APIRouter

from storage.session import db_connection
from web.dependencies import SettingsDep
from web.schemas import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health(settings: SettingsDep) -> HealthResponse:
    """
    Return a health check response with database connectivity.

    Args:
        settings: Application settings.

    Returns:
        Health status payload.
    """
    with db_connection(settings.db_path) as connection:
        connection.execute("SELECT 1")
    return HealthResponse()
