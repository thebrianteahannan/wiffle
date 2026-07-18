#!/usr/bin/env python3
"""Draw beginner-friendly Wiffle ball physics / grip illustrations."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).resolve().parents[1] / "docs" / "physics_assets"

BALL = (245, 214, 58)
BALL_EDGE = (180, 140, 20)
HOLE = (55, 70, 85)
SMOOTH = (255, 235, 120)
INK = (25, 35, 45)
TEAL = (31, 122, 140)
NAVY = (11, 61, 92)
ACCENT = (196, 92, 38)
AIR = (120, 175, 205)
BG = (248, 250, 252)
WHITE = (255, 255, 255)
HAND = (240, 205, 175)
HAND_EDGE = (190, 145, 110)


def font(size: int, bold: bool = False):
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in candidates:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def new_img(w=900, h=560, color=BG):
    img = Image.new("RGB", (w, h), color)
    return img, ImageDraw.Draw(img)


def label(draw, xy, text, size=22, fill=INK, bold=False, anchor="lt"):
    draw.text(xy, text, fill=fill, font=font(size, bold=bold), anchor=anchor)


def draw_ball(draw, cx, cy, r, holes_angle_deg=0, show_seam=True, hole_alpha=True):
    """Draw a Wiffle ball. holes_angle_deg rotates hole half: 0=holes right, 90=up, 180=left, 270=down."""
    import math

    # Ball body
    draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=BALL, outline=BALL_EDGE, width=3)

    # Smooth vs hole halves via chord shading
    rad = math.radians(holes_angle_deg)
    # Seam line perpendicular to hole direction
    seam_ang = rad + math.pi / 2
    x1 = cx + r * math.cos(seam_ang)
    y1 = cy + r * math.sin(seam_ang)
    x2 = cx - r * math.cos(seam_ang)
    y2 = cy - r * math.sin(seam_ang)
    if show_seam:
        draw.line((x1, y1, x2, y2), fill=BALL_EDGE, width=2)

    # 8 oblong holes arranged on hole hemisphere
    # Center of hole hemisphere
    hx = math.cos(rad)
    hy = math.sin(rad)
    positions = [
        (-0.35, -0.55),
        (0.05, -0.55),
        (-0.55, -0.18),
        (-0.15, -0.18),
        (0.25, -0.18),
        (-0.55, 0.22),
        (-0.15, 0.22),
        (0.25, 0.22),
        (-0.35, 0.55),
        (0.05, 0.55),
    ]
    # Use 8 classic positions in two columns of 4
    classic = [
        (-0.28, -0.55),
        (0.12, -0.55),
        (-0.45, -0.18),
        (-0.05, -0.18),
        (-0.45, 0.18),
        (-0.05, 0.18),
        (-0.28, 0.55),
        (0.12, 0.55),
    ]
    # Rotate local coords so +x points toward hole direction
    for lx, ly in classic:
        # local: x toward holes, y up on page before rotation
        # map local (toward holes, lateral) into screen
        # First treat local x as along hole direction, local y perpendicular
        sx = lx * r
        sy = ly * r * 0.95
        # Rotate so local +x aligns with holes_angle
        rx = sx * math.cos(rad) - sy * math.sin(rad)
        ry = sx * math.sin(rad) + sy * math.cos(rad)
        px, py = cx + rx, cy + ry
        # Only draw if roughly on ball
        if (px - cx) ** 2 + (py - cy) ** 2 < (r * 0.92) ** 2:
            w, h = r * 0.16, r * 0.28
            # Orient hole oblong roughly radial
            box = [px - w, py - h, px + w, py + h]
            draw.ellipse(box, fill=HOLE)


def arrow(draw, start, end, color=TEAL, width=4, head=14):
    import math

    draw.line([start, end], fill=color, width=width)
    ang = math.atan2(end[1] - start[1], end[0] - start[0])
    p1 = (end[0] - head * math.cos(ang - 0.4), end[1] - head * math.sin(ang - 0.4))
    p2 = (end[0] - head * math.cos(ang + 0.4), end[1] - head * math.sin(ang + 0.4))
    draw.polygon([end, p1, p2], fill=color)


def draw_hand_grip(draw, cx, cy, scale=1.0, holes_angle=0, style="two_finger"):
    """Simplified hand holding ball. Fingers stay on the seam and off the holes."""
    import math

    r = int(78 * scale)
    # Palm under ball
    draw.ellipse((cx - 55 * scale, cy + 10 * scale, cx + 70 * scale, cy + 95 * scale), fill=HAND, outline=HAND_EDGE, width=2)
    # Thumb on smooth side (opposite hole direction when possible)
    thumb_side = -1 if math.cos(math.radians(holes_angle)) >= 0 else 1
    tx = cx + thumb_side * 70 * scale
    draw.ellipse((tx - 28 * scale, cy + 5 * scale, tx + 28 * scale, cy + 55 * scale), fill=HAND, outline=HAND_EDGE, width=2)
    draw_ball(draw, cx, cy, r, holes_angle_deg=holes_angle)

    if style == "two_finger":
        # Place fingertips on the seam (equator), slightly toward the top of the ball.
        # Seam is perpendicular to hole direction; keep pads off the holed half.
        seam = math.radians(holes_angle) + math.pi / 2
        # Two points along seam near top of ball
        for idx, along in enumerate((-0.22, 0.22)):
            # Start from top-ish, project onto seam line near surface
            px = cx + along * r * math.cos(seam) * 0.85
            py = cy - r * 0.72 + abs(along) * 8 * scale
            # Nudge fingers slightly toward smooth half so holes stay clear
            smooth = holes_angle + 180
            px += 0.12 * r * math.cos(math.radians(smooth))
            py += 0.12 * r * math.sin(math.radians(smooth))
            draw.ellipse(
                (px - 13 * scale, py - 20 * scale, px + 13 * scale, py + 28 * scale),
                fill=HAND,
                outline=HAND_EDGE,
                width=2,
            )
            label(draw, (px, py), "1" if idx == 0 else "2", size=16, fill=NAVY, bold=True, anchor="mm")
        label(draw, (tx, cy + 30 * scale), "thumb", size=15, fill=NAVY, bold=True, anchor="mm")
    elif style == "knuckle":
        for dx in (-22, 0, 22):
            tip_y = cy - r + 10 * scale
            draw.ellipse(
                (cx + dx * scale - 10 * scale, tip_y, cx + dx * scale + 10 * scale, tip_y + 22 * scale),
                fill=HAND,
                outline=HAND_EDGE,
                width=2,
            )
        label(draw, (cx, cy - r - 18 * scale), "fingernails dig in", size=16, fill=ACCENT, bold=True, anchor="mm")


def make_ball_anatomy():
    img, draw = new_img(900, 520)
    label(draw, (450, 28), "Official Wiffle Ball Anatomy", size=28, fill=NAVY, bold=True, anchor="mm")
    label(draw, (450, 58), "Eight oblong holes on ONE half • Smooth plastic on the other", size=18, fill=TEAL, anchor="mm")

    # Holes facing viewer-ish (right)
    draw_ball(draw, 230, 280, 140, holes_angle_deg=0)
    label(draw, (230, 450), "HOLED HALF", size=20, fill=NAVY, bold=True, anchor="mm")
    label(draw, (230, 478), "Air can enter here", size=16, fill=INK, anchor="mm")
    arrow(draw, (360, 220), (300, 240), TEAL)

    # Smooth side
    draw_ball(draw, 670, 280, 140, holes_angle_deg=180)
    # Cover holes visually by redrawing smooth emphasis - angle 180 puts holes left, show right as smooth
    label(draw, (670, 450), "SMOOTH HALF", size=20, fill=NAVY, bold=True, anchor="mm")
    label(draw, (670, 478), "No holes — air flows over", size=16, fill=INK, anchor="mm")

    # Seam callout
    label(draw, (450, 150), "Seam / equator", size=16, fill=ACCENT, bold=True, anchor="mm")
    label(draw, (450, 175), "(hold fingers here)", size=15, fill=ACCENT, anchor="mm")
    return img


def make_physics_forces():
    img, draw = new_img(900, 560)
    label(draw, (450, 28), "Why the Ball Curves (Beginner Physics)", size=28, fill=NAVY, bold=True, anchor="mm")

    cx, cy, r = 320, 300, 120
    draw_ball(draw, cx, cy, r, holes_angle_deg=90)  # holes up for diagram clarity - actually show holes on left
    draw_ball(draw, cx, cy, r, holes_angle_deg=180)  # holes on left

    # Airflow lines from left (pitch direction to the right - wait, air relative comes from front)
    # Show ball moving right, oncoming air from right... better: ball thrown to right, air relative from ahead
    for y in range(180, 430, 28):
        arrow(draw, (40, y), (160, y), AIR, width=3, head=10)
    label(draw, (100, 155), "Oncoming air", size=16, fill=TEAL, bold=True, anchor="mm")

    # Labels
    label(draw, (cx - 150, cy - 20), "Holes", size=18, fill=NAVY, bold=True, anchor="mm")
    arrow(draw, (cx - 120, cy), (cx - 70, cy), ACCENT, width=3)

    label(draw, (cx + 170, cy - 80), "1) Outside: holes create", size=16, fill=INK, anchor="lm")
    label(draw, (cx + 170, cy - 55), "turbulence / uneven drag", size=16, fill=INK, anchor="lm")
    label(draw, (cx + 170, cy), "2) Inside: air forms", size=16, fill=INK, anchor="lm")
    label(draw, (cx + 170, cy + 25), "trapped vortices", size=16, fill=INK, anchor="lm")
    label(draw, (cx + 170, cy + 75), "3) Net force pushes", size=16, fill=INK, anchor="lm")
    label(draw, (cx + 170, cy + 100), "the ball off a straight line", size=16, fill=INK, anchor="lm")

    arrow(draw, (cx, cy + r + 10), (cx, cy + r + 70), ACCENT, width=5)
    label(draw, (cx, cy + r + 95), "Example break direction", size=16, fill=ACCENT, bold=True, anchor="mm")
    label(draw, (450, 530), "Hole angle + arm slot + release decide WHICH way it breaks.", size=17, fill=NAVY, bold=True, anchor="mm")
    return img


def make_hole_orientations():
    img, draw = new_img(900, 620)
    label(draw, (450, 26), "Hole Orientation Map (Right-Handed Pitcher View)", size=26, fill=NAVY, bold=True, anchor="mm")
    label(draw, (450, 54), "You are looking at the ball in your hand before the throw", size=16, fill=TEAL, anchor="mm")

    configs = [
        (160, 200, 90, "HOLES UP", "Straighter / \"get me over\"\n(classic package tip)"),
        (450, 200, 0, "HOLES RIGHT", "Often away break\n(slider family)"),
        (740, 200, 180, "HOLES LEFT", "Often in / rise family\n(screw / riser)"),
        (300, 470, 270, "HOLES DOWN", "Helps riser look\nwith sidearm slot"),
        (600, 470, 45, "HOLES DIAGONAL", "Mixed break\n(up+away, etc.)"),
    ]
    for x, y, ang, title, desc in configs:
        draw_ball(draw, x, y, 78, holes_angle_deg=ang)
        label(draw, (x, y + 105), title, size=16, fill=NAVY, bold=True, anchor="mm")
        for i, line in enumerate(desc.split("\n")):
            label(draw, (x, y + 128 + i * 18), line, size=14, fill=INK, anchor="mm")
    return img


def make_basic_grip():
    img, draw = new_img(900, 560)
    label(draw, (450, 28), "Basic Grip: Fingers on the Seam", size=28, fill=NAVY, bold=True, anchor="mm")
    label(draw, (450, 58), "Do NOT cover the holes — blocked holes kill movement", size=17, fill=ACCENT, bold=True, anchor="mm")

    draw_hand_grip(draw, 280, 260, scale=1.35, holes_angle=0, style="two_finger")
    label(draw, (280, 430), "GOOD GRIP", size=20, fill=TEAL, bold=True, anchor="mm")
    label(draw, (280, 458), "Index + middle on seam", size=16, fill=INK, anchor="mm")
    label(draw, (280, 482), "Thumb under smooth half", size=16, fill=INK, anchor="mm")
    label(draw, (280, 506), "Holes stay open", size=16, fill=INK, anchor="mm")

    # Bad grip
    draw_hand_grip(draw, 680, 260, scale=1.35, holes_angle=0, style="two_finger")
    # Cover holes with fingers to show bad
    draw.ellipse((620, 200, 740, 320), fill=HAND, outline=HAND_EDGE, width=2)
    label(draw, (680, 250), "covering\nholes", size=16, fill=ACCENT, bold=True, anchor="mm")
    label(draw, (680, 430), "BAD GRIP", size=20, fill=ACCENT, bold=True, anchor="mm")
    label(draw, (680, 458), "Fingers smother holes", size=16, fill=INK, anchor="mm")
    label(draw, (680, 482), "Less air in → less break", size=16, fill=INK, anchor="mm")
    return img


def make_pitch_grips():
    img, draw = new_img(1000, 720)
    label(draw, (500, 24), "Starter Pitch Book (≤ 55 mph, New Ball)", size=28, fill=NAVY, bold=True, anchor="mm")

    pitches = [
        (180, 170, 0, "two_finger", "SLIDER / AWAY", "Holes toward outer fingers\n(right for RHP)\nSidearm / ¾ arm slot\nBreaks away from RHH"),
        (500, 170, 180, "two_finger", "SCREW / IN", "Holes toward thumb\n(left for RHP)\nOverhand to ¾\nRuns in on RHH"),
        (820, 170, 270, "two_finger", "RISER", "Holes down / down-left\nSidearm release\nKeep wrist firm\nBall stays up / climbs"),
        (180, 480, 90, "two_finger", "DROP / SINK", "Holes up or up-right\nOverhand slot\nLoose wrist, pull down\nBall falls late"),
        (500, 480, 90, "two_finger", "STRAIGHT", "Holes mostly up\nOverhand, clean spin\nAim the seam release\nUse when you need a strike"),
        (820, 480, 0, "knuckle", "KNUCKLE", "Holes toward batter\nFingernails dig in\nPush — almost no spin\nDances / flutters"),
    ]
    for x, y, ang, style, title, desc in pitches:
        draw.rounded_rectangle((x - 150, y - 130, x + 150, y + 200), radius=16, outline=TEAL, width=2, fill=WHITE)
        draw_hand_grip(draw, x, y - 10, scale=0.85, holes_angle=ang, style=style)
        label(draw, (x, y + 95), title, size=16, fill=NAVY, bold=True, anchor="mm")
        for i, line in enumerate(desc.split("\n")):
            label(draw, (x, y + 118 + i * 17), line, size=13, fill=INK, anchor="mm")
    return img


def make_throw_path():
    img, draw = new_img(900, 560)
    label(draw, (450, 28), "How to Throw It: Clean Release Beats Muscle", size=26, fill=NAVY, bold=True, anchor="mm")
    label(draw, (450, 58), "League limit: 55 mph  •  Brand-new unscuffed balls only", size=17, fill=ACCENT, bold=True, anchor="mm")

    # Arm slots
    slots = [
        (160, "OVERHAND", "Drop / straight / screw"),
        (450, "THREE-QUARTER", "Most versatile slot"),
        (740, "SIDEARM", "Slider / riser look"),
    ]
    for x, name, tip in slots:
        # pitcher stick figure shoulder
        sx, sy = x, 320
        draw.ellipse((sx - 18, sy - 70, sx + 18, sy - 34), fill=HAND, outline=HAND_EDGE, width=2)  # head
        draw.line((sx, sy - 34, sx, sy + 40), fill=NAVY, width=5)  # torso
        # arm angle
        if name == "OVERHAND":
            arm_end = (sx + 70, sy - 50)
        elif name == "THREE-QUARTER":
            arm_end = (sx + 80, sy - 10)
        else:
            arm_end = (sx + 85, sy + 25)
        draw.line((sx, sy - 10, arm_end), fill=TEAL, width=6)
        draw_ball(draw, arm_end[0] + 35, arm_end[1], 28, holes_angle_deg=0 if "SIDE" in name else 90)
        label(draw, (x, 420), name, size=18, fill=NAVY, bold=True, anchor="mm")
        label(draw, (x, 448), tip, size=14, fill=INK, anchor="mm")

    label(draw, (450, 500), "Cue: pick hole direction → pick arm slot → throw THROUGH the target (don't aim the break).", size=15, fill=NAVY, bold=True, anchor="mm")
    label(draw, (450, 528), "At ≤55 mph, orientation accuracy matters more than velocity.", size=15, fill=TEAL, bold=True, anchor="mm")
    return img


def make_new_ball_rules():
    img, draw = new_img(900, 520)
    label(draw, (450, 30), "Your Rules Change the Physics", size=28, fill=NAVY, bold=True, anchor="mm")

    # Left card - new ball
    draw.rounded_rectangle((40, 80, 430, 470), radius=18, fill=WHITE, outline=TEAL, width=3)
    label(draw, (235, 110), "NEW BALL (Required)", size=20, fill=TEAL, bold=True, anchor="mm")
    draw_ball(draw, 235, 230, 70, holes_angle_deg=20)
    tips = [
        "• Shiny, no scuffs / scratches",
        "• Holes sharp and uniform",
        "• Movement is cleaner but subtler",
        "• You must aim holes carefully",
        "• Same ball every batter = fair",
    ]
    for i, t in enumerate(tips):
        label(draw, (60, 330 + i * 24), t, size=15, fill=INK, anchor="lm")

    # Right card - 55 mph
    draw.rounded_rectangle((470, 80, 860, 470), radius=18, fill=WHITE, outline=ACCENT, width=3)
    label(draw, (665, 110), "55 MPH CAP", size=20, fill=ACCENT, bold=True, anchor="mm")
    label(draw, (665, 175), "55", size=72, fill=NAVY, bold=True, anchor="mm")
    label(draw, (665, 230), "mph max", size=18, fill=NAVY, bold=True, anchor="mm")
    tips2 = [
        "• No need to overthrow",
        "• Interior vortices still work",
        "• Focus on repeatable release",
        "• Change holes, not just speed",
        "• Soft changeups still disrupt timing",
    ]
    for i, t in enumerate(tips2):
        label(draw, (490, 290 + i * 24), t, size=15, fill=INK, anchor="lm")
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
