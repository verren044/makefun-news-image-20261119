#!/usr/bin/env python3
"""THE WORLD, THURSDAY 19 NOVEMBER 2026 — v2.

Denser newspaper front page: 52 verified stories of the day (13 anchor
cards with picture strips, a world map with numbered story sites, a UTC
timeline strip, a by-region index, and 39 briefs). Pure Python 3.13
standard library, deterministic, no network, no randomness, no external
files. All 52 stories are real events of 19 November 2026 (or first
reported that day), cross-checked against the day's news digests.
"""
import math
import os
import struct
import zlib

W, H = 1024, 1024

PAPER = (248, 244, 233)
INK = (18, 18, 18)
RED = (176, 32, 32)
GREY = (96, 92, 84)
DARKGREY = (60, 58, 52)
BLUE = (38, 84, 140)
OCEAN = (52, 110, 168)
SKY = (168, 198, 224)
NIGHT = (16, 26, 52)
SEA = (14, 38, 70)
SAND = (214, 186, 138)
SAND2 = (196, 164, 112)
GREEN = (74, 120, 66)
GREEN2 = (96, 142, 82)
YELLOW = (232, 184, 48)
ORANGE = (226, 106, 28)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT = (226, 222, 210)

# ---------------------------------------------------------------- pixel buffer
BUF = bytearray(W * H * 3)


def set_px(x, y, c):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        BUF[i] = c[0]
        BUF[i + 1] = c[1]
        BUF[i + 2] = c[2]


def get_px(x, y):
    i = (y * W + x) * 3
    return (BUF[i], BUF[i + 1], BUF[i + 2])


def rect(x, y, w, h, c):
    x0 = max(0, x)
    y0 = max(0, y)
    x1 = min(W, x + w)
    y1 = min(H, y + h)
    for yy in range(y0, y1):
        base = yy * W * 3
        for xx in range(x0, x1):
            i = base + xx * 3
            BUF[i] = c[0]
            BUF[i + 1] = c[1]
            BUF[i + 2] = c[2]


def hline(x, y, w, c):
    rect(x, y, w, 1, c)


def vline(x, y, h, c):
    rect(x, y, 1, h, c)


def frame(x, y, w, h, c, t=1):
    rect(x, y, w, t, c)
    rect(x, y + h - t, w, t, c)
    rect(x, y, t, h, c)
    rect(x + w - t, y, t, h, c)


def ellipse(cx, cy, rx, ry, c):
    for dy in range(-ry, ry + 1):
        t = 1.0 - (dy * dy) / float(ry * ry)
        if t < 0:
            continue
        dx = int(rx * math.sqrt(t))
        rect(cx - dx, cy + dy, dx * 2 + 1, 1, c)


def circle(cx, cy, r, c):
    ellipse(cx, cy, r, r, c)


def line(x0, y0, x1, y1, c, thick=1):
    dx = abs(x1 - x0)
    dy = -abs(y1 - y0)
    sx = 1 if x0 < x1 else -1
    sy = 1 if y0 < y1 else -1
    err = dx + dy
    x, y = x0, y0
    half = thick // 2
    while True:
        rect(x - half, y - half, thick, thick, c)
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 >= dy:
            err += dy
            x += sx
        if e2 <= dx:
            err += dx
            y += sy


def poly(points, c):
    """Scanline fill of a polygon given as [(x, y), ...]."""
    if len(points) < 3:
        return
    ys = [p[1] for p in points]
    y0, y1 = min(ys), max(ys)
    n = len(points)
    for y in range(y0, y1 + 1):
        xs = []
        for i in range(n):
            x0, ya = points[i]
            x1, yb = points[(i + 1) % n]
            if ya == yb:
                continue
            if (ya <= y < yb) or (yb <= y < ya):
                t = (y - ya) / float(yb - ya)
                xs.append(x0 + t * (x1 - x0))
        xs.sort()
        for i in range(0, len(xs) - 1, 2):
            xa = int(math.ceil(xs[i]))
            xb = int(math.floor(xs[i + 1]))
            if xb >= xa:
                rect(xa, y, xb - xa + 1, 1, c)


