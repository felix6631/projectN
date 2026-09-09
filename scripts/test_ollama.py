"""1단계: Ollama 로컬 LLM 서빙 확인.

사전 준비:
  ollama pull qwen2.5:7b   # 또는 COMPANION_OLLAMA_MODEL 로 지정한 모델
  ollama serve             # 이미 서비스로 떠 있다면 생략 가능
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from companion.config import Config
from companion.llm import LLMClient
from companion.persona import load_persona


def main() -> None:
    config = Config()
    persona = load_persona(config.persona_path)
    client = LLMClient(config, persona.system_prompt)

    print(f"Ollama host : {config.ollama_host}")
    print(f"Model       : {config.ollama_model}")
    print("테스트 메시지를 보냅니다...\n")

    result = client.chat(history=[], user_text="안녕! 네 소개를 짧게 해줘.")
    print(f"[{persona.name}] {result.text}")
    print(f"(지연시간: {result.latency_sec:.2f}s)")


if __name__ == "__main__":
    main()
