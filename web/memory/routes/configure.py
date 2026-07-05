from fastapi import APIRouter
from pydantic_ai.ui._web.api import BuiltinToolInfo  # private API

from web.dependencies import ChatRuntimeDep
from web.schemas import ConfigureResponse, build_configure_response

router = APIRouter()


@router.get("/configure", response_model=ConfigureResponse)
async def configure_frontend(runtime: ChatRuntimeDep) -> ConfigureResponse:
    """
    Return frontend model, tool, and reasoning configuration.

    Args:
        runtime: Shared chat runtime from application state.

    Returns:
        Frontend configuration payload.
    """
    return build_configure_response(
        models=runtime.model_infos,
        builtin_tools=[
            BuiltinToolInfo(id=tool.unique_id, name=tool.label) for tool in runtime.ui_native_tools
        ],
    )
