from radar_api.config import get_settings


def estimated_brl_from_usd(value: float) -> float:
    return value * get_settings().usd_brl_rate


def format_usd(value: float) -> str:
    return f"US$ {value:.4f}"


def format_brl(value: float) -> str:
    formatted = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    return f"R$ {formatted}"
