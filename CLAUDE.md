# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository layout

This is a fork of `anthropics/claude-code`. Most top-level content (`plugins/`,
`scripts/`, `examples/`, `Script/`, `CHANGELOG.md`, `feed.xml`, `.github/`) is
upstream Claude Code material. The **active, project-specific work** lives in two
places:

- **`debate-module/`** — a Next.js + Supabase debate-chat app (the
  "Reunião de Cultura" platform). This is where almost all application code is.
- **`docs/index.html`** — a separate, self-contained single-file React app
  ("Chat de Debates") that loads React and `@supabase/supabase-js` from a CDN via
  an `importmap` (no build step). It talks directly to a hard-coded Supabase
  project. Edit it as one standalone HTML file; it is not part of the Next.js build.
- **`reuniaodecultura-tags/`** — paste-ready GA4 / GTM / Google Ads conversion
  snippets for the `reuniaodecultura.com` site, which is **hosted on Hostinger,
  not in this repo**. These are reference/backup files; the live files are edited
  in the Hostinger hPanel File Manager.

The root `package.json` is a thin proxy: `dev`/`build`/`start` just forward to
`debate-module` (this is what Vercel runs via `vercel.json`).

## Commands

All app commands run inside `debate-module/` (or via the root proxy scripts):

```bash
# from repo root (proxies into debate-module)
npm run dev        # next dev — http://localhost:3000
npm run build      # installs deps in debate-module, then next build

# from debate-module/
npm run dev
npm run build
npm run start
npm run lint       # eslint (flat config, eslint-config-next)
```

There is **no test runner configured** — no `test` script and no test files exist.
Do not assume Jest/Vitest; if asked to add tests, set up the tooling first.

The Supabase schema is **not** applied automatically. Apply
`debate-module/supabase/migrations/001_initial_schema.sql` to the Supabase project
before the app will work.

### Required environment variables (`debate-module/.env.local`)

- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_ANON_KEY`
- `SUPABASE_SERVICE_ROLE_KEY` (server-only; used by the admin client)

The app degrades gracefully when these are missing: `proxy.ts` and the server
client short-circuit instead of throwing, so a missing env var shows as "not
configured" rather than a crash.

## Next.js version warning

Per `debate-module/AGENTS.md`: this is **not** the Next.js you may know from
training data (it tracks a very new major — `next@16`, `react@19`). APIs,
conventions, and file structure may differ. Read the relevant guide in
`debate-module/node_modules/next/dist/docs/` before writing Next.js code, and
heed deprecation notices.

## debate-module architecture

App Router (`src/app/`) with three areas: public debate browsing
(`/debates/...`), an `/admin` console (themes, debates, users, moderation), and
`/auth` (Supabase email/OAuth login, callback, signout).

### Three Supabase clients — pick deliberately

This is the most important pattern to get right (`src/lib/supabase/`):

- **`client.ts` → `getSupabaseBrowserClient()`** — browser, anon key. Used by
  client components and the realtime hook. Subject to Row Level Security (RLS).
- **`server.ts` → `getSupabaseServerClient()`** — SSR, anon key + request
  cookies. Used in Server Components and most Server Actions. Acts **as the logged-in
  user** and is subject to RLS.
- **`admin.ts` → `getSupabaseAdminClient()`** — service-role key, **bypasses RLS**.
  Server-only; never import into client code. Use **only** for privileged
  moderation/admin operations.

Rule of thumb: ordinary user actions (send message, toggle reaction) go through
the **server** client so RLS enforces permissions; moderation that must override
RLS (hiding/deleting others' messages) goes through the **admin** client. See
`src/lib/actions/messages.ts` for both styles side by side.

### Server Actions

Mutations live in `src/lib/actions/*.ts`, each marked `'use server'`. They return
`{ error }` / `{ success }` shaped objects (error strings are in Portuguese) rather
than throwing, and call `revalidatePath(...)` after admin writes to refresh cached
Server Component data.

### Security model is RLS-first

`supabase/migrations/001_initial_schema.sql` is the source of truth for
authorization. Roles (`admin`, `moderator`) live in the `user_roles` table, and
policies reference it (e.g. only admins manage themes/debates; only the author can
edit a message, and only within 5 minutes). A trigger (`handle_new_user`)
auto-creates a `profiles` row on signup. When changing who-can-do-what, update the
RLS policies — not just the UI or actions.

### Realtime

`src/lib/hooks/useDebateRoom.ts` subscribes to a per-debate channel
(`debate:${debateId}`) and merges Postgres `INSERT`/`UPDATE`/`DELETE` events for
`messages` and `reactions` into local state. Only `messages` and `reactions` are
in the `supabase_realtime` publication (see the migration). Reaction counts are
derived client-side in the hook, not read from the `message_reaction_counts` view.

### Session refresh

`src/proxy.ts` is Supabase SSR session-refresh logic (middleware-style, with a
`matcher` excluding static assets). It calls `supabase.auth.getUser()` on each
matched request to keep the auth cookie fresh.

## Deployment

Two independent surfaces, both for `debate-module`:

- **`vercel.json`** (root) drives Vercel: builds `debate-module/.next` via the root
  proxy build script.
- **`debate-module/.github/workflows/deploy.yml`** deploys to Vercel via the Vercel
  CLI on pushes that touch `debate-module/**` on `main` (and one feature branch),
  injecting the Supabase secrets at build time.

Note: Vercel only builds `debate-module`. Changes outside it (e.g.
`reuniaodecultura-tags/`, `docs/`) do not affect — and cannot break — the Vercel
build.
