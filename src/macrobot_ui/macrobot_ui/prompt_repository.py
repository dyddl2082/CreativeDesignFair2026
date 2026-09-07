from __future__ import annotations

from pathlib import Path


class PromptRepository:
    """Build immutable generation instructions from packaged knowledge assets."""

    def __init__(self, knowledge_dir: Path) -> None:
        self._knowledge_dir = Path(knowledge_dir)

    def build_instructions(self) -> str:
        system_prompt = self._read("system_instructions.md")
        bundle = self._read("llm_bundle.yaml")
        examples = self._read("examples.md")
        return "\n\n".join(
            (
                system_prompt.strip(),
                "# 권한 있는 Robot API 계약 (llm_bundle.yaml)\n" + bundle.strip(),
                "# 승인된 응답 예시 (examples.md)\n" + examples.strip(),
            )
        )

    def _read(self, filename: str) -> str:
        path = self._knowledge_dir / filename
        if not path.is_file():
            raise FileNotFoundError(f"필수 지식 파일을 찾을 수 없습니다: {path}")
        return path.read_text(encoding="utf-8")
