# Deploy no servidor OVH

Servidor:

- SSH: configure em `RADAR_SSH_HOST`
- Chave: configure em `RADAR_SSH_KEY`
- Diretorio da aplicacao: `/opt/radar-tech-ia`
- API interna: `127.0.0.1:4101`
- Web interna: `127.0.0.1:4100`
- API publica: configure em `RADAR_API_URL`
- Web publica: configure em `RADAR_WEB_URL`

O servidor e compartilhado. Nao use Docker nem tente ocupar as portas 80/443.
O nginx do host deve fazer proxy para as portas internas acima.

## Primeiro deploy

No computador local:

```bash
bash update.sh
```

Exemplo com nip.io:

```bash
RADAR_SSH_HOST=ubuntu@SEU_IP \
RADAR_SSH_KEY=~/.ssh/ovh-acp \
RADAR_API_URL=https://api-radar.SEU_IP_COM_HIFENS.nip.io \
RADAR_WEB_URL=https://radar.SEU_IP_COM_HIFENS.nip.io \
bash update.sh
```

No primeiro deploy, o script cria `/opt/radar-tech-ia/ecosystem.config.cjs` a
partir de `ecosystem.config.example.cjs`.

Depois entre no servidor e edite os segredos reais:

```bash
ssh -i ~/.ssh/ovh-acp ubuntu@SEU_IP
nano /opt/radar-tech-ia/ecosystem.config.cjs
pm2 startOrReload /opt/radar-tech-ia/ecosystem.config.cjs --update-env
pm2 save
```

## Variaveis necessarias

Configure no `ecosystem.config.cjs` do servidor:

```env
APP_ENV=production
APP_NAME=Radar Tech IA
PUBLIC_APP_URL=https://radar.example.com
API_BASE_URL=https://api-radar.example.com
DATABASE_URL=sqlite:////opt/radar-tech-ia/radar.db
STORAGE_DIR=/opt/radar-tech-ia/storage
TIMEZONE=America/Rio_Branco
OPENAI_API_KEY=
OPENAI_SUMMARY_MODEL=gpt-5-mini
OPENAI_TTS_MODEL=gpt-4o-mini-tts
OPENAI_TTS_VOICE_LIA=nova
OPENAI_TTS_VOICE_BRUNO=onyx
EVOLUTION_API_URL=https://evolution-evolution.h9te5z.easypanel.host
EVOLUTION_API_KEY=
EVOLUTION_INSTANCE=WebBot
WHATSAPP_TARGET_NUMBER=
```

## Nginx

Use `infra/ovh-nginx.conf` como base. Copie para o servidor:

```bash
sudo cp /opt/radar-tech-ia/infra/ovh-nginx.conf /etc/nginx/sites-available/radar-tech-ia
sudo ln -s /etc/nginx/sites-available/radar-tech-ia /etc/nginx/sites-enabled/radar-tech-ia
sudo nginx -t
sudo systemctl reload nginx
```

Se usar Certbot, emita HTTPS apenas para estes hosts:

```bash
sudo certbot --nginx -d api-radar.example.com -d radar.example.com
```

## Testes

```bash
curl http://127.0.0.1:4101/health
curl https://api-radar.example.com/health
pm2 status
```
