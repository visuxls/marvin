from dataclasses import dataclass
from typing import cast

from pydantic_ai import Agent
from pydantic_ai.models import KnownModelName, Model, infer_model
from pydantic_ai.native_tools import SUPPORTED_NATIVE_TOOLS, AbstractNativeTool
from pydantic_ai.settings import ModelSettings
from pydantic_ai.ui._web.api import ModelInfo, ModelsParam  # private API

ModelRef = Model | KnownModelName | str


@dataclass(frozen=True)
class ChatRuntime[AgentDepsT, OutputDataT]:
    """
    Agent and model configuration shared by chat API routes.
    """

    agent: Agent[AgentDepsT, OutputDataT]
    deps: AgentDepsT | None
    model_settings: ModelSettings | None
    instructions: str | None
    model_id_to_ref: dict[str, ModelRef]
    model_infos: list[ModelInfo]
    model_ids: set[str]
    ui_native_tools: list[AbstractNativeTool]
    allowed_tool_ids: set[str]


def build_chat_runtime[AgentDepsT, OutputDataT](
    agent: Agent[AgentDepsT, OutputDataT],
    *,
    models: ModelsParam = None,
    deps: AgentDepsT | None = None,
    model_settings: ModelSettings | None = None,
    instructions: str | None = None,
) -> ChatRuntime[AgentDepsT, OutputDataT]:
    """
    Build shared runtime state for chat API routes.

    Args:
        agent: Marvin agent instance.
        models: Optional additional models for the UI.
        deps: Dependencies injected into each agent run.
        model_settings: Optional per-request model settings.
        instructions: Optional per-request instructions.

    Returns:
        Frozen runtime object stored on the application for dependency injection.
    """
    model_id_to_ref: dict[str, ModelRef] = {}
    model_infos: list[ModelInfo] = []

    ui_native_tools: list[AbstractNativeTool] = []

    all_models: list[tuple[str | None, ModelRef]] = []
    items = cast(
        list[tuple[str | None, ModelRef]],
        list(models.items())
        if isinstance(models, dict)
        else [(None, model) for model in (models or [])],
    )
    if items:
        all_models.extend(items)
    elif agent.model is not None:
        all_models.append((None, agent.model))

    seen_model_ids: set[str] = set()
    for label, model_ref in all_models:
        model = infer_model(model_ref)
        model_id = model_ref if isinstance(model_ref, str) else model.model_id
        if model_id in seen_model_ids:
            continue
        seen_model_ids.add(model_id)
        display_name = label or model.label
        model_supported_tools = model.profile.get("supported_native_tools", SUPPORTED_NATIVE_TOOLS)
        supported_tool_ids = [
            tool.unique_id for tool in ui_native_tools if type(tool) in model_supported_tools
        ]
        model_id_to_ref[model_id] = model_ref
        model_infos.append(
            ModelInfo(id=model_id, name=display_name, builtin_tools=supported_tool_ids)
        )

    return ChatRuntime(
        agent=agent,
        deps=deps,
        model_settings=model_settings,
        instructions=instructions,
        model_id_to_ref=model_id_to_ref,
        model_infos=model_infos,
        model_ids=set(model_id_to_ref.keys()),
        ui_native_tools=ui_native_tools,
        allowed_tool_ids={tool.unique_id for tool in ui_native_tools},
    )
