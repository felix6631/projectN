"""파이프라인 전역 설정.

모두 환경변수로 오버라이드 가능. 기본값은 로봇 온보드(Raspberry Pi)에서
완전 오프라인으로 동작하는 것을 가정한다.

Ollama를 홈서버에 올리고 LAN으로 연결하는 구성을 쓰려면
COMPANION_OLLAMA_HOST=http://<홈서버IP>:11434 로 설정하면 된다.
"""
import os
from dataclasses import dataclass


def _env_int(name: str, default: int) -> int:
    value = os.environ.get(name)
    return int(value) if value else default


@dataclass
class Config:
    # 추론 모듈 (Ollama)
    ollama_host: str = os.environ.get("COMPANION_OLLAMA_HOST", "http://localhost:11434")
    ollama_model: str = os.environ.get("COMPANION_OLLAMA_MODEL", "qwen2.5:7b")

    # STT (faster-whisper)
    whisper_model: str = os.environ.get("COMPANION_WHISPER_MODEL", "small")
    whisper_device: str = os.environ.get("COMPANION_WHISPER_DEVICE", "cpu")
    whisper_compute_type: str = os.environ.get("COMPANION_WHISPER_COMPUTE", "int8")
    stt_language: str = os.environ.get("COMPANION_STT_LANGUAGE", "ko")

    # TTS (Piper)
    piper_binary: str = os.environ.get("COMPANION_PIPER_BIN", "piper")
    piper_model_path: str = os.environ.get(
        "COMPANION_PIPER_MODEL", "models/piper/voice.onnx"
    )

    # 퍼스널리티
    persona_path: str = os.environ.get("COMPANION_PERSONA", "config/persona.yaml")

    # 대화 히스토리 저장
    db_path: str = os.environ.get("COMPANION_DB", "data/conversations.db")
    history_turns: int = _env_int("COMPANION_HISTORY_TURNS", 6)

    # 오디오
    sample_rate: int = _env_int("COMPANION_SAMPLE_RATE", 16000)
    max_record_seconds: int = _env_int("COMPANION_MAX_RECORD_SECONDS", 20)
