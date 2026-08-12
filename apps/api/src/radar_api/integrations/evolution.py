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
            json={"number": number, "audio": audio_url, "delay": 1200},
        )
        if response.is_success:
            return response.json()

        media_url = f"{settings.evolution_api_url}/message/sendMedia/{settings.evolution_instance}"
        media_payload = {
            "number": number,
            "mediatype": "audio",
            "mimetype": "audio/mpeg",
            "media": audio_url,
            "fileName": "radar-tech-ia.mp3",
            "delay": 1200,
        }
        media_response = await client.post(
            media_url,
            headers={"apikey": settings.evolution_api_key},
            json=media_payload,
        )
        if media_response.is_success:
            result = media_response.json()
            result["fallback_endpoint"] = "sendMediaAudio"
            result["primary_audio_error"] = response.text[:500]
            return result

        document_payload = {
            **media_payload,
            "mediatype": "document",
            "mimetype": "audio/mpeg",
        }
        document_response = await client.post(
            media_url,
            headers={"apikey": settings.evolution_api_key},
            json=document_payload,
        )
        document_response.raise_for_status()
        result = document_response.json()
        result["fallback_endpoint"] = "sendMediaDocument"
        result["primary_audio_error"] = response.text[:500]
        result["media_audio_error"] = media_response.text[:500]
        return result
