from pathlib import Path
import re
import shutil

from openai import OpenAI

from radar_api.config import get_settings


def generate_audio(script: str, episode_date: str) -> str | None:
    settings = get_settings()
    if not settings.openai_api_key:
        return None

    output_dir = settings.storage_dir / "audio"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{episode_date}.mp3"
    for old_part in output_dir.glob(f"{episode_date}-part-*.mp3"):
        old_part.unlink(missing_ok=True)

    client = OpenAI(api_key=settings.openai_api_key)
    segments = _split_dialogue(script)
    part_index = 1
    with output_path.open("wb") as final_audio:
        for speaker, text in segments:
            voice = (
                settings.openai_tts_voice_secondary
                if speaker.lower().startswith("goku")
                else settings.openai_tts_voice_lia
            )
            for chunk in _chunk_text(text):
                speech_kwargs = {
                    "model": settings.openai_tts_model,
                    "voice": voice,
                    "input": chunk,
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
                    temp_path = output_dir / f".{episode_date}-{speaker}-{part_index}.part.mp3"
                    part_path = output_dir / f"{episode_date}-part-{part_index:02d}.mp3"
                    response.stream_to_file(temp_path)
                    shutil.copyfile(temp_path, part_path)
                    final_audio.write(temp_path.read_bytes())
                    temp_path.unlink(missing_ok=True)
                    part_index += 1

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


def _chunk_text(text: str, max_chars: int = 1300) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text.strip())
    chunks: list[str] = []
    current: list[str] = []
    current_len = 0
    for sentence in sentences:
        if current and current_len + len(sentence) + 1 > max_chars:
            chunks.append(" ".join(current))
            current = []
            current_len = 0
        current.append(sentence)
        current_len += len(sentence) + 1
    if current:
        chunks.append(" ".join(current))
    return chunks or [text[:max_chars]]


def _public_audio_url(path: Path) -> str:
    settings = get_settings()
    return f"{settings.api_base_url}/static/audio/{path.name}"


def public_whatsapp_audio_urls(episode_date: str) -> list[str]:
    settings = get_settings()
    output_dir = settings.storage_dir / "audio"
    parts = sorted(output_dir.glob(f"{episode_date}-part-*.mp3"))
    if parts:
        return [_public_audio_url(path) for path in parts]
    combined = output_dir / f"{episode_date}.mp3"
    return [_public_audio_url(combined)] if combined.exists() else []
