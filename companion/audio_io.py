"""음성 I/O 모듈 - 마이크 녹음 / 스피커 재생.

VAD 기반 자동 종료(agent.md 6단계, 스트레치 목표)는 아직 구현하지 않는다.
녹음 종료 시점은 push-to-talk(Enter 키)로 명시적으로 지정한다.
"""
import threading
import wave

import numpy as np
import sounddevice as sd


def record_push_to_talk(sample_rate: int, max_seconds: int, out_path: str) -> str:
    input("녹음을 시작하려면 Enter를 누르세요...")
    print("녹음 중... 말이 끝나면 Enter를 다시 누르세요.")

    stop_flag = threading.Event()

    def wait_for_enter():
        input()
        stop_flag.set()

    threading.Thread(target=wait_for_enter, daemon=True).start()

    frames = []
    max_samples = sample_rate * max_seconds
    total_samples = 0

    stream = sd.InputStream(samplerate=sample_rate, channels=1, dtype="int16")
    with stream:
        while not stop_flag.is_set() and total_samples < max_samples:
            chunk, _ = stream.read(1024)
            frames.append(chunk.copy())
            total_samples += len(chunk)

    audio = (
        np.concatenate(frames, axis=0)
        if frames
        else np.zeros((0, 1), dtype="int16")
    )

    with wave.open(out_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio.tobytes())

    return out_path


def play_audio(path: str) -> None:
    with wave.open(path, "rb") as wf:
        sample_rate = wf.getframerate()
        raw = wf.readframes(wf.getnframes())

    audio = np.frombuffer(raw, dtype="int16")
    sd.play(audio, sample_rate)
    sd.wait()
