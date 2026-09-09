# 컴패니언 로봇 — 음성 대화 프로토타입

`agent.md`에 정의된 스펙에 따라 구현한 음성 I/O(STT/TTS) + 추론 모듈(LLM) 캐스케이드 파이프라인.
전체 아키텍처: `마이크 입력 → STT → 추론(LLM) → TTS → 스피커 출력`

이번 구현 범위: 순차 캐스케이드 파이프라인 + 퍼스널리티(system prompt) 적용.
duplex 대화, 로보틱스 액션, 안전 설계는 범위 밖(`agent.md` 참고).

## 구성

```
agent.md                 스펙 문서
config/persona.yaml       로봇 퍼스널리티(이름, 성격, 말투) 정의
companion/
  config.py                환경변수 기반 설정
  persona.py                persona.yaml -> system prompt 빌드
  stt.py                    STT (faster-whisper, 오프라인)
  tts.py                    TTS (Piper 바이너리 subprocess 호출)
  llm.py                    추론 모듈 (Ollama /api/chat 클라이언트)
  audio_io.py                마이크 녹음(push-to-talk) / 스피커 재생
  conversation.py            대화 히스토리 저장 (SQLite)
  pipeline.py                 STT->LLM->TTS 전체 파이프라인 + 지연시간 로깅
scripts/
  test_ollama.py   1단계: Ollama 서빙 확인
  test_stt.py       2단계: 마이크->텍스트 확인
  test_tts.py       3단계: 텍스트->음성 확인
  run_demo.py        4~5단계: 전체 파이프라인 데모
```

## 사전 준비

### 1. Python 의존성

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Ollama + LLM

```bash
# 설치: https://ollama.com/download (Raspberry Pi 등 ARM64 지원)
ollama pull qwen2.5:7b
ollama serve   # 이미 서비스로 떠 있다면 생략
```

로봇 온보드가 아니라 홈서버에서 LLM을 돌리고 LAN으로 연결하려면:

```bash
export COMPANION_OLLAMA_HOST="http://<홈서버IP>:11434"
```

### 3. Piper (TTS)

```bash
pip install piper-tts   # 또는 https://github.com/rhasspy/piper 릴리스에서 aarch64 바이너리 다운로드
```

Piper 음성 모델(.onnx + .onnx.json)을 받아 `models/piper/voice.onnx` 경로에 두거나
`COMPANION_PIPER_MODEL` 환경변수로 경로를 지정한다.

> **주의(한국어 보이스):** Piper는 커뮤니티 기여 보이스 위주라 한국어 보이스 품질/가용성이
> 영어권만큼 좋지 않을 수 있다. 사용 가능한 한국어 보이스를 확인하고, 품질이 부족하면
> `agent.md`에 후보로 언급된 Coqui TTS 등으로 교체를 검토한다 (TTSEngine은 교체하기 쉽게
> 별도 모듈로 분리해뒀다).

### 4. faster-whisper (STT)

별도 설치 불필요 — `pip install -r requirements.txt` 시 함께 설치되며, 첫 실행 시
HuggingFace에서 모델 가중치를 자동 다운로드한다(이후에는 캐시로 오프라인 동작).

## 실행 순서 (agent.md 4절과 동일)

```bash
python scripts/test_ollama.py   # 1. LLM 응답 확인
python scripts/test_stt.py      # 2. 마이크 -> 텍스트
python scripts/test_tts.py      # 3. 텍스트 -> 음성
python scripts/run_demo.py      # 4~5. 전체 파이프라인 + 지연시간 측정
```

`run_demo.py`는 매 턴마다 STT/LLM/TTS 구간별 지연시간과 왕복(발화 종료 → 응답 재생 시작)
지연시간을 콘솔에 출력하고 `data/latency_log.csv`에 누적 기록한다.

## 퍼스널리티 수정

`config/persona.yaml`의 `name` / `traits` / `speaking_style`만 수정하면
코드 변경 없이 로봇의 성격과 말투를 바꿀 수 있다.

## 환경변수 설정 요약

| 변수 | 기본값 | 설명 |
|---|---|---|
| `COMPANION_OLLAMA_HOST` | `http://localhost:11434` | Ollama 서버 주소 |
| `COMPANION_OLLAMA_MODEL` | `qwen2.5:7b` | 사용할 모델 |
| `COMPANION_WHISPER_MODEL` | `small` | faster-whisper 모델 크기 |
| `COMPANION_STT_LANGUAGE` | `ko` | STT 언어 |
| `COMPANION_PIPER_BIN` | `piper` | Piper 실행 파일 경로 |
| `COMPANION_PIPER_MODEL` | `models/piper/voice.onnx` | Piper 보이스 모델 경로 |
| `COMPANION_PERSONA` | `config/persona.yaml` | 퍼스널리티 정의 파일 |
| `COMPANION_DB` | `data/conversations.db` | 대화 히스토리 DB |
| `COMPANION_HISTORY_TURNS` | `6` | LLM에 넘길 최근 대화 턴 수 |

## 알려진 범위 밖 항목

`agent.md`의 비범위 섹션 참고: 로보틱스 액션 정책, 안전 설계, 완전한 duplex 대화는
이 구현에 포함되지 않는다. VAD 기반 자동 발화 종료 감지(스트레치 목표)도 아직
구현되지 않았고, 현재는 push-to-talk(Enter 키) 방식으로 녹음을 시작/종료한다.
