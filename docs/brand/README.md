# OpenStudy brand

Quick reference for the logo, colors, and type. Everything else in this folder is source/output assets — this file is the map.

## Colors

| Name         | Hex       | Use                                           |
| ------------ | --------- | --------------------------------------------- |
| Ink          | `#1a1512` | Primary dark — text, mark on light bg         |
| Cream        | `#f3ebd8` | Primary light — paper, mark on dark bg        |
| Sepia        | `#a8804a` | Accent dots on light bg (logo only)           |
| Sepia bright | `#c6a572` | Accent dots on dark bg (logo only)            |

The sepia dots are part of the mark. Don't use them as UI accents elsewhere.

## Type

**Fraunces** (variable serif) — primary display + body serif. Used for the wordmark at weight 600 + default optical sizing. Loaded via Google Fonts.

**Inter Tight** — UI sans, buttons, nav.

**JetBrains Mono** — code, technical UI, Terminal-theme body text.

## Files

```
docs/brand/
├── wordmark/           OpenStudy wordmark (mark + type)
│   ├── on-light.svg    ink — use on light backgrounds
│   ├── on-dark.svg     cream — use on dark backgrounds
│   ├── card-light.svg  full cream-filled canvas, ink artwork baked in
│   └── card-dark.svg   full ink-filled canvas, cream artwork baked in
├── mark/               mark alone (no wordmark)
│   └── … same four variants
└── raster/             PNG exports for app icons + favicons + OG card source
    ├── source.png      2048×2048 master — input for _export_brand.py
    ├── mark-{64,180,256,512}.png
    └── favicon-{16,32}.png
```

## Usage

- **README / GitHub:** use `wordmark/on-light.svg` inside a `<picture>` with `prefers-color-scheme: dark` switching to `wordmark/on-dark.svg`. See the top of the project README for the exact snippet.
- **Inside the app:** import `<Wordmark />` from `web/src/components/brand/wordmark.tsx`. It auto-picks ink vs cream based on the current theme.
- **Favicon / PWA icons:** live in `web/public/` (copied from `raster/`). Served from the site root.
- **OG card:** `web/public/og-card.png` (1200×630, rebuilt when the wordmark changes).

## Rebuilding (internal)

The generator scripts (`scripts/_vectorize_mark.py`, `scripts/_build_wordmark.py`, `scripts/_export_brand.py`) are gitignored — they require `potracer`, `resvg_py`, and the Fraunces variable TTF. Output is the committed SVG/PNG set above. Don't edit the generated SVGs by hand; re-run the relevant script instead.
