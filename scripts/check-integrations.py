import asyncio
import json

import httpx
from openai import OpenAI

from radar_api.config import get_settings


def mask(value: str | None) -> str:
    if not value:
        return "<vazio>"
    if len(value) <= 8:
        return "<preenchido>"
    return f"{value[:4]}...{value[-4:]} ({len(value)} caracteres)"


async def check_evolution() -> dict:
    settings = get_settings()
    result: dict = {
        "configured": bool(settings.evolution_api_url and settings.evolution_api_key),
        "base_url": settings.evolution_api_url,
        "instance": settings.evolution_instance,
        "api_key": mask(settings.evolution_api_key),
    }
    if not result["configured"]:
        result["status"] = "skipped"
        return result

    async with httpx.AsyncClient(timeout=20) as client:
        fetch = await client.get(
            f"{settings.evolution_api_url}/instance/fetchInstances",
            headers={"apikey": settings.evolution_api_key or ""},
        )
        result["fetch_instances_status"] = fetch.status_code
        result["fetch_instances_ok"] = fetch.is_success
        if fetch.is_success:
            instances = fetch.json()
            result["instances_count"] = len(instances) if isinstance(instances, list) else None
            result["instance_found"] = _find_instance(instances, settings.evolution_instance)
        else:
            result["fetch_instances_body"] = fetch.text[:300]

        if settings.evolution_instance:
            state = await client.get(
                f"{settings.evolution_api_url}/instance/connectionState/{settings.evolution_instance}",
                headers={"apikey": settings.evolution_api_key or ""},
            )
            result["connection_state_status"] = state.status_code
            result["connection_state_ok"] = state.is_success
            result["connection_state_body"] = state.text[:500]
    return result


def _find_instance(instances, wanted: str | None) -> bool | None:
    if not wanted or not isinstance(instances, list):
        return None
    wanted_lower = wanted.lower()
    for item in instances:
        text = json.dumps(item, ensure_ascii=False).lower()
        if wanted_lower in text:
            return True
    return False


def check_openai() -> dict:
    settings = get_settings()
    result = {
        "configured": bool(settings.openai_api_key),
        "api_key": mask(settings.openai_api_key),
        "summary_model": settings.openai_summary_model,
        "tts_model": settings.openai_tts_model,
    }
    if not settings.openai_api_key:
        result["status"] = "skipped"
        return result
    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.create(
        model=settings.openai_summary_model,
        input="Responda apenas: ok",
    )
    result["status"] = "ok"
    result["response"] = response.output_text.strip()
    return result


async def main() -> None:
    report = {
        "openai": None,
        "evolution": None,
    }
    try:
        report["openai"] = check_openai()
    except Exception as exc:
        report["openai"] = {"status": "error", "error": str(exc)}

    try:
        report["evolution"] = await check_evolution()
    except Exception as exc:
        report["evolution"] = {"status": "error", "error": str(exc)}

    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
