"""3단계: 텍스트 -> 음성 출력 확인.

사용법: python scripts/test_tts.py "합성할 문장"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from companion.audio_io import play_audio
from companion.config import Config
from companion.tts import TTSEngine


def main() -> None:
    config = Config()
    tts = TTSEngine(config)

    text = sys.argv[1] if len(sys.argv) > 1 else "안녕하세요, 저는 컴패니언 로봇입니다."
    wav_path = "/tmp/companion_tts_test.wav"

    result = tts.synthesize(text, wav_path)
    print(f"합성 완료: {wav_path} (지연시간: {result.latency_sec:.2f}s)")

    play_audio(wav_path)


if __name__ == "__main__":
    main()
