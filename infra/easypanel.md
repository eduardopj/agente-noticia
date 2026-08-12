# Deploy no EasyPanel

## Servicos

Crie os servicos abaixo no projeto `radar-tech-ia`:

- `postgres`: banco Postgres 16.
- `redis`: cache/fila para evolucao futura.
- `api`: app Docker usando `apps/api/Dockerfile`.
- `web`: app Docker usando `apps/web/Dockerfile`.
- `n8n`: workflow de agenda e envio.

## Variaveis da API

```text
APP_ENV=production
DATABASE_URL=postgresql+psycopg://USER:PASSWORD@HOST:5432/DATABASE
STORAGE_DIR=/app/storage
API_BASE_URL=https://api.seudominio.com
PUBLIC_APP_URL=https://radar.seudominio.com
OPENAI_API_KEY=...
EVOLUTION_API_URL=https://evolution.seudominio.com
EVOLUTION_API_KEY=...
EVOLUTION_INSTANCE=...
WHATSAPP_TARGET_NUMBER=55XXXXXXXXXXX
TIMEZONE=America/Rio_Branco
```

## Volumes

No servico `api`, crie um volume persistente:

```text
/app/storage
```

Esse volume guarda os audios MP3 e artefatos gerados.

## Dominios

- `web`: porta 3000, dominio publico da plataforma.
- `api`: porta 8000, dominio publico ou privado acessivel pelo n8n.

## n8n

Importe `infra/n8n/daily-radar.workflow.json`.

Configure credenciais/variaveis:

- `API_BASE_URL`
- `EVOLUTION_API_URL`
- `EVOLUTION_API_KEY`
- `EVOLUTION_INSTANCE`

O workflow deve rodar diariamente as 7h no fuso do projeto. Mensagens, briefing e datas devem sair em portugues do Brasil.
