# Evolution API

## Informacoes extraidas do workflow WebBot

Arquivo analisado: `C:\Users\eduar\Downloads\WebBot.json`

URL base encontrada:

```text
https://evolution-evolution.h9te5z.easypanel.host
```

Padrao de envio de texto encontrado:

```text
POST /message/sendText/{instance}
header: apikey
body:
{
  "number": "55...",
  "text": "mensagem"
}
```

Outros endpoints usados no workflow existente:

```text
POST /chat/sendPresence/{instance}
POST /chat/markMessageAsRead/{instance}
POST /instance/setPresence/{instance}
```

## Variaveis que ainda precisam ser preenchidas

No `.env`:

```text
EVOLUTION_API_KEY=
EVOLUTION_INSTANCE=
WHATSAPP_TARGET_NUMBER=
```

O arquivo exportado do n8n nao trouxe a chave real nem o nome da instancia como valor fixo. Ele usa:

```text
$('Webhook').item.json.body.apikey
$('Webhook').item.json.body.instance
```

Ou seja: esses valores chegam dinamicamente no webhook do WebBot, mas precisam ser configurados manualmente neste projeto para envio diario automatico.

## Diagnostico de 12 de agosto de 2026

Teste executado com as variaveis atuais do `.env`:

- OpenAI: autenticacao funcionando.
- Evolution API: retornou `401 Unauthorized` em `/instance/fetchInstances`.
- Evolution instance: o valor `1625913A1AD5-4287-86F1-C87611842C61` retornou `404`, indicando que isso parece ser um `instanceId` interno, nao o nome da instancia usado nas URLs da Evolution.

Correcoes necessarias:

```text
EVOLUTION_API_KEY=<chave correta da Evolution>
EVOLUTION_INSTANCE=<nome da instancia, nao instanceId interno>
```

Resolvido no `.env`:

```text
EVOLUTION_INSTANCE=WebBot
```

Estado retornado pela Evolution:

```text
instanceName=WebBot
state=open
```

Na Evolution Manager, procure pelo nome da instancia conectada. Normalmente e o nome exibido na lista de instancias, usado em rotas como:

```text
/message/sendText/NOME_DA_INSTANCIA
```

No EasyPanel, procure a chave em variaveis como:

```text
AUTHENTICATION_API_KEY
API_KEY
```

## Webhook do n8n informado

URL informada pelo usuario:

```text
https://primary-production-c02dc.up.railway.app/webhook/5400296b-1798-4bc7-bf72-e933686fa8b4
```

Essa URL corresponde ao `Webhook` do workflow `WebBot`, pois o arquivo exportado tem o mesmo path:

```text
5400296b-1798-4bc7-bf72-e933686fa8b4
```

Importante: essa URL nao e a URL base da Evolution API. Ela e a entrada do n8n que recebe eventos/mensagens. A Evolution API continua sendo:

```text
https://evolution-evolution.h9te5z.easypanel.host
```

Para o Radar Tech IA Diario, o caminho recomendado e usar o n8n como agendador chamando os endpoints da nossa API. O webhook do `WebBot` pode servir como referencia, mas nao deve ser usado como endpoint de envio do resumo diario sem adaptar o workflow.
