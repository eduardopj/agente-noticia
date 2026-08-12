# Agente diario de tendencias em tecnologia, ML, redes neurais e IA

## Observacao sobre o video

Nao e possivel transcrever integralmente o video do YouTube apenas a partir do link, por direito autoral e porque a transcricao publica confiavel nao esta disponivel no ambiente. A partir do trecho descrito pelo usuario, a ideia central e:

- um agente coleta diariamente noticias relevantes da internet;
- outro agente resume, organiza e preserva as fontes;
- outro agente transforma os temas em uma conversa entre dois personagens;
- a conversa vira audio para consumo diario.

Trecho fornecido pelo usuario:

> "Todo dia de manha ele vasculha todas as noticias de IA que aconteceram no dia anterior. Gera um resuminho, e ai eu jogo dentro do conjunto de IA do Google, e ele gera pra mim um audio de duas pessoas conversando sobre esse assunto. E eu escuto esse audio todo dia, dirigindo da minha casa ate o estudio, ou da minha casa ate a fundacao. Entao assim, eu me mantenho atualizado [...] E ai, quando eu vejo uma noticia maneirissima, eu vou la no meu resumo, porque no resumo tambem tem o link de onde ele pegou essa informacao, pra eu validar se aquela noticia que ele me deu e verdadeira tambem, que e outra coisa pouca gente faz. Validar o que a IA ta te entregando."

Este documento transforma essa ideia em uma especificacao de produto e em um prompt mestre para criar a ferramenta.

## Objetivo

Criar um sistema diario que monitora tendencias tecnologicas, com foco em:

- inteligencia artificial;
- aprendizado de maquina;
- redes neurais;
- agentes de IA;
- modelos de linguagem;
- ferramentas para desenvolvedores;
- pesquisa academica aplicada;
- empresas, produtos, frameworks e open source relevantes.

O sistema deve entregar, todos os dias, um pacote com:

- resumo executivo;
- lista de noticias ranqueadas por relevancia;
- fontes originais armazenadas;
- analise do impacto para um desenvolvedor senior;
- roteiro em formato de conversa entre dois personagens;
- audio estilo podcast curto.

A experiencia ideal e: voce recebe pela manha um resumo das principais noticias de IA do dia anterior, escuta um audio curto no deslocamento e, quando algo chamar sua atencao, abre o briefing para validar a fonte original.

## Estrategia recomendada

### Visao geral dos agentes

1. **Agente Coletor**
   - Busca noticias, artigos, papers, releases e repositorios.
   - Prioriza fontes primarias e confiaveis.
   - Remove duplicatas.
   - Salva URL, titulo, autor, data, fonte, resumo bruto e data da coleta.

2. **Agente Curador**
   - Classifica por relevancia, novidade, impacto tecnico e confiabilidade.
   - Filtra clickbait e republicacoes repetidas.
   - Separa conteudo por categorias.
   - Marca cada item como: pesquisa, produto, mercado, ferramenta, tutorial, opiniao ou alerta.

3. **Agente Analista**
   - Explica por que aquilo importa.
   - Traduz impactos para quem programa, lidera times ou estuda IA.
   - Identifica oportunidades praticas: o que testar, estudar, ignorar ou acompanhar.

4. **Agente Redator**
   - Gera um briefing diario curto.
   - Mantem links das fontes ao lado de cada afirmacao importante.
   - Evita afirmar algo que nao esteja sustentado por fonte.

5. **Agente Roteirista**
   - Cria dois personagens fixos:
     - **Lia**, pesquisadora tecnica, criteriosa e atualizada.
     - **Bruno**, desenvolvedor senior pragmatico, curioso e cético na medida certa.
   - Transforma o briefing em dialogo natural.
   - Faz os personagens discordarem quando houver incerteza.
   - Mantem a conversa informativa, leve e sem exageros.

6. **Agente de Audio**
   - Converte o roteiro em audio.
   - Usa duas vozes distintas.
   - Gera arquivo MP3 diario.
   - Salva tambem o roteiro em texto.

### Fontes recomendadas

Prioridade 1: fontes primarias

- blogs oficiais de empresas: OpenAI, Anthropic, Google DeepMind, Meta AI, Microsoft, NVIDIA, Hugging Face, AWS, Cloudflare, GitHub;
- arXiv para papers;
- papers com codigo e repositórios oficiais;
- documentacao oficial de frameworks;
- releases de produtos e changelogs.

Prioridade 2: fontes tecnicas e agregadores

- Hacker News;
- GitHub Trending;
- Papers with Code;
- The Batch;
- Latent Space;
- Import AI;
- Simon Willison;
- Ben's Bites;
- TLDR AI;
- Towards Data Science, com cautela;
- MIT Technology Review, The Verge, TechCrunch e similares, marcando como imprensa.