def star(cx, cy, r_outer, r_inner, c, rot=-math.pi / 2):
    pts = []
    for i in range(10):
        r = r_outer if i % 2 == 0 else r_inner
        a = rot + i * math.pi / 5
        pts.append((int(cx + r * math.cos(a)), int(cy + r * math.sin(a))))
    poly(pts, c)


# ------------------------------------------------------------------- 5x7 font
# Each glyph: 7 rows of 5 bits, written as strings. Uppercase only.
FONT = {
    'A': ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    'B': ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    'C': ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    'D': ("11110", "10001", "10001", "10001", "10001", "10001", "11110"),
    'E': ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    'F': ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    'G': ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    'H': ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    'I': ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    'J': ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    'K': ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    'L': ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    'M': ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    'N': ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    'O': ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    'P': ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    'Q': ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    'R': ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    'S': ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    'T': ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    'U': ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    'V': ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    'W': ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    'X': ("10001", "10001", "01010", "00100", "01010", "10001", "10001"),
    'Y': ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    'Z': ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    '0': ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    '1': ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    '2': ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    '3': ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    '4': ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    '5': ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    '6': ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    '7': ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    '8': ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    '9': ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    ' ': ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
    '.': ("00000", "00000", "00000", "00000", "00000", "01100", "01100"),
    ',': ("00000", "00000", "00000", "00000", "01100", "00100", "01000"),
    ':': ("00000", "01100", "01100", "00000", "01100", "01100", "00000"),
    ';': ("00000", "01100", "01100", "00000", "01100", "00100", "01000"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    '-': ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    '/': ("00001", "00010", "00010", "00100", "01000", "01000", "10000"),
    '%': ("11001", "11010", "00010", "00100", "01000", "01011", "10011"),
    '$': ("00100", "01111", "10100", "01110", "00101", "11110", "00100"),
    '(': ("00010", "00100", "01000", "01000", "01000", "00100", "00010"),
    ')': ("01000", "00100", "00010", "00010", "00010", "00100", "01000"),
    '!': ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    '?': ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    '&': ("01100", "10010", "10100", "01000", "10101", "10010", "01101"),
    '+': ("00000", "00100", "00100", "11111", "00100", "00100", "00000"),
}


def text_width(s, scale):
    return len(s) * 6 * scale - scale


def draw_text(x, y, s, scale, c):
    s = s.upper()
    cx = x
    for ch in s:
        glyph = FONT.get(ch)
        if glyph is None:
            raise ValueError("missing glyph for %r" % ch)
        for row in range(7):
            bits = glyph[row]
            for col in range(5):
                if bits[col] == '1':
                    rect(cx + col * scale, y + row * scale, scale, scale, c)
        cx += 6 * scale
    return cx


def draw_text_centered(cx, y, s, scale, c):
    x = cx - text_width(s, scale) // 2
    draw_text(x, y, s, scale, c)
    return x


# ------------------------------------------------------------------- PNG writer
def png_bytes():
    raw = bytearray()
    for y in range(H):
        raw.append(0)
        raw += BUF[y * W * 3:(y + 1) * W * 3]

    def chunk(tag, data):
        out = struct.pack(">I", len(data)) + tag + data
        return out + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    ihdr = struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))

# ------------------------------------------------------------- mini scenes
# Each draws a small picture strip inside (x, y, w, h); h is 36 for the
# four anchor rows and 56 for the row-5 Van Gogh card.


