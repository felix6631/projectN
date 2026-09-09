"""퍼스널리티 정의(config/persona.yaml)를 로드해 추론 모듈의 system prompt를 구성한다."""
from dataclasses import dataclass

import yaml


@dataclass
class Persona:
    name: str
    system_prompt: str


def load_persona(path: str) -> Persona:
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    traits = "\n".join(f"- {t}" for t in data.get("traits", []))
    system_prompt = data["system_prompt_template"].format(
        name=data["name"],
        traits=traits,
        speaking_style=data.get("speaking_style", "").strip(),
    )
    return Persona(name=data["name"], system_prompt=system_prompt.strip())
