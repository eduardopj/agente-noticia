from pathlib import Path
import re

from openai import OpenAI

from radar_api.config import get_settings


def generate_audio(script: str, episode_date: str) -> str | None:
    settings = get_settings()
    if not settings.openai_api_key:
        return None

    output_dir = settings.storage_dir / "audio"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{episode_date}.mp3"

    client = OpenAI(api_key=settings.openai_api_key)
    segments = _split_dialogue(script)
    with output_path.open("wb") as final_audio:
        for speaker, text in segments:
            voice = (
                settings.openai_tts_voice_secondary
                if speaker.lower().startswith("goku")
                else settings.openai_tts_voice_lia
            )
            speech_kwargs = {
                "model": settings.openai_tts_model,
                "voice": voice,
                "input": text[:3500],
                "instructions": (
                    "Fale em portugues do Brasil de forma natural, conversada, calorosa e menos mecanica. "
                    "Use ritmo de conversa cotidiana, com leve cadencia nortista/acreana, sem caricatura."
                ),
                "response_format": "mp3",
            }
            try:
                response_context = client.audio.speech.with_streaming_response.create(**speech_kwargs)
            except TypeError:
                speech_kwargs.pop("instructions", None)
                response_context = client.audio.speech.with_streaming_response.create(**speech_kwargs)
            with response_context as response:
                temp_path = output_dir / f".{episode_date}-{speaker}.part.mp3"
                response.stream_to_file(temp_path)
                final_audio.write(temp_path.read_bytes())
                temp_path.unlink(missing_ok=True)

    return _public_audio_url(output_path)


def _split_dialogue(script: str) -> list[tuple[str, str]]:
    pattern = re.compile(r"^(Lia|Goku)\s*:\s*(.+)$", re.IGNORECASE)
    segments: list[tuple[str, str]] = []
    current_speaker = "Lia"
    current_lines: list[str] = []

    for line in script.splitlines():
        match = pattern.match(line.strip())
        if match:
            if current_lines:
                segments.append((current_speaker, " ".join(current_lines)))
            current_speaker = match.group(1)
            current_lines = [match.group(2)]
        elif line.strip() and not line.strip().startswith("#"):
            current_lines.append(line.strip())

    if current_lines:
        segments.append((current_speaker, " ".join(current_lines)))

    return segments or [("Lia", script)]


def _public_audio_url(path: Path) -> str:
    settings = get_settings()
    return f"{settings.api_base_url}/static/audio/{path.name}"