Prioridade 3: redes sociais e sinais fracos

- X/Twitter, LinkedIn, Reddit e YouTube so devem ser usados como sinal inicial.
- Sempre que possivel, encontrar a fonte primaria antes de citar.

## Modelo de dados minimo

Cada noticia deve ser salva com:

```json
{
  "id": "2026-08-11-openai-exemplo",
  "coletado_em": "2026-08-11T08:00:00-05:00",
  "publicado_em": "2026-08-10",
  "titulo": "Titulo original",
  "url": "https://...",
  "fonte": "Nome da fonte",
  "tipo_fonte": "primaria|imprensa|agregador|rede_social|paper",
  "autores": ["Autor"],
  "categoria": "ia|ml|redes_neurais|devtools|mercado|paper|open_source",
  "resumo_bruto": "...",
  "resumo_curado": "...",
  "impacto_para_dev_senior": "...",
  "confiabilidade": 0.0,
  "relevancia": 0.0,
  "novidade": 0.0,
  "links_relacionados": []
}
```

## Arquitetura tecnica sugerida

### Stack simples e robusta

- **Python** para orquestracao.
- **SQLite** no inicio; migrar para Postgres quando houver historico grande.
- **RSS + APIs + busca web** para coleta.
- **BeautifulSoup / trafilatura** para extrair texto limpo de paginas.
- **OpenAI Responses API** para agentes, resumo, classificacao e roteiro.
- **Text-to-speech** para gerar audio.
- **Cron, GitHub Actions, Windows Task Scheduler ou Cloudflare Workers** para executar diariamente.
- **Markdown/HTML** para relatorio diario.
- **MP3** para podcast.

### Stack recomendada para Evolution API + EasyPanel

Como o usuario ja possui Evolution API e EasyPanel, o melhor caminho pratico muda para uma arquitetura self-hosted:

- **Next.js + React + TypeScript** para a plataforma web.
- **FastAPI + Python** para o robo coletor, curadoria, resumo, roteiro e audio.
- **Postgres** para armazenar noticias, fontes, episodios, scores e historico.
- **Redis + worker** para filas de processamento diario.
- **Evolution API** para enviar resumo, links e audio via WhatsApp.
- **EasyPanel** para deploy dos containers, variaveis de ambiente, dominios HTTPS e volumes.
- **OpenAI Responses API** para curadoria, analise, resumo e roteiro.
- **OpenAI TTS** para gerar o audio em MP3.
- **MinIO, S3 ou storage local persistente** para guardar arquivos MP3 e snapshots de fontes.

Com essa stack, a entrega diaria fica independente da API oficial do WhatsApp Business, reduzindo burocracia. O cuidado e que a Evolution API depende de uma sessao WhatsApp conectada e precisa de monitoramento de conexao.

## Entrega diaria via WhatsApp

Fluxo recomendado:

1. O scheduler dispara o job diario as 7h.
2. O backend coleta as noticias do dia anterior.
3. O sistema gera o briefing, as fontes e o roteiro.
4. O TTS gera o arquivo MP3.
5. O arquivo e salvo em storage publico ou assinado.
6. A Evolution API envia:
   - uma mensagem curta com o resumo do dia;
   - o link da plataforma web;
   - o audio MP3;
   - opcionalmente, um PDF/Markdown com o briefing completo.

Formato ideal da mensagem:

```text
Bom dia. Seu Radar Diario de IA esta pronto.

Top temas:
1. ...
2. ...
3. ...

Resumo completo: https://...
Fontes para validacao: https://...
Audio do dia: enviado abaixo.
```

## Plataforma web de validacao

A plataforma web deve ser o centro de confiabilidade do produto. Ela nao e so um dashboard bonito; e onde o usuario valida o que a IA entregou.

Telas principais:

- **Hoje:** briefing do dia, top noticias, player do audio e status de envio no WhatsApp.
- **Validacao:** cada noticia com resumo da IA ao lado da fonte original.
- **Fontes:** lista de URLs usadas, tipo da fonte, confiabilidade e data de coleta.
- **Historico:** busca por data, tema, empresa, tecnologia e score.
- **Tendencias:** assuntos recorrentes da semana e do mes.
- **Configuracoes:** horario de envio, numero WhatsApp, fontes preferidas, temas prioritarios e tamanho do audio.

Status de validacao por noticia:

- **Pendente:** ainda nao validada pelo usuario.
- **Confiavel:** fonte primaria ou boa evidencia.
- **Duvidosa:** precisa de mais fonte.
- **Descartada:** noticia irrelevante, repetida ou mal sustentada.

## Servicos no EasyPanel

Projeto recomendado no EasyPanel:

