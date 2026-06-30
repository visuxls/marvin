import sqlite3

from pydantic_ai.messages import (
    BinaryContent,
    ModelRequest,
    ModelResponse,
    SystemPromptPart,
    TextPart,
    UserPromptPart,
)

from storage.conversation_memory import (
    MAX_STORED_MESSAGES,
    delete_conversation,
    list_conversation_summaries,
    load_conversation_messages,
    resolve_conversation_title,
    save_conversation_messages,
    strip_system_messages,
    title_from_messages,
    update_conversation_metadata,
)
from tests.helpers import model_request
from web.conversations import (
    conversation_summary_response,
    load_conversation_ui_messages,
    title_from_ui_messages,
)


def test_conversation_round_trip(db_path):
    messages = [model_request("hello"), model_request("world")]
    save_conversation_messages("chat-1", messages, db_path=db_path)
    loaded = load_conversation_messages("chat-1", db_path=db_path)
    assert len(loaded) == 2


def test_load_missing_conversation_returns_empty(db_path):
    assert load_conversation_messages("missing", db_path=db_path) == []


def test_save_trims_to_max_messages(db_path):
    messages = [model_request(str(index)) for index in range(MAX_STORED_MESSAGES + 5)]
    save_conversation_messages("chat-1", messages, db_path=db_path)
    loaded = load_conversation_messages("chat-1", db_path=db_path)
    assert len(loaded) == MAX_STORED_MESSAGES


def test_strip_system_messages_removes_system_prompt_parts():
    messages = [
        ModelRequest(parts=[SystemPromptPart(content="Profile: Age 30")]),
        model_request("hello"),
        ModelResponse(parts=[TextPart(content="hi there")]),
    ]
    stripped = strip_system_messages(messages)
    assert len(stripped) == 2
    user_part = stripped[0].parts[0]
    assert isinstance(user_part, UserPromptPart)
    assert user_part.content == "hello"
    response_part = stripped[1].parts[0]
    assert isinstance(response_part, TextPart)
    assert response_part.content == "hi there"


def test_save_and_load_strip_system_messages(db_path):
    messages = [
        ModelRequest(parts=[SystemPromptPart(content="Profile: Age 30")]),
        model_request("hello"),
    ]
    save_conversation_messages("chat-1", messages, db_path=db_path)
    loaded = load_conversation_messages("chat-1", db_path=db_path)
    assert len(loaded) == 1
    user_part = loaded[0].parts[0]
    assert isinstance(user_part, UserPromptPart)
    assert user_part.content == "hello"


def test_load_conversation_ui_messages_omits_system_prompts(db_path):
    messages = [
        ModelRequest(parts=[SystemPromptPart(content="Profile: Age 30")]),
        model_request("hello"),
    ]
    save_conversation_messages("chat-1", messages, db_path=db_path)
    ui_messages = load_conversation_ui_messages("chat-1", db_path=db_path)
    assert len(ui_messages) == 1
    assert ui_messages[0]["role"] == "user"


def test_title_from_ui_messages_skips_non_user_and_blank_text():
    messages = [
        {"role": "assistant", "parts": [{"type": "text", "text": "nope"}]},
        {"role": "user", "parts": [{"type": "text", "text": "   "}]},
        {"role": "user", "parts": [{"type": "file", "url": "x"}]},
        {"role": "user", "parts": [{"type": "text", "text": "Real title"}]},
    ]
    assert title_from_ui_messages(messages) == "Real title"


def test_title_from_ui_messages_truncates_long_text():
    text = "b" * 50
    assert (
        title_from_ui_messages([{"role": "user", "parts": [{"type": "text", "text": text}]}])
        == f"{'b' * 40}…"
    )


def test_list_conversation_summaries_keeps_new_chat_without_user_text(db_path):
    save_conversation_messages("chat-a", [], db_path=db_path)
    summary = list_conversation_summaries(db_path=db_path)[0]
    assert summary.title == "New chat"


def test_title_from_ui_messages_returns_none_without_user_text():
    assert title_from_ui_messages([{"role": "assistant", "parts": []}]) is None


def test_title_from_ui_messages_uses_first_user_text():
    messages = [
        {
            "id": "1",
            "role": "user",
            "parts": [{"type": "text", "text": "What is my net worth?"}],
        }
    ]
    assert title_from_ui_messages(messages) == "What is my net worth?"


def test_resolve_conversation_title_prefers_existing_title():
    assert (
        resolve_conversation_title(
            "Custom title",
            [model_request("ignored")],
            fallback_title="Fallback",
        )
        == "Custom title"
    )


