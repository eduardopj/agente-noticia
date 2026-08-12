import httpx

from radar_api.config import get_settings

EVOLUTION_TIMEOUT = httpx.Timeout(connect=30, read=180, write=30, pool=30)


async def send_text(number: str, text: str) -> dict:
    settings = get_settings()
    if not settings.evolution_api_key or not settings.evolution_instance:
        raise RuntimeError("Evolution API nao configurada")

    url = f"{settings.evolution_api_url}/message/sendText/{settings.evolution_instance}"
    async with httpx.AsyncClient(timeout=EVOLUTION_TIMEOUT) as client:
        response = await client.post(
            url,
            headers={"apikey": settings.evolution_api_key},
            json={"number": number, "text": text},
        )
        response.raise_for_status()
        return response.json()


async def send_audio(number: str, audio_url: str) -> dict:
    settings = get_settings()
    if not settings.evolution_api_key or not settings.evolution_instance:
        raise RuntimeError("Evolution API nao configurada")

    url = f"{settings.evolution_api_url}/message/sendWhatsAppAudio/{settings.evolution_instance}"
    async with httpx.AsyncClient(timeout=EVOLUTION_TIMEOUT) as client:
        response = await client.post(
            url,
            headers={"apikey": settings.evolution_api_key},
            json={"number": number, "audio": audio_url},
        )
        response.raise_for_status()
        return response.json()
