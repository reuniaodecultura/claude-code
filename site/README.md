# site/ — código-fonte das páginas do reuniaodecultura.com

Esta pasta é a **fonte da verdade** do HTML publicado no Hostinger. O fluxo é
**editar → aprovar → publicar**, todo pelo GitHub (o pipeline roda nos
servidores do GitHub Actions, então não sofre o bloqueio de rede do ambiente).

```
site/index.html, site/obrigado.html
        │  edição numa branch
        ▼
   Pull Request   ← você revê o diff e APROVA
        │  merge na branch de produção (main)
        ▼
 GitHub Actions (hostinger-deploy) → FTPS → public_html no Hostinger
```

## Configuração (uma vez)

1. **Secrets** em *Settings → Secrets and variables → Actions → New repository secret*:
   - `HOSTINGER_FTP_HOST` — host/IP de FTP (hPanel → Arquivos → Contas de FTP)
   - `HOSTINGER_FTP_USER` — usuário de FTP
   - `HOSTINGER_FTP_PASS` — senha de FTP
   - (opcional) variável `HOSTINGER_REMOTE_DIR` se as páginas não estiverem em `public_html`.
2. *Settings → Actions → General → Workflow permissions*: marque
   **Read and write** e **Allow GitHub Actions to create and approve pull requests**
   (necessário para o import abrir PR).
3. (Opcional, portão de aprovação) *Settings → Environments → New environment →*
   `production` → **Required reviewers** = você. Assim a publicação espera seu
   "Approve" mesmo após o merge.

## Uso

- **Semear o repo com o que já está no ar:** aba *Actions* →
  *Hostinger · Importar páginas ao vivo* → **Run workflow**. Ele abre um PR com
  o `index.html` e o `obrigado.html` atuais.
- **Mudar algo:** edite `site/index.html` / `site/obrigado.html` numa branch,
  abra PR, revise e faça merge. A publicação no Hostinger é automática.

## Segurança

Use uma **conta de FTP dedicada** (limitada a `public_html`) e troque/remova
após o uso. Os secrets ficam no GitHub, nunca no código.