def mini_shenzhen(x, y, w, h):
    rect(x, y, w, h, SKY)
    circle(x + w - 26, y + 9, 6, (240, 214, 120))
    base = y + h - 3
    heights = [12, 20, 15, 26, 18, 22, 13]
    bw = w // 7
    for i, bh in enumerate(heights):
        bx = x + i * bw
        rect(bx + 1, base - bh, bw - 2, bh, (52, 66, 92))
    rect(x, base, w, 3, (88, 96, 88))
    fx = x + w // 2 - 36
    for i in range(3):
        px = fx + i * 26
        vline(px, y + 4, base - (y + 4), INK)
        if i == 0:  # US
            rect(px + 1, y + 4, 18, 8, WHITE)
            for s in range(0, 8, 4):
                rect(px + 1, y + 4 + s, 18, 2, RED)
            rect(px + 1, y + 4, 8, 5, BLUE)
        elif i == 1:  # CN
            rect(px + 1, y + 4, 18, 8, RED)
            star(px + 6, y + 8, 3, 1, YELLOW)
        else:  # RU
            rect(px + 1, y + 4, 18, 8, WHITE)
            rect(px + 1, y + 6, 18, 3, BLUE)
            rect(px + 1, y + 9, 18, 3, RED)


def mini_kerch(x, y, w, h):
    rect(x, y, w, h, NIGHT)
    for sx, sy in ((20, 8), (60, 14), (120, 6), (200, 12), (260, 8),
                   (300, 16), (90, 20), (180, 18)):
        set_px(x + sx, y + sy, WHITE)
    circle(x + w - 26, y + 9, 5, (238, 232, 200))
    rect(x, y + h - 9, w, 9, SEA)
    deck_y = y + h - 13
    rect(x, deck_y, w, 3, (120, 118, 110))
    for t in range(0, 181, 15):
        ax = x + w // 2 + int(70 * math.cos(math.radians(t)))
        ay = deck_y - int(14 * math.sin(math.radians(t)))
        rect(ax - 1, ay - 1, 3, 3, (150, 148, 140))
    ex, ey = x + w // 2 + 30, deck_y - 6
    star(ex, ey, 9, 4, ORANGE)
    star(ex, ey, 5, 2, YELLOW)
    circle(ex - 18, ey - 8, 4, (90, 88, 84))


def mini_anthropic(x, y, w, h):
    rect(x, y, w, h, WHITE)
    bars = [8, 13, 10, 18, 24]
    bw = (w - 30) // 5
    base = y + h - 4
    for i, bh in enumerate(bars):
        rect(x + 15 + i * bw, base - bh, bw - 4, bh, BLUE)
    line(x + 18, base - 8, x + w - 18, base - 26, RED, 2)


