"""음성 I/O 모듈 - TTS: Piper 바이너리를 subprocess로 호출한다.

Piper의 python 바인딩 대신 CLI 바이너리를 직접 호출하는 이유:
pip 패키지(piper-tts)와 공식 사전빌드 바이너리(rhasspy/piper release,
Raspberry Pi aarch64 포함) 어느 쪽을 설치하든 동일한 방식으로 동작하고,
python API 버전 변경에 영향을 받지 않는다.
"""
import subprocess
import time
from dataclasses import dataclass


@dataclass
class TTSResult:
    audio_path: str
    latency_sec: float


class TTSEngine:
    def __init__(self, config):
        self.config = config

    def synthesize(self, text: str, output_path: str) -> TTSResult:
        start = time.monotonic()
        subprocess.run(
            [
                self.config.piper_binary,
                "--model",
                self.config.piper_model_path,
                "--output_file",
                output_path,
            ],
            input=text.encode("utf-8"),
            check=True,
            capture_output=True,
        )
        latency = time.monotonic() - start
        return TTSResult(audio_path=output_path, latency_sec=latency)
