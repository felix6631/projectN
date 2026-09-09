"""음성 I/O 모듈 - STT: faster-whisper 기반, 완전 오프라인 실행."""
import time
from dataclasses import dataclass

from faster_whisper import WhisperModel


@dataclass
class STTResult:
    text: str
    latency_sec: float


class STTEngine:
    def __init__(self, config):
        self.config = config
        self.model = WhisperModel(
            config.whisper_model,
            device=config.whisper_device,
            compute_type=config.whisper_compute_type,
        )

    def transcribe(self, audio_path: str) -> STTResult:
        start = time.monotonic()
        segments, _ = self.model.transcribe(
            audio_path, language=self.config.stt_language, beam_size=1
        )
        text = "".join(segment.text for segment in segments).strip()
        latency = time.monotonic() - start
        return STTResult(text=text, latency_sec=latency)
