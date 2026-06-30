import asyncio

from fastapi import APIRouter, HTTPException

from storage.conversation_memory import (
    delete_conversation,
    list_conversation_summaries,
    update_conversation_metadata,
)
from web.conversations import conversation_summary_response, load_conversation_ui_messages
from web.dependencies import SettingsDep
from web.schemas import (
    ConversationMessagesResponse,
    ConversationPatch,
    ConversationSummaryResponse,
    ErrorDetail,
    OkResponse,
)

router = APIRouter()


@router.get("/conversations", response_model=list[ConversationSummaryResponse])
async def list_conversations(settings: SettingsDep) -> list[ConversationSummaryResponse]:
    """
    List stored conversations for the sidebar.

    Args:
        settings: Application settings.

    Returns:
        Conversation summaries for the sidebar.
    """
    summaries = await asyncio.to_thread(
        list_conversation_summaries,
        db_path=settings.db_path,
    )
    return [conversation_summary_response(summary) for summary in summaries]


@router.get(
    "/conversations/{conversation_id}/messages",
    response_model=ConversationMessagesResponse,
)
async def get_conversation_messages(
    conversation_id: str,
    settings: SettingsDep,
) -> ConversationMessagesResponse:
    """
    Load persisted UI messages for a conversation.

    Args:
        conversation_id: Conversation identifier.
        settings: Application settings.

    Returns:
        UI messages suitable for chat hydration.
    """
    messages = await asyncio.to_thread(
        load_conversation_ui_messages,
        conversation_id,
        db_path=settings.db_path,
    )
    return ConversationMessagesResponse(messages=messages)


@router.patch(
    "/conversations/{conversation_id}",
    response_model=OkResponse,
    responses={400: {"model": ErrorDetail}, 404: {"model": ErrorDetail}},
)
async def patch_conversation(
    conversation_id: str,
    body: ConversationPatch,
    settings: SettingsDep,
) -> OkResponse:
    """
    Update conversation title and/or pinned state.

    Args:
        conversation_id: Conversation identifier.
        body: Fields to update.
        settings: Application settings.

    Returns:
        Success indicator.

    Raises:
        HTTPException: When no fields are provided or the conversation is missing.
    """
    if body.title is None and body.pinned is None:
        raise HTTPException(
            status_code=400,
            detail=ErrorDetail(error="No updates provided").model_dump(),
        )

    updated = await asyncio.to_thread(
        update_conversation_metadata,
        conversation_id,
        db_path=settings.db_path,
        title=body.title,
        pinned=body.pinned,
    )
    if not updated:
        raise HTTPException(
            status_code=404,
            detail=ErrorDetail(error="Conversation not found").model_dump(),
        )
    return OkResponse()


@router.delete(
    "/conversations/{conversation_id}",
    response_model=OkResponse,
    responses={404: {"model": ErrorDetail}},
)
async def remove_conversation(
    conversation_id: str,
    settings: SettingsDep,
) -> OkResponse:
    """
    Delete a stored conversation.

    Args:
        conversation_id: Conversation identifier.
        settings: Application settings.

    Returns:
        Success indicator.

    Raises:
        HTTPException: When the conversation does not exist.
    """
    deleted = await asyncio.to_thread(
        delete_conversation,
        conversation_id,
        db_path=settings.db_path,
    )
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=ErrorDetail(error="Conversation not found").model_dump(),
        )
    return OkResponse()
