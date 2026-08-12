from datetime import date, datetime
from zoneinfo import ZoneInfo

from radar_api.config import get_settings

WEEKDAYS = [
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo",
]

MONTHS = [
    "janeiro",
    "fevereiro",
    "março",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
]


def app_timezone() -> ZoneInfo:
    return ZoneInfo(get_settings().timezone)


def today_local() -> date:
    return datetime.now(app_timezone()).date()


def format_date_br(value: date | datetime | str) -> str:
    if isinstance(value, str):
        parsed = date.fromisoformat(value)
    elif isinstance(value, datetime):
        parsed = value.astimezone(app_timezone()).date() if value.tzinfo else value.date()
    else:
        parsed = value
    weekday = WEEKDAYS[parsed.weekday()]
    month = MONTHS[parsed.month - 1]
    return f"{weekday}, {parsed.day} de {month} de {parsed.year}"


def format_datetime_br(value: datetime) -> str:
    local = value.astimezone(app_timezone()) if value.tzinfo else value.replace(tzinfo=app_timezone())
    return f"{format_date_br(local)}, às {local:%H:%M}"


def format_short_date_br(value: date | datetime | str) -> str:
    if isinstance(value, str):
        parsed = date.fromisoformat(value)
    elif isinstance(value, datetime):
        parsed = value.astimezone(app_timezone()).date() if value.tzinfo else value.date()
    else:
        parsed = value
    return parsed.strftime("%d/%m/%Y")
