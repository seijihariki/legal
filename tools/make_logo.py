#!/usr/bin/env python3
"""Generate the app logo (PNG, no dependencies).

Writes logo.png (512x512), logo-120.png (120x120, what Google Cloud wants on the
OAuth consent screen), favicon.png (64x64). Design: rounded slate/blue tile with a
white house glyph and a small accent dot, anti-aliased by 4x supersampling.
"""
import struct
import zlib
import sys

# brand colours
BG_TOP = (0x17, 0x23, 0x3B)
BG_BOTTOM = (0x2B, 0x6C, 0xB0)
GLYPH = (0xFF, 0xFF, 0xFF)
ACCENT = (0x7C, 0xB0, 0xE8)


def rounded_rect(x, y, s, r):
    """Normalised point in a rounded square of side s, corner radius r."""
    cx, cy = s / 2, s / 2
    dx, dy = abs(x - cx), abs(y - cy)
    half = s / 2
    qx, qy = dx - (half - r), dy - (half - r)
    if qx <= 0 or qy <= 0:
        return dx <= half and dy <= half
    return qx * qx + qy * qy <= r * r


def in_triangle(px, py, a, b, c):
    def sign(p1, p2, p3):
        return (p1[0] - p3[0]) * (p2[1] - p3[1]) - (p2[0] - p3[0]) * (p1[1] - p3[1])

    d1 = sign((px, py), a, b)
    d2 = sign((px, py), b, c)
    d3 = sign((px, py), c, a)
    has_neg = d1 < 0 or d2 < 0 or d3 < 0
    has_pos = d1 > 0 or d2 > 0 or d3 > 0
    return not (has_neg and has_pos)


def in_rect(px, py, x0, y0, x1, y1):
    return x0 <= px <= x1 and y0 <= py <= y1


def in_circle(px, py, cx, cy, r):
    return (px - cx) ** 2 + (py - cy) ** 2 <= r * r


def render(size):
    """Return (width, height, rows of RGB tuples) at `size` px."""
    s = float(size)
    ss = 4                      # supersamples per axis
    roof = ((0.50 * s, 0.20 * s), (0.13 * s, 0.50 * s), (0.87 * s, 0.50 * s))
    body = (0.23 * s, 0.48 * s, 0.77 * s, 0.82 * s)
    door = (0.42 * s, 0.62 * s, 0.58 * s, 0.82 * s)
    dot = (0.745 * s, 0.245 * s, 0.075 * s)
    radius = 0.23 * s

    rows = []
    for py in range(size):
        row = []
        for px in range(size):
            bg_acc = [0, 0, 0]
            glyph_cov = 0
            accent_cov = 0
            for oy in range(ss):
                for ox in range(ss):
                    x = px + (ox + 0.5) / ss
                    y = py + (oy + 0.5) / ss
                    if not rounded_rect(x, y, s, radius):
                        continue
                    t = y / s
                    bg_acc[0] += BG_TOP[0] + (BG_BOTTOM[0] - BG_TOP[0]) * t
                    bg_acc[1] += BG_TOP[1] + (BG_BOTTOM[1] - BG_TOP[1]) * t
                    bg_acc[2] += BG_TOP[2] + (BG_BOTTOM[2] - BG_TOP[2]) * t
                    house = in_triangle(x, y, *roof) or (
                        in_rect(x, y, *body) and not in_rect(x, y, *door)
                    )
                    if in_circle(x, y, *dot):
                        accent_cov += 1
                    elif house:
                        glyph_cov += 1
            n = ss * ss
            bg = [c / n for c in bg_acc]
            # nothing painted outside the tile at all
            if bg == [0, 0, 0] and not glyph_cov and not accent_cov:
                row.append((0, 0, 0))
                continue
            alpha_g = glyph_cov / n
            alpha_a = accent_cov / n
            r = bg[0] * (1 - alpha_g - alpha_a) + GLYPH[0] * alpha_g + ACCENT[0] * alpha_a
            g = bg[1] * (1 - alpha_g - alpha_a) + GLYPH[1] * alpha_g + ACCENT[1] * alpha_a
            b = bg[2] * (1 - alpha_g - alpha_a) + GLYPH[2] * alpha_g + ACCENT[2] * alpha_a
            row.append((int(round(r)), int(round(g)), int(round(b))))
        rows.append(row)
    return size, size, rows


def write_png(path, w, h, rows):
    raw = bytearray()
    for row in rows:
        raw.append(0)  # filter: none
        for r, g, b in row:
            raw += bytes((r, g, b))

    def chunk(tag, data):
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)
    print(f"wrote {path} ({w}x{h}, {len(png)} bytes)")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    for name, size in (("logo.png", 512), ("logo-120.png", 120), ("favicon.png", 64)):
        write_png(f"{out}/{name}", *render(size))
