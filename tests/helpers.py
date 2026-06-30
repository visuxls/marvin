from pydantic_ai.messages import ModelRequest, UserPromptPart


def model_request(text: str) -> ModelRequest:
    """
    Build a simple user model request for conversation tests.
    """
    return ModelRequest(parts=[UserPromptPart(content=text)])
