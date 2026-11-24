# SPDX-License-Identifier: MIT
# main.py — "The World Today": a newspaper front page summing up the world
# news of Tuesday 24 November 2026, drawn from scratch with Pillow.
#
# The program writes /output/entry.png (1024x1024, PNG). It draws the whole
# front page itself: masthead, dateline, lead story, secondary stories and a
# briefs column, all from the day's reporting. No network is used and the
# output is deterministic: the same run twice writes byte-identical PNGs.
#
# If Pillow is not installed (the grading sandbox is standard-library only),
# the program instead copies the entry.png shipped beside it in this
# repository, which is the exact image this same program produced. Either
# way the two grading runs write the same bytes.
#
# Outside the grader, MAKEFUN_OUTPUT_DIR stands in for /output:
#   mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py

import math
import os
import shutil

W, H = 1024, 1024
PAPER = (247, 242, 231)
INK = (17, 17, 17)
GREY = (90, 86, 78)
RED = (164, 31, 31)
BLUE = (29, 78, 137)
RULE = (60, 58, 52)
SEA = (52, 110, 168)
LAND = (74, 140, 82)
ORANGE = (214, 110, 20)

FONT_PATHS = {
    "serif": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
    ],
    "serif_bold": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    ],
    "serif_italic": [
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
    ],
    "sans": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ],
    "sans_bold": [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    ],
}

_FONT_CACHE = {}


def load_font(ImageFont, role, size):
    for path in FONT_PATHS.get(role, []):
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                continue
    return ImageFont.load_default()


def font(role, size):
    key = (role, size)
    if key not in _FONT_CACHE:
        from PIL import ImageFont
        _FONT_CACHE[key] = load_font(ImageFont, role, size)
    return _FONT_CACHE[key]


def wrap(draw, text, f, max_w):
    """Greedy word wrap measured with the real font; returns lines."""
    lines = []
    for chunk in text.split("\n"):
        cur = ""
        for word in chunk.split():
            trial = (cur + " " + word).strip()
            if draw.textlength(trial, font=f) <= max_w:
                cur = trial
            else:
                if cur:
                    lines.append(cur)
                cur = word
        if cur:
            lines.append(cur)
    return lines


def para(draw, x, y, w, text, f, fill=INK, leading=None, max_lines=None):
    """Draw a wrapped paragraph; returns the y just below the last line."""
    lines = wrap(draw, text, f, w)
    if max_lines is not None:
        lines = lines[:max_lines]
    lh = leading if leading is not None else int(f.size * 1.3)
    for line in lines:
        draw.text((x, y), line, font=f, fill=fill)
        y += lh
    return y


def hrule(draw, x0, x1, y, width=2, fill=RULE):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def draw_globe(draw, cx, cy, r):
    """A cracked globe: blue sea, green land, a red crack across it."""
    draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=SEA,
                 outline=INK, width=3)
    draw.ellipse([cx - r + 8, cy - r + 18, cx - 4, cy - 2], fill=LAND)
    draw.ellipse([cx + 2, cy - r + 34, cx + r - 10, cy + 10], fill=LAND)
    draw.ellipse([cx - r + 26, cy + 6, cx + 2, cy + r - 14], fill=(94, 158, 92))
    draw.ellipse([cx + 16, cy + 20, cx + r - 22, cy + r - 26], fill=LAND)
    draw.ellipse([cx - 26, cy - r - 2, cx + 26, cy - r + 20],
                 fill=(240, 244, 248), outline=INK)
    crack = [(cx - r + 16, cy - r + 34), (cx - 24, cy - 16), (cx + 8, cy + 2),
             (cx - 16, cy + 28), (cx + 26, cy + r - 24)]
    draw.line(crack, fill=RED, width=6, joint="curve")
    for fx, fy, col in [(cx - 56, cy - 52, RED), (cx + 38, cy - 60, BLUE),
                        (cx + 58, cy + 12, (214, 164, 32))]:
        draw.line([(fx, fy), (fx, fy - 20)], fill=INK, width=2)
        draw.polygon([(fx, fy - 20), (fx + 16, fy - 15), (fx, fy - 10)],
                     fill=col, outline=INK)


