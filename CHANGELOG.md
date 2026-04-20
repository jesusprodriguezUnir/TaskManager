# Changelog

All notable changes to study-dashboard will be documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
versions follow [SemVer](https://semver.org/spec/v2.0.0.html).

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

[v0.2.0]: https://github.com/AmmarSaleh50/study-dashboard/releases/tag/v0.2.0

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

[v0.1.0]: https://github.com/AmmarSaleh50/study-dashboard/releases/tag/v0.1.0
