"""2단계: 마이크 입력 -> 텍스트 변환 확인."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from companion.audio_io import record_push_to_talk
from companion.config import Config
from companion.stt import STTEngine


def main() -> None:
    config = Config()
    stt = STTEngine(config)

    wav_path = "/tmp/companion_stt_test.wav"
    record_push_to_talk(config.sample_rate, config.max_record_seconds, wav_path)

    result = stt.transcribe(wav_path)
    print(f"\n인식 결과: {result.text}")
    print(f"(지연시간: {result.latency_sec:.2f}s)")


if __name__ == "__main__":
    main()
