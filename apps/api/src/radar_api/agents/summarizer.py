from openai import OpenAI

from radar_api.config import get_settings
from radar_api.schemas import CollectedItem
from radar_api.utils.dates import format_date_br, today_local


def build_fallback_briefing(items: list[CollectedItem]) -> tuple[str, str]:
    lines = [
        f"# Radar Tech IA Diario - {format_date_br(today_local())}",
        "",
        "Resumo gerado em modo local. Configure OPENAI_API_KEY para analise completa.",
        "",
        "## Principais itens",
    ]
    for index, item in enumerate(items, start=1):
        authors = ", ".join(item.authors[:4]) if item.authors else "autoria nao informada"
        lines.extend(
            [
                "",
                f"### {index}. {item.title}",
                f"- Fonte: {item.source_name} ({item.source_type})",
                f"- Autores: {authors}",
                f"- Link: {item.url}",
                f"- Resumo base: {item.raw_summary or 'sem resumo disponivel'}",
            ]
        )
    summary = "Radar diario com noticias e artigos academicos recentes sobre IA e tecnologia."
    return summary, "\n".join(lines)


def generate_briefing(items: list[CollectedItem]) -> tuple[str, str]:
    settings = get_settings()
    if not settings.openai_api_key:
        return build_fallback_briefing(items)

    client = OpenAI(api_key=settings.openai_api_key)
    payload = [
        {
            "title": item.title,
            "url": item.url,
            "source": item.source_name,
            "source_type": item.source_type,
            "category": item.category,
            "authors": item.authors,
            "summary": item.raw_summary,
        }
        for item in items
    ]
    response = client.responses.create(
        model=settings.openai_summary_model,
        input=[
            {
                "role": "system",
                "content": (
                    "Voce e um editor tecnico senior. Gere um briefing em portugues do Brasil, "
                    "com fontes preservadas, foco academico e pratico para um professor/desenvolvedor. "
                    "Toda data e hora mencionada deve estar em portugues do Brasil. "
                    "Artigos academicos em ingles devem manter titulo original, autores e link, "
                    "mas a explicacao deve ser em portugues claro e rigoroso."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Hoje e {format_date_br(today_local())}. "
                    "Crie um resumo executivo e um briefing em Markdown. "
                    "Use esta estrutura: Resumo executivo, Noticias gerais, Artigos academicos, "
                    "O que testar, O que estudar, O que acompanhar, Fontes para validacao. "
                    "Inclua links de validacao em cada item. "
                    "Nao invente impacto que a fonte nao sustente.\n\n"
                    f"Itens:\n{payload}"
                ),
            },
        ],
    )
    text = response.output_text
    executive = text.split("\n", 1)[0].replace("#", "").strip() or "Radar Tech IA Diario"
    return executive, text
