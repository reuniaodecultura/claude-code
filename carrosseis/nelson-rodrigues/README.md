# Carrossel Instagram — Nelson Rodrigues

Carrossel de 8 cards para o perfil **Reunião de Cultura**.

## Arquivos

| Arquivo | O que é |
| --- | --- |
| `index.html` | Fonte dos 8 cards. Um `<div class="card">` por card, canvas fixo 1080×1350. |
| `png/card-01.png` … `card-08.png` | Os 8 cards exportados, 1080×1350 (4:5), prontos para postar. |
| `canva.html` | Variante para importar no Canva — mesmo layout, fontes trocadas. |
| `legenda.md` | Legenda + hashtags, com um ponto de atenção no 3º parágrafo. |

## Variante Canva (`canva.html`)

Design importado: https://www.canva.com/d/6uzq0M-GKGvRe3i (8 páginas editáveis)

Duas diferenças em relação ao `index.html`, e as duas são exigência do importador:

1. **Fontes.** O kit da Adobe Fonts é travado por domínio, então o Canva não
   consegue resolvê-lo — a primeira importação caiu inteira numa sans genérica.
   A variante usa famílias que existem tanto no Google Fonts quanto na
   biblioteca do Canva, então o nome casa mesmo sem baixar o webfont:

   | Papel | `index.html` | `canva.html` |
   | --- | --- | --- |
   | Display e manchete | Miller Display / Headline | Playfair Display |
   | Texto corrido | Miller Text | PT Serif |
   | Chapéus | Acumin Pro Condensed | Oswald |
   | Fólio e cabeçalho | News Gothic Std | Archivo |

   Playfair e PT Serif compõem mais largo que Miller no mesmo corpo, então os
   tamanhos de display caem de 10% a 15% para as linhas longas continuarem
   dentro da coluna de 904 px.

2. **Capitular do card 3.** O importador ignora `float`, e a capitular caía por
   cima do parágrafo. Na variante ela virou uma linha flex com a letra em caixa
   própria de largura fixa.

Cada card leva `data-document-role="page"` e um `data-label`, que é o que faz o
Canva criar 8 páginas em vez de uma rolagem única.

Para reimportar depois de editar: use a URL crua fixada no SHA do commit
(`raw.githubusercontent.com/<owner>/<repo>/<sha>/…`) — a URL por branch fica em
cache no CDN e serve a versão antiga.

## Direção de arte

Estética de jornal brasileiro dos anos 1930–40: papel envelhecido, tipografia serifada de
manchete, fios grossos e finos, sem nenhuma foto de pessoa.

| | |
| --- | --- |
| Formato | 1080 × 1350 px (4:5) |
| Papel | `#F5EFE0` com manchas de envelhecimento e vinheta nas bordas |
| Tinta | `#1A1A1A` |
| Vermelho manchete | `#B3261E` |
| Margem de texto | 88 px nas laterais |

### Tipografia (Adobe Fonts, kit `ksh4kev`)

| Papel na página | Fonte |
| --- | --- |
| Display (capa, ano, título, citação) | Miller Display Bold |
| Manchete dos cards | Miller Headline Bold / Light |
| Texto corrido | Miller Text Roman / Bold / Italic |
| Chapéus e etiquetas | Acumin Pro Condensed Bold |
| Fólio e cabeçalho | News Gothic Std Bold |

Miller é o Scotch Roman de Matthew Carter (Carter & Cone) — a família desenhada justamente
para manchete e texto de jornal, o que ancora o carrossel no período sem virar pastiche.

## Estrutura dos cards

1. **Capa** — masthead + "NELSON RODRIGUES" em display, deck com a frase-isca
2. **1929** — o ano em vermelho gigante; o irmão baleado na redação
3. **A escola** — repórter policial aos 13, com capitular
4. **A estreia** — anúncio teatral centrado: 28/12/1943, *Vestido de Noiva*
5. **Três planos** — três colunas: realidade / memória / alucinação
6. **O que veio depois** — razão tabular: 17 peças, censura, escândalo
7. **A citação** — "Toda unanimidade é burra", em destaque
8. **Fechamento** — a pergunta, o CTA e a assinatura

## Regerar os PNGs

Os cards são renderizados a partir do HTML com Chromium headless (Playwright), fotografando
cada `.card` em 1080×1350. Ao editar `index.html`, exporte de novo para manter os PNGs em dia.

## Checagem de fatos

Conferido: nascimento (Recife, 1912) e morte (Rio, 1980); estreia de *Vestido de Noiva* em
28 de dezembro de 1943 no Theatro Municipal do Rio, direção de Ziembinski; as 17 peças;
*A Vida Como Ela É...*; a autoria de "toda unanimidade é burra".

**A verificar:** o card 2 diz que Roberto morreu "três dias depois" do tiro (dezembro de
1929). A maior parte dos relatos dá a morte no dia seguinte. O texto foi mantido como
enviado — vale confirmar antes de publicar.
