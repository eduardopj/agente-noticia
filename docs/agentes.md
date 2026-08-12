# Agentes do Radar Tech IA Diario

## Coletor geral

Busca noticias em feeds RSS e fontes tecnicas. Prioriza fonte primaria quando disponivel.

## Coletor academico

Busca artigos recentes no arXiv em categorias e consultas ligadas a:

- IA;
- machine learning;
- processamento de linguagem natural;
- visao computacional;
- redes neurais;
- agentes de IA;
- modelos de linguagem.

Os artigos podem estar em ingles, mas resumo, impacto e conversa final devem ser em portugues do Brasil.

## Curador

Remove duplicatas, classifica fonte, categoria, confiabilidade, relevancia e novidade.

## Analista

Explica por que a noticia ou artigo importa para:

- professor;
- desenvolvedor senior;
- pesquisador aplicado;
- pessoa que quer estudar tendencias.

## Roteirista

Transforma o briefing em conversa entre Lia e Bit.

## Audio

Gera MP3 com vozes diferentes para Lia e Bit quando o roteiro estiver marcado como:

```text
Lia: fala da Lia
Bit: fala do Bit
```

## Entregador

Envia a mensagem diaria e o audio pela Evolution API. O n8n agenda e dispara a entrega.
