#!/usr/bin/env python3
"""Generate a beginner Wiffle ball pitching physics PDF with illustrations."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from wiffle_physics_illustrations import generate_all

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "Wiffle_Ball_Pitching_Physics.pdf"
ASSETS = ROOT / "docs" / "physics_assets"

NAVY = colors.HexColor("#0B3D5C")
TEAL = colors.HexColor("#1F7A8C")
SAND = colors.HexColor("#F2F6F8")
INK = colors.HexColor("#1A2428")
MUTED = colors.HexColor("#4A5A63")
ACCENT = colors.HexColor("#C45C26")


def styles():
    base = getSampleStyleSheet()
    return {
        "cover": ParagraphStyle("cover", parent=base["Title"], fontName="Helvetica-Bold", fontSize=26, leading=32, textColor=NAVY, alignment=TA_CENTER, spaceAfter=8),
        "sub": ParagraphStyle("sub", parent=base["Normal"], fontName="Helvetica", fontSize=12.5, leading=17, textColor=TEAL, alignment=TA_CENTER, spaceAfter=8),
        "tag": ParagraphStyle("tag", parent=base["Normal"], fontName="Helvetica-Oblique", fontSize=10.5, leading=14, textColor=MUTED, alignment=TA_CENTER, spaceAfter=14),
        "h1": ParagraphStyle("h1", parent=base["Heading1"], fontName="Helvetica-Bold", fontSize=15, leading=19, textColor=NAVY, spaceBefore=2, spaceAfter=8),
        "h2": ParagraphStyle("h2", parent=base["Heading2"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=TEAL, spaceBefore=8, spaceAfter=5),
        "body": ParagraphStyle("body", parent=base["Normal"], fontName="Helvetica", fontSize=10.2, leading=14.5, textColor=INK, alignment=TA_JUSTIFY, spaceAfter=7),
        "bullet": ParagraphStyle("bullet", parent=base["Normal"], fontName="Helvetica", fontSize=10.2, leading=14, textColor=INK),
        "callout": ParagraphStyle("callout", parent=base["Normal"], fontName="Helvetica-Oblique", fontSize=10.2, leading=14, textColor=NAVY),
        "caption": ParagraphStyle("caption", parent=base["Normal"], fontName="Helvetica-Oblique", fontSize=9, leading=12, textColor=MUTED, alignment=TA_CENTER, spaceBefore=2, spaceAfter=10),
        "th": ParagraphStyle("th", parent=base["Normal"], fontName="Helvetica-Bold", fontSize=9, leading=11, textColor=colors.white, alignment=TA_CENTER),
        "td": ParagraphStyle("td", parent=base["Normal"], fontName="Helvetica", fontSize=8.5, leading=11, textColor=INK),
    }


def bullets(items, s):
    return ListFlowable(
        [ListItem(Paragraph(i, s["bullet"]), leftIndent=10, bulletColor=TEAL) for i in items],
        bulletType="bullet",
        start="•",
        leftIndent=16,
        spaceAfter=6,
    )


def callout(text, s):
    t = Table([[Paragraph(text, s["callout"])]], colWidths=[6.5 * inch])
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SAND),
                ("BOX", (0, 0), (-1, -1), 1, TEAL),
                ("LEFTPADDING", (0, 0), (-1, -1), 10),
                ("RIGHTPADDING", (0, 0), (-1, -1), 10),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    return t


def fig(name, s, width=6.5 * inch, caption=None):
    path = ASSETS / name
    # Keep aspect roughly; reportlab Image will scale height
    img = Image(str(path), width=width, height=width * 0.62)
    img.hAlign = "CENTER"
    flow = [img]
    if caption:
        flow.append(Paragraph(caption, s["caption"]))
    else:
        flow.append(Spacer(1, 8))
    return flow


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(TEAL)
    canvas.setLineWidth(0.7)
    canvas.line(0.7 * inch, 0.55 * inch, 7.8 * inch, 0.55 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(0.7 * inch, 0.35 * inch, "Wiffle Ball Pitching Physics • New balls • ≤55 mph")
    canvas.drawRightString(7.8 * inch, 0.35 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build():
    generate_all()
    s = styles()
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        leftMargin=0.7 * inch,
        rightMargin=0.7 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.8 * inch,
        title="Wiffle Ball Pitching Physics",
        author="Wiffle Physics Guide",
    )
    story = []

    story.append(Spacer(1, 0.7 * inch))
    story.append(Paragraph("WIFFLE BALL", s["cover"]))
    story.append(Paragraph("Pitching Physics for Newer Players", s["sub"]))
    story.append(
        Paragraph(
            "Illustrated guide to holes, finger placement, and throws — built for brand-new unscuffed balls and a 55 mph speed limit.",
            s["tag"],
        )
    )
    story.append(
        callout(
            "Big idea: You do not need to throw harder to make the ball move. "
            "With a new official Wiffle ball, movement comes from hole direction, a clean grip on the seam, and a repeatable arm slot.",
            s,
        )
    )
    story.append(Spacer(1, 8))
    story.append(Paragraph("What you will learn", s["h2"]))
    story.append(
        bullets(
            [
                "How the 8 holes create curve (outside turbulence + inside vortices)",
                "Where the holes should face for common pitches",
                "Where your fingers go (and what not to cover)",
                "How to throw each pitch at ≤ 55 mph",
                "Why “no scuff marks” means you must be sharper with orientation",
            ],
            s,
        )
    )
    story.append(PageBreak())

    # Anatomy
    story.append(Paragraph("1. Ball Anatomy: Where the Holes Go", s["h1"]))
    story.append(
        Paragraph(
            "An official Wiffle ball is not symmetric. One hemisphere has <b>eight oblong holes</b>. "
            "The other half is smooth plastic. That uneven shape is the whole pitching game. "
            "Air treats each half differently, so the ball refuses to fly straight unless you ask it to.",
            s["body"],
        )
    )
    story.extend(fig("01_ball_anatomy.png", s, caption="Figure 1. Holed half vs smooth half. Hold near the seam; keep holes open."))
    story.append(
        bullets(
            [
                "<b>Holed half:</b> air can rush inside and create swirling pockets (vortices).",
                "<b>Smooth half:</b> air flows over the plastic more cleanly.",
                "<b>Seam / equator:</b> the dividing line — this is your finger home base.",
            ],
            s,
        )
    )

    # Physics
    story.append(Paragraph("2. The Physics (Without the Heavy Math)", s["h1"]))
    story.append(
        Paragraph(
            "Researchers (including wind-tunnel work popularized from Lafayette College studies) describe two cooperating effects:",
            s["body"],
        )
    )
    story.append(
        bullets(
            [
                "<b>Outside the ball:</b> holes stir the air, creating extra turbulence and uneven drag/lift on one side.",
                "<b>Inside the ball:</b> air entering the holes can form <b>trapped vortices</b> that push from within.",
                "<b>Net force:</b> those inside and outside forces constantly shift. Their sum is the break you see.",
            ],
            s,
        )
    )
    story.extend(fig("02_physics_forces.png", s, caption="Figure 2. Asymmetric airflow is why orientation matters more than arm strength."))
    story.append(
        callout(
            "At 55 mph and under, you are in a sweet learning zone: hard enough for real movement, "
            "soft enough that overthrowing usually makes command worse, not break better.",
            s,
        )
    )
    story.append(PageBreak())

    # Orientations
    story.append(Paragraph("3. Hole Orientation Map", s["h1"]))
    story.append(
        Paragraph(
            "Before every pitch, ask: <b>Which way are the holes facing?</b> "
            "Classic package tips put holes up for straighter, toward the thumb for curve, and toward the outer fingers for slider. "
            "Modern backyard systems use the same idea with left/right + arm slot.",
            s["body"],
        )
    )
    story.extend(fig("03_hole_orientations.png", s, width=6.6 * inch, caption="Figure 3. Learn these five looks first. Same arm speed, different holes → different pitch."))

    # Grip
    story.append(Paragraph("4. Finger Placement: The Basic Grip", s["h1"]))
    story.append(
        Paragraph(
            "Most beginner pitches use the same hand shape. Change the <b>hole direction</b> and <b>arm slot</b>, not a brand-new claw every time.",
            s["body"],
        )
    )
    story.append(
        bullets(
            [
                "Index and middle fingers rest on the seam (the equator).",
                "Thumb supports underneath on the smooth half.",
                "Hold loosely — death grip adds bad spin and blocks feel.",
                "<b>Never smother the holes</b> with your fingers. Open holes = more air in = more movement.",
            ],
            s,
        )
    )
    story.extend(fig("04_basic_grip.png", s, caption="Figure 4. Good seam grip vs blocked-hole grip."))
    story.append(PageBreak())

    # Pitch book
    story.append(Paragraph("5. Starter Pitches: Holes + Fingers + Throw", s["h1"]))
    story.append(
        Paragraph(
            "All of these assume a <b>brand-new ball</b> (no scuffs) and staying at or under <b>55 mph</b>. "
            "Directions below are for a <b>right-handed pitcher</b>. Lefties mirror left/right.",
            s["body"],
        )
    )
    story.extend(fig("05_pitch_grips.png", s, width=6.7 * inch, caption="Figure 5. Six beginner pitches with hole direction and finger cues."))

    rows = [
        [Paragraph("Pitch", s["th"]), Paragraph("Holes", s["th"]), Paragraph("Fingers / throw", s["th"]), Paragraph("What to expect", s["th"])],
        [Paragraph("<b>Straight</b>", s["td"]), Paragraph("Mostly up", s["td"]), Paragraph("Seam grip, overhand, clean release", s["td"]), Paragraph("Strike-steal pitch", s["td"])],
        [Paragraph("<b>Slider / away</b>", s["td"]), Paragraph("Toward outer fingers (R)", s["td"]), Paragraph("¾ or sidearm; stay online", s["td"]), Paragraph("Breaks away from RHH", s["td"])],
        [Paragraph("<b>Screw / in</b>", s["td"]), Paragraph("Toward thumb (L)", s["td"]), Paragraph("Overhand/¾; firm wrist", s["td"]), Paragraph("Runs in on RHH", s["td"])],
        [Paragraph("<b>Riser</b>", s["td"]), Paragraph("Down or down-left", s["td"]), Paragraph("Sidearm; throw through high target", s["td"]), Paragraph("Stays up / late rise look", s["td"])],
        [Paragraph("<b>Drop</b>", s["td"]), Paragraph("Up or up-right", s["td"]), Paragraph("Overhand; soft pull-down finish", s["td"]), Paragraph("Late fall", s["td"])],
        [Paragraph("<b>Knuckle</b>", s["td"]), Paragraph("Toward batter", s["td"]), Paragraph("Nails dig; push with almost no spin", s["td"]), Paragraph("Flutter / dance", s["td"])],
    ]
    table = Table(rows, colWidths=[1.15 * inch, 1.55 * inch, 2.2 * inch, 1.6 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("BACKGROUND", (0, 1), (-1, 1), SAND),
                ("BACKGROUND", (0, 3), (-1, 3), SAND),
                ("BACKGROUND", (0, 5), (-1, 5), SAND),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C9D5DC")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]
        )
    )
    story.append(Spacer(1, 4))
    story.append(table)
    story.append(PageBreak())

    # Throw
    story.append(Paragraph("6. How to Throw It (Arm Slot Pictures)", s["h1"]))
    story.append(
        Paragraph(
            "Think of a tiny checklist on the mound: <b>holes → slot → target</b>. "
            "Do not try to “help” the break by yanking your wrist sideways every pitch. "
            "A clean release with the holes set correctly does most of the work — especially under 55 mph.",
            s["body"],
        )
    )
    story.extend(fig("06_throw_slots.png", s, caption="Figure 6. Overhand, three-quarter, and sidearm — match the slot to the pitch family."))
    story.append(Paragraph("Release cues that help new players", s["h2"]))
    story.append(
        bullets(
            [
                "Pick a glove-sized target and throw through it (not “at the break”).",
                "Keep the same arm speed between pitches; change holes/slot instead of muscling up.",
                "Finish your throw — stopping your hand early often kills both aim and movement.",
                "If the pitch spins like a helicopter, your fingers slid across the ball. Reset to seam grip.",
            ],
            s,
        )
    )

    # Rules physics
    story.append(Paragraph("7. New Balls + 55 mph: What That Means", s["h1"]))
    story.append(
        Paragraph(
            "Some backyard pitchers scuff or scratch balls to sharpen break. <b>You cannot do that here.</b> "
            "Only brand-new Wiffle balls with no scuff marks are legal, and velocity caps at 55 mph. "
            "Good news: that is still plenty for real movement if your orientation is honest.",
            s["body"],
        )
    )
    story.extend(fig("07_rules_physics.png", s, caption="Figure 7. Your constraints are also your training plan: precision over doctoring."))
    story.append(
        bullets(
            [
                "<b>No scuffs</b> means less “free” turbulence — so hole aim and seam grip matter more.",
                "<b>55 mph max</b> means command and sequencing beat raw power.",
                "Practice at game speed. If you only warm up at 30 and then jump to 55, orientation drifts.",
                "Rotate new balls as required; do not “wear one in.” Learn to win with fresh plastic.",
            ],
            s,
        )
    )
    story.append(PageBreak())

    # Practice
    story.append(Paragraph("8. 15-Minute Practice Plan", s["h1"]))
    story.append(
        bullets(
            [
                "<b>Minutes 1–3:</b> Seam grip only. 10 throws holes-up for strikes.",
                "<b>Minutes 4–7:</b> Holes-right slider family. Same arm speed, sidearm/¾.",
                "<b>Minutes 8–11:</b> Holes-left screw/riser family. Notice the different flight.",
                "<b>Minutes 12–14:</b> Alternate straight / away / in. Call the pitch before you throw.",
                "<b>Minute 15:</b> 5 knuckle pushes for feel (accept some wildness).",
            ],
            s,
        )
    )
    story.append(
        callout(
            "Troubleshooting: If nothing moves, check three things in order — (1) are holes open? "
            "(2) are holes actually facing the direction you think? (3) are you throwing the slot that matches the pitch?",
            s,
        )
    )
    story.append(Spacer(1, 10))
    story.append(Paragraph("9. Quick Pocket Card", s["h1"]))
    story.append(
        bullets(
            [
                "New ball, no scuffs, ≤ 55 mph.",
                "Fingers on the seam. Holes uncovered.",
                "Holes up → straighter. Holes outer → away. Holes thumb → in/curve.",
                "Sidearm helps slider/riser looks. Overhand helps drop/straight.",
                "Throw through the target. Let the ball’s shape create the break.",
            ],
            s,
        )
    )
    story.append(Spacer(1, 12))
    story.append(
        Paragraph(
            "Master orientation first. Speed is capped — craft is not.",
            s["sub"],
        )
    )

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"Wrote {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    build()
