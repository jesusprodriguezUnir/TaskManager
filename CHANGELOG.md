# Changelog

All notable changes to OpenStudy will be documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
versions follow [SemVer](https://semver.org/spec/v2.0.0.html).

## [v0.5.0] — 2026-04-26

**Self-hosted by default.** Big architectural shift: OpenStudy no longer
depends on Supabase or Vercel. The whole stack — Postgres, PostgREST,
FastAPI, and the React frontend — runs as four containers on any Docker
host, brought up with a single `./deploy.sh`. Course files live on a
bind-mounted directory instead of object storage, indexed locally for
full-text search. On top of the architectural move, this release also
ships a public landing page, brand identity, TOTP 2FA, and a Telegram
bot integration.

### Added — infrastructure
- **`docker-compose.yml`** — four-service stack on an internal bridge
  network: `openstudy-postgres` (Postgres 16-alpine), `openstudy-postgrest`
  (PostgREST 12.2.3, JWT auth disabled, only reachable from the network),
  `openstudy` (the FastAPI image built from `Dockerfile`), and
  `openstudy-frontend` (the React SPA served by an in-container Caddy).
  Only the frontend (`127.0.0.1:8080`) and FastAPI (`127.0.0.1:8000`) are
  bound to the host; an outer reverse proxy (Caddy / nginx / Traefik)
  forwards a single `127.0.0.1:8080` upstream.
- **`Dockerfile`** — `python:3.12-slim` base, uv-managed deps, multi-layer
  cache for fast rebuilds.
- **`web/Dockerfile`** — multi-stage build: Node 20 + pnpm builds the
  Vite SPA, then a `caddy:alpine` image serves it. The Caddyfile inside
  the image does SPA fallback (`try_files`) plus `reverse_proxy
  openstudy:8000` for `/api`, `/mcp`, `/oauth` paths.
- **`./deploy.sh`** — single-command deploy with rollback. Pre-flight →
  build both images → apply migrations → health-gate (`GET /api/health`
  polled for 60s) → rollback to the previous image if health doesn't go
  green. Flags: `--skip-build`, `--no-rollback`, `--status`, `--help`.
- **Migrations runner** (`scripts/run_migrations.py`) — idempotent,
  transactional, sha256-tracked. State lives in a `_migrations` table.
  Files under `migrations/` apply in filename order.
- **Initial schema as `migrations/00000000000000_baseline.sql`** —
  canonical starting point for fresh deployments. Earlier development
  history preserved under `migrations/_archive/` for reference.
- **Filesystem storage layer** (`app/services/storage.py`) — files live
  at `STUDY_ROOT` (default `/opt/courses`); the storage service does
  read / write / list / move / delete directly on disk. Browser file
  serving via new `/api/files/raw` and `/api/files/upload-target`
  endpoints (cookie-authenticated, same-origin).
- **Filesystem full-text index** (`app/services/file_index.py`,
  `scripts/index_files.py`, baked into the baseline migration): walks
  `STUDY_ROOT`, extracts text from PDFs / notebooks / markdown / typst,
  upserts into `file_index`. Search exposed as `GET /api/files/search`,
  backed by the `search_files` Postgres RPC for ranking + snippet
  generation in one round-trip.
- **`/api/health`** now checks dependencies (DB SELECT + storage stat)
  instead of returning a static `{ok: true}`.
- **`/api/internal/*`** router (`app/routers/internal.py`) —
  bearer-gated (`X-Internal-Secret`) endpoints for cron jobs to trigger
  reindex, plus a Telegram-bot webhook (authed via Telegram's own
  `X-Telegram-Bot-Api-Secret-Token` header) exposing `/sync`, `/status`,
  `/help` to the operator's allowlisted chat.

### Added — frontend & brand
- **Brand assets** — `web/public/brand/{mark,wordmark}/{on-light,on-dark}.svg`,
  rendered via the new `<Wordmark>` React component
  (`web/src/components/brand/wordmark.tsx`) and embedded in the README
  header.
- **Landing page** at `/` (`web/src/routes/landing.tsx` +
  `web/src/styles/landing.css`): hero with auto-rotating five-theme
  carousel, animated MCP / Day-0 demo, real Claude Desktop screenshots,
  self-host terminal block, GitHub-stars CTA, floating navbar that
  hides on scroll-down. All CTAs link to the GitHub repo — no waitlist
  or signup.
- **`VITE_SHOW_LANDING`** env flag (default `false`) — when `true`, `/`
  renders the landing page; when `false`, `/` redirects straight to the
  app (`/app` if signed in, `/login` otherwise). Self-hosters typically
  leave it off.
- **`scripts/build-seo.mjs`** — Vite prebuild step that regenerates
  `robots.txt`, `sitemap.xml`, and `manifest.webmanifest` from
  `VITE_SITE_URL` / `VITE_SITE_NAME`. Forks deploying to a custom domain
  get correct canonical URLs and PWA metadata without code edits.
- **SEO + PWA assets** — `web/public/og-card.png`, `apple-touch-icon.png`,
  `icon-192/256/512.png`, `security.txt`, `manifest.webmanifest`.
- **TOTP / 2FA** for the dashboard login
  (`web/src/components/settings/totp-card.tsx`, baked into the baseline
  migration). Setup-key + QR + recovery-code flow inside Settings.
- **Multi-language `<title>` and `<html lang>`** via
  `web/src/lib/document-head.ts` — switches between EN / DE based on
  the active i18n locale.

### Changed
- **`POSTGREST_URL` / `POSTGREST_API_KEY`** env vars replace
  `SUPABASE_URL` / `SUPABASE_SERVICE_KEY`. Breaking change for anyone
  upgrading from v0.3.x — see migration notes below.
- **`POSTGREST_AUTH`** flag — set to `false` to skip Bearer auth headers
  when targeting a self-hosted PostgREST that has JWT validation off.
- **`app/db.py`** — function renamed `supabase()` → `client()`. All
  service files migrated to `from app.db import client`.
- **`/api/internal/sync`** — runs reindexing in a FastAPI background
  task instead of spawning subprocesses. The `mode` query parameter is
  still accepted (and echoed back) for caller compatibility, but no
  longer affects behaviour.
- **README**, **INSTALL.md**, **CONTRIBUTING.md**, **`.env.example`**
  all rewritten around the docker-compose deploy. README header shows
  the OpenStudy wordmark with auto light / dark variants instead of a
  plain heading; database badge updated from "Supabase Postgres" to
  "Postgres 16".
- **`PUBLIC_SITE_URL`** is the single source of truth for the domain
  baked into canonical / OG / sitemap / manifest tags. Previous default
  `openstudy.dev` removed; default is now `http://localhost:8080` so
  forks don't accidentally ship with someone else's domain.
- **`N8N_MOODLE_WEBHOOK_URL`** has no default any more — endpoints that
  use it 503 with a helpful message when unset, instead of trying to
  hit a hardcoded host.

### Removed
- **Vercel artefacts** — `vercel.json`, the `api/index.py` shim, related
  `.vercel/` config. Vercel was retired as a host; the "build dist +
  rsync to a static web server" deploy path is gone too.
- **Supabase-specific layout** — top-level `supabase/` folder. Migrations
  live under `migrations/` now.
- **Bucket-sync scripts** — `force_push_to_bucket.py`, `sync.py`,
  `openstudy.py`, the bidirectional CONFLICT-DEL-REMOTE state machine.
  With local filesystem storage there's nothing to mirror to a separate
  object store. Moved to `scripts/_deprecated/` for reference.
- **`TRADEMARK.md`** — the project ships under MIT only, with no
  separate trademark policy. Self-host rebranding guidance now lives
  in CONTRIBUTING.md (`VITE_SITE_URL` / `VITE_SITE_NAME` + brand assets).

### Migration notes (upgrading from v0.3.x)

This is a breaking release. If you're moving an existing OpenStudy
install over from Supabase + Vercel:

1. `pg_dump` your Supabase database and restore it into the new local
   Postgres before first running `./deploy.sh` against real users — see
   [INSTALL.md §4](./INSTALL.md#restoring-data-into-a-fresh-box).
2. Rename `SUPABASE_URL` → `POSTGREST_URL` and `SUPABASE_SERVICE_KEY` →
   `POSTGREST_API_KEY` in your `.env`. Add a new `.env.docker` next to
   it with `POSTGRES_USER` / `POSTGRES_PASSWORD` / `POSTGRES_DB` for the
   database container.
3. Move your course files into the path you'll mount as `STUDY_ROOT` in
   the compose file (default `/opt/courses`).
4. Make sure the `courses.folder_name` column is populated for every
   course — it's now the source of truth that `/api/files/lecture-materials`
   and the file browser use to map a course code to its on-disk folder
   (replaces the previously hardcoded mapping).
5. Drop your Vercel deployment once the new docker host is healthy.
   Point your domain at the new outer reverse proxy.

## [v0.3.0] — 2026-04-21

Big visual + localization release. Five dashboard themes, full English/German
i18n, per-course schedule CRUD, a proper file manager in the Files tab, and a
pile of phone-UX fixes. All backwards compatible — just run the one new
migration on upgrade.

### Added
- **Five dashboard themes.** Pick from **Classic** (the default — serif,
  airy), **Terminal** (mono, teal-on-black, hacker cockpit), **Zine**
  (pastel cream + hand-drawn stickers), **Library** (sepia, card-catalog
  aesthetic), or **Swiss** (12-col grid, red accent). Each one is a full
  reskin — its own sidebar, CSS, and dashboard route, not just a palette.
  Picker lives in **Settings → Theme**.
- **Full in-app i18n — English and German.** Every route, form, toast,
  empty state, error message, and theme-specific prose now runs through
  `i18next`. Language is picked explicitly in **Profile → Language** and
  persists in localStorage, decoupled from the date-format locale.
- **Per-course schedule CRUD.** Add / edit / delete weekly slots from the
  course-detail **Schedule** tab without leaving the page.
- **File manager.** Rename files and folders, recursive folder delete,
  create new folders, and a folder picker on the course form so each
  course scopes its Files tab to a specific prefix in the bucket. New
  backend endpoints `/files/move`, `/files/folder`, and a recursive
  listing helper.
- **Claude Design prompt template** under `docs/claude-design-prompt.md`
  plus four worked-example outputs under `docs/examples/` — the starting
  points for the Terminal / Zine / Library / Swiss themes.

### Changed
- **Phone UX pass.** 16 px form inputs (no more iOS zoom-on-focus), dvh
  for keyboard-aware layout, date-picker chrome contained inside its
  Field on iOS Safari, classic-theme weekly grid now renders the same
  multi-column time grid on phone (with horizontal scroll) instead of a
  stacked list — matches what the themed dashboards do.
- **Course edit affordance** moved from a hover overlay on the course
  card to an explicit **Edit course** button inside the course-detail
  header. Notes and exam editing split out into their own cards with
  their own edit buttons. "Scheduled" field on exams relabeled to
  "Exam date".
- **Dashboard top strip** on phone shows weekday / date / semester /
  week at a glance.
- **Settings pickers** (timezone, date format) auto-save on change; the
  semester-label text field gets an inline Save button while dirty.
  Success toasts are now neutral instead of green.
- **README hero** replaced with a 2×2 still collage of the four paper
  themes plus a looping GIF of Terminal. Mirrored in the German section.

### Upgrade from v0.2.0

```bash
git pull origin main
npx supabase db push   # applies 20260421000001_theme.sql
cd web && pnpm install && pnpm build
```

The migration adds `app_settings.theme` with default `'editorial'`, so
existing rows land on the Classic theme until you pick something else.

[v0.5.0]: https://github.com/openstudy-dev/OpenStudy/releases/tag/v0.5.0
[v0.3.0]: https://github.com/openstudy-dev/OpenStudy/releases/tag/v0.3.0

## [v0.2.0] — 2026-04-20

Rename pass: the project is now English-canonical from the database up through
the MCP tool names. Migrations moved to `supabase/migrations/` so the Supabase
CLI tracks them properly. If you're upgrading an existing deploy, see the
upgrade notes below — pushing `main` won't fix your schema on its own.

### Breaking
- **MCP tools renamed.** `list_klausuren` → `list_exams`, `update_klausur` →
  `update_exam`. `upsert_schedule_slot` → `create_schedule_slot` (signature
  is a pure create now; use `update_schedule_slot` to patch). `now_berlin`
  removed — use `now_here`. Any cached tool lists in Claude.ai / Claude Code
  will need to re-fetch after the push.
- **DB schema.** Table `klausuren` renamed to `exams`. Columns
  `courses.klausur_weight` / `klausur_retries` renamed to `exam_weight` /
  `exam_retries`.
- **Enum values.** Slot / lecture kinds moved from
  `Vorlesung|Übung|Tutorium|Praktikum` to `lecture|exercise|tutorial|lab`.
  Study-topic kinds from `vorlesung|uebung|reading` to
  `lecture|exercise|reading`. Deliverable kinds from
  `abgabe|project|praktikum|block` to `submission|project|lab|block`. Legacy
  German values are still accepted at the API boundary via a Pydantic
  `BeforeValidator` and normalised on the way in — existing MCP integrations
  keep working.
- **Migration location.** `db/migrations/` → `supabase/migrations/` with
  timestamp-based filenames.

### Added
- Single-file README with a same-page `<details name="lang">` language
  toggle — click 🇬🇧 English or 🇩🇪 Deutsch, the other collapses.
- New migration `20260420000001_english_canonical_kinds.sql` that normalises
  existing German values + renames the table/columns on upgrade.
- FastMCP server-level `instructions` — mental model of the domain, enum
  conventions, and orient-before-you-act guidance injected on every
  `initialize`.

### Changed
- Every MCP tool description rewritten with "when to use / when NOT to use"
  disambiguation plus sibling pointers. Goal: Claude picks the right tool
  first try instead of listing + retrying. Tool count down from 46 → 44.
- UI: hardcoded German strings replaced with English (slot-kind selects,
  deliverable-kind selects, sidebar `Klausuren` → `Exams`, /klausuren →
  /exams, etc.). Displayed kind strings pick up a `capitalize` class for
  polish.
- `INSTALL.md` §4 rewritten around `supabase db push` with an upgrade flow
  for existing DBs (`supabase migration repair --status applied …`) and a
  dashboard-SQL-editor fallback.

### Upgrade from v0.1.0

```bash
git pull origin main
npx supabase link --project-ref YOUR-PROJECT-REF
# If you applied 0001–0004 via the SQL editor, mark them applied first:
npx supabase migration repair --status applied 20260101000001 20260115000001 20260201000001 20260301000001
npx supabase db push   # applies the English-canonical migration
```

Then rebuild the frontend (`cd web && pnpm install && pnpm build`) and redeploy.

[v0.2.0]: https://github.com/openstudy-dev/OpenStudy/releases/tag/v0.2.0

## [v0.1.0] — 2026-04-20

First public release. A self-hostable personal study dashboard with an MCP
connector so Claude (claude.ai, iOS, or Claude Code) can read and write your
coursework.

### Added
- Web app: Dashboard, Courses (create / edit / delete with per-course accent
  color), Course detail, Tasks, Deliverables, Files, Klausuren, Activity,
  Settings (profile + semester).
- Streamable HTTP MCP server at `/mcp`, OAuth 2.1-gated. ~45 tools — every UI
  action exposed plus convenience helpers like `get_fall_behind`,
  `mark_studied`, `read_course_file` (renders PDF pages to PNGs for vision).
- Dark visual design — Fraunces serif + Inter Tight + JetBrains Mono, OKLCH
  palette, ink-dot signature motif, 3 px course-accent stripes.
- Empty-by-default schema + a self-healing settings singleton so new deploys
  boot to an onboarding screen rather than a pre-populated dashboard.
- Docs: [INSTALL.md](./INSTALL.md), [CONTRIBUTING.md](./CONTRIBUTING.md),
  [CODE_OF_CONDUCT.md](./CODE_OF_CONDUCT.md), plus templates for a Claude.ai
  Project system prompt and a Claude Design redesign brief (under `docs/`).
- SQL migrations under `supabase/migrations/` — the complete schema, applied
  via `supabase db push` (or pasted into any Postgres SQL editor, in filename
  order).
- Vercel deployment config (`vercel.json`) — one project hosts both the
  static frontend and the Python API functions.

### Known gaps
- Light mode is tokenised but untested.
- No automated test suite yet (manual QA only).
- Slot kinds are German-labeled by default (`Vorlesung`, `Übung`, `Tutorium`,
  `Praktikum`) — not yet user-configurable.
- Postgres driver is Supabase-specific; swapping it out is a fork, not a
  config flag.

PRs on any of the above are welcome — see
[CONTRIBUTING.md](./CONTRIBUTING.md).

[v0.1.0]: https://github.com/openstudy-dev/OpenStudy/releases/tag/v0.1.0
