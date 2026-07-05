from web.schemas import (
    ChatRequestOptions,
    build_configure_response,
    resolve_reasoning_effort,
)


def test_build_configure_response_includes_reasoning_efforts():
    response = build_configure_response(models=[], builtin_tools=[])
    assert response.default_reasoning_effort == "off"
    assert [option.id for option in response.reasoning_efforts] == [
        "off",
        "minimal",
        "low",
        "medium",
        "high",
        "xhigh",
    ]


def test_resolve_reasoning_effort_defaults_to_off():
    assert resolve_reasoning_effort(None) == "off"
    assert resolve_reasoning_effort(ChatRequestOptions()) == "off"


def test_resolve_reasoning_effort_uses_request_value():
    assert resolve_reasoning_effort(ChatRequestOptions(reasoning_effort="high")) == "high"


def test_chat_request_options_blank_reasoning_effort_is_ignored():
    options = ChatRequestOptions.model_validate({"reasoningEffort": ""})
    assert options.reasoning_effort is None
    assert resolve_reasoning_effort(options) == "off"
