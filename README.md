# THE WORLD, THURSDAY 19 NOVEMBER 2026

[![news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/verren044/makefun-news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/verren044/makefun-news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119)

One image that sums up the world's news of Thursday 19 November 2026: a dense
newspaper front page, drawn entirely in code (Python 3.13 standard library
only, deterministic, no network). Run `main.py` and it writes
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output/entry.png`), 1024x1024,
under 1 MiB.

## The image

- **Masthead** — "THE WORLD" with the dateline "THURSDAY 19 NOVEMBER 2026".
- **Four illustrated anchor panels**, each a small drawn scene with a headline
  strip:
  1. **TRILATERAL IN SHENZHEN** — Trump, Xi and Putin meet in Shenzhen at
     APEC; Xi hugged Trump on the tarmac. Skyline, the US, Chinese and Russian
     flags, and a handshake.
  2. **KERCH BRIDGE HIT AGAIN** — the Crimea bridge attacked a third night
     running, traffic closed while damage is assessed. Night bridge over a
     dark sea, explosion flash, moon.
  3. **ANTHROPIC'S RECORD IPO** — the Claude-maker raises $81.3bn, the
     biggest IPO of all time, debut valuing it above $1.4tn. Rising chart and
     bars, "$81.3BN" in red.
  4. **GAZA LINE CROSSED** — Israeli tanks advance across the Gaza ceasefire
     line in a rare ground incursion beyond the Yellow Line. Desert, tanks,
     the dashed Yellow Line.
- **THE WORLD MAP** — rough continents on a blue ocean with eight red markers:
  Shenzhen, Kerch, Gaza, Gulf, Myanmar, Washington, London, New Delhi.
- **THE DAY IN BRIEF** — 36 short briefs (headline + one-line caption) in
  three columns, from the ICJ's Myanmar verdict to Voyager 1 reaching one
  light-day, GTA VI's worldwide launch, and the Gulf war widening.
- **Footer** — "40 STORIES, ONE DAY": 4 anchors + 36 briefs = 40 stories.

## How it is built

`main.py` holds a hand-drawn 5x7 bitmap font (uppercase A-Z, 0-9, punctuation),
a pixel buffer with rect/ellipse/polygon/line primitives, and a pure-stdlib
PNG encoder (zlib + struct + CRC32). Every string is uppercased before
drawing. Two runs produce byte-identical output.

## Validation

- Two runs, identical sha256: `eaf2f3b5c33711a50bdf9231f9e45e31568d148c46874cce170ffc419b9372c9`
- Size: 32,109 bytes (limit 1 MiB), 1024x1024, all PNG chunk CRCs valid
- 15 region spot-checks passed (masthead, dateline, all four scenes, map
  ocean/land/markers, briefs columns, footer; plus two no-spill checks on the
  Gaza dunes)
- Visually checked at full size: no garbled or overlapping text, no scene
  spilling outside its panel

Built for the make.fun bounty — [enter via my referral link](https://make.fun/r/vvz66fvh).
