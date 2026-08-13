# Descricao completa do agente Radar Tech IA

Documento atualizado em quinta-feira, 13 de agosto de 2026.

## Visao geral

O Radar Tech IA e um agente diario criado para manter um professor e desenvolvedor senior atualizado sobre tecnologia, inteligencia artificial, aprendizado de maquina, redes neurais, agentes de IA, devtools, seguranca, infraestrutura, mercado digital, videos tecnicos e pesquisa academica.

A ideia central e simples: todos os dias pela manha, o sistema coleta fontes recentes, remove repeticoes, seleciona o que parece mais importante, gera um briefing em portugues do Brasil, preserva links para validacao, cria um roteiro conversado entre Lia e Bit, gera audio e envia tudo pelo WhatsApp usando n8n e Evolution API. Alem disso, uma plataforma web guarda o historico dos episodios e permite validar as fontes.

## O que o agente ja faz

- Coleta noticias brasileiras de tecnologia em portais como Canaltech, Tecnoblog, Olhar Digital, TecMundo, G1 Tecnologia, Folha Tecnologia e Baguete.
- Coleta noticias globais e fontes primarias como OpenAI, Google DeepMind, Google AI, Hugging Face, GitHub Blog, MIT Technology Review, The Verge, TechCrunch, Ars Technica, Wired, VentureBeat AI, NVIDIA Blog e BleepingComputer.
- Coleta videos recentes de canais como Filipe Deschamps, Fabio Akita, Gustavo Guanabara / Curso em Video, Mano Deyvin, Codigo Fonte TV, Fireship, Two Minute Papers e Google Developers.
- Coleta artigos academicos de arXiv e tambem tenta enriquecer a parte academica com Crossref, Semantic Scholar, Communications of the ACM, IEEE Spectrum, Nature Machine Intelligence, Nature Technology e MIT Press.
- Busca conteudos recentes em uma janela de ate 7 dias.
- Evita repetir noticias, videos e artigos que ja entraram em episodios anteriores.
- Salva tudo em banco de dados SQLite no servidor.
- Gera briefing escrito com resumo executivo, Brasil, Mundo, IA/devtools, videos, artigos academicos, o que testar, o que estudar, o que acompanhar e fontes para validacao.
- Gera roteiro de podcast em portugues do Brasil com duas vozes: Lia e Bit.
- Gera arquivo de audio em MP3.
- Envia mensagem e audio pelo WhatsApp via Evolution API.
- Mostra plataforma web com episodio em destaque, historico, custos estimados em dolar e real, player de audio, fontes e validacao.
- Permite aprovar todas as fontes de um episodio de uma vez.

## Como funciona o fluxo diario

1. O n8n executa o workflow publicado todos os dias as 07:00.
2. O primeiro no chama a API em `POST /jobs/daily-radar`.
3. A API coleta RSS, YouTube, fontes academicas e indexadores publicos.
4. O pipeline filtra itens recentes, remove duplicatas e evita repeticoes historicas.
5. O curador ranqueia fontes por relevancia, confiabilidade e novidade.
6. O agente de briefing usa OpenAI para criar o resumo estruturado em portugues do Brasil.
7. O agente roteirista transforma o briefing em uma conversa entre Lia e Bit.
8. O agente de audio gera o MP3.
9. O segundo no do n8n chama `POST /deliver/whatsapp/latest`.
10. A API envia o texto, o link do episodio, o link direto do audio e o audio no WhatsApp.
11. A plataforma web passa a exibir o episodio no historico.

## Tecnologias utilizadas

### Backend

- Python.
- FastAPI.
- SQLAlchemy.
- SQLite para persistencia.
- httpx para chamadas HTTP.
- feedparser para RSS.
- OpenAI API para resumo, roteiro e texto para audio.
- Uvicorn para servir a API.

### Frontend

- React.
- Next.js.
- CSS proprio, sem dependencia pesada de UI.
- Server Components e Server Actions para buscar episodios, fontes e atualizar validacao.

### Automacao

- n8n para agendamento e orquestracao diaria.
- Cron diario as 07:00.
- HTTP Request nodes para gerar briefing e disparar WhatsApp.

### WhatsApp

- Evolution API.
- Instancia `WebBot`.
- Envio para o numero configurado no servidor.

### Servidor

- Servidor OVH.
- IP: `149.56.98.229`.
- Usuario: `ubuntu`.
- Caminho da aplicacao: `/opt/radar-tech-ia`.
- Processos gerenciados por PM2.
- API interna na porta `4211`.
- Web interna na porta `4210`.
- Nginx do host faz proxy reverso para as URLs publicas.

URLs publicas:

- Plataforma: `https://radar.149-56-98-229.nip.io`
- API: `https://api-radar.149-56-98-229.nip.io`
- Health check: `https://api-radar.149-56-98-229.nip.io/health`

## Como os dados sao salvos

O banco SQLite fica no servidor e armazena:

