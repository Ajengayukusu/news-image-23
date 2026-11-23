#!/usr/bin/env python3
"""Render the 23 November 2026 front page into assets/entry.png.

A single-page newspaper drawn with Pillow and the system DejaVu fonts:
a teal masthead naming the day, a lead panel on the COP31 collapse with
a cracked-globe motif, six story cards in a 3x2 grid (each with its own
small drawn motif), and a dark footer ticker of shorter items. Every
fact comes from news first reported on Monday 23 November 2026, as
gathered from live sources while building this entry (BBC, The Hindu,
Reuters via Google News, AFP wire, USGS). Output is 1024x1024 PNG,
under 1 MiB, byte-identical on every run.
"""

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

PAGE = 1024
MARGIN = 28
PAPER = (251, 250, 244)
INK = (20, 20, 20)
TEAL = (11, 61, 74)
TEAL_DARK = (7, 44, 54)
GOLD = (198, 158, 38)
CRIMSON = (172, 30, 30)
GREY = (110, 110, 102)
RULE = (206, 206, 196)
CARD = (247, 247, 239)
SEA = (46, 120, 138)
FLAME = (214, 96, 32)

FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")


def font(name, size):
    return ImageFont.truetype(str(FONT_DIR / name), size)


SERIF_B = lambda s: font("DejaVuSerif-Bold.ttf", s)  # noqa: E731
SERIF = lambda s: font("DejaVuSerif.ttf", s)  # noqa: E731
SANS_B = lambda s: font("DejaVuSans-Bold.ttf", s)  # noqa: E731
SANS = lambda s: font("DejaVuSans.ttf", s)  # noqa: E731


def wrap_text(draw, text, fnt, width):
    """Greedy word wrap returning a list of lines fitting width."""
    lines = []
    for paragraph in text.split("\n"):
        current = ""
        for word in paragraph.split():
            trial = (current + " " + word).strip()
            if draw.textlength(trial, font=fnt) <= width or not current:
                current = trial
            else:
                lines.append(current)
                current = word
        if current:
            lines.append(current)
    return lines


def paragraph(draw, text, fnt, width, x, y, fill=INK, leading=4):
    for line in wrap_text(draw, text, fnt, width):
        draw.text((x, y), line, font=fnt, fill=fill)
        y += fnt.size + leading
    return y


