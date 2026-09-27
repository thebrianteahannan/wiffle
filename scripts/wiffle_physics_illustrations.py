#!/usr/bin/env python3
"""Draw beginner-friendly Wiffle ball physics / grip illustrations."""

from __future__ import annotations

import math
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from wiffle_ball_render import render_wiffle_ball

OUT = Path(__file__).resolve().parents[1] / "docs" / "physics_assets"

INK = (25, 35, 45)
TEAL = (31, 122, 140)
NAVY = (11, 61, 92)
ACCENT = (196, 92, 38)
AIR = (120, 175, 205)
BG = (248, 250, 252)
WHITE = (255, 255, 255)
HAND = (235, 198, 168)
HAND_EDGE = (175, 130, 100)
NAIL = (245, 230, 220)
FORCE = (220, 60, 50)


def font(size: int, bold: bool = False):
    for path in (
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ):
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def new_img(w=960, h=560, color=BG):
    img = Image.new("RGB", (w, h), color)
    return img, ImageDraw.Draw(img)


def label(draw, xy, text, size=22, fill=INK, bold=False, anchor="lt"):
    draw.text(xy, text, fill=fill, font=font(size, bold=bold), anchor=anchor)


def arrow(draw, start, end, color=TEAL, width=4, head=14):
    draw.line([start, end], fill=color, width=width)
    ang = math.atan2(end[1] - start[1], end[0] - start[0])
    p1 = (end[0] - head * math.cos(ang - 0.4), end[1] - head * math.sin(ang - 0.4))
    p2 = (end[0] - head * math.cos(ang + 0.4), end[1] - head * math.sin(ang + 0.4))
    draw.polygon([end, p1, p2], fill=color)


def ball(img, cx, cy, r, ang=0, face=0.0, away=False):
    render_wiffle_ball(
        img, cx, cy, r, ang, face_camera=face, holes_away=away, show_seam=True, color="white"
    )


def draw_hand_grip(img, cx, cy, scale=1.0, holes_angle=0, style="two_finger"):
    draw = ImageDraw.Draw(img)
    r = int(84 * scale)
    draw.ellipse(
        (cx - 60 * scale, cy + 28 * scale, cx + 78 * scale, cy + 108 * scale),
        fill=HAND, outline=HAND_EDGE, width=2,
    )
    thumb_left = math.cos(math.radians(holes_angle)) >= -0.1
    if thumb_left:
        tbox = (cx - 108 * scale, cy + 8 * scale, cx - 42 * scale, cy + 62 * scale)
        tx = cx - 75 * scale
    else:
        tbox = (cx + 42 * scale, cy + 8 * scale, cx + 108 * scale, cy + 62 * scale)
        tx = cx + 75 * scale
    draw.ellipse(tbox, fill=HAND, outline=HAND_EDGE, width=2)
    label(draw, (tx, cy + 34 * scale), "thumb", size=14, fill=NAVY, bold=True, anchor="mm")

    face = 0.85 if style == "knuckle" else 0.2
    ball(img, cx, cy, r, ang=holes_angle, face=face)

    if style == "two_finger":
        smooth = holes_angle + 180
        sx = math.cos(math.radians(smooth))
        sy = -math.sin(math.radians(smooth))
        bx = cx + 0.18 * r * sx
        by = cy - 0.80 * r + 0.10 * r * sy
        for i, dx in enumerate((-22 * scale, 22 * scale)):
            box = (bx + dx - 14 * scale, by - 6 * scale, bx + dx + 14 * scale, by + 50 * scale)
            draw.rounded_rectangle(box, radius=9, fill=HAND, outline=HAND_EDGE, width=2)
            label(draw, ((box[0] + box[2]) / 2, (box[1] + box[3]) / 2), "1" if i == 0 else "2",
                  size=15, fill=NAVY, bold=True, anchor="mm")
    else:
        for dx in (-24, 0, 24):
            x0 = cx + dx * scale - 9 * scale
            y0 = cy - r + 2 * scale
            draw.ellipse((x0, y0, x0 + 18 * scale, y0 + 20 * scale), fill=NAIL, outline=HAND_EDGE, width=2)
        label(draw, (cx, cy - r - 16 * scale), "fingernails dig in", size=15, fill=ACCENT, bold=True, anchor="mm")


