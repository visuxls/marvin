from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from pydantic_ai.ui._web.app import _get_ui_html  # private API

from web.dependencies import HtmlSourceDep

router = APIRouter()


@router.get("/")
@router.get("/{id}")
async def index(html_source: HtmlSourceDep) -> HTMLResponse:
    """
    Serve the bundled chat UI HTML.

    Args:
        html_source: Optional HTML source override from application state.

    Returns:
        Cached or CDN-fetched chat UI document.
    """
    content = await _get_ui_html(html_source)
    return HTMLResponse(
        content=content,
        headers={"Cache-Control": "public, max-age=3600"},
    )
