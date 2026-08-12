from openai import OpenAI

from radar_api.config import get_settings


def generate_script(briefing_markdown: str) -> str:
    settings = get_settings()
    if not settings.openai_api_key:
        return (
            "# Roteiro\n\n"
            "Lia: Hoje temos um radar com noticias tecnicas e artigos academicos sobre IA.\n\n"
            "Bruno: O ponto central e validar as fontes antes de transformar novidade em decisao.\n\n"
            "Lia: Configure a chave da OpenAI para gerar um roteiro completo em portugues do Brasil.\n"
        )

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.create(
        model=settings.openai_summary_model,
        input=[
            {
                "role": "system",
                "content": (
                    "Voce escreve roteiros de podcast em portugues do Brasil. "
                    "Os personagens sao Lia, pesquisadora de IA, e Bruno, desenvolvedor senior. "
                    "Use apenas o briefing fornecido e preserve cautela academica. "
                    "Toda data e hora deve ser falada em portugues do Brasil."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Transforme o briefing em uma conversa de 8 a 12 minutos. "
                    "Inclua noticias gerais e artigos academicos. "
                    "Explique papers em ingles em portugues do Brasil. "
                    "Nao leia URLs em voz alta. "
                    "Escreva falas sempre no formato 'Lia:' e 'Bruno:' para permitir vozes separadas.\n\n"
                    f"{briefing_markdown}"
                ),
            },
        ],
    )
    return response.output_text
