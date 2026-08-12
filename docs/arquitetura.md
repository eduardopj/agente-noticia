# Arquitetura do Radar Tech IA Diario

## Separacao de responsabilidades

### Frontend

Responsavel pela experiencia de validacao:

- dashboard do dia;
- player de audio;
- briefing;
- fontes;
- historico;
- status de envio.

Tecnologia: Next.js, React e TypeScript.

### Backend

Responsavel por API, persistencia e integracoes:

- endpoints para episodios;
- endpoints para fontes;
- job diario;
- entrega via Evolution API;
- arquivos estaticos de audio.

Tecnologia: FastAPI, SQLAlchemy e Postgres.

### Agentes de IA

Responsaveis pela inteligencia editorial:

- coletor geral;
- coletor academico;
- curador;
- sumarizador;
- roteirista;
- gerador de audio.

Tecnologia: Python, OpenAI Responses API e OpenAI TTS.

### Automacao

Responsavel pelo horario e orquestracao:

- n8n dispara o job diario;
- n8n chama a entrega via WhatsApp;
- EasyPanel hospeda os servicos.

O n8n nao contem a inteligencia editorial. Ele apenas agenda e chama os endpoints:

1. `POST /jobs/daily-radar`
2. `POST /deliver/whatsapp/latest`

Assim a regra de negocio fica versionada em codigo e o workflow visual permanece simples.

## Regra de idioma

Toda saida final para usuario deve estar em portugues do Brasil. Isso inclui:

- datas;
- horas;
- mensagens de WhatsApp;
- briefing;
- roteiro;
- interface web;
- erros exibidos ao usuario.

## Academico

Artigos em ingles devem manter:

- titulo original;
- autores;
- link;
- fonte;
- data de publicacao.

O resumo, impacto e conversa devem ser em portugues do Brasil.
