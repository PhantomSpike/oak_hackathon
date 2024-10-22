from typing import Dict, List, Optional, Type, Union

from openai import OpenAI
from pydantic import BaseModel

from oak_hackaton.settings import get_settings

# We use settings to give us defaults
settings = get_settings()

# Not all GPT models can provide structured responses.
structured_models = [
    "gpt-4o-mini",
    "gpt-4o-2024-08-06",
]


def get_open_ai_client(api_key: str = settings.OPENAI_API_KEY_OAK):
    return OpenAI(api_key=api_key)


class LLMResponse(BaseModel):
    content: Union[str, dict, BaseModel]
    input_token_count: int
    output_token_count: int
    used_model: str

    def get_token_info(self) -> dict:
        token_dict = {
            "input": {
                "count": self.input_token_count,
            },
            "output": {
                "count": self.output_token_count,
            },
            "model": self.used_model,
        }

        return token_dict


def create_system_msg(msg: str) -> Dict[str, str]:
    return {"role": "system", "content": msg}


def create_user_msg(msg: str) -> Dict[str, str]:
    return {"role": "user", "content": msg}


def create_assistant_msg(msg: str) -> Dict[str, str]:
    return {"role": "assistant", "content": msg}


def chat_completion(
    messages: List[Dict[str, str]],
    model: str = "gpt-4o-2024-08-06",
    temperature: float = 0,
    structured_response: bool = False,
    json_schema: Optional[Dict] = None,
    pydantic_model: Optional[Type[BaseModel]] = None,
    client: OpenAI = get_open_ai_client(),
) -> LLMResponse:
    """
    Get text response and token count from LLM based on message history

    Parameters
    ----------
    messages : List[Dict[str, str]]
        list of messages which is how we encode the chat history
    model : str, optional
        which OpenAI model to use, by default "gpt-4o-2024-08-06"
    temperature : float, optional
        Model temperature, by default 0
    structured_response : bool, optional
        If the response should have a structured format, by default False
    json_schema : Optional[Dict], optional
        JSON schema to use for structured responses, by default None
    pydantic_model : Optional[Type[BaseModel]], optional
        Pydantic model class to use for structured responses, by default None
    client : OpenAI, optional
        OpenAI client to use, by default get_open_ai_client()

    Returns
    -------
    LLMResponse
        Class which has text and token counts.

    Notes
    -----
    When `structured_response` is True, either `json_schema` or `pydantic_model`
    must be provided, but not both. This is required for structured responses.
    """

    if model not in structured_models and structured_response:
        raise ValueError(f"Model {model} does not support structured responses")

    if structured_response:
        if json_schema is not None and pydantic_model is not None:
            raise ValueError("Provide either JSON schema or Pydantic model, not both")
        elif json_schema is None and pydantic_model is None:
            raise ValueError(
                "Either JSON schema or Pydantic model must be provided for structured responses"
            )

    if json_schema is not None:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            response_format={
                "type": "json_schema",
                "json_schema": json_schema,
            },
        )
        content = response.choices[0].message.content

    elif pydantic_model is not None:
        response = client.beta.chat.completions.parse(
            model=model,
            messages=messages,
            temperature=temperature,
            response_format=pydantic_model,
        )
        content = response.choices[0].message.parsed

    else:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        content = response.choices[0].message.content

    # Extract token counts
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens

    response_object = LLMResponse(
        content=content,
        input_token_count=input_tokens,
        output_token_count=output_tokens,
        used_model=model,
    )

    return response_object
