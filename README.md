# Guia Prático de Diretrizes da LGPD para Desenvolvedores

**Site:*https://viniciusoliver13.github.io/guia-pratico-para-desenvolvedores/* 

Guia para equipes de desenvolvimento aplicarem a Lei Geral de Proteção de Dados Pessoais (LGPD) nas etapas de requisitos, arquitetura e implementação de sistemas de informação. São 30 fichas de diretrizes e um *checklist* de 89 itens. Cada item indica onde procurar a evidência de atendimento: no código, no repositório, no banco de dados, na configuração, na infraestrutura ou em um documento.

O guia foi elaborado como produto de um Trabalho de Conclusão de Curso (TCC) e avaliado em um estudo de caso.

> **Aviso:** o guia apoia a adequação técnica de sistemas à LGPD, mas não substitui orientação jurídica. Ele não foi revisado por especialista da área do Direito, e atender aos seus itens não garante a conformidade com a lei.

## O que o site oferece

- **Início:** Apresentação e Como usar.
- **Etapa de Preparação:** o que levantar antes de aplicar as diretrizes.
- **Fichas:** as 30 diretrizes, com filtros por etapa e por forma de verificação, busca por texto e destaque para as 4 diretrizes condicionais.
- **Checklist:** os 89 itens, que podem ser marcados como "atende", "não atende" ou "não se aplica" e baixados em CSV. As marcações ficam salvas só no seu navegador e não são enviadas a nenhum servidor.
- **Fontes e limites** e **Referências.**

## Versão

O site publica a **versão do guia avaliada no TCC** (texto de 28/10/2026), sem ajustes posteriores. O texto é copiado do `guia-pratico.pdf`, que é a fonte de referência. O site não acrescenta conteúdo ao guia.


## Estrutura do repositório

| Caminho | Conteúdo |
|---|---|
| `index.html` e demais `.html` | páginas do site, já geradas |
| `guia-fichas.json` | dados das 30 fichas, lidos pelas páginas Fichas e Checklist |
| `guia-pratico.pdf` | o guia completo, fonte de todo o texto |
| `verificar_texto.py` | confere se o texto do site está no PDF |
| `textos_interface.txt` | textos da interface que o verificador ignora |
| `ferramentas/gerar_paginas.py` | gera as páginas de texto a partir do PDF |

## Para quem mantém o site

O site não tem etapa de *build*: as páginas publicadas já estão no repositório. Os passos abaixo só são necessários quando o guia mudar.

### 1. Gerar as páginas de texto de novo

As páginas Início, Etapa de Preparação, Fontes e limites e Referências, e o índice lateral, são geradas a partir do PDF:

```bash
python3 ferramentas/gerar_paginas.py
```

### 2. Conferir o texto

Depois de qualquer mudança, confira se todo o texto do site está no PDF:

```bash
python3 verificar_texto.py guia-pratico.pdf .
```

O resultado esperado é "Todo o texto do site está no PDF do guia." O script precisa do `pdftotext`, do pacote `poppler-utils`. Um texto novo de interface, como o rótulo de um botão, deve ser acrescentado ao `textos_interface.txt`.

### 3. Ver localmente

As páginas Fichas e Checklist carregam o `guia-fichas.json` pela rede, e os navegadores bloqueiam isso quando a página é aberta direto do disco. Para testar, rode um servidor local na pasta do repositório:

```bash
python3 -m http.server 8000
```

e abra `http://localhost:8000/`.

## Autoria

Antonio Vinícius Oliveira Lima, com orientação do prof. José Ferdinandy Silva Chagas.