- episodios diarios;
- fontes coletadas;
- relacao entre episodio e fontes;
- status de validacao;
- resumo gerado;
- roteiro do audio;
- URL do audio;
- custos estimados;
- tokens usados;
- datas de publicacao, atualizacao e coleta.

Isso permite historico, validacao posterior e evita repeticao de noticias/artigos em novos episodios.

## Como a plataforma web funciona

A pagina principal mostra:

- episodio em destaque;
- player de audio;
- link direto do episodio;
- historico dos episodios;
- custo estimado em dolar e real;
- quantidade de fontes;
- quantidade de fontes academicas;
- filtros por classificacao;
- briefing completo;
- fontes agrupadas por:
  - academicas;
  - portais brasileiros;
  - jornais;
  - videos;
  - fontes primarias;
  - mundo;
  - infraestrutura e seguranca;
  - outras.

Cada fonte pode ser marcada como confiavel, duvidosa ou descartada.

## Avaliacao do briefing de hoje

O briefing de quarta-feira, 12 de agosto de 2026 funcionou tecnicamente: coletou fontes, gerou texto, criou audio, salvou no banco, apareceu na web e enviou mensagem pelo WhatsApp.

Mas a qualidade editorial ficou abaixo do desejado. O conteudo ficou superficial em varios pontos, com muitas chamadas e pouco entendimento real. Em alguns temas, nao deu para compreender bem o contexto, a consequencia pratica, o que muda para professor/desenvolvedor e qual acao tomar depois. O audio tambem soou mecanico demais, mais perto de leitura de lista do que de uma conversa humana.

Essa avaliacao precisa guiar a evolucao do agente: ele nao deve apenas listar noticias. Ele precisa explicar, contextualizar, comparar, apontar incertezas e transformar informacao em entendimento.

## Melhorias ja aplicadas nos prompts

Foram reforcadas as instrucoes para o briefing:

- evitar resumo superficial;
- explicar o que aconteceu;
- explicar por que importa;
- mostrar quem e afetado;
- apontar riscos e oportunidades;
- indicar o que acompanhar em seguida;
- preferir menos itens com mais profundidade quando houver muitas fontes;
- detalhar melhor artigos academicos com objetivo, metodologia, discussoes, resultados, conclusao e futuro.

Tambem foram reforcadas as instrucoes para o audio:

- aumentar o roteiro para 6 a 8 minutos;
- evitar empilhar manchetes;
- dar contexto suficiente para entender sem abrir links;
- usar transicoes mais naturais;
- deixar Bit com cadencia acreana/Rio Branco de forma sutil;
- humanizar a fala sem caricatura;
- evitar bordoes e girias artificiais;
- manter uma conversa de deslocamento, mas com profundidade.

## O que pode evoluir

### Qualidade editorial

- Criar uma etapa intermediaria de analise profunda antes do briefing.
- Fazer o agente responder, para cada topico: fato, contexto, impacto, risco, oportunidade, acao recomendada e fonte.
- Limitar o numero de topicos principais para aumentar profundidade.
- Criar uma nota editorial diaria: "por que isso entra no radar de um professor/desenvolvedor".

### Fontes academicas

- Adicionar APIs oficiais quando houver credenciais ou acesso institucional.
- Integrar OpenAlex para ampliar metadados de pesquisa.
- Integrar Papers with Code para conectar papers a codigo, datasets e benchmarks.
- Guardar DOI, venue, citacoes e area academica em campos proprios.
- Criar filtro separado para surveys, benchmarks, modelos novos, datasets e aplicacoes educacionais.

### Audio

- Ajustar vozes para ficarem menos roboticas.
- Testar vozes diferentes do modelo TTS.
- Adicionar marcas de pausa no roteiro.
- Criar um "modo conversa acreana" mais natural, com ritmo de Rio Branco, sem exagero.
- Gerar um audio unico mais leve, com fallback em partes somente quando necessario.

### Plataforma web

- Criar pagina individual com rota propria por episodio, por exemplo `/episodios/2026-08-13`.
- Criar busca por palavra-chave.
- Criar filtro por fonte, assunto, confiabilidade e tipo.
- Criar painel de custos por mes.
- Mostrar evolucao dos temas ao longo dos dias.
- Permitir anotacoes do professor em cada fonte.
- Criar exportacao em PDF ou Markdown para aula.

### Governanca e confiabilidade

- Registrar motivo da selecao de cada fonte.
- Guardar hash de titulo/link para deduplicacao mais forte.
- Criar status "revisado pelo professor".
- Criar alerta quando uma fonte for agregador e nao fonte primaria.
- Criar nota de confiabilidade explicada, nao apenas numerica.

## Objetivo final

O objetivo do Radar Tech IA nao e ser apenas um robo que manda links. Ele deve funcionar como um assistente editorial diario: coleta, organiza, explica, contextualiza, grava, entrega e preserva fontes para validacao.

O resultado ideal e que o professor consiga ouvir o audio no caminho, entender o que realmente importa, abrir a plataforma quando quiser validar fontes, e transformar parte do conteudo em aula, estudo, pesquisa ou decisao tecnica.
