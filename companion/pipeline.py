"""STT -> 추론(LLM) -> TTS 전체 파이프라인 (agent.md 4단계).

구간별 지연시간을 측정해 콘솔에 출력하고 data/latency_log.csv에 기록한다
(agent.md 5단계, 완료 기준: "측정 가능한 상태").
"""
import csv
import time
from pathlib import Path

from .audio_io import play_audio, record_push_to_talk
from .config import Config
from .conversation import ConversationStore
from .llm import LLMClient
from .persona import load_persona
from .stt import STTEngine
from .tts import TTSEngine

LATENCY_LOG = Path("data/latency_log.csv")


def _log_latency(row: dict) -> None:
    LATENCY_LOG.parent.mkdir(parents=True, exist_ok=True)
    is_new = not LATENCY_LOG.exists()
    with LATENCY_LOG.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(row.keys()))
        if is_new:
            writer.writeheader()
        writer.writerow(row)


def run() -> None:
    config = Config()
    persona = load_persona(config.persona_path)

    stt = STTEngine(config)
    tts = TTSEngine(config)
    llm = LLMClient(config, persona.system_prompt)
    store = ConversationStore(config.db_path)

    print(f"=== 컴패니언 로봇 음성 대화 데모 ({persona.name} / {config.ollama_model}) ===")
    print("Ctrl+C로 종료합니다.\n")

    turn = 0
    try:
        while True:
            turn += 1
            wav_in = f"/tmp/companion_in_{turn}.wav"
            wav_out = f"/tmp/companion_out_{turn}.wav"

            record_push_to_talk(config.sample_rate, config.max_record_seconds, wav_in)
            end_of_speech = time.monotonic()

            stt_result = stt.transcribe(wav_in)
            if not stt_result.text:
                print("(인식된 텍스트가 없습니다. 다시 시도하세요.)\n")
                continue
            print(f"[사용자] {stt_result.text}")

            history = store.recent(config.history_turns)
            llm_result = llm.chat(history, stt_result.text)
            print(f"[{persona.name}] {llm_result.text}")

            tts_result = tts.synthesize(llm_result.text, wav_out)
            playback_start = time.monotonic()
            play_audio(wav_out)

            store.add("user", stt_result.text)
            store.add("assistant", llm_result.text)

            round_trip = playback_start - end_of_speech
            _log_latency(
                {
                    "turn": turn,
                    "stt_sec": round(stt_result.latency_sec, 3),
                    "llm_sec": round(llm_result.latency_sec, 3),
                    "tts_sec": round(tts_result.latency_sec, 3),
                    "round_trip_sec": round(round_trip, 3),
                }
            )
            print(
                f"(지연시간 - STT: {stt_result.latency_sec:.2f}s, "
                f"LLM: {llm_result.latency_sec:.2f}s, "
                f"TTS: {tts_result.latency_sec:.2f}s, "
                f"왕복(발화종료→응답재생시작): {round_trip:.2f}s)\n"
            )
    except KeyboardInterrupt:
        print("\n종료합니다.")


if __name__ == "__main__":
    run()
