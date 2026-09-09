"""4~5단계: STT -> LLM -> TTS 전체 파이프라인 데모 (지연시간 측정 포함)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from companion.pipeline import run

if __name__ == "__main__":
    run()
