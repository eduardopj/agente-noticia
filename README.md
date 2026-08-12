# Radar Tech IA Diario

Sistema diario para coletar noticias e artigos academicos sobre IA, ML, redes neurais, agentes, devtools e tecnologia. Ele gera briefing em portugues do Brasil, preserva fontes para validacao, cria roteiro em formato de conversa e envia texto/audio via Evolution API usando n8n.

## Arquitetura

- `apps/api`: FastAPI + agentes Python.
- `apps/web`: Next.js + React para validacao e historico.
- `infra`: Docker Compose, EasyPanel e workflow n8n.
- `prompts`: prompts editoriais dos agentes.

## Fluxo diario

1. n8n dispara o job pela manha.
2. API coleta noticias gerais e artigos academicos.
3. Agentes deduplicam, ranqueiam, resumem e geram roteiro.
4. API gera ou registra audio.
5. n8n envia resumo e audio pela Evolution API.
6. Plataforma web exibe fontes, resumo e validacao.

## Regra de idioma e datas

Todo texto final deve ser em portugues do Brasil. Datas e horas exibidas ao usuario, enviadas no WhatsApp ou geradas no briefing devem usar formato brasileiro, por exemplo: `quarta-feira, 12 de agosto de 2026, as 07:00`.

## Execucao local

Ambiente local do backend:

```powershell
cd apps/api
python -m venv .venv
.\.venv\Scripts\pip install -e ".[dev]"
```

Backend:

```powershell
.\scripts\api-dev.ps1
```

Frontend:

```powershell
cd apps/web
npm install
cd ..\..
.\scripts\web-dev.ps1
```

Job manual:

```powershell
.\scripts\run-daily.ps1
```

Testes:

```powershell
.\scripts\test-backend.ps1
cd apps/web
npm run build
```

Teste de integracoes:

```powershell
.\apps\api\.venv\Scripts\python.exe scripts\check-integrations.py
```

Esse comando mascara chaves na saida e verifica OpenAI e Evolution API.

Teste de envio WhatsApp:

```powershell
.\apps\api\.venv\Scripts\python.exe scripts\send-whatsapp-test.py
```

## Entrega diaria via n8n

Importe `infra/n8n/daily-radar.workflow.json`, ajuste:

- URL da API;
- URL da Evolution API;
- API key da Evolution;
- instancia;
- numero de destino.

## Escopo academico

O coletor academico consulta arXiv para temas como:

- artificial intelligence;
- machine learning;
- neural networks;
- large language models;
- AI agents;
- reinforcement learning;
- computer vision;
- natural language processing.

Artigos em ingles sao resumidos em portugues do Brasil, mantendo titulo original, link, autores e uma explicacao pratica para professor/desenvolvedor.