```text
radar-tech-ia/
  web           -> Next.js
  api           -> FastAPI
  worker        -> processamento em background
  postgres      -> banco principal
  redis         -> fila/cache
  storage       -> MinIO ou volume persistente
```

Variaveis de ambiente principais:

```text
OPENAI_API_KEY=
DATABASE_URL=
REDIS_URL=
PUBLIC_APP_URL=
EVOLUTION_API_URL=
EVOLUTION_API_KEY=
EVOLUTION_INSTANCE=
WHATSAPP_TARGET_NUMBER=
DAILY_RUN_TIME=07:00
TIMEZONE=America/Rio_Branco
```

## MVP recomendado

Para evitar complexidade cedo demais, construir em fases:

1. **MVP 1 - cerebro do robo**
   - Coleta RSS/APIs.
   - Salva fontes no banco.
   - Gera briefing diario.
   - Gera roteiro.

2. **MVP 2 - audio e WhatsApp**
   - Gera MP3.
   - Envia resumo e audio via Evolution API.
   - Registra status de envio.

3. **MVP 3 - plataforma web**
   - Dashboard React.
   - Tela de validacao de fontes.
   - Historico dos dias anteriores.

4. **MVP 4 - inteligencia editorial**
   - Feedback do usuario.
   - Ajuste de relevancia por preferencia.
   - Consolidado semanal.
   - Deteccao de tendencias recorrentes.

### Execucao diaria

1. Rodar as 7h da manha.
2. Coletar itens das ultimas 24-48 horas.
3. Normalizar e deduplicar.
4. Buscar fonte primaria para cada item.
5. Classificar e pontuar.
6. Selecionar top 8 a 12 noticias.
7. Gerar briefing com fontes.
8. Gerar roteiro conversado.
9. Gerar audio.
10. Salvar tudo em pastas por data:

```text
outputs/
  2026-08-11/
    briefing.md
    fontes.json
    roteiro.md
    episodio.mp3
```

### Rotina de consumo

- **Manha:** receber o briefing e o audio do dia.
- **Durante deslocamento:** ouvir a conversa entre dois personagens.
- **Depois:** abrir apenas as fontes das noticias mais relevantes.
- **Semanalmente:** gerar um consolidado com os temas recorrentes e tecnologias que merecem estudo mais profundo.

## Regras editoriais

- Nao publicar noticia sem URL.
- Distinguir fato, rumor, opiniao e especulacao.
- Preferir fonte primaria.
- Quando houver incerteza, explicitar.
- Nao transformar release de empresa em verdade absoluta.
- Evitar hype.
- Sempre responder: "por que isso importa para mim?"
- Manter um historico para detectar assuntos recorrentes.
- Facilitar a validacao humana: toda noticia relevante precisa ter um link direto para a fonte usada.

## Prompt mestre para criar a ferramenta

Use este prompt em um agente de codigo para construir o sistema:

