from openai import OpenAI

from radar_api.agents.costs import TextResult, usage_from_response
from radar_api.config import get_settings


def generate_script(briefing_markdown: str) -> TextResult:
    settings = get_settings()
    if not settings.openai_api_key:
        text = (
            "# Roteiro\n\n"
            "Lia: Hoje temos um radar com noticias tecnicas e artigos academicos sobre IA.\n\n"
            "Bit: O ponto central e validar as fontes antes de transformar novidade em decisao.\n\n"
            "Lia: Configure a chave da OpenAI para gerar um roteiro completo em portugues do Brasil.\n"
        )
        return TextResult(text=text)

    client = OpenAI(api_key=settings.openai_api_key)
    response = client.responses.create(
        model=settings.openai_summary_model,
        input=[
            {
                "role": "system",
                "content": (
                    "Voce escreve roteiros de podcast em portugues do Brasil. "
                    "Os personagens sao Lia, pesquisadora de IA, e Bit, desenvolvedor senior acreano. "
                    "Use apenas o briefing fornecido. Equilibre noticias brasileiras, panorama global, "
                    "videos/canais, IA aplicada, devtools e artigos academicos. "
                    "Preserve cautela academica, mas explique o suficiente para o ouvinte realmente entender. "
                    "A conversa deve soar humana, como duas pessoas inteligentes conversando no caminho entre "
                    "Rio Branco e o trabalho: frases com respiro, pequenas reacoes naturais, transicoes suaves "
                    "e um leve sotaque acreano na cadencia e em expressoes discretas, sem caricatura, sem bordao "
                    "e sem girias forcadas. "
                    "Toda data e hora deve ser falada em portugues do Brasil."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Transforme o briefing em uma conversa de 6 a 8 minutos, objetiva, mas realmente informativa. "
                    "Comece pelas noticias mais importantes do Brasil e do mundo, depois IA/devtools, "
                    "videos relevantes e, por fim, papers academicos. "
                    "Em cada topico importante, explique: o que aconteceu, por que importa, impacto pratico, "
                    "riscos ou incertezas, e uma acao concreta para professor/desenvolvedor acompanhar, testar "
                    "ou estudar. "
                    "Priorize o que muda decisao, aula, estudo ou desenvolvimento; corte detalhes secundarios. "
                    "Explique papers em ingles em portugues do Brasil. "
                    "Nao empilhe manchetes. Se uma noticia entrar no roteiro, ela precisa ter contexto suficiente "
                    "para fazer sentido sem o ouvinte abrir o link. "
                    "Nao leia URLs em voz alta. "
                    "Evite voz robotica no texto: varie tamanho de frase, use perguntas curtas, confirmacoes naturais "
                    "e pausas textuais leves como 'olha,' ou 'o ponto aqui e'. "
                    "Escreva falas sempre no formato 'Lia:' e 'Bit:' para permitir vozes separadas.\n\n"
                    f"{briefing_markdown}"
                ),
            },
        ],
    )
    input_tokens, output_tokens = usage_from_response(response)
    return TextResult(text=response.output_text, input_tokens=input_tokens, output_tokens=output_tokens)
