from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .config import AppConfig


class ApiConfigurationError(RuntimeError):
    pass


@dataclass(frozen=True)
class ApiResponse:
    text: str
    response_id: str | None


class OpenAIChatService:
    """Use Responses API while retaining complete output items locally."""

    def __init__(self, config: AppConfig, instructions: str) -> None:
        self._config = config
        self._instructions = instructions
        self._api_history: list[Any] = []

    def reset_conversation(self) -> None:
        self._api_history.clear()

    def reply(self, user_message: str) -> ApiResponse:
        if not self._config.api_ready:
            raise ApiConfigurationError(
                "OPENAI_API_KEY가 없습니다. ~/.config/macrobot_ui/.env에 설정하세요."
            )
        try:
            from openai import OpenAI
        except ImportError as exc:
            raise ApiConfigurationError(
                "openai Python 패키지가 없습니다. requirements-ui.txt를 설치하세요."
            ) from exc

        client = OpenAI(api_key=self._config.api_key)
        input_items = [
            *self._api_history,
            {"role": "user", "content": user_message},
        ]
        response = client.responses.create(
            model=self._config.model,
            instructions=self._instructions,
            input=input_items,
            max_output_tokens=5000,
            store=self._config.store_responses,
        )
        self._api_history = [*input_items, *response.output]
        return ApiResponse(text=response.output_text, response_id=response.id)