def mini_gaza(x, y, w, h):
    rect(x, y, w, h, SAND)
    circle(x + w - 30, y + 8, 6, (240, 200, 110))
    for dy in range(0, h, 9):
        rect(x + w // 2 - 1, y + 2 + dy, 2, 5, YELLOW)
    rect(x + 18, y + h - 12, 36, 8, (92, 96, 66))
    rect(x + 26, y + h - 18, 18, 7, (92, 96, 66))
    line(x + 44, y + h - 15, x + 62, y + h - 18, (92, 96, 66), 3)
    rect(x + 16, y + h - 4, 40, 3, INK)
    rect(x + w - 56, y + h - 12, 36, 8, (110, 104, 70))
    rect(x + w - 48, y + h - 18, 18, 7, (110, 104, 70))
    line(x + w - 56, y + h - 15, x + w - 74, y + h - 18, (110, 104, 70), 3)
    rect(x + w - 58, y + h - 4, 40, 3, INK)


def mini_tanker(x, y, w, h):
    rect(x, y, w, h, (24, 68, 118))
    rect(x, y + h - 14, w, 14, (16, 44, 84))
    rect(x + 40, y + h - 16, 160, 10, (28, 28, 34))
    rect(x + 40, y + h - 19, 160, 3, (70, 70, 78))
    rect(x + 168, y + h - 30, 26, 12, WHITE)
    rect(x + 52, y + h - 26, 10, 8, (200, 60, 40))
    circle(x + 57, y + h - 30, 4, (120, 118, 112))
    circle(x + 62, y + h - 33, 3, (120, 118, 112))
    star(x + 130, y + h - 20, 7, 3, ORANGE)
    star(x + 130, y + h - 20, 4, 2, YELLOW)


def mini_gta(x, y, w, h):
    rect(x, y, w, h, NIGHT)
    base = y + h - 3
    heights = [16, 24, 12, 28, 20, 26, 14]
    bw = w // 7
    for i, bh in enumerate(heights):
        bx = x + i * bw
        rect(bx + 1, base - bh, bw - 2, bh, (34, 40, 66))
        for wy in range(base - bh + 4, base - 3, 7):
            set_px(bx + 6, wy, YELLOW)
            set_px(bx + bw - 8, wy + 3, YELLOW)
    draw_text(x + w - 50, y + 4, "99", 2, YELLOW)


def mini_voyager(x, y, w, h):
    rect(x, y, w, h, BLACK)
    for sx, sy in ((20, 8), (70, 16), (130, 6), (200, 12), (260, 8),
                   (300, 18), (150, 22), (240, 24)):
        set_px(x + sx, y + sy, WHITE)
    px, py = x + w // 2, y + 16
    rect(px - 8, py - 3, 16, 7, (200, 170, 80))
    line(px + 8, py, px + 20, py - 6, (200, 170, 80), 2)
    circle(px + 23, py - 8, 4, (200, 170, 80))
    for dx, dy in ((30, -12), (36, -14), (42, -12)):
        set_px(px + dx, py + dy, WHITE)
    circle(x + 22, y + h - 8, 6, BLUE)
    circle(x + 20, y + h - 10, 2, GREEN)


def mini_icj(x, y, w, h):
    rect(x, y, w, h, (24, 48, 96))
    cx = x + w // 2
    poly([(cx - 42, y + 13), (cx + 42, y + 13), (cx, y + 3)], (220, 220, 210))
    for i in range(4):
        colx = cx - 36 + i * 20
        rect(colx, y + 14, 6, h - 20, (220, 220, 210))
    rect(cx - 48, y + h - 6, 96, 4, (220, 220, 210))


def mini_nvidia(x, y, w, h):
    rect(x, y, w, h, (16, 52, 28))
    cx, cy = x + 60, y + h // 2
    rect(cx - 11, cy - 10, 22, 20, (118, 200, 90))
    rect(cx - 6, cy - 5, 12, 10, (60, 140, 50))
    for p in range(4):
        rect(cx - 15, cy - 8 + p * 5, 4, 3, (200, 180, 80))
        rect(cx + 11, cy - 8 + p * 5, 4, 3, (200, 180, 80))
    line(x + 110, y + h - 8, x + w - 30, y + 8, YELLOW, 2)
    line(x + w - 30, y + 8, x + w - 44, y + 8, YELLOW, 2)
    line(x + w - 30, y + 8, x + w - 30, y + 20, YELLOW, 2)


def mini_odesa(x, y, w, h):
    rect(x, y, w, h, NIGHT)
    base = y + h - 3
    heights = [18, 26, 14, 22, 16]
    bw = w // 5
    for i, bh in enumerate(heights):
        bx = x + i * bw
        rect(bx + 2, base - bh, bw - 4, bh, (52, 52, 60))
        for wy in range(base - bh + 5, base - 3, 8):
            set_px(bx + 8, wy, YELLOW)
    ex, ey = x + w // 2, y + 10
    star(ex, ey, 10, 4, ORANGE)
    star(ex, ey, 6, 2, YELLOW)
    circle(ex - 26, ey - 4, 5, (90, 88, 84))
    circle(ex + 28, ey - 6, 4, (90, 88, 84))


def mini_berlin(x, y, w, h):
    rect(x, y, w, h, (210, 208, 198))
    cx = x + w // 2
    rect(cx - 34, y + 6, 68, 5, (90, 88, 84))
    rect(cx - 34, y + 11, 7, h - 14, (90, 88, 84))
    rect(cx + 27, y + 11, 7, h - 14, (90, 88, 84))
    for i, cols in enumerate((
            ((0, 0, 0), (200, 0, 0), (220, 180, 0)),
            ((0, 60, 160), (255, 255, 255), (220, 0, 0)),
            ((0, 90, 180), (240, 200, 0), (0, 90, 180)))):
        fx = x + 20 + i * 26
        for j, c in enumerate(cols):
            rect(fx, y + h - 12 + j * 3, 20, 3, c)


def mini_exam(x, y, w, h):
    rect(x, y, w, h, WHITE)
    for r in range(3):
        for c in range(5):
            dx = x + 24 + c * 34
            dy = y + 10 + r * 9
            circle(dx, dy - 3, 2, INK)
            rect(dx - 5, dy, 10, 4, (90, 90, 96))
    circle(x + w - 24, y + 11, 8, WHITE)
    frame(x + w - 32, y + 3, 16, 16, INK)
    line(x + w - 24, y + 11, x + w - 24, y + 5, INK, 1)
    line(x + w - 24, y + 11, x + w - 19, y + 13, INK, 1)


def mini_vangogh(x, y, w, h):
    rect(x, y, w, h, (36, 68, 140))
    circle(x + w - 42, y + 10, 7, YELLOW)
    for dx, dy in ((30, 22), (50, 16), (70, 20), (90, 14), (110, 20),
                   (130, 15)):
        set_px(x + dx, y + dy, YELLOW)
        set_px(x + dx + 1, y + dy, YELLOW)
    rect(x, y + h - 9, w, 9, (90, 120, 60))
    poly([(x + 30, y + h - 9), (x + 38, y + h - 9), (x + 34, y + 12)],
         (20, 50, 30))


# world map panel ------------------------------------------------------------
CONTINENTS = {
    'NA': [(-168, 66), (-140, 70), (-125, 72), (-110, 73), (-95, 80),
           (-85, 70), (-75, 62), (-60, 55), (-55, 47), (-65, 44),
           (-75, 35), (-80, 25), (-90, 21), (-97, 16), (-105, 20),
           (-115, 28), (-125, 40), (-140, 60), (-155, 58)],
    'SA': [(-80, 10), (-60, 10), (-50, 0), (-40, -5), (-35, -10),
           (-40, -20), (-50, -30), (-60, -35), (-70, -40), (-70, -50),
           (-65, -55), (-70, -20), (-80, -5)],
    'AF': [(-17, 15), (-10, 30), (0, 35), (10, 37), (20, 32), (30, 31),
           (35, 28), (40, 15), (43, 11), (48, 10), (40, 0), (35, -10),
           (30, -20), (25, -30), (20, -35), (15, -30), (12, -18),
           (9, -5), (9, 4), (-8, 4), (-13, 8)],
    'EU': [(-10, 36), (-9, 43), (-2, 48), (0, 50), (5, 53), (8, 57),
           (10, 59), (18, 56), (21, 55), (24, 58), (28, 60), (30, 70),
           (25, 71), (18, 70), (12, 65), (5, 60), (0, 55), (-5, 50),
           (-10, 45)],
    'AS': [(30, 70), (40, 72), (60, 73), (90, 75), (120, 73), (150, 70),
           (170, 66), (180, 65), (170, 60), (160, 55), (140, 40),
           (130, 35), (127, 40), (120, 35), (110, 20), (105, 10),
           (100, 8), (95, 15), (90, 22), (85, 20), (80, 8), (75, 8),
           (70, 20), (60, 25), (55, 26), (50, 29), (45, 30), (40, 36),
           (35, 36), (30, 40)],
    'OC': [(113, -22), (114, -30), (120, -34), (130, -32), (140, -38),
           (150, -37), (153, -27), (146, -19), (142, -11), (136, -12),
           (132, -11), (126, -14), (122, -17)],
}

# Numbered story sites on the map; the key lives in the index panel.
MAP_NUMBERS = [
    ("1", 114.0, 22.5),   # Shenzhen
    ("2", 36.4, 45.3),    # Kerch
    ("3", 34.5, 31.5),    # Gaza
    ("4", 51.0, 26.0),    # Gulf / Hormuz
    ("5", 127.0, 37.5),   # Seoul
]


def scene_map_numbered(x, y, w, h):
    rect(x, y, w, h, OCEAN)
    for lonlat in CONTINENTS.values():
        pts = []
        for lon, lat in lonlat:
            px = x + int((lon + 180) / 360.0 * w)
            py = y + int((75 - lat) / 135.0 * h)
            pts.append((px, py))
        poly(pts, GREEN)
    for num, lon, lat in MAP_NUMBERS:
        mx = x + int((lon + 180) / 360.0 * w)
        my = y + int((75 - lat) / 135.0 * h)
        circle(mx, my, 4, RED)
        circle(mx, my, 2, WHITE)
        draw_text(mx + 6, my - 3, num, 1, WHITE)


# ---------------------------------------------------------------------- layout
def anchor_card(x, y, w, h, kicker, headline, sub, scene_fn, scene_h):
    frame(x, y, w, h, INK)
    scene_fn(x + 1, y + 1, w - 2, scene_h)
    hline(x + 1, y + scene_h + 1, w - 2, INK)
    ty = y + scene_h + 6
    draw_text(x + 10, ty, kicker, 1, RED)
    draw_text(x + 10, ty + 12, headline, 2, INK)
    draw_text(x + 10, ty + 30, sub, 1, GREY)


def draw_timeline():
    line_y = 100
    hline(16, line_y, 992, INK)
    for hh, lab in ((0, "00"), (6, "06"), (12, "12"), (18, "18"), (24, "24")):
        tx = 16 + int(hh / 24 * 992)
        vline(tx, line_y - 4, 9, INK)
        draw_text_centered(tx, line_y + 6, lab, 1, GREY)
    events = [(0, "SUNEUNG"), (2, "KERCH"), (3, "APEC"), (12, "BERLIN"),
              (19, "FED MINUTES")]
    for hh, lab in events:
        ex = 16 + int(hh / 24 * 992)
        circle(ex, line_y, 4, RED)
        circle(ex, line_y, 2, WHITE)
        lx = ex - text_width(lab, 1) // 2
        lx = max(16, min(1008 - text_width(lab, 1), lx))
        draw_text(lx, 89, lab, 1, INK)
    draw_text(1008 - text_width("UTC", 1), 89, "UTC", 1, GREY)


def index_panel(x, y, w, h):
    frame(x, y, w, h, INK)
    draw_text(x + 10, y + 8, "BY REGION: 52 STORIES", 1, RED)
    rows = [("MIDDLE EAST", 9), ("ASIA-PACIFIC", 10), ("EUROPE", 9),
            ("AMERICAS", 7), ("AFRICA", 6), ("MARKETS + TECH", 11)]
    for i, (name, n) in enumerate(rows):
        ty = y + 22 + i * 11
        draw_text(x + 10, ty, name, 1, INK)
        draw_text(x + w - 10 - text_width(str(n), 1), ty, str(n), 1, INK)
    hline(x + 10, y + 92, w - 20, LIGHT)
    draw_text(x + 10, y + 98, "MAP: 1 SHENZHEN 2 KERCH", 1, GREY)
    draw_text(x + 10, y + 108, "3 GAZA 4 GULF 5 SEOUL", 1, GREY)


# 13 anchor cards: (kicker, headline, caption, scene)
ANCHORS = [
    ("APEC SUMMIT", "TRILATERAL IN SHENZHEN", "TRUMP, XI AND PUTIN MEET",
     mini_shenzhen),
    ("CRIMEA", "KERCH BRIDGE HIT AGAIN", "THIRD NIGHT RUNNING", mini_kerch),
    ("MARKETS", "ANTHROPIC'S RECORD IPO", "$81.3BN, BIGGEST EVER",
     mini_anthropic),
    ("MIDDLE EAST", "GAZA LINE CROSSED", "TANKS PAST YELLOW LINE",
     mini_gaza),
    ("GULF WAR", "HORMUZ TANKER STRUCK", "11 HURT, ONE MISSING",
     mini_tanker),
    ("GAMING", "GTA VI LAUNCHES", "99 ON METACRITIC, RECORDS FALL",
     mini_gta),
    ("SPACE", "VOYAGER 1, ONE LIGHT-DAY", "25.9BN KM FROM EARTH",
     mini_voyager),
    ("THE HAGUE", "ICJ TO RULE ON MYANMAR", "ROHINGYA GENOCIDE CASE",
     mini_icj),
    ("TECH", "NVIDIA'S $115.8BN QUARTER", "HUANG COMEBACK REJECTED",
     mini_nvidia),
    ("UKRAINE", "ODESA DRONE STRIKE", "FOUR KILLED, CENTRE HIT",
     mini_odesa),
    ("COALITION OF THE WILLING", "BERLIN COALITION MEETS",
     "20+ LEADERS, US ENVOYS", mini_berlin),
    ("SOUTH KOREA", "SUNEUNG EXAM DAY", "550,000 STUDENTS SIT TEST",
     mini_exam),
    ("ART", "VAN GOGH SELLS $190.4M", "RECORD AFTER NAZI-ERA ROW",
     mini_vangogh),
]

# 39 briefs, column-major (3 columns x 13 rows).
BRIEFS = [
    # column 1: Middle East + markets
    ("GULF WAR WIDENS", "IRAN HITS BASES; FIGHTING SPREADS"),
    ("SAUDI INTERCEPTS MISSILES", "TWO HOUTHI MISSILES DOWNED OVER RIYADH"),
    ("64 CHILDREN KILLED IN YEMEN", "UNICEF TOLL SINCE 3 SEPTEMBER"),
    ("GAZA RAINS DISPLACE 46,000", "SHELTERS FLOOD, TENTS HELD UP"),
    ("KNESSET PICKS NEW SPEAKER", "MATAN KAHANA WINS 66 VOTES"),
    ("US SANCTIONS HEZBOLLAH-LINKED NETWORK",
     "THREE ENTITIES AND THREE PEOPLE LISTED"),
    ("UAE ECONOMY TO GROW 7.3 PC", "IMF FORECAST FOR NEXT YEAR"),
    ("OIL PRICES FALL", "BRENT $92.6 AS US STOCKS RISE"),
    ("FED MINUTES POINT TO MORE HIKES", "MOST OFFICIALS EXPECT FURTHER RISES"),
    ("EU PROPOSES 45BN EURO UKRAINE LOAN",
     "REPAID AFTER RUSSIA PAYS REPARATIONS"),
    ("MELENCHON COULD WIN IN FRANCE", "JUSTICE MINISTER WARNS ON HARD LEFT"),
    ("UK-EU SUMMIT SET FOR 20 NOV", "BREXIT RESET TALKS IN BRUSSELS"),
    ("EU-INDONESIA TRADE DEALS APPROVED", "COUNCIL SIGNS OFF AGREEMENTS"),
    # column 2: Asia + Europe + tech
    ("CYCLONE AKVAN NEARS INDIA",
     "STORM TO CROSS BETWEEN MACHILIPATNAM AND PURI"),
    ("NORTH KOREA ENRICHMENT EXPANDS", "IAEA REPORTS URANIUM GROWTH"),
    ("INDIA-JAPAN 2+2 IN TOKYO", "DEFENCE AND FOREIGN MINISTERS MEET"),
    ("SINDHU BACK IN TOP FIVE", "INDIAN STAR RETURNS TO WORLD TOP FIVE"),
    ("DELHI SCHOOLS REOPEN", "OFFLINE CLASSES RESUME AS CURBS LIFT"),
    ("BANGLADESH GARMENT PROTESTS", "THIRD WEEK, TEAR GAS FIRED"),
    ("US-PHILIPPINES EYE $2BN LOAN", "FINANCING PACKAGE PURSUED VIA FMF"),
    ("LIU YUNPING MAKES HISTORY", "FIRST TAIWANESE AMERICAN CAUCUS CHAIR"),
    ("NVIDIA HALTS H-SERIES TO CHINA", "ACTING CEO ALSO PROMISES EARLIER PAY"),
    ("MICROSOFT EYES BYTEDANCE AI DEAL",
     "TALKS TO SELL AI SERVICES TO BYTEDANCE"),
    ("SENATORS WARN ON AI CYBER THREAT", "AI ATTACKS OUTPACING DEFENCES"),
    ("RUSSIAN HELD OVER PALANTIR SPYING",
     "ARRESTED FOR SPYING ON US DEFENCE FIRM"),
    ("CARNEY ADJUSTS CHINA TIES", "CANADA SEEKS RIGHT DEAL WITH US"),
    # column 3: Americas + Africa + world
    ("JEFFRIES SET FOR SPEAKER", "NOMINATED WITH 251 VOTES"),
    ("US AND VENEZUELA RESTORE MILITARY TIES",
     "TRAINING AND INTELLIGENCE TIES RESUME"),
    ("CANADA SANCTIONS SETTLERS", "MEASURES OVER WEST BANK EXPANSION"),
    ("PANAMA ARREST IN JOURNALIST ATTACK",
     "SECOND SUSPECT HELD OVER HOME ATTACK"),
    ("SUDAN DEATH TOLL CONFIRMED", "UN COUNTS OVER 2,230 CIVILIAN DEATHS"),
    ("LIBYA DRUG HAUL", "COCAINE AND MILLIONS OF PILLS SEIZED"),
    ("ETHIOPIA-ERITREA TROOPS MASS", "CLASH FEARS RISE NEAR BADME"),
    ("SOWETO FLOODS KILL ONE", "CHILD MISSING AFTER HEAVY RAIN"),
    ("MALAWI WATER 74% TAINTED", "GOLD MINING POLLUTES SUPPLY"),
    ("RUTO ADDRESSES THE NATION", "KENYAN LEADER SEEKS SECOND TERM"),
    ("MCDONALD'S ABUSE REPORT", "STAFF SAY THEY WAITED FOR GIRLS TO TURN 18"),
    ("WORLD COPD DAY", "EARLY DIAGNOSIS IN FOCUS"),
    ("ISLAM TO TOP WORLD FAITHS BY 2035",
     "PEW REPORT PROJECTS LARGEST RELIGION"),
]


def draw_page():
    rect(0, 0, W, H, PAPER)
    # masthead
    draw_text_centered(W // 2, 12, "THE WORLD", 6, INK)
    draw_text_centered(W // 2, 60, "THURSDAY 19 NOVEMBER 2026", 2, INK)
    rect(16, 84, 992, 3, INK)
    # UTC timeline strip
    draw_timeline()
    # anchor grid: rows 1-4 (h 84), row 5 (h 124)
    cols = (16, 352, 688)
    rows = (118, 207, 296, 385)
    for r in range(4):
        for c in range(3):
            kicker, headline, sub, scene_fn = ANCHORS[r * 3 + c]
            anchor_card(cols[c], rows[r], 320, 84, kicker, headline, sub,
                        scene_fn, 36)
    kicker, headline, sub, scene_fn = ANCHORS[12]
    anchor_card(16, 474, 320, 124, kicker, headline, sub, scene_fn, 56)
    frame(352, 474, 320, 124, INK)
    scene_map_numbered(353, 475, 318, 122)
    index_panel(688, 474, 320, 124)
    # briefs header
    draw_text_centered(W // 2, 606, "THE DAY IN BRIEF - 39 MORE STORIES", 2,
                       INK)
    rect(16, 626, 992, 2, INK)
    # briefs: 3 columns x 13 rows
    for i, (head, cap) in enumerate(BRIEFS):
        col = i // 13
        row = i % 13
        bx = 16 + col * 336
        by = 632 + row * 27
        draw_text(bx, by, head, 1, INK)
        draw_text(bx, by + 11, cap, 1, GREY)
        if row < 12:
            hline(bx, by + 24, 320, LIGHT)
    # footer
    rect(16, 988, 992, 2, INK)
    draw_text_centered(W // 2, 996, "52 STORIES, ONE DAY", 2, RED)


def main():
    draw_page()
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output/entry.png")
    if out_dir.endswith(".png"):
        path = out_dir
    else:
        os.makedirs(out_dir, exist_ok=True)
        path = os.path.join(out_dir, "entry.png")
    parent = os.path.dirname(path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    with open(path, "wb") as f:
        f.write(png_bytes())
    print("wrote", path)


if __name__ == "__main__":
    main()