def globe(draw, cx, cy, r, fill=SEA):
    """A simple globe: disc, meridians, parallels, and a jagged crack."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=fill,
                 outline=TEAL_DARK, width=4)
    for k in range(1, 4):
        rx = r * k / 4
        draw.ellipse([cx - rx, cy - r, cx + rx, cy + r],
                     outline=(255, 255, 255), width=2)
    for frac in (-0.5, 0.0, 0.5):
        yy = cy + frac * r
        half = int(r * math.sqrt(max(0.0, 1 - frac * frac)))
        draw.line([cx - half, yy, cx + half, yy], fill=(255, 255, 255),
                  width=2)
    crack = [(cx - r * 0.15, cy - r * 0.9), (cx + r * 0.1, cy - r * 0.45),
             (cx - r * 0.2, cy - r * 0.1), (cx + r * 0.25, cy + r * 0.25),
             (cx - r * 0.05, cy + r * 0.6), (cx + r * 0.2, cy + r * 0.95)]
    draw.line(crack, fill=(255, 255, 255), width=5, joint="curve")


def rubble(draw, x, y, w, h):
    """Broken building silhouette: two leaning blocks and dust dots."""
    draw.polygon([(x, y + h), (x, y + 18), (x + w * 0.45, y),
                  (x + w * 0.5, y + h)], fill=(120, 120, 112))
    draw.polygon([(x + w * 0.55, y + h), (x + w * 0.6, y + 26),
                  (x + w, y + 8), (x + w, y + h)], fill=(88, 88, 82))
    for dx, dy, r in ((6, 8, 3), (20, 4, 2), (34, 10, 3), (48, 5, 2)):
        draw.ellipse([x + dx, y + h - dy - r, x + dx + r, y + h - dy],
                     fill=GREY)


def waves_ship(draw, x, y, w, h):
    """A small ship on three wave lines."""
    draw.polygon([(x + 6, y + 26), (x + w - 6, y + 26),
                  (x + w - 16, y + 42), (x + 16, y + 42)], fill=TEAL)
    draw.rectangle([x + w // 2 - 4, y + 6, x + w // 2 + 4, y + 26],
                   fill=TEAL_DARK)
    for i, yy in enumerate((y + 50, y + 60, y + 70)):
        draw.arc([x, yy - 8, x + w, yy + 8], 200, 340,
                 fill=SEA, width=3)


def seismograph(draw, x, y, w, h):
    """A quake trace: flat line, sharp spikes, flat again."""
    pts = [(x, y + h // 2 + 8)]
    n = 16
    for i in range(1, n + 1):
        xx = x + w * i / n
        if 5 <= i <= 10:
            yy = y + h // 2 + 8 + (h * 0.30 if i % 2 else -h * 0.30)
        else:
            yy = y + h // 2 + 8 + (3 if i % 2 else -3)
        pts.append((xx, yy))
    draw.line(pts, fill=CRIMSON, width=4, joint="curve")


def flame(draw, x, y, w, h):
    """A flame: outer teardrop with an inner tongue."""
    cx = x + w // 2
    draw.polygon([(cx, y + 2), (cx + w * 0.32, y + h * 0.45),
                  (cx + w * 0.22, y + h * 0.75), (cx, y + h),
                  (cx - w * 0.22, y + h * 0.75),
                  (cx - w * 0.32, y + h * 0.45)], fill=FLAME)
    draw.polygon([(cx, y + h * 0.35), (cx + w * 0.16, y + h * 0.62),
                  (cx, y + h * 0.85), (cx - w * 0.16, y + h * 0.62)],
                 fill=GOLD)


def crowd(draw, x, y, w, h):
    """A marching crowd: rows of heads with one placard."""
    for row, yy in enumerate((y + 46, y + 62)):
        for i in range(5):
            xx = x + 8 + i * 13 + (6 if row else 0)
            draw.ellipse([xx, yy, xx + 10, yy + 10], fill=TEAL)
            draw.rectangle([xx - 1, yy + 11, xx + 11, yy + 22],
                           fill=TEAL_DARK)
    draw.rectangle([x + w - 30, y + 8, x + w - 4, y + 34], fill=CRIMSON)
    draw.line([x + w - 17, y + 34, x + w - 17, y + h - 6],
              fill=INK, width=3)


def ball_flag(draw, x, y, w, h):
    """A football beside a chequered flag strip."""
    cx, cy, r = x + 26, y + h // 2, 24
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=(255, 255, 255),
                 outline=INK, width=3)
    draw.polygon([(cx, cy - 9), (cx + 9, cy - 3), (cx + 5, cy + 8),
                  (cx - 5, cy + 8), (cx - 9, cy - 3)], fill=INK)
    for k in range(4):
        sq = 8
        xx = x + 52 + (k % 2) * sq
        yy = y + 18 + (k // 2) * sq
        if (k % 2 == 0) != ((k // 2) % 2 == 0):
            draw.rectangle([xx, yy, xx + sq, yy + sq], fill=INK)


MOTIFS = {"globe": globe, "rubble": rubble, "waves": waves_ship,
          "quake": seismograph, "flame": flame, "crowd": crowd,
          "ball": ball_flag}


def story_card(draw, x, y, w, h, motif, kicker, head, body):
    draw.rectangle([x, y, x + w, y + h], fill=CARD, outline=RULE, width=2)
    draw.rectangle([x, y, x + w, y + 4], fill=TEAL)
    mx, my = x + 12, y + 12
    if motif == "globe":
        globe(draw, mx + 30, my + 30, 28)
    elif motif in MOTIFS:
        MOTIFS[motif](draw, mx, my, 64, 64)
    tx = x + 88
    draw.text((tx, y + 14), kicker, font=SANS_B(16), fill=CRIMSON)
    yy = paragraph(draw, head, SERIF_B(24), w - 102, tx, y + 38, leading=2)
    paragraph(draw, body, SERIF(17), w - 28, x + 14, yy + 6, leading=3)


def main():
    img = Image.new("RGB", (PAGE, PAGE), PAPER)
    d = ImageDraw.Draw(img)

    # Masthead.
    d.rectangle([0, 0, PAGE, 148], fill=TEAL)
    globe(d, 86, 74, 52)
    d.text((158, 26), "THE WORLD IN ONE PAGE", font=SERIF_B(52),
           fill=(255, 255, 255))
    d.text((160, 92), "MONDAY  ·  23 NOVEMBER 2026", font=SANS_B(30),
           fill=GOLD)
    d.text((158, 124), "make.fun daily news picture",
           font=SANS(17), fill=(200, 220, 224))
    d.rectangle([0, 148, PAGE, 154], fill=GOLD)

    # Lead story: COP31 collapse.
    ly = 168
    d.rectangle([MARGIN, ly, PAGE - MARGIN, ly + 236], fill=CARD,
                outline=RULE, width=2)
    globe(d, 150, ly + 118, 92)
    d.rectangle([212, ly + 196, 322, ly + 224], fill=CRIMSON)
    d.text((222, ly + 200), "NO DEAL", font=SANS_B(18),
           fill=(255, 255, 255))
    tx = 330
    d.text((tx, ly + 16), "CLIMATE  ·  COP31, TÜRKIYE", font=SANS_B(18),
           fill=CRIMSON)
    yy = paragraph(d, "Climate talks collapse as\nfossil-fuel deal fails",
                   SERIF_B(40), PAGE - MARGIN - tx - 16, tx, ly + 46,
                   leading=2)
    paragraph(d, "Two weeks of negotiation in Antalya end without "
                 "agreement, as the EU and others reject any pact "
                 "lacking a fossil-fuel phase-out.",
              SERIF(21), PAGE - MARGIN - tx - 16, tx, yy + 8, leading=4)

    # Six story cards, 3 x 2.
    cards = [
        ("rubble", "UKRAINE",
         "Boy, 7, pulled alive from rubble",
         "Rescuers find a child hours after a Russian strike levels "
         "a home in the Kyiv region; 14 people still missing."),
        ("waves", "LIBYA",
         "Drones blamed for blast on Russian ship",
         "An explosion rocks a Russian vessel at Benghazi port; "
         "officials suspect a sea-drone attack."),
        ("quake", "VANUATU",
         "Magnitude 6.5 quake strikes",
         "A deep tremor shakes the Vanuatu region at 02:40 UTC; "
         "no tsunami warning is issued."),
        ("flame", "INDONESIA",
         "Factory fire leaves 50 missing",
         "Seven bodies are recovered after a blaze at an Indonesian "
         "factory; dozens remain unaccounted for."),
        ("crowd", "LISBON",
         "Thousands march over living costs",
         "Crowds fill Lisbon's streets to protest rising prices "
         "and falling living standards."),
        ("ball", "SPORT",
         "UK set for 2035 Women's World Cup",
         "FIFA is to confirm the United Kingdom as host; Verstappen "
         "wins the Las Vegas Grand Prix."),
    ]
    cw = (PAGE - 2 * MARGIN - 2 * 16) // 3
    ch = 216
    top = 424
    for i, (motif, kicker, head, body) in enumerate(cards):
        cx = MARGIN + (i % 3) * (cw + 16)
        cy = top + (i // 3) * (ch + 16)
        story_card(d, cx, cy, cw, ch, motif, kicker, head, body)

    # Footer ticker.
    fy = 888
    d.rectangle([0, fy, PAGE, PAGE], fill=TEAL_DARK)
    ticker = ("US  ·  Democrats win their biggest House majority since "
              "1992    —    INDIA–NEPAL  ·  Modi meets PM Balen Shah in "
              "Delhi    —    HEALTH  ·  NHS launches the world's largest "
              "AI breast-cancer trial    —    OBITUARY  ·  Jeweller Paolo "
              "Bulgari dies at 89")
    paragraph(d, ticker, SANS(19), PAGE - 2 * MARGIN, MARGIN, fy + 16,
              fill=(235, 238, 235), leading=8)

    out = Path(__file__).resolve().parent / "assets" / "entry.png"
    img.save(out, format="PNG", optimize=True)
    print(f"wrote {out} ({out.stat().st_size} bytes)")


if __name__ == "__main__":
    main()
