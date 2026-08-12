# Agentes do Radar Tech IA Diario

## Coletor geral

Busca noticias em feeds RSS e fontes tecnicas. Prioriza fonte primaria quando disponivel.

## Coletor academico

Busca artigos recentes em arXiv, RSS academicos e indexadores publicos como Crossref e Semantic Scholar, cobrindo editoras e veiculos como ACM, IEEE, Nature, Springer, Elsevier, MIT Press e Communications of the ACM quando houver itens recentes. O coletor prioriza pesquisas ligadas a:

- IA;
- machine learning;
- processamento de linguagem natural;
- visao computacional;
- redes neurais;
- agentes de IA;
- modelos de linguagem.

Os artigos podem estar em ingles, mas resumo, impacto e conversa final devem ser em portugues do Brasil.

Para cada pesquisa selecionada, o briefing deve trazer titulo original, fonte/editora, autores, data brasileira de publicacao/atualizacao, objetivo, metodologia, discussoes e principais resultados, conclusao curta, proximos caminhos e link de validacao. Se a fonte nao fornecer abstract ou detalhes suficientes, o texto deve marcar `nao informado no resumo disponivel`.

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
