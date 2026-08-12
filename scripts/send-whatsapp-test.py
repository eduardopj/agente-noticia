import asyncio
from datetime import datetime

from radar_api.config import get_settings
from radar_api.integrations.evolution import send_text
from radar_api.utils.dates import format_datetime_br


async def main() -> None:
    settings = get_settings()
    text = (
        "Teste do Radar Tech IA realizado em "
        f"{format_datetime_br(datetime.now())}. "
        "Evolution API conectada e envio funcionando."
    )
    result = await send_text(settings.whatsapp_target_number or "", text)
    print({"status": "ok", "result_type": type(result).__name__})


if __name__ == "__main__":
    asyncio.run(main())
