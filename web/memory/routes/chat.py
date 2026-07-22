import asyncio

from fastapi import APIRouter, HTTPException, Request, Response
from pydantic import ValidationError
from pydantic_ai.capabilities import NativeTool
from pydantic_ai.run import AgentRunResult
from pydantic_ai.ui._web.api import ChatRequestExtra, validate_request_options  # private API
from pydantic_ai.ui.vercel_ai import VercelAIAdapter

from agent.model import build_model_settings
from storage.conversation_memory import (
    DEFAULT_CONVERSATION_ID,
    load_conversation_messages,
    save_conversation_messages,
)
from web.chat_history import (
    VERCEL_AI_SDK_VERSION,
    reconcile_chat_payload,
    request_with_payload,
)
from web.conversations import title_from_ui_messages
from web.dependencies import ChatRuntimeDep, SettingsDep
from web.request import read_json_body
from web.schemas import ChatRequestOptions, ErrorDetail, resolve_reasoning_effort

router = APIRouter()


@router.post("/chat", responses={400: {"model": ErrorDetail}})
async def post_chat(
    request: Request,
    runtime: ChatRuntimeDep,
    settings: SettingsDep,
) -> Response:
    """
    Stream a chat response with server-side conversation persistence.

    Args:
        request: Incoming Vercel AI chat request.
        runtime: Shared chat runtime from application state.
        settings: Application settings.

    Returns:
        Streaming or JSON response from the Vercel AI adapter.

    Raises:
        HTTPException: When request validation or model/tool options fail.
    """
    request, payload = await read_json_body(request)
    conversation_id = payload.get("id") or DEFAULT_CONVERSATION_ID
    client_messages = payload.get("messages", [])

    stored_messages = await asyncio.to_thread(
        load_conversation_messages,
        conversation_id,
        db_path=settings.DB_PATH,
    )
    message_history, payload = reconcile_chat_payload(
        payload,
        stored_messages,
        sdk_version=VERCEL_AI_SDK_VERSION,
    )
    request = request_with_payload(request, payload)

    try:
        adapter = await VercelAIAdapter.from_request(
            request,
            agent=runtime.agent,
            sdk_version=VERCEL_AI_SDK_VERSION,
        )
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc

    extra_data = ChatRequestExtra.model_validate(adapter.run_input.__pydantic_extra__)
    if error := validate_request_options(
        extra_data,
        runtime.model_ids,
        runtime.allowed_tool_ids,
    ):
        raise HTTPException(
            status_code=400,
            detail=ErrorDetail(error=error).model_dump(),
        )

    try:
        chat_options = ChatRequestOptions.model_validate(payload)
    except ValidationError as exc:
        raise HTTPException(status_code=422, detail=exc.errors()) from exc

    model_ref = runtime.model_id_to_ref.get(extra_data.model) if extra_data.model else None
    default_model_id = runtime.model_infos[0].id if runtime.model_infos else None
    persisted_model_id = extra_data.model or default_model_id
    request_native_tools = [
        tool for tool in runtime.ui_native_tools if tool.unique_id in extra_data.builtin_tools
    ]
    request_capabilities = [NativeTool(tool) for tool in request_native_tools]
    request_model_settings = build_model_settings(
        reasoning_effort=resolve_reasoning_effort(chat_options),
        session_id=conversation_id,
        model_id=persisted_model_id,
    )

    async def on_complete(result: AgentRunResult) -> None:
        await asyncio.to_thread(
            save_conversation_messages,
            conversation_id,
            result.all_messages(),
            db_path=settings.DB_PATH,
            fallback_title=title_from_ui_messages(client_messages),
            model_id=persisted_model_id,
        )

    return await adapter.dispatch_request(
        request,
        agent=runtime.agent,
        sdk_version=VERCEL_AI_SDK_VERSION,
        model=model_ref,
        capabilities=request_capabilities,
        deps=runtime.deps,
        model_settings=request_model_settings,
        instructions=runtime.instructions,
        message_history=message_history,
        conversation_id=conversation_id,
        manage_system_prompt="server",
        on_complete=on_complete,
    )