```text
Atue como um engenheiro senior de software, especialista em agentes de IA, automacao editorial, aprendizado de maquina, redes neurais e curadoria de noticias tecnicas.

Crie uma ferramenta chamada "Radar Tech IA Diario".

Objetivo:
Todos os dias pela manha, a ferramenta deve coletar as noticias relevantes de inteligencia artificial que aconteceram no dia anterior, incluindo aprendizado de maquina, redes neurais, agentes de IA, modelos de linguagem, pesquisa academica, ferramentas para desenvolvedores e tendencias tecnologicas. Depois deve gerar um briefing com fontes, uma analise pratica para desenvolvedores senior e um roteiro em formato de conversa entre dois personagens. Por fim, deve gerar um audio estilo podcast curto para ser ouvido durante deslocamento.

Requisitos funcionais:
1. Coletar noticias das ultimas 24 a 48 horas usando RSS, APIs publicas e busca web.
2. Priorizar fontes primarias: blogs oficiais, documentacao oficial, repositorios, papers e comunicados de empresas.
3. Usar fontes secundarias apenas quando a fonte primaria nao existir ou para contexto.
4. Armazenar todas as fontes em JSON com URL, titulo, fonte, autor, data de publicacao, data de coleta, categoria, confiabilidade e resumo.
5. Remover duplicatas por URL canonica, titulo parecido e conteudo parecido.
6. Classificar cada item nas categorias: IA, machine learning, redes neurais, agentes, devtools, open source, pesquisa, mercado, seguranca, infraestrutura e produto.
7. Pontuar cada item por relevancia, novidade, impacto pratico e confiabilidade.
8. Selecionar as 8 a 12 noticias mais importantes do dia.
9. Gerar um briefing em Markdown com:
   - resumo executivo;
   - principais noticias;
   - por que cada noticia importa;
   - links das fontes;
   - links destacados para validacao humana;
   - secoes "o que testar", "o que estudar" e "o que acompanhar".
10. Criar dois personagens fixos:
   - Lia: pesquisadora de IA, precisa, tecnica e cuidadosa com evidencias.
   - Bruno: desenvolvedor senior, pragmatico, curioso e atento ao impacto real no trabalho.
11. Gerar um roteiro de 8 a 12 minutos em formato de dialogo entre Lia e Bruno.
12. O dialogo deve soar natural, com perguntas, discordancias saudaveis e explicacoes claras.
13. O roteiro deve citar as fontes de forma natural, sem virar leitura de links.
14. Gerar audio MP3 com duas vozes diferentes.
15. Salvar os arquivos por data em outputs/YYYY-MM-DD/.

Requisitos nao funcionais:
1. O sistema deve ser modular, testavel e facil de evoluir.
2. Separar claramente coleta, extracao, curadoria, resumo, roteiro e audio.
3. Incluir logs.
4. Incluir arquivo .env.example.
5. Incluir README com instrucoes de instalacao, execucao manual e agendamento diario.
6. Criar testes unitarios para deduplicacao, classificacao e persistencia.
7. Evitar dependencias desnecessarias.

Arquitetura sugerida:
- Python 3.12+
- SQLite inicialmente
- Pydantic para modelos de dados
- feedparser para RSS
- httpx para HTTP
- trafilatura ou BeautifulSoup para extracao de texto
- OpenAI Responses API para tarefas de IA
- OpenAI text-to-speech para audio
- pytest para testes

Estrutura de arquivos:
src/
  config.py
  models.py
  storage.py
  collectors/
    rss.py
    web_search.py
    arxiv.py
    github.py
  processors/
    extract.py
    dedupe.py
    rank.py
    summarize.py
    script.py
    audio.py
  main.py
prompts/
  curator.md
  analyst.md
  scriptwriter.md
outputs/
tests/
README.md
.env.example

Cuidados editoriais:
- Nunca afirme algo sem fonte.
- Sempre diferencie fato, opiniao e rumor.
- Sempre prefira fonte primaria.
- Seja cético com marketing.
- Diga claramente quando uma noticia ainda nao foi confirmada.
- Escreva para uma pessoa que quer se manter atualizada em tecnologia, mas nao quer desperdiçar tempo com hype.
- Facilite a validacao: ao lado de cada noticia, inclua a fonte original e explique se ela e fonte primaria, imprensa, paper, agregador ou rede social.

Entregue o projeto funcionando, com uma execucao manual via:
python -m src.main

Inclua exemplos de saida em Markdown e JSON.
```

## Prompt do agente curador

```text
Voce e um curador tecnico senior especializado em IA, ML, redes neurais, agentes e ferramentas para desenvolvedores.

Recebera uma lista de itens coletados da internet. Para cada item:
1. identifique se a fonte e primaria, secundaria, agregador, opiniao ou rede social;
2. classifique a categoria tecnica;
3. avalie confiabilidade de 0 a 10;
4. avalie relevancia para um desenvolvedor senior de 0 a 10;
5. avalie novidade de 0 a 10;
6. resuma em ate 4 frases;
7. explique por que importa;
8. indique se deve entrar no briefing diario.

Nao use hype. Nao confunda release comercial com fato tecnico comprovado. Se a fonte nao sustentar uma afirmacao, marque como incerto.
```

## Prompt do roteiro em audio

```text
Transforme o briefing diario em um roteiro de podcast conversado entre dois personagens:

Lia: pesquisadora de IA, precisa, tecnica e cuidadosa com evidencias.
Bruno: desenvolvedor senior, pragmatico, curioso e preocupado com impacto real.

Tom:
- conversa natural;
- inteligente, mas acessivel;
- sem exageros publicitarios;
- com discordancias saudaveis;
- com exemplos praticos;
- duracao estimada de 8 a 12 minutos.

Estrutura:
1. abertura rapida com os 3 temas mais importantes do dia;
2. conversa sobre cada noticia principal;
3. quadro "o que vale testar";
4. quadro "o que vale estudar";
5. fechamento com uma previsao cautelosa do que acompanhar.

Regras:
- Nao invente fatos.
- Use apenas o briefing e as fontes fornecidas.
- Quando houver incerteza, os personagens devem dizer isso.
- As fontes devem ser mencionadas de forma natural.
- Nao leia URLs em voz alta, exceto quando indispensavel.
```

## Proximos passos tecnicos

1. Criar o esqueleto Python do projeto.
2. Definir lista inicial de feeds e APIs.
3. Implementar armazenamento SQLite.
4. Implementar coleta e deduplicacao.
5. Implementar prompts e chamadas ao modelo.
6. Gerar primeiro briefing em Markdown.
7. Adicionar geracao de audio.
8. Agendar execucao diaria.