def test_resolve_conversation_title_uses_fallback_when_needed():
    assert (
        resolve_conversation_title(
            "",
            [],
            fallback_title="Fallback title",
        )
        == "Fallback title"
    )


def test_list_conversation_summaries_derives_title_without_persisting(db_path):
    save_conversation_messages("chat-a", [model_request("alpha")], db_path=db_path)

    connection = sqlite3.connect(db_path)
    connection.execute("UPDATE conversations SET title = '' WHERE conversation_id = 'chat-a'")
    connection.commit()
    connection.close()

    summary = list_conversation_summaries(db_path=db_path)[0]
    assert summary.title == "alpha"

    connection = sqlite3.connect(db_path)
    row = connection.execute(
        "SELECT title FROM conversations WHERE conversation_id = 'chat-a'"
    ).fetchone()
    connection.close()
    assert row[0] == ""


def test_save_conversation_messages_uses_fallback_title(db_path):
    save_conversation_messages(
        "chat-a",
        [],
        db_path=db_path,
        fallback_title="From client",
    )
    summary = list_conversation_summaries(db_path=db_path)[0]
    assert summary.title == "From client"


def test_title_from_messages_uses_first_user_prompt():
    assert title_from_messages([model_request("  Hello world  ")]) == "Hello world"


def test_title_from_messages_truncates_long_text():
    text = "a" * 50
    assert title_from_messages([model_request(text)]) == f"{'a' * 40}…"


def test_title_from_messages_returns_none_without_user_text():
    assert title_from_messages([]) is None


def test_list_conversation_summaries(db_path):
    save_conversation_messages("chat-a", [model_request("alpha")], db_path=db_path)
    save_conversation_messages("chat-b", [model_request("beta")], db_path=db_path)
    update_conversation_metadata("chat-b", db_path=db_path, pinned=True)

    summaries = list_conversation_summaries(db_path=db_path)
    assert [summary.id for summary in summaries] == ["chat-b", "chat-a"]
    assert summaries[0].pinned is True


def test_conversation_summary_response(db_path):
    save_conversation_messages("chat-a", [model_request("alpha")], db_path=db_path)
    summary = list_conversation_summaries(db_path=db_path)[0]
    payload = conversation_summary_response(summary)
    assert payload.id == "chat-a"
    assert payload.title == "alpha"
    assert isinstance(payload.created_at, int)


def test_update_conversation_metadata(db_path):
    save_conversation_messages("chat-a", [model_request("alpha")], db_path=db_path)
    updated = update_conversation_metadata(
        "chat-a",
        db_path=db_path,
        title="Renamed",
        pinned=True,
    )
    assert updated is True
    summary = list_conversation_summaries(db_path=db_path)[0]
    assert summary.title == "Renamed"
    assert summary.pinned is True


def test_update_conversation_metadata_missing_returns_false(db_path):
    assert update_conversation_metadata("missing", db_path=db_path, title="Nope") is False


def test_delete_conversation(db_path):
    save_conversation_messages("chat-a", [model_request("alpha")], db_path=db_path)
    assert delete_conversation("chat-a", db_path=db_path) is True
    assert list_conversation_summaries(db_path=db_path) == []


def test_title_from_messages_skips_non_requests_and_blank_text():
    messages = [
        ModelResponse(parts=[TextPart(content="assistant")]),
        model_request("   "),
        model_request("final"),
    ]
    assert title_from_messages(messages) == "final"


def test_title_from_messages_skips_non_string_user_content():
    messages = [
        ModelRequest(
            parts=[UserPromptPart(content=[BinaryContent(data=b"abc", media_type="image/png")])]
        ),
        model_request("final"),
    ]
    assert title_from_messages(messages) == "final"


def test_load_conversation_ui_messages_missing_conversation(db_path):
    assert load_conversation_ui_messages("missing", db_path=db_path) == []


def test_update_conversation_metadata_without_fields_returns_false(db_path):
    save_conversation_messages("chat-a", [model_request("alpha")], db_path=db_path)
    assert update_conversation_metadata("chat-a", db_path=db_path) is False


def test_save_conversation_messages_preserves_existing_title(db_path):
    save_conversation_messages("chat-a", [model_request("alpha")], db_path=db_path)
    update_conversation_metadata("chat-a", db_path=db_path, title="Pinned title")
    save_conversation_messages("chat-a", [model_request("beta")], db_path=db_path)
    summary = list_conversation_summaries(db_path=db_path)[0]
    assert summary.title == "Pinned title"
