"""추론 모듈: Ollama 로컬(혹은 LAN 상의) 서버에 대화를 위임한다.

인터페이스 계약(agent.md 3절):
- 입력: 텍스트(STT 결과) + 대화 히스토리
- 출력: 자연어 텍스트 + (예약된, 아직 채우지 않는) 구조화 action 필드

action 필드는 나중에 로보틱스 액션 정책 모듈이 붙을 때를 위해 포맷만
열어둔 것이다. 이번 구현에서는 항상 None이며, 모델에게 JSON 등
구조화 출력을 강제하지 않는다.
"""
import time
from dataclasses import dataclass
from typing import Dict, List, Optional

import requests


@dataclass
class LLMResponse:
    text: str
    latency_sec: float
    action: Optional[dict] = None


class LLMClient:
    def __init__(self, config, system_prompt: str):
        self.config = config
        self.system_prompt = system_prompt

    def chat(self, history: List[Dict[str, str]], user_text: str) -> LLMResponse:
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": user_text})

        start = time.monotonic()
        resp = requests.post(
            f"{self.config.ollama_host}/api/chat",
            json={
                "model": self.config.ollama_model,
                "messages": messages,
                "stream": False,
            },
            timeout=120,
        )
        resp.raise_for_status()
        data = resp.json()
        latency = time.monotonic() - start

        text = data["message"]["content"].strip()
        return LLMResponse(text=text, latency_sec=latency)