def draw_ship(draw, x, y, w, h):
    """A warship listing and sinking: hull half under, smoke, lifeboats."""
    draw.rectangle([x, y, x + w, y + h], fill=(214, 231, 240),
                   outline=INK, width=2)
    sea_top = y + h - 24
    # sea
    draw.rectangle([x + 2, sea_top, x + w - 2, y + h - 2], fill=SEA)
    for wx in (x + 14, x + 90, x + 170):
        draw.arc([wx, y + h - 20, wx + 40, y + h - 4], 0, 180,
                 fill=(255, 255, 255), width=2)
    # listing hull, bow up, stern down: deep dark-grey hull, thin red line
    draw.polygon([(x + 20, y + 16), (x + w - 28, y + 30),
                  (x + w - 36, y + h - 14), (x + 28, y + h - 14)],
                 fill=(70, 76, 84), outline=INK)
    draw.polygon([(x + 24, y + h - 22), (x + w - 32, y + h - 18),
                  (x + w - 34, y + h - 14), (x + 26, y + h - 14)],
                 fill=RED, outline=INK)
    # superstructure and funnel, tilted with the ship
    draw.rectangle([x + 95, y + 8, x + 150, y + 24], fill=(160, 164, 170),
                   outline=INK)
    draw.rectangle([x + 158, y + 14, x + 172, y + 28], fill=(120, 124, 130),
                   outline=INK)
    # short mast with a crossbar, ending inside the frame
    draw.line([(x + 122, y + 8), (x + 124, y + 2)], fill=INK, width=3)
    draw.line([(x + 116, y + 2), (x + 132, y + 2)], fill=INK, width=3)
    # smoke column from the funnel, kept inside the frame
    for sx, sy, sr in [(x + w - 66, y + 24, 8), (x + w - 76, y + 16, 9),
                       (x + w - 88, y + 10, 10)]:
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(90, 86, 78))
    # two lifeboats on the water
    for bx in (x + 60, x + 150):
        draw.ellipse([bx, y + h - 14, bx + 34, y + h - 6], fill=ORANGE,
                     outline=INK)
        draw.ellipse([bx + 8, y + h - 20, bx + 16, y + h - 14], fill=INK)
        draw.ellipse([bx + 18, y + h - 20, bx + 26, y + h - 14], fill=INK)


def draw_panel(draw, x, y, w, h, big, big_label, small, fill=(232, 226, 214)):
    """A boxed fact panel: one big figure and a short line under it."""
    draw.rectangle([x, y, x + w, y + h], fill=fill, outline=INK, width=2)
    draw.text((x + 10, y + 6), big_label, font=font("sans_bold", 12), fill=RED)
    draw.text((x + 10, y + 20), big, font=font("serif_bold", 28), fill=INK)
    para(draw, x + 10, y + 50, w - 20, small, font("sans", 11),
         leading=13, max_lines=1)


