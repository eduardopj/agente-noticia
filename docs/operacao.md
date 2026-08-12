# Operacao local

## Regra geral

Nao deixe servidores em background sem necessidade. Para desenvolvimento local, abra dois terminais e rode:

Terminal 1:

```powershell
.\scripts\api-dev.ps1
```

Terminal 2:

```powershell
.\scripts\web-dev.ps1
```

## Rodar o radar manualmente

```powershell
.\scripts\run-daily.ps1
```

Sem `OPENAI_API_KEY`, o sistema gera briefing em modo local, sem resumo avancado e sem audio. Com `OPENAI_API_KEY`, gera resumo, roteiro e MP3.

## Validar

```powershell
.\scripts\test-backend.ps1
cd apps/web
npm run build
npm audit --audit-level=high
```

## URLs locais

- API: `http://127.0.0.1:8000`
- Healthcheck: `http://127.0.0.1:8000/health`
- Web: `http://localhost:3000`

## Endpoints principais

- `POST /jobs/daily-radar`: gera o episodio diario.
- `GET /episodes/latest`: busca o ultimo episodio.
- `GET /episodes/latest/share`: gera mensagem pronta para WhatsApp.
- `POST /deliver/whatsapp/latest`: envia texto e audio pela Evolution API.
- `GET /sources`: lista fontes.
- `PATCH /sources/{source_id}/validation`: atualiza validacao.
- `GET /stats`: estatisticas da plataforma.

## Status de validacao

- `pending`: pendente.
- `trusted`: confiavel.
- `doubtful`: duvidosa.
- `discarded`: descartada.
