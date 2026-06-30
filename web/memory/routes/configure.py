from fastapi import APIRouter
from pydantic_ai.ui._web.api import BuiltinToolInfo, ConfigureFrontend  # private API

from web.dependencies import ChatRuntimeDep

router = APIRouter()


@router.get("/configure", response_model=ConfigureFrontend)
async def configure_frontend(runtime: ChatRuntimeDep) -> ConfigureFrontend:
    """
    Return frontend model and builtin-tool configuration.

    Args:
        runtime: Shared chat runtime from application state.

    Returns:
        Frontend configuration payload.
    """
    return ConfigureFrontend(
        models=runtime.model_infos,
        builtin_tools=[
            BuiltinToolInfo(id=tool.unique_id, name=tool.label) for tool in runtime.ui_native_tools
        ],
    )
