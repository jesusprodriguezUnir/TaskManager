# Claude Design prompt template

Paste into [Claude Design](https://claude.ai/design) to produce a **drastically
different** dashboard variant. The constraints force a design that doesn't fall
back to Claude's default Fraunces + ink-dot preset, while keeping the output
portable to this codebase (same data model, same sections, Tailwind + React).

Fill in the `VIBE:` line with one of the options at the bottom, then run it.
Send the generated dashboard code back and I'll port the design language across
the rest of the app (sidebar, course detail, settings, etc.).

---

```
You are designing the DASHBOARD ROUTE of a personal study tracker for
a single user. The goal is a visually DISTINCTIVE design — it must not
resemble the default "Claude frontend" preset.

## VIBE
VIBE: <PICK ONE — see options at the bottom>

## WHAT TO DESIGN
One page. Responsive (375px → 1440px). Dark mode only. The page has
these sections, top-to-bottom, in this order:

1. Greeting line — time-of-day greeting + user's first name +
   optional "Next up" chip (course code + relative time, e.g. "ASB · in 3h").
   Optional subline with 1 sentence of context.
2. Fall-behind banner — red-tinted card, only shown when user has
   unstudied topics before a nearby lecture. Shows: headline, 1-2 bullet
   details, 4 severity-colored course dots.
3. Metric tiles — 4 small cards in a 2-col (mobile) or 4-col (desktop) grid.
   Each tile: icon, label (e.g. "Next deadline"), value (e.g. "3"),
   unit ("days"), hint ("MATH · Problem Set 4"), one of 4 tones:
   default / warn / critical / ok.
4. Weekly grid — Mon–Fri, 08:00 → 18:00. Shows lectures/exercises/tutorials
   as blocks positioned by time. Each block has: course code pill, room,
   start time. Today's column is highlighted. A horizontal "now" line.
5. Course cards — 2–4 courses in a responsive grid. Each card: course code
   (colored), full name, module code / ECTS / language meta, next-lecture
   relative time, and a horizontal progress bar. Cards are clickable.
6. Two side-by-side panels:
   - Upcoming deadlines — list of submissions, each with name, course,
     countdown chip
   - Task inbox — list of tasks, each with name, course dot, status chip

## HARD CONSTRAINTS
- NO Fraunces serif, NO crafted-serif variable font, NO "opsz"/"SOFT"
  font-variation-settings.
- NO hand-drawn ink-dot motif (small dot next to headings/today marker).
- NO warm near-black OKLCH palette (0.18 L, 0.006 C, 60 H) — pick a
  palette that feels fundamentally different.
- NO "Good evening, <Name>." in a serif hero paragraph — it must still
  greet the user, but find a completely different typographic approach.
- NO timestamp in monospace right-aligned in the top bar — handle date/time
  placement however fits the vibe.
- Must work on mobile at 375px wide. All interactive targets ≥ 40px on mobile.
- All course accents come from four CSS vars: --course-asb, --course-rn,
  --course-ra, --course-aml. Use them for course-specific color.

## SOFT CONSTRAINTS
- Tailwind utility classes preferred; no runtime CSS-in-JS.
- Icons from lucide-react only.
- Assume shadcn/ui primitives are available but feel free to restyle them.

## VIBE OPTIONS
Pick ONE for this run and commit fully to it:

- BRUTALIST — hard edges, zero border-radius, heavy type (one weight),
  high-contrast (e.g. stark black / white / one neon accent), deliberately
  raw, visible grid, no shadows, Helvetica Now or IBM Plex Sans,
  possibly oversized captions.

- CYBERPUNK TERMINAL — deep near-black with teal/magenta accents,
  monospace everywhere (JetBrains Mono / IBM Plex Mono), subtle scanlines
  or glitch accents on hover, square corners, all-caps kickers, ASCII
  decorations (│ ─ ▌) used as dividers and accents.

- ARCHIVAL / LIBRARY — cream/ivory background (light theme exception),
  sepia-brown accents, typewriter-style body (Courier Prime / Special Elegant),
  rules between sections, tabular numerals, subtle paper texture,
  roman-numeral or sequential number badges.

- PASTEL ZINE — punchy yellow/pink/cyan on cream, playful sans (Redaction,
  Work Sans), hand-scribbled underlines and arrows (SVG), sticker-style
  course badges, generous whitespace, oversized section numbers.

- CLINICAL / MEDICAL — clean near-white grey palette with Vichy-green or
  clinical-blue accents, Inter or Neue Haas Grotesk, flat cards with thin
  hairlines, precise number formatting (monospace numerals), subtle icons,
  no decorative typography.

## ATMOSPHERE CHECK
Before generating: picture this design next to 10 other apps built with
your default preset. Can a user tell them apart instantly? If not, you're
still too close to the default — push further.
```
