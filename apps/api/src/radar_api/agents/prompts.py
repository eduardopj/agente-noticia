from pathlib import Path


ROOT = Path(__file__).resolve().parents[5]
PROMPTS_DIR = ROOT / "prompts"


def load_prompt(name: str) -> str:
    return (PROMPTS_DIR / name).read_text(encoding="utf-8")
