from openai import OpenAI

from radar_api.agents.costs import TextResult, usage_from_response
from radar_api.config import get_settings
from radar_api.schemas import CollectedItem
from radar_api.utils.dates import format_date_br, format_datetime_br, today_local


def build_fallback_briefing(items: list[CollectedItem]) -> tuple[str, str, TextResult]:
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
                f"- Publicado em: {format_datetime_br(item.published_at) if item.published_at else 'data nao informada'}",
                f"- Atualizado em: {format_datetime_br(item.updated_at) if item.updated_at else 'atualizacao nao informada'}",
                f"- Link: {item.url}",
                f"- Resumo base: {item.raw_summary or 'sem resumo disponivel'}",
            ]
        )
    summary = "Radar diario com noticias e artigos academicos recentes sobre IA e tecnologia."
    text = "\n".join(lines)
    return summary, text, TextResult(text=text)


def generate_briefing(items: list[CollectedItem]) -> tuple[str, str, TextResult]:
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
            "published_at": format_datetime_br(item.published_at) if item.published_at else None,
            "updated_at": format_datetime_br(item.updated_at) if item.updated_at else None,
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
                    "com fontes preservadas, foco em tecnologia, IA, desenvolvimento, ciencia aplicada, "
                    "mercado, produtos, infraestrutura, seguranca e pesquisa academica. "
                    "Toda data e hora mencionada deve estar em portugues do Brasil. "
                    "Artigos academicos em ingles devem manter titulo original, autores e link, "
                    "mas a explicacao deve ser em portugues claro e rigoroso. "
                    "Ao explicar pesquisas academicas, extraia apenas o que estiver sustentado pelo titulo, "
                    "abstract, fonte e metadados. Se faltar informacao, diga explicitamente que a fonte nao "
                    "traz aquele detalhe no resumo disponivel. "
                    "Nao deixe os artigos academicos dominarem o briefing quando houver noticias relevantes."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Hoje e {format_date_br(today_local())}. "
                    "Crie um resumo executivo e um briefing em Markdown. "
                    "Comece com uma linha chamada 'Resumo executivo:' com 2 a 4 frases. "
                    "Use esta estrutura: Resumo executivo, Brasil, Mundo, IA e devtools, "
                    "Videos e canais, Artigos academicos, O que testar, O que estudar, "
                    "O que acompanhar, Fontes para validacao. "
                    "Em Brasil, priorize sites brasileiros e impacto local. "
                    "Em Mundo, priorize tendencias globais, produtos, chips, seguranca, big techs e startups. "
                    "Em Videos e canais, destaque videos novos quando forem relevantes. "
                    "Em Artigos academicos, selecione ate 5 trabalhos entre arXiv, ACM, IEEE, Nature, Springer, "
                    "Elsevier, MIT Press e Semantic Scholar quando houver itens relevantes. Para cada pesquisa, "
                    "use este formato: Titulo original; fonte/editora; autores; publicado em; atualizado em "
                    "quando houver; objetivo da pesquisa; metodologia usada; discussoes e principais resultados; "
                    "breve conclusao; o que esperar no futuro; link para validacao. "
                    "Nao invente metodologia ou resultado quando o resumo nao informar; nesses casos, registre "
                    "'nao informado no resumo disponivel'. "
                    "Inclua links de validacao em cada item. "
                    "Quando houver data de publicacao ou atualizacao, cite em portugues do Brasil. "
                    "Nao invente impacto que a fonte nao sustente.\n\n"
                    f"Itens:\n{payload}"
                ),
            },
        ],
    )
    text = response.output_text
    executive = text.split("\n", 1)[0].replace("#", "").strip() or "Radar Tech IA Diario"
    input_tokens, output_tokens = usage_from_response(response)
    return executive, text, TextResult(text=text, input_tokens=input_tokens, output_tokens=output_tokens)
