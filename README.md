# THE WORLD, THURSDAY 19 NOVEMBER 2026

[![news-image-20261119](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)
[![rank](https://make.fun/badge/news-image-20261119/verren044/makefun-news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119)
[![reward](https://make.fun/badge/news-image-20261119/verren044/makefun-news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119)

One image that sums up the world's news of Thursday 19 November 2026: a dense
newspaper front page, drawn entirely in code (Python 3.13 standard library
only, deterministic, no network). Run `main.py` and it writes
`$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output/entry.png`), 1024x1024,
under 1 MiB.

## The image (v2 — 52 stories)

- **Masthead** — "THE WORLD" with the dateline "THURSDAY 19 NOVEMBER 2026".
- **UTC timeline strip** — the day in UTC (00/06/12/18/24 ticks) with five
  timed moments: SUNEUNG exams begin in Seoul (~00 UTC), Kerch bridge hit
  (~02 UTC), APEC trilateral (~03 UTC), Berlin coalition meeting (12 UTC),
  Fed minutes out (19 UTC, 14:00 ET).
- **Thirteen illustrated anchor cards**, each a small drawn picture strip
  with a kicker, a headline and a caption:
  1. **TRILATERAL IN SHENZHEN** — Trump, Xi and Putin meet in Shenzhen at
     APEC. Skyline, the US, Chinese and Russian flags.
  2. **KERCH BRIDGE HIT AGAIN** — the Crimea bridge attacked a third night
     running. Night bridge over a dark sea, explosion flash, moon.
  3. **ANTHROPIC'S RECORD IPO** — the Claude-maker raises $81.3bn, the
     biggest IPO of all time. Rising chart and bars.
  4. **GAZA LINE CROSSED** — Israeli tanks advance across the Gaza ceasefire
     line. Desert, tanks, the dashed Yellow Line.
  5. **HORMUZ TANKER STRUCK** — a UAE ADNOC tanker hit in the Strait of
     Hormuz, 11 crew hurt, one missing. Burning tanker at sea.
  6. **GTA VI LAUNCHES** — record launch, 99 on Metacritic. Night city,
     big yellow "99".
  7. **VOYAGER 1, ONE LIGHT-DAY** — the probe is now 25.9bn km from Earth.
     Gold probe, dish, Earth below.
  8. **ICJ TO RULE ON MYANMAR** — the Rohingya genocide case. Courthouse
     columns and pediment.
  9. **NVIDIA'S $115.8BN QUARTER** — revenue doubled, Huang's CEO comeback
     rejected by the board. Green chip, rising arrow.
  10. **ODESA DRONE STRIKE** — four killed, historic centre hit. Night
      buildings, explosion flash.
  11. **BERLIN COALITION MEETS** — 20+ leaders, US envoys Witkoff and
      Kushner. Brandenburg-style gate, allied flags.
  12. **SUNEUNG EXAM DAY** — 550,000 South Korean students sit the college
      entrance exam. Desks, clock.
  13. **VAN GOGH SELLS $190.4M** — record price after a Nazi-era row.
      Starry-night canvas, sun, cypress, field.
- **THE WORLD MAP** — rough continents on a blue ocean with five numbered
  red markers: 1 Shenzhen, 2 Kerch, 3 Gaza, 4 Gulf, 5 Seoul (key in the
  index panel).
- **BY REGION index** — story counts per region: Middle East 9,
  Asia-Pacific 10, Europe 9, Americas 7, Africa 6, Markets + Tech 11.
- **THE DAY IN BRIEF — 39 MORE STORIES** — 39 short briefs (headline +
  one-line caption) in three columns, from the Gulf war widening to the
  Knesset's new speaker, Ethiopia-Eritrea troops massing, Bangladesh
  garment protests, Soweto floods and the UK-EU summit set for 20 Nov.
- **Footer** — "52 STORIES, ONE DAY": 13 anchors + 39 briefs = 52 stories.

## How it is built

`main.py` holds a hand-drawn 5x7 bitmap font (uppercase A-Z, 0-9, punctuation),
a pixel buffer with rect/ellipse/polygon/line primitives, and a pure-stdlib
PNG encoder (zlib + struct + CRC32). Every string is uppercased before
drawing. Two runs produce byte-identical output.

## Validation (v2)

- Two runs, identical sha256: `fc8872515c500789c8501747c407cc70320bcc34daff17e69f8f118ce47c40b3`
- Size: 34,988 bytes (limit 1 MiB), 1024x1024, all PNG chunk CRCs valid
- 41 region spot-checks passed (masthead, dateline, timeline dots/ticks/
  labels, all 13 mini-scenes, map ocean/land/numbered markers, index title,
  briefs ink + captions in all 3 columns, footer; plus two no-spill checks)
- Visually checked at full size: no garbled or overlapping text, no scene
  spilling outside its panel; all 13 anchor headlines legible, map markers
  distinct, briefs readable

## Validation (v1)

- Two runs, identical sha256: `eaf2f3b5c33711a50bdf9231f9e45e31568d148c46874cce170ffc419b9372c9`
- Size: 32,109 bytes (limit 1 MiB), 1024x1024, all PNG chunk CRCs valid
- 15 region spot-checks passed (masthead, dateline, all four scenes, map
  ocean/land/markers, briefs columns, footer; plus two no-spill checks on the
  Gaza dunes)
- Visually checked at full size: no garbled or overlapping text, no scene
  spilling outside its panel

Built for the make.fun bounty — [enter via my referral link](https://make.fun/r/vvz66fvh).
