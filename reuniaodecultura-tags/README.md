# Tags de conversão e métricas — reuniaodecultura.com

O site **reuniaodecultura.com está hospedado no Hostinger**, então estes arquivos
são **referência/backup versionado**. O código real precisa ser colado nos arquivos
`index.html` e `obrigado.html` pelo **Gerenciador de Arquivos do hPanel**.

## Arquivos

| Arquivo | Onde colar | O que faz |
|---|---|---|
| `index.html-snippets.html` | `public_html/index.html` | GTM + GA4 + evento de conversão no **envio do formulário de inscrição** (`generate_lead` / `form_inscricao`) |
| `obrigado.html-snippets.html` | `public_html/obrigado.html` | GTM + GA4 + **conversão do Google Ads** disparada no carregamento da página de confirmação |

## Placeholders a substituir

| Placeholder | Onde encontrar |
|---|---|
| `GTM-XXXXXXX` | Painel do Google Tag Manager (topo) |
| `G-XXXXXXXXXX` | GA4 → Administrador → Fluxos de dados → seu site |
| `AW-XXXXXXXXX` | Google Ads → Metas → Conversões → ação → Configurar tag |
| `AW-XXXXXXXXX/AbC-D_efG-h1i2` | Mesmo lugar: Conversion ID **/** Conversion Label da ação de "inscrição" |

## Passo a passo no Hostinger

1. **hPanel** → **Gerenciador de Arquivos** → pasta `public_html`.
2. Clique com o botão direito em `index.html` → **Editar**.
3. Cole os blocos conforme os comentários (`<head>` e início/fim do `<body>`).
4. Ajuste o seletor do `<form>` no BLOCO 4 se o formulário tiver um `id`.
5. Repita com `obrigado.html` usando `obrigado.html-snippets.html`.
6. Salve e teste (veja abaixo).

> Se o site usa o **Hostinger Website Builder** (não HTML manual), use
> **Configurações → Integrações** para colar GTM/GA4, ou o bloco de "Código
> personalizado" para inserir os snippets.

## Como validar

- **GTM/GA4:** instale a extensão **Google Tag Assistant** (tagassistant.google.com)
  e navegue pelo site; confirme que o container GTM e a tag GA4 disparam.
- **GA4 em tempo real:** GA4 → Relatórios → **Tempo real**; faça uma inscrição de
  teste e veja os eventos `generate_lead` (index) e `sign_up` (obrigado).
- **Google Ads:** Google Ads → Metas → Conversões → a ação deve sair de
  "Sem atividade recente" depois de uma conversão de teste (pode levar horas).

## Evitar contagem dupla

GA4 e Google Ads podem ser disparados **via GTM** (recomendado) **ou** direto no
HTML (gtag.js). Não use os dois caminhos para a mesma tag — escolha um. Os
comentários nos snippets indicam quais blocos omitir em cada caso.
