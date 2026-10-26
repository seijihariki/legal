#!/usr/bin/env python3
"""Generate the app logo (PNG, no dependencies).

Design: "signal roof" — three stacked chevrons forming a gabled roof over a small
hub, on a dark slate-to-blue tile. Reads as a house and as a signal, and is
deliberately not a copy of any third-party mark.

Everything is drawn from signed distance fields, so the edges are analytically
anti-aliased at any size (no supersampling).

Writes, with an alpha channel (so the tile's corners are transparent):
logo.png (512x512), logo-120.png (120x120), favicon.png (64x64) and
logo-120-solid.png (120x120, fully opaque square — the safest file to upload to the
Google OAuth consent screen, which shows the logo on a white card).
"""
import math
import struct
import zlib
import sys

TILE_TOP = (0x08, 0x1C, 0x14)
TILE_BOTTOM = (0x12, 0x7A, 0x50)

CHEVRONS = [
    # (apex_y, half_width, thickness, colour, alpha)
    (0.300, 0.135, 0.060, (0xFF, 0xFF, 0xFF), 1.0),
    (0.430, 0.215, 0.060, (0xC6, 0xF2, 0xD9), 1.0),
    (0.560, 0.295, 0.060, (0x63, 0xD2, 0x9A), 1.0),
]
HUB = (0.5, 0.79, 0.0, (0xFF, 0xFF, 0xFF))  # cx, cy, radius, colour (radius 0 = none)
TILE_RADIUS = 0.235


def sd_round_rect(px, py, cx, cy, hw, hh, r):
    qx, qy = abs(px - cx) - (hw - r), abs(py - cy) - (hh - r)
    return math.hypot(max(qx, 0.0), max(qy, 0.0)) + min(max(qx, qy), 0.0) - r


def sd_segment(px, py, ax, ay, bx, by):
    vx, vy = bx - ax, by - ay
    wx, wy = px - ax, py - ay
    t = 0.0 if vx == vy == 0 else max(0.0, min(1.0, (wx * vx + wy * vy) / (vx * vx + vy * vy)))
    return math.hypot(wx - t * vx, wy - t * vy)


def coverage(d, px):
    """Anti-aliased coverage from a signed distance in normalised units."""
    return max(0.0, min(1.0, 0.5 - d / px))


def blend(dst, colour, alpha):
    return tuple(dst[i] * (1 - alpha) + colour[i] * alpha for i in range(3))


def render(size, solid=False):
    px = 1.0 / size                      # one pixel in normalised units
    radius = 0.0 if solid else TILE_RADIUS
    rows = []
    for iy in range(size):
        y = (iy + 0.5) / size
        row = []
        for ix in range(size):
            x = (ix + 0.5) / size
            # tile
            d_tile = sd_round_rect(x, y, 0.5, 0.5, 0.5, 0.5, radius)
            a_tile = coverage(d_tile, px)
            if a_tile <= 0.0:
                row.append((0, 0, 0, 0))
                continue
            t = 0.5 * (x + y)
            bg = tuple(TILE_TOP[i] + (TILE_BOTTOM[i] - TILE_TOP[i]) * t for i in range(3))
            col = bg
            for apex_y, hw, thick, colour, alpha in CHEVRONS:
                d = min(
                    sd_segment(x, y, 0.5, apex_y, 0.5 - hw, apex_y + hw),
                    sd_segment(x, y, 0.5, apex_y, 0.5 + hw, apex_y + hw),
                )
                c = coverage(d - thick / 2.0, px) * alpha
                if c > 0.0:
                    col = blend(col, colour, c)
            hx, hy, hr, hcol = HUB
            if hr > 0.0:
                c = coverage(math.hypot(x - hx, y - hy) - hr, px)
                if c > 0.0:
                    col = blend(col, hcol, c)
            row.append(
                (int(round(col[0])), int(round(col[1])), int(round(col[2])), int(round(255 * a_tile)))
            )
        rows.append(row)
    return size, size, rows


def write_png(path, w, h, rows):
    raw = bytearray()
    for row in rows:
        raw.append(0)
        for r, g, b, a in row:
            raw += bytes((r, g, b, a))

    def chunk(tag, data):
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 6, 0, 0, 0))  # colour type 6 = RGBA
    png += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
    png += chunk(b"IEND", b"")
    with open(path, "wb") as fh:
        fh.write(png)
    print(f"wrote {path} ({w}x{h}, {len(png)} bytes)")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    for name, size, solid in (
        ("logo.png", 512, False),
        ("logo-120.png", 120, False),
        ("favicon.png", 64, False),
        ("logo-120-solid.png", 120, True),
    ):
        write_png(f"{out}/{name}", *render(size, solid))