def make_ball_anatomy():
    img, draw = new_img(960, 580)
    label(draw, (480, 28), "Official Wiffle Ball Anatomy", size=28, fill=NAVY, bold=True, anchor="mm")
    label(draw, (480, 58), "Eight oblong slots on ONE half — arranged like spokes around the face center",
          size=16, fill=TEAL, anchor="mm")

    # Face-on hole pole: radial spoke pattern (matches real photos)
    ball(img, 250, 300, 155, ang=0, face=1.0)
    label(draw, (250, 480), "HOLED HALF (face-on)", size=18, fill=NAVY, bold=True, anchor="mm")
    label(draw, (250, 508), "Slots point toward the center", size=15, fill=INK, anchor="mm")

    # Classic 3/4 side view like product photos / PopSci
    ball(img, 710, 300, 155, ang=200, face=0.12)
    label(draw, (710, 480), "SIDE VIEW (holes on left)", size=18, fill=NAVY, bold=True, anchor="mm")
    label(draw, (710, 508), "Smooth half on the right", size=15, fill=INK, anchor="mm")

    label(draw, (480, 120), "Seam / equator", size=16, fill=ACCENT, bold=True, anchor="mm")
    label(draw, (480, 145), "(hold fingers here)", size=14, fill=ACCENT, anchor="mm")
    arrow(draw, (480, 165), (400, 250), ACCENT, width=3, head=12)
    arrow(draw, (480, 165), (620, 250), ACCENT, width=3, head=12)
    return img


def _soft_ellipse(draw, box, fill, outline=None, width=1):
    draw.ellipse(box, fill=fill, outline=outline, width=width)