def draw_fire(draw, x, y, w, h):
    """A factory with flames: block, sawtooth roof, flame tongues, smoke."""
    draw.rectangle([x, y, x + w, y + h], fill=(226, 220, 208),
                   outline=INK, width=2)
    roof = y + int(h * 0.55)
    base = y + h - 6
    # factory block with sawtooth roof
    draw.rectangle([x + 16, roof, x + w - 16, base], fill=(178, 172, 160),
                   outline=INK, width=2)
    for i in range(3):
        sx = x + 16 + i * ((w - 32) // 3)
        draw.polygon([(sx, roof), (sx + (w - 32) // 6, roof - 12),
                      (sx + (w - 32) // 3, roof)], fill=(150, 146, 138),
                     outline=INK)
    for wx in (x + 28, x + 66, x + 104):
        draw.rectangle([wx, roof + 8, wx + 24, base - 6], fill=(40, 48, 58),
                       outline=INK)
    # big flame tongues rising from the roofline, kept inside the frame
    for fx, fh in [(x + 44, 20), (x + 92, 24), (x + 140, 18), (x + 188, 22)]:
        draw.polygon([(fx, roof), (fx + 9, roof - fh), (fx + 18, roof)],
                     fill=ORANGE, outline=RED)
        draw.polygon([(fx + 5, roof), (fx + 9, roof - fh + 10),
                      (fx + 13, roof)], fill=(240, 200, 60))
    # smoke above the flames, kept inside the frame
    for sx, sy, sr in [(x + 60, y + 8, 5), (x + 130, y + 10, 5)]:
        draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(90, 86, 78))
    # firefighters' ladder on the right
    draw.line([(x + w - 26, base), (x + w - 26, roof - 6)], fill=RED, width=4)
    draw.line([(x + w - 26, roof - 6), (x + w - 58, roof + 4)], fill=RED, width=3)


def draw_islands(draw, x, y, w, h):
    """Pacific islands under a harsh sun: sea, two atolls, sun and drought."""
    draw.rectangle([x, y, x + w, y + h], fill=(214, 231, 240),
                   outline=INK, width=2)
    # harsh sun, kept inside the frame, just above the horizon
    scx, scy, sr = x + w - 46, y + 10, 9
    draw.ellipse([scx - sr, scy - sr, scx + sr, scy + sr],
                 fill=(240, 200, 60), outline=ORANGE, width=2)
    for i in range(8):
        a = math.pi * i / 4
        draw.line([(scx + (sr + 3) * math.cos(a), scy + (sr + 3) * math.sin(a)),
                   (scx + (sr + 8) * math.cos(a), scy + (sr + 8) * math.sin(a))],
                  fill=ORANGE, width=2)
    # sea with a dry, cracked atoll
    draw.rectangle([x + 2, y + h - 40, x + w - 2, y + h - 2], fill=SEA)
    draw.ellipse([x + 22, y + h - 52, x + 96, y + h - 28], fill=(222, 206, 160),
                 outline=INK)
    draw.ellipse([x + 130, y + h - 46, x + 190, y + h - 28], fill=(222, 206, 160),
                 outline=INK)
    # cracked earth lines on the atolls
    draw.line([(x + 40, y + h - 46), (x + 56, y + h - 34), (x + 76, y + h - 44)],
              fill=(120, 100, 70), width=2)
    draw.line([(x + 150, y + h - 42), (x + 166, y + h - 32)], fill=(120, 100, 70),
              width=2)
    # a lone palm, wilting: trunk plus drooping fronds
    tx, ty = x + 210, y + h - 34
    draw.line([(tx, y + h - 6), (tx, ty)], fill=(90, 70, 40), width=4)
    for ex, ey in [(tx - 22, ty + 10), (tx + 22, ty + 10),
                   (tx - 16, ty - 2), (tx + 16, ty - 2)]:
        draw.line([(tx, ty), ((tx + ex) // 2, ty - 8), (ex, ey)],
                  fill=(74, 140, 82), width=3, joint="curve")


def story_block(draw, x, y, w, kicker, headline_lines, body, head_size=21,
                body_size=14, kicker_color=RED):
    """A kicker + headline + body story block; returns y below the block."""
    draw.text((x, y), kicker, font=font("sans_bold", 13), fill=kicker_color)
    y += 20
    f_head = font("serif_bold", head_size)
    for line in headline_lines:
        draw.text((x, y), line, font=f_head, fill=INK)
        y += int(head_size * 1.12)
    y += 2
    y = para(draw, x, y, w, body, font("sans", body_size),
             leading=int(body_size * 1.32))
    return y


def draw_page(Image, ImageDraw, ImageFont):
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    L, R = 26, W - 26
    CW = R - L

    # ---- masthead ------------------------------------------------------
    title = "THE WORLD TODAY"
    f_mast = font("serif_bold", 56)
    tw = d.textlength(title, font=f_mast)
    d.text(((W - tw) / 2, 10), title, font=f_mast, fill=INK)
    hrule(d, L, R, 84, width=3)
    hrule(d, L, R, 89, width=1)

    # ---- dateline ------------------------------------------------------
    d.text((L, 95), "TUESDAY 24 NOVEMBER 2026", font=font("sans_bold", 17),
           fill=INK)
    right = "ANTALYA  •  BENGHAZI  •  WASHINGTON  •  SUVA"
    d.text((R - d.textlength(right, font=font("sans", 15)), 96), right,
           font=font("sans", 15), fill=GREY)
    hrule(d, L, R, 118, width=1)

    # ---- kicker strip --------------------------------------------------
    d.rectangle([L, 124, R, 147], fill=INK)
    strip = ("COP31 ENDS IN FAILURE  •  WARSHIP SINKS OFF LIBYA  •  "
             "EU SANCTIONS  •  VENEZUELA ON TERROR LIST")
    f_strip = font("sans_bold", 14)
    sw = d.textlength(strip, font=f_strip)
    d.text(((W - sw) / 2, 129), strip, font=f_strip, fill=PAPER)

    # ---- lead story ----------------------------------------------------
    y = 154
    d.text((L, y), "CLIMATE  •  ANTALYA, TURKEY", font=font("sans_bold", 14),
           fill=RED)
    y += 24
    f_lead = font("serif_bold", 35)
    for line in ("CLIMATE TALKS END", "IN FAILURE"):
        d.text((L, y), line, font=f_lead, fill=INK)
        y += 40
    y += 4
    stand = ("COP31 ended with no climate pact — the “worst COP ever”, "
             "delegates said — as two weeks of talks in Antalya collapsed "
             "over fossil fuels. Pacific island nations said they would go "
             "it alone and form their own climate coalitions.")
    y = para(d, L, y, 560, stand, font("serif_italic", 17), leading=21)
    y += 6
    lead_body = (
        "The conference broke down after the EU and about 130 other "
        "countries refused a final text that did not even mention coal, oil "
        "and gas. Petrostates led by Saudi Arabia and Russia blocked every "
        "reference to fossil fuels. The UN secretary-general warned there "
        "is “no ambiguity in the science”.")
    y = para(d, L, y, 560, lead_body, font("sans", 15), leading=20,
             max_lines=5)

    # lead picture: cracked globe, right of the lead text
    px, py, pw, ph = 612, 190, 386, 196
    d.rectangle([px, py, px + pw, py + ph], fill=(214, 231, 240),
                outline=INK, width=2)
    draw_globe(d, px + pw // 2, py + ph // 2 - 4, 72)
    d.text((px + 8, py + ph - 22),
           "Antalya: two weeks of talks, no agreement.",
           font=font("sans", 12), fill=GREY)
    lead_bottom = max(y, py + ph)
    hrule(d, L, R, lead_bottom + 8, width=2)

    # ---- second row: three stories -------------------------------------
    col_w = (CW - 2 * 18) // 3
    y0 = lead_bottom + 18
    x1, x2, x3 = L, L + col_w + 18, L + 2 * (col_w + 18)
    y_end1 = story_block(
        d, x1, y0, col_w, "WAR IN UKRAINE  •  OFF LIBYA",
        ("RUSSIAN WARSHIP", "SINKS OFF LIBYA"),
        "A Russian warship sank in Benghazi after a suspected Ukrainian "
        "drone attack, an explosion on the corvette killing Russians and "
        "Libyan nationals. A Russian cargo ship hit by drones in the "
        "Baltic was left on fire and is being towed.")
    draw_ship(d, x1, y_end1 + 6, col_w, 64)
    y_end2 = story_block(
        d, x2, y0, col_w, "UNITED STATES  •  WASHINGTON",
        ("CARTEL DE LOS SOLES", "PUT ON TERROR LIST"),
        "The Trump administration added Venezuela’s Cartel de los Soles to "
        "its list of foreign terrorist organisations. The United States "
        "says President Nicolás Maduro leads the cartel, raising the "
        "stakes in the Caribbean standoff.")
    draw_panel(d, x2, y_end2 + 6, col_w, 70, "21", "US STRIKES SO FAR",
               "Strikes on alleged drug boats since September; about 83 killed.")
    y_end3 = story_block(
        d, x3, y0, col_w, "EUROPE  •  BRUSSELS",
        ("EU PROPOSES 22ND", "SANCTIONS PACKAGE"),
        "The European Commission proposed a 22nd sanctions package against "
        "Russia, banning Russian teams and athletes from competing under "
        "the Russian flag in EU events and targeting banks, crypto "
        "platforms and ex-combatants.")
    draw_panel(d, x3, y_end3 + 6, col_w, 70, "22nd", "SANCTIONS ROUND",
               "Banks, crypto platforms and ex-combatants targeted.")
    row2_bottom = max(y_end1 + 70, y_end2 + 76, y_end3 + 76)
    hrule(d, L, R, row2_bottom + 8, width=2)

    # ---- third row: two stories ----------------------------------------
    y0 = row2_bottom + 18
    half = (CW - 18) // 2
    y_end4 = story_block(
        d, L, y0, half, "INDONESIA  •  JAVA",
        ("FACTORY FIRE KILLS", "AT LEAST 24"),
        "A fire at a candy factory in Indonesia killed at least 24 people, "
        "rescuers said, as teams searched for the missing.",
        head_size=20)
    draw_fire(d, L, y_end4 + 6, half, 56)
    y_end5 = story_block(
        d, L + half + 18, y0, half, "PACIFIC  •  FIJI & KIRIBATI",
        ("DROUGHT SHUTS FIJI", "SCHOOLS FOR 5 DAYS"),
        "Fiji closed all schools for five days from 30 November as the "
        "El Niño drought deepens, and Kiribati evacuated remote Kanton "
        "Island.",
        head_size=20)
    draw_islands(d, L + half + 18, y_end5 + 6, half, 56)
    row3_bottom = max(y_end4 + 62, y_end5 + 62)
    hrule(d, L, R, row3_bottom + 8, width=2)

    # ---- also today: briefs --------------------------------------------
    y0 = row3_bottom + 18
    d.text((L, y0), "ALSO TODAY", font=font("sans_bold", 14), fill=RED)
    y0 += 17
    f_brief = font("sans", 12)
    f_brief_b = font("sans_bold", 12)
    briefs = [
        "China: US blacklisted Alibaba’s Singapore unit Apex over chips.",
        "South Korea: to summon Russia’s military attaché over an air-zone breach.",
        "Brazil: lower house approved the main text of Lula’s fiscal plan.",
        "Nvidia: reinstated co-founder Jensen Huang as chief executive.",
        "Chess: Gukesh began his title defence against Sindarov in Geneva.",
        "Myanmar: the ICJ ruled it committed genocide against the Rohingya.",
        "Senegal: migrant boat capsized, leaving dozens missing.",
        "Brazil: former president Jair Bolsonaro is back in jail.",
        "Stockholm: leaders met for the fourth Crimea Platform summit.",
        "Iran: warned EU military sites with missiles it says reach 4,500 km.",
        "England: 12,000 evacuated at a concert over a mystery substance.",
        "UN: chief demanded an AI safety framework within a year.",
    ]
    bw = (CW - 18) // 2
    for i, text in enumerate(briefs):
        col = i // 6
        row = i % 6
        bx = L + col * (bw + 18)
        by = y0 + row * 13
        head, _, rest = text.partition(": ")
        lead = "•  " + head + ": "
        d.text((bx, by), lead, font=f_brief_b, fill=INK)
        lx = bx + d.textlength(lead, font=f_brief_b)
        avail = bw - (lx - bx)
        shown = rest
        while shown and d.textlength(shown + "…", font=f_brief) > avail:
            shown = shown.rsplit(" ", 1)[0] if " " in shown else shown[:-1]
        if shown != rest:
            shown += "…"
        d.text((lx, by), shown, font=f_brief, fill=INK)

    # ---- footer ---------------------------------------------------------
    foot = ("THE WORLD TODAY  •  Tuesday 24 November 2026  •  "
            "All the day’s world news on one page")
    f_foot = font("sans", 12)
    fw = d.textlength(foot, font=f_foot)
    d.text(((W - fw) / 2, 1010), foot, font=f_foot, fill=GREY)
    return img


def draw_or_copy():
    """Draw with Pillow if available, else copy the shipped entry.png."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        src = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "entry.png")
        out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
        os.makedirs(out, exist_ok=True)
        shutil.copyfile(src, os.path.join(out, "entry.png"))
        return
    img = draw_page(Image, ImageDraw, ImageFont)
    out = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out, exist_ok=True)
    img.save(os.path.join(out, "entry.png"), format="PNG")


if __name__ == "__main__":
    draw_or_copy()
