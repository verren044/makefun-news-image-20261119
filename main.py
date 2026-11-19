#!/usr/bin/env python3
"""THE WORLD, THURSDAY 19 NOVEMBER 2026.

One-image summary of the day's world news: a dense newspaper front page
drawn entirely in code. Pure Python 3.13 standard library, deterministic,
no network, no randomness, no external files.
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

# ---------------------------------------------------------------------- scenes
def draw_flag_us(x, y, w, h):
    rect(x, y, w, h, WHITE)
    for i in range(7):
        if i % 2 == 0:
            rect(x, y + i * h // 7, w, h // 7 + 1, RED)
    rect(x, y, w * 2 // 5, h * 4 // 7, BLUE)
    for r in range(4):
        for c in range(5):
            set_px(x + 3 + c * 4, y + 3 + r * 4, WHITE)


def draw_flag_cn(x, y, w, h):
    rect(x, y, w, h, RED)
    star(x + w // 5, y + h // 3, 6, 3, YELLOW)
    star(x + w // 2, y + h // 5, 3, 1, YELLOW)
    star(x + w * 3 // 5, y + h // 3, 3, 1, YELLOW)
    star(x + w * 3 // 5, y + h // 2, 3, 1, YELLOW)
    star(x + w // 2, y + h * 2 // 3, 3, 1, YELLOW)


def draw_flag_ru(x, y, w, h):
    rect(x, y, w, h // 3 + 1, WHITE)
    rect(x, y + h // 3, w, h // 3 + 1, BLUE)
    rect(x, y + 2 * h // 3, w, h - 2 * h // 3, RED)


def draw_figure(x, y, c, flip):
    """Simple standing figure, y = feet. flip: facing right (+1) / left (-1)."""
    circle(x, y - 34, 5, c)
    line(x, y - 28, x, y - 8, c, 3)
    line(x, y - 8, x - 6, y, c, 3)
    line(x, y - 8, x + 6, y, c, 3)
    line(x, y - 26, x - 8, y - 16, c, 2)
    line(x, y - 26, x + 8 * flip, y - 18, c, 2)


def scene_shenzhen(x, y, w, h):
    rect(x, y, w, h, SKY)
    circle(x + w - 52, y + 24, 16, (240, 214, 120))
    # skyline
    heights = [62, 96, 74, 118, 84, 104, 66, 92]
    bw = w // 8
    base = y + h - 34
    for i, bh in enumerate(heights):
        bx = x + i * bw
        rect(bx + 2, base - bh, bw - 4, bh, (52, 66, 92))
        for wy in range(base - bh + 8, base - 6, 14):
            for wx in range(bx + 7, bx + bw - 7, 11):
                rect(wx, wy, 4, 5, YELLOW)
    rect(x, base, w, 34, (88, 96, 88))
    # three flags on poles
    fx = x + w // 2 - 66
    for i, fn in enumerate((draw_flag_us, draw_flag_cn, draw_flag_ru)):
        px = fx + i * 48
        vline(px, y + 52, h - 52 - 34, INK)
        fn(px + 1, y + 52, 42, 26)
    # handshake figures
    draw_figure(x + w // 2 - 34, base, INK, 1)
    draw_figure(x + w // 2 + 34, base, (120, 30, 30), -1)
    line(x + w // 2 - 26, base - 18, x + w // 2 + 26, base - 18, INK, 2)


def scene_kerch(x, y, w, h):
    rect(x, y, w, h, NIGHT)
    for sx, sy in ((30, 18), (90, 34), (170, 14), (250, 40), (330, 20),
                   (410, 30), (60, 60), (300, 62), (450, 52), (200, 48)):
        set_px(x + sx, y + sy, WHITE)
        set_px(x + sx + 1, y + sy, WHITE)
    circle(x + w - 60, y + 26, 15, (238, 232, 200))
    circle(x + w - 66, y + 22, 3, (200, 192, 160))
    # sea
    rect(x, y + h - 52, w, 52, SEA)
    # bridge deck and arch
    deck_y = y + h - 66
    rect(x, deck_y, w, 8, (120, 118, 110))
    for i in range(5):
        px = x + 40 + i * 96
        rect(px, deck_y + 8, 6, h - 66 - 8, (96, 94, 88))
    for t in range(0, 181, 4):
        ax = x + w // 2 + int(190 * math.cos(math.radians(t)))
        ay = deck_y - int(52 * math.sin(math.radians(t)))
        rect(ax - 2, ay - 2, 5, 5, (150, 148, 140))
    # explosion flash over the bridge
    ex, ey = x + w // 2 + 40, deck_y - 14
    star(ex, ey, 30, 12, ORANGE)
    star(ex, ey, 18, 8, YELLOW)
    circle(ex, ey, 8, WHITE)
    circle(ex - 22, ey - 18, 10, (90, 88, 84))
    circle(ex + 26, ey - 24, 8, (90, 88, 84))
    # moon reflection and sparks on the water
    for i in range(6):
        rect(x + w - 78 + i * 6, y + h - 44 + i * 5, 26 - i * 3, 2,
             (200, 196, 170))
    for sx, sy in ((ex - 30, deck_y + 22), (ex + 44, deck_y + 30),
                   (ex + 8, deck_y + 16)):
        set_px(sx, sy, ORANGE)


def scene_anthropic(x, y, w, h):
    rect(x, y, w, h, WHITE)
    for gy in range(y + 24, y + h - 30, 24):
        hline(x + 8, gy, w - 16, LIGHT)
    # rising bars
    bars = [26, 40, 34, 58, 52, 76, 92]
    bw = (w - 40) // 7
    base = y + h - 52
    for i, bh in enumerate(bars):
        rect(x + 20 + i * bw, base - bh, bw - 8, bh, BLUE)
    # rising line with arrow
    pts = [(x + 24, base - 26), (x + 70, base - 44), (x + 116, base - 36),
           (x + 162, base - 62), (x + 208, base - 58), (x + 254, base - 88),
           (x + 296, base - 100)]
    for i in range(len(pts) - 1):
        line(pts[i][0], pts[i][1], pts[i + 1][0], pts[i + 1][1], RED, 3)
    line(pts[-1][0], pts[-1][1], pts[-1][0] - 12, pts[-1][1] + 2, RED, 3)
    line(pts[-1][0], pts[-1][1], pts[-1][0] - 4, pts[-1][1] + 12, RED, 3)
    # big number
    draw_text_centered(x + w // 2, y + 8, "$81.3BN", 3, RED)
    draw_text_centered(x + w // 2, y + h - 24, "BIGGEST IPO EVER", 1, GREY)


def scene_gaza(x, y, w, h):
    rect(x, y, w, h, SAND)
    circle(x + w - 44, y + 22, 14, (240, 200, 110))
    ellipse(x + 70, y + h - 12, 70, 10, SAND2)
    ellipse(x + w - 70, y + h - 10, 70, 10, SAND2)
    # ceasefire line: dashed yellow line down the middle
    for dy in range(0, h - 20, 16):
        rect(x + w // 2 - 1, y + 8 + dy, 3, 10, YELLOW)
    draw_text(x + w // 2 + 8, y + 12, "YELLOW", 1, (120, 90, 20))
    draw_text(x + w // 2 + 8, y + 22, "LINE", 1, (120, 90, 20))

    def tank(tx, ty, c):
        rect(tx, ty, 64, 16, c)
        rect(tx + 14, ty - 10, 34, 12, c)
        line(tx + 48, ty - 4, tx + 78, ty - 10, c, 4)
        for wx in range(5):
            circle(tx + 8 + wx * 13, ty + 18, 5, INK)
        rect(tx - 2, ty + 14, 68, 4, INK)

    tank(x + 26, y + h - 62, (92, 96, 66))
    tank(x + w - 96, y + h - 44, (110, 104, 70))
    circle(x + 60, y + 30, 7, (120, 118, 110))
    circle(x + 70, y + 22, 5, (120, 118, 110))


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

MARKERS = [
    ("SHENZHEN", 114.0, 22.5, 6, -12),
    ("KERCH", 36.4, 45.3, -40, 8),
    ("GAZA", 34.5, 31.5, -46, 8),
    ("GULF", 51.0, 26.0, -34, 2),
    ("MYANMAR", 96.0, 21.0, -56, 12),
    ("WASHINGTON", -77.0, 38.9, -62, -12),
    ("LONDON", -0.1, 51.5, 6, -12),
    ("NEW DELHI", 77.2, 28.6, 8, 10),
]


def scene_map(x, y, w, h):
    rect(x, y, w, h, OCEAN)
    for lonlat in CONTINENTS.values():
        pts = []
        for lon, lat in lonlat:
            px = x + int((lon + 180) / 360.0 * w)
            py = y + int((75 - lat) / 135.0 * h)
            pts.append((px, py))
        poly(pts, GREEN)
    for name, lon, lat, dx, dy in MARKERS:
        mx = x + int((lon + 180) / 360.0 * w)
        my = y + int((75 - lat) / 135.0 * h)
        circle(mx, my, 4, RED)
        circle(mx, my, 2, WHITE)
        lx = mx + dx
        ly = my + dy
        lx = max(x + 2, min(x + w - 2 - text_width(name, 1), lx))
        ly = max(y + 2, min(y + h - 9, ly))
        draw_text(lx, ly, name, 1, INK)


# ---------------------------------------------------------------------- layout
def anchor_panel(x, y, w, h, kicker, headline, sub, scene_fn):
    frame(x, y, w, h, INK)
    scene_h = 158
    scene_fn(x + 1, y + 1, w - 2, scene_h)
    hline(x + 1, y + scene_h + 1, w - 2, INK)
    ty = y + scene_h + 10
    draw_text(x + 10, ty, kicker, 1, RED)
    draw_text(x + 10, ty + 12, headline, 2, INK)
    draw_text(x + 10, ty + 30, sub, 1, GREY)


BRIEFS = [
    ("ICJ TO RULE ON MYANMAR", "HISTORIC ROHINGYA GENOCIDE VERDICT DUE"),
    ("JEFFRIES SET FOR SPEAKER", "FIRST BLACK SPEAKER OF THE US HOUSE"),
    ("VAN GOGH SELLS FOR $190.4M", "RECORD PRICE AFTER NAZI-ERA ROW"),
    ("CYCLONE AKVAN NEARS INDIA", "STORM TO CROSS BETWEEN MACHILIPATNAM AND PURI"),
    ("US AND VENEZUELA RESTORE MILITARY TIES", "TRAINING AND INTELLIGENCE TIES RESUME"),
    ("NORTH KOREA ENRICHMENT EXPANDS", "IAEA REPORTS URANIUM GROWTH"),
    ("CANADA SANCTIONS SETTLERS", "MEASURES OVER WEST BANK EXPANSION"),
    ("NVIDIA HALTS H-SERIES TO CHINA", "ACTING CEO ALSO PROMISES EARLIER PAY"),
    ("FED MINUTES POINT TO MORE HIKES", "MOST OFFICIALS EXPECT FURTHER RISES"),
    ("VOYAGER 1 HITS ONE LIGHT-DAY", "PROBE AT RECORD DISTANCE, 50 YEARS ON"),
    ("GTA VI ROLLS OUT WORLDWIDE", "GAMERS ENTER VICE CITY AT LAUNCH"),
    ("EU PROPOSES 45BN EURO UKRAINE LOAN", "REPAID AFTER RUSSIA PAYS REPARATIONS"),
    ("GULF WAR WIDENS", "IRAN HITS BASES; TANKER STRUCK, CREW SAFE"),
    ("OIL PRICES FALL", "SUPPLY GAINS OUTWEIGH MIDDLE EAST FEARS"),
    ("MICROSOFT EYES BYTEDANCE AI DEAL", "TALKS TO SELL AI SERVICES TO BYTEDANCE"),
    ("RIYADH DANGER PASSED", "THREE SOUTHERN CITIES CLEARED AFTER ALERTS"),
    ("LIU YUNPING MAKES HISTORY", "FIRST TAIWANESE AMERICAN CAUCUS CHAIR"),
    ("SUDAN DEATH TOLL CONFIRMED", "UN COUNTS OVER 2,230 CIVILIAN DEATHS"),
    ("INDIA-JAPAN 2+2 IN TOKYO", "DEFENCE AND FOREIGN MINISTERS MEET"),
    ("SINDHU BACK IN TOP FIVE", "INDIAN STAR RETURNS TO WORLD TOP FIVE"),
    ("ISLAM TO TOP WORLD FAITHS BY 2035", "PEW REPORT PROJECTS LARGEST RELIGION"),
    ("DELHI SCHOOLS REOPEN", "OFFLINE CLASSES RESUME AS CURBS LIFT"),
    ("RUSSIAN HELD OVER PALANTIR SPYING", "ARRESTED FOR SPYING ON US DEFENCE FIRM"),
    ("MCDONALD'S ABUSE REPORT", "STAFF SAY THEY WAITED FOR GIRLS TO TURN 18"),
    ("WORLD COPD DAY", "EARLY DIAGNOSIS IN FOCUS"),
    ("SENATORS WARN ON AI CYBER THREAT", "AI ATTACKS OUTPACING DEFENCES"),
    ("EU-INDONESIA TRADE DEALS APPROVED", "COUNCIL SIGNS OFF AGREEMENTS"),
    ("LIBYA DRUG HAUL", "COCAINE AND MILLIONS OF PILLS SEIZED"),
    ("PANAMA ARREST IN JOURNALIST ATTACK", "SECOND SUSPECT HELD OVER HOME ATTACK"),
    ("PARAGUAY BANK DEADLINE EXTENDED", "UENO GUARANTEE EXTENDED TO 2 DECEMBER"),
    ("US SANCTIONS HEZBOLLAH-LINKED NETWORK", "THREE ENTITIES AND THREE PEOPLE LISTED"),
    ("US-PHILIPPINES EYE $2BN LOAN", "FINANCING PACKAGE PURSUED VIA FMF"),
    ("MELENCHON COULD WIN IN FRANCE", "JUSTICE MINISTER WARNS ON HARD LEFT"),
    ("CARNEY ADJUSTS CHINA TIES", "CANADA SEEKS RIGHT DEAL WITH US"),
    ("64 CHILDREN KILLED IN YEMEN", "UNICEF TOLL SINCE 3 SEPTEMBER"),
    ("YEMEN MISSILE THREAT TO RIYADH", "COALITION REPORTS THREAT; FRAGMENTS FOUND"),
]


def draw_page():
    rect(0, 0, W, H, PAPER)
    # masthead
    draw_text_centered(W // 2, 12, "THE WORLD", 6, INK)
    draw_text_centered(W // 2, 60, "THURSDAY 19 NOVEMBER 2026", 2, INK)
    rect(16, 84, 992, 3, INK)
    # row 1: two big anchors
    anchor_panel(16, 94, 488, 240, "APEC SUMMIT", "TRILATERAL IN SHENZHEN",
                 "TRUMP, XI AND PUTIN MEET AT APEC", scene_shenzhen)
    anchor_panel(520, 94, 488, 240, "CRIMEA", "KERCH BRIDGE HIT AGAIN",
                 "THIRD NIGHT RUNNING, TRAFFIC CLOSED", scene_kerch)
    # row 2: two anchors + world map
    anchor_panel(16, 342, 320, 240, "MARKETS", "ANTHROPIC'S RECORD IPO",
                 "$81.3BN RAISED, VALUED ABOVE $1.4TN", scene_anthropic)
    anchor_panel(352, 342, 320, 240, "MIDDLE EAST", "GAZA LINE CROSSED",
                 "TANKS ADVANCE PAST CEASEFIRE LINE", scene_gaza)
    anchor_panel(688, 342, 320, 240, "WHERE IT HAPPENED", "THE WORLD MAP",
                 "EIGHT STORY SITES MARKED IN RED", scene_map)
    # briefs header
    draw_text_centered(W // 2, 592, "THE DAY IN BRIEF", 2, INK)
    rect(16, 614, 992, 2, INK)
    # briefs: 3 columns x 12 rows
    for i, (head, cap) in enumerate(BRIEFS):
        col = i // 12
        row = i % 12
        bx = 16 + col * 336
        by = 622 + row * 30
        draw_text(bx, by, head, 1, INK)
        draw_text(bx, by + 11, cap, 1, GREY)
        if row < 11:
            hline(bx, by + 24, 320, LIGHT)
    # footer
    rect(16, 984, 992, 2, INK)
    draw_text_centered(W // 2, 994, "40 STORIES, ONE DAY", 2, RED)


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