def make_physics_forces():
    """PopSci-style flight diagram: airflow, vortices, forces."""
    img, draw = new_img(960, 620, color=(45, 48, 52))
    label(draw, (480, 30), "Flight of the Wiffle Ball", size=28, fill=(255, 255, 255), bold=True, anchor="mm")
    label(draw, (480, 58), "How holes create curve — air outside + vortices inside", size=15, fill=(180, 190, 200), anchor="mm")

    cx, cy, r = 420, 300, 135
    # Airflow lines from left
    for i, y in enumerate(range(170, 450, 22)):
        # bend around ball
        if abs(y - cy) < r + 10:
            # skip through ball; draw approach only
            arrow(draw, (40, y), (cx - r - 18, y), (200, 210, 220), width=2, head=8)
        else:
            arrow(draw, (40, y), (cx + r + 80, y + int(0.08 * (y - cy))), (200, 210, 220), width=2, head=8)
    label(draw, (90, 150), "AIRFLOW", size=14, fill=(220, 230, 240), bold=True, anchor="mm")

    ball(img, cx, cy, r, ang=180, face=0.18)

    # Vortex wisps inside / near holes (left side)
    for i, (vx, vy, rw, rh) in enumerate([
        (cx - 40, cy - 30, 50, 28),
        (cx - 55, cy + 10, 45, 26),
        (cx - 35, cy + 45, 40, 22),
    ]):
        _soft_ellipse(draw, (vx - rw, vy - rh, vx + rw, vy + rh), fill=(255, 255, 255, ))
        # redraw as semi via light circles
        draw.arc((vx - rw, vy - rh, vx + rw, vy + rh), 0, 270, fill=(230, 235, 240), width=3)
        draw.arc((vx - rw // 2, vy - rh // 2, vx + rw // 2, vy + rh // 2), 40, 300, fill=(210, 220, 230), width=2)
    label(draw, (cx - 90, cy + 95), "VORTICES", size=13, fill=(255, 200, 120), bold=True, anchor="mm")

    # Wake turbulence on right
    for i in range(6):
        wx = cx + r + 20 + i * 18
        wy = cy - 40 + (i % 3) * 30
        draw.ellipse((wx, wy, wx + 35, wy + 28), outline=(190, 200, 210), width=2)

    # Force arrows (red) like the reference
    arrow(draw, (cx + 20, cy - r + 10), (cx + 90, cy - r - 40), FORCE, width=5, head=16)
    label(draw, (cx + 120, cy - r - 50), "EXTERNAL FORCE", size=13, fill=FORCE, bold=True, anchor="mm")

    arrow(draw, (cx - 20, cy + 10), (cx - 110, cy + 70), FORCE, width=5, head=16)
    label(draw, (cx - 150, cy + 95), "INTERIOR FORCE", size=13, fill=FORCE, bold=True, anchor="mm")

    arrow(draw, (cx - 10, cy - 10), (cx - 100, cy + 20), (255, 140, 60), width=5, head=16)
    label(draw, (cx - 160, cy + 5), "NET FORCE", size=13, fill=(255, 160, 80), bold=True, anchor="mm")

    arrow(draw, (cx + r + 10, cy - 20), (cx + r + 120, cy - 20), (255, 255, 255), width=5, head=16)
    label(draw, (cx + r + 70, cy - 45), "BALL'S DIRECTION", size=13, fill=(255, 255, 255), bold=True, anchor="mm")

    label(draw, (480, 580), "Hole orientation sets which way these forces push — you aim the holes, not just the throw.",
          size=14, fill=(200, 210, 220), bold=True, anchor="mm")
    return img


def make_hole_orientations():
    img, draw = new_img(960, 680)
    label(draw, (480, 26), "Hole Orientation Map (Right-Handed Pitcher View)", size=26, fill=NAVY, bold=True, anchor="mm")
    label(draw, (480, 54), "Point the hole face (the spoke pattern) in the direction shown", size=16, fill=TEAL, anchor="mm")

    configs = [
        (170, 210, 90, "HOLES UP", "Straighter / \"get me over\"\n(classic package tip)"),
        (480, 210, 0, "HOLES RIGHT", "Often away break\n(slider family)"),
        (790, 210, 180, "HOLES LEFT", "Often in / rise family\n(screw / riser)"),
        (320, 500, 270, "HOLES DOWN", "Helps riser look\nwith sidearm slot"),
        (640, 500, 45, "HOLES DIAGONAL", "Mixed break\n(up+away, etc.)"),
    ]
    for x, y, ang, title, desc in configs:
        # 3/4 view: classic product-photo look with slots readable on one side
        ball(img, x, y, 95, ang=ang, face=0.15)
        label(draw, (x, y + 120), title, size=16, fill=NAVY, bold=True, anchor="mm")
        for i, line in enumerate(desc.split("\n")):
            label(draw, (x, y + 145 + i * 18), line, size=14, fill=INK, anchor="mm")
    return img


def make_basic_grip():
    img, draw = new_img(960, 580)
    label(draw, (480, 28), "Basic Grip: Fingers on the Seam", size=28, fill=NAVY, bold=True, anchor="mm")
    label(draw, (480, 58), "Do NOT cover the holes — blocked holes kill movement",
          size=17, fill=ACCENT, bold=True, anchor="mm")
    draw_hand_grip(img, 280, 270, scale=1.4, holes_angle=0, style="two_finger")
    label(draw, (280, 455), "GOOD GRIP", size=20, fill=TEAL, bold=True, anchor="mm")
    for i, t in enumerate(["Index + middle on seam", "Thumb under smooth half", "All 8 holes stay open"]):
        label(draw, (280, 482 + i * 22), t, size=15, fill=INK, anchor="mm")
    draw_hand_grip(img, 700, 270, scale=1.4, holes_angle=0, style="two_finger")
    draw.ellipse((640, 210, 780, 340), fill=HAND, outline=HAND_EDGE, width=2)
    label(draw, (710, 270), "covering\nholes", size=16, fill=ACCENT, bold=True, anchor="mm")
    label(draw, (700, 455), "BAD GRIP", size=20, fill=ACCENT, bold=True, anchor="mm")
    label(draw, (700, 482), "Fingers smother holes", size=15, fill=INK, anchor="mm")
    label(draw, (700, 504), "Less air in → less break", size=15, fill=INK, anchor="mm")
    return img


def make_pitch_grips():
    img, draw = new_img(1040, 760)
    label(draw, (520, 24), "Starter Pitch Book (≤ 55 mph, New Ball)", size=28, fill=NAVY, bold=True, anchor="mm")
    pitches = [
        (185, 185, 0, "two_finger", "SLIDER / AWAY",
         "Holes toward outer fingers\n(right for RHP)\nSidearm / ¾ arm slot\nBreaks away from RHH"),
        (520, 185, 180, "two_finger", "SCREW / IN",
         "Holes toward thumb\n(left for RHP)\nOverhand to ¾\nRuns in on RHH"),
        (855, 185, 270, "two_finger", "RISER",
         "Holes down / down-left\nSidearm release\nKeep wrist firm\nBall stays up / climbs"),
        (185, 510, 90, "two_finger", "DROP / SINK",
         "Holes up or up-right\nOverhand slot\nLoose wrist, pull down\nBall falls late"),
        (520, 510, 90, "two_finger", "STRAIGHT",
         "Holes mostly up\nOverhand, clean spin\nAim the seam release\nUse when you need a strike"),
        (855, 510, 0, "knuckle", "KNUCKLE",
         "Holes toward batter\nFingernails dig in\nPush — almost no spin\nDances / flutters"),
    ]
    for x, y, ang, style, title, desc in pitches:
        draw.rounded_rectangle((x - 155, y - 140, x + 155, y + 210), radius=16, outline=TEAL, width=2, fill=WHITE)
        draw_hand_grip(img, x, y - 5, scale=0.95, holes_angle=ang, style=style)
        label(draw, (x, y + 108), title, size=16, fill=NAVY, bold=True, anchor="mm")
        for i, line in enumerate(desc.split("\n")):
            label(draw, (x, y + 132 + i * 17), line, size=13, fill=INK, anchor="mm")
    return img


def make_throw_path():
    img, draw = new_img(960, 560)
    label(draw, (480, 28), "How to Throw It: Clean Release Beats Muscle", size=26, fill=NAVY, bold=True, anchor="mm")
    label(draw, (480, 58), "League limit: 55 mph  •  Brand-new unscuffed balls only",
          size=17, fill=ACCENT, bold=True, anchor="mm")
    slots = [
        (170, "OVERHAND", "Drop / straight / screw", 90),
        (480, "THREE-QUARTER", "Most versatile slot", 45),
        (790, "SIDEARM", "Slider / riser look", 0),
    ]
    for x, name, tip, ang in slots:
        sx, sy = x, 320
        draw.ellipse((sx - 18, sy - 70, sx + 18, sy - 34), fill=HAND, outline=HAND_EDGE, width=2)
        draw.line((sx, sy - 34, sx, sy + 40), fill=NAVY, width=5)
        arm_end = {
            "OVERHAND": (sx + 70, sy - 50),
            "THREE-QUARTER": (sx + 80, sy - 10),
            "SIDEARM": (sx + 85, sy + 25),
        }[name]
        draw.line((sx, sy - 10, arm_end), fill=TEAL, width=6)
        ball(img, arm_end[0] + 40, arm_end[1], 34, ang=ang, face=0.2)
        label(draw, (x, 420), name, size=18, fill=NAVY, bold=True, anchor="mm")
        label(draw, (x, 448), tip, size=14, fill=INK, anchor="mm")
    label(draw, (480, 500), "Cue: pick hole direction → pick arm slot → throw THROUGH the target.",
          size=15, fill=NAVY, bold=True, anchor="mm")
    label(draw, (480, 528), "At ≤55 mph, orientation accuracy matters more than velocity.",
          size=15, fill=TEAL, bold=True, anchor="mm")
    return img


def make_new_ball_rules():
    img, draw = new_img(960, 520)
    label(draw, (480, 30), "Your Rules Change the Physics", size=28, fill=NAVY, bold=True, anchor="mm")
    draw.rounded_rectangle((40, 80, 450, 470), radius=18, fill=WHITE, outline=TEAL, width=3)
    label(draw, (245, 110), "NEW BALL (Required)", size=20, fill=TEAL, bold=True, anchor="mm")
    ball(img, 245, 235, 82, ang=200, face=0.2)
    for i, t in enumerate([
        "• Shiny, no scuffs / scratches", "• Holes sharp and uniform",
        "• Movement cleaner but subtler", "• Aim holes carefully",
        "• Same ball every batter = fair",
    ]):
        label(draw, (65, 340 + i * 22), t, size=15, fill=INK, anchor="lm")
    draw.rounded_rectangle((510, 80, 920, 470), radius=18, fill=WHITE, outline=ACCENT, width=3)
    label(draw, (715, 110), "55 MPH CAP", size=20, fill=ACCENT, bold=True, anchor="mm")
    label(draw, (715, 175), "55", size=72, fill=NAVY, bold=True, anchor="mm")
    label(draw, (715, 230), "mph max", size=18, fill=NAVY, bold=True, anchor="mm")
    for i, t in enumerate([
        "• No need to overthrow", "• Interior vortices still work",
        "• Focus on repeatable release", "• Change holes, not just speed",
        "• Soft changeups still disrupt timing",
    ]):
        label(draw, (535, 290 + i * 24), t, size=15, fill=INK, anchor="lm")
    return img


def generate_all() -> list[Path]:
    OUT.mkdir(parents=True, exist_ok=True)
    specs = [
        ("01_ball_anatomy.png", make_ball_anatomy),
        ("02_physics_forces.png", make_physics_forces),
        ("03_hole_orientations.png", make_hole_orientations),
        ("04_basic_grip.png", make_basic_grip),
        ("05_pitch_grips.png", make_pitch_grips),
        ("06_throw_slots.png", make_throw_path),
        ("07_rules_physics.png", make_new_ball_rules),
    ]
    paths = []
    for name, fn in specs:
        path = OUT / name
        fn().save(path, "PNG", optimize=True)
        paths.append(path)
        print("wrote", path)
    return paths


if __name__ == "__main__":
    generate_all()
