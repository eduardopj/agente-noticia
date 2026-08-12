from datetime import date

from radar_api.utils.dates import format_date_br


def test_format_date_br_uses_portuguese_brazilian_text():
    formatted = format_date_br(date(2026, 8, 12))

    assert formatted == "quarta-feira, 12 de agosto de 2026"
