#!/usr/bin/env python3
"""Generate a beginner-friendly Wiffle ball pitching strategy PDF."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    KeepTogether,
    ListFlowable,
    ListItem,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

OUTPUT = Path(__file__).resolve().parents[1] / "docs" / "Wiffle_Ball_Pitching_Strategies.pdf"

NAVY = colors.HexColor("#0B3D5C")
TEAL = colors.HexColor("#1F7A8C")
SAND = colors.HexColor("#F2F6F8")
INK = colors.HexColor("#1A2428")
MUTED = colors.HexColor("#4A5A63")
ACCENT = colors.HexColor("#C45C26")


def make_styles():
    base = getSampleStyleSheet()
    styles = {
        "cover_title": ParagraphStyle(
            "cover_title",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=28,
            leading=34,
            textColor=NAVY,
            alignment=TA_CENTER,
            spaceAfter=12,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=13,
            leading=18,
            textColor=TEAL,
            alignment=TA_CENTER,
            spaceAfter=8,
        ),
        "cover_tag": ParagraphStyle(
            "cover_tag",
            parent=base["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=11,
            leading=15,
            textColor=MUTED,
            alignment=TA_CENTER,
            spaceAfter=18,
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            leading=20,
            textColor=NAVY,
            spaceBefore=4,
            spaceAfter=10,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12.5,
            leading=16,
            textColor=TEAL,
            spaceBefore=12,
            spaceAfter=6,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=15,
            textColor=INK,
            alignment=TA_JUSTIFY,
            spaceAfter=8,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=10.5,
            leading=14.5,
            textColor=INK,
            leftIndent=4,
        ),
        "callout": ParagraphStyle(
            "callout",
            parent=base["Normal"],
            fontName="Helvetica-Oblique",
            fontSize=10.5,
            leading=14.5,
            textColor=NAVY,
            alignment=TA_LEFT,
        ),
        "table_header": ParagraphStyle(
            "table_header",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            leading=12,
            textColor=colors.white,
            alignment=TA_CENTER,
        ),
        "table_cell": ParagraphStyle(
            "table_cell",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9,
            leading=12,
            textColor=INK,
        ),
        "footer": ParagraphStyle(
            "footer",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            textColor=MUTED,
            alignment=TA_CENTER,
        ),
        "tip_label": ParagraphStyle(
            "tip_label",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=9.5,
            textColor=ACCENT,
            spaceAfter=2,
        ),
    }
    return styles


def bullets(items, styles):
    return ListFlowable(
        [ListItem(Paragraph(item, styles["bullet"]), leftIndent=12, bulletColor=TEAL) for item in items],
        bulletType="bullet",
        start="•",
        leftIndent=18,
        bulletFontSize=10,
        spaceBefore=2,
        spaceAfter=8,
    )


def callout_box(text, styles):
    data = [[Paragraph(text, styles["callout"])]]
    table = Table(data, colWidths=[6.5 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), SAND),
                ("BOX", (0, 0), (-1, -1), 1, TEAL),
                ("LEFTPADDING", (0, 0), (-1, -1), 12),
                ("RIGHTPADDING", (0, 0), (-1, -1), 12),
                ("TOPPADDING", (0, 0), (-1, -1), 10),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ]
        )
    )
    return KeepTogether([table, Spacer(1, 12)])


def count_table(styles):
    header = [
        Paragraph("Count", styles["table_header"]),
        Paragraph("Batter is thinking...", styles["table_header"]),
        Paragraph("Your move", styles["table_header"]),
    ]
    rows = [
        ["0-0", "Looking for a clean first pitch to drive.", "Start with a strike at the edge—not the middle. Steal an early advantage."],
        ["0-1 / 0-2", "Protecting. Expecting something tough or off-speed.", "Expand the zone. Chase pitches just off the plate work best here."],
        ["1-0 / 2-0", "Sitting dead-red. Waiting for a cookie.", "Do NOT groove one. Nibble corners. Make them prove they can wait."],
        ["2-1 / 3-1", "Hitter's count. Looking for a pitch to crush.", "Best strike you can still locate. Challenge with purpose, not hope."],
        ["3-2", "Must swing at anything close. Nervous about walking.", "Your money pitch. Trust aim. Edge of the zone beats middle of the plate."],
        ["1-2 / 2-2", "Pitcher's count. Defensive swing coming.", "Set up with a show pitch, then finish with your best location."],
    ]
    data = [header]
    for count, think, move in rows:
        data.append(
            [
                Paragraph(f"<b>{count}</b>", styles["table_cell"]),
                Paragraph(think, styles["table_cell"]),
                Paragraph(move, styles["table_cell"]),
            ]
        )
    table = Table(data, colWidths=[0.9 * inch, 2.6 * inch, 3.0 * inch])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("BACKGROUND", (0, 1), (-1, 1), SAND),
                ("BACKGROUND", (0, 3), (-1, 3), SAND),
                ("BACKGROUND", (0, 5), (-1, 5), SAND),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C9D5DC")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    return table


def footer(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(TEAL)
    canvas.setLineWidth(0.8)
    canvas.line(0.75 * inch, 0.6 * inch, 7.75 * inch, 0.6 * inch)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(0.75 * inch, 0.4 * inch, "Wiffle Ball Pitching Strategies")
    canvas.drawRightString(7.75 * inch, 0.4 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build_pdf():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    styles = make_styles()
    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        leftMargin=0.75 * inch,
        rightMargin=0.75 * inch,
        topMargin=0.7 * inch,
        bottomMargin=0.85 * inch,
        title="Wiffle Ball Pitching Strategies",
        author="Wiffle Strategy Guide",
    )

    story = []

    # Cover
    story.append(Spacer(1, 1.4 * inch))
    story.append(Paragraph("WIFFLE BALL", styles["cover_title"]))
    story.append(Paragraph("Pitching Strategies for Newer Players", styles["cover_sub"]))
    story.append(
        Paragraph(
            "How to use the count, location, and psychology to beat batters—even when you're still learning.",
            styles["cover_tag"],
        )
    )
    story.append(callout_box(
        "Your edge: good aim. Strategy turns aim into outs. This guide shows when to throw where, "
        "what the batter is usually thinking, and how to stay one pitch ahead.",
        styles,
    ))
    story.append(Paragraph("What's inside", styles["h2"]))
    story.append(
        bullets(
            [
                "Using the count to your advantage",
                "Where to place the ball in common situations",
                "Batter psychology (what they're thinking)",
                "Simple sequences that make your aim more dangerous",
                "A starter game plan you can use tonight",
            ],
            styles,
        )
    )
    story.append(PageBreak())

    # Section 1
    story.append(Paragraph("1. The Big Idea: Pitching Is Chess, Not Darts", styles["h1"]))
    story.append(
        Paragraph(
            "Great aim alone will get you strikes. Strategy gets you outs. In Wiffle ball, the ball moves, "
            "the zone is often informal, and hitters swing with big intentions. Your job is not to throw "
            "unhittable pitches every time—it's to make the hitter uncomfortable, guess wrong, and put "
            "weak contact in the air or miss entirely.",
            styles["body"],
        )
    )
    story.append(
        Paragraph(
            "Think in three layers on every pitch:",
            styles["body"],
        )
    )
    story.append(
        bullets(
            [
                "<b>Count</b> — Who is ahead? That decides how aggressive you can be.",
                "<b>Location</b> — Where in the zone (or just outside) do you want this pitch?",
                "<b>Story</b> — What did you just throw, and what are you setting up next?",
            ],
            styles,
        )
    )
    story.append(
        callout_box(
            "Rule of thumb: Never throw the same pitch to the same spot twice in a row unless you're "
            "intentionally freezing a hitter who keeps missing there.",
            styles,
        )
    )

    # Section 2
    story.append(Paragraph("2. Using the Count to Your Advantage", styles["h1"]))
    story.append(
        Paragraph(
            "The count is free information. Batters change their approach based on it—and so should you. "
            "When you're ahead, make them chase. When you're behind, don't panic and throw a meatball. "
            "When it's even, steal strikes at the edges.",
            styles["body"],
        )
    )
    story.append(count_table(styles))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Quick count principles", styles["h2"]))
    story.append(
        bullets(
            [
                "<b>Ahead in the count (more strikes than balls):</b> Expand. Aim just off the plate or at the "
                "corners. Force a defensive swing.",
                "<b>Behind in the count:</b> Compete. Throw your most confident strike location—usually low "
                "and away or a rising strike at the letters—not dead middle.",
                "<b>Two-strike mindset:</b> You have permission to miss by an inch outside. One soft foul or "
                "whiff is better than a hanging pitch over the heart.",
                "<b>Full count:</b> Commit. Pick one location you trust and throw it with conviction.",
            ],
            styles,
        )
    )

    # Section 3
    story.append(Paragraph("3. Where to Place the Ball (And When)", styles["h1"]))
    story.append(
        Paragraph(
            "Because you have good aim, location is your superpower. In Wiffle ball, the sweet spot of the "
            "bat is small and timing is everything. Hitting the edges of the zone makes hard contact rare.",
            styles["body"],
        )
    )
    story.append(Paragraph("High-value targets", styles["h2"]))
    story.append(
        bullets(
            [
                "<b>Low and away:</b> Your bread-and-butter. Hard for most hitters to drive. Great first pitch "
                "and great two-strike pitch.",
                "<b>Up and in (carefully):</b> Crowds the hands. Use after you've lived away. Makes the next "
                "away pitch look farther.",
                "<b>High rising strike:</b> Many Wiffle pitches climb. A high strike looks tempting and often "
                "produces pop-ups or late swings.",
                "<b>Just off the plate (chase zone):</b> Best when you're ahead 0-2 or 1-2. Looks hittable for "
                "a split second, then isn't.",
                "<b>Knee-high on the black:</b> Steal strikes early in the count when the umpire/zone is generous.",
            ],
            styles,
        )
    )
    story.append(Paragraph("When NOT to aim for the middle", styles["h2"]))
    story.append(
        Paragraph(
            "The middle of the plate is for emergencies only—like 3-0 when you absolutely must throw a strike "
            "and even then, aim for the lower half. A middle-middle Wiffle pitch is the one that leaves the yard.",
            styles["body"],
        )
    )
    story.append(
        callout_box(
            "Aim tip: Pick a tiny target. Don't think \"outside.\" Think \"glove-side corner, belt-high, "
            "two inches off the black.\" Specific targets sharpen good aim.",
            styles,
        )
    )

    story.append(PageBreak())

    # Section 4
    story.append(Paragraph("4. What the Batter Is Thinking", styles["h1"]))
    story.append(
        Paragraph(
            "If you can guess their mental script, you can interrupt it. Most recreational Wiffle hitters "
            "fall into predictable patterns:",
            styles["body"],
        )
    )
    story.append(
        bullets(
            [
                "<b>\"I'm going to crush the first good one.\"</b> — So don't give a center-cut first pitch. "
                "Start on the edge.",
                "<b>\"He's been living outside… I'm diving that way.\"</b> — After 2–3 away pitches, bust one "
                "inside or change eye level.",
                "<b>\"Two strikes—don't strike out looking.\"</b> — They expand their swing zone. Feed them "
                "borderline chase pitches.",
                "<b>\"3-1, here comes a cookie.\"</b> — They sit heater/middle. Throw a confident corner strike "
                "or a pitch that moves off the barrel.",
                "<b>\"That last pitch was nasty—same one is coming.\"</b> — Rarely throw the exact same pitch "
                "again. Change speed, height, or side.",
                "<b>\"I'm late / I'm early.\"</b> — If they foul tip late, they need more time—throw something "
                "that looks similar but arrives differently (higher, softer, or farther away).",
            ],
            styles,
        )
    )
    story.append(Paragraph("Read their body language", styles["h2"]))
    story.append(
        bullets(
            [
                "Big leg kick / aggressive load → they're hunting. Change speeds or go away.",
                "Choked up / quiet stance after a miss → protecting. Expand the zone.",
                "Stepping in the bucket (front foot flies open) → they fear inside. Keep going away… then "
                "surprise with one inside later.",
                "Late fouls to the opposite side → they're behind. Don't speed up; freeze them with location "
                "changes and soft movement.",
            ],
            styles,
        )
    )

    # Section 5
    story.append(Paragraph("5. Psychology: Getting Inside Their Head (Fairly)", styles["h1"]))
    story.append(
        Paragraph(
            "Psychology in pitching is not trash talk—it's pattern control. You show them one thing, then "
            "take it away. You make them feel safe, then punish the guess.",
            styles["body"],
        )
    )
    story.append(Paragraph("Simple mind games that work", styles["h2"]))
    story.append(
        bullets(
            [
                "<b>The setup pitch:</b> Throw a clear ball outside on purpose when ahead. Now they wonder if "
                "you'll come back. Next pitch: steal the outside corner for a strike or chase.",
                "<b>Eye-level change:</b> Low, low, then high. Or high, high, then bury one. Vertical change "
                "wrecks timing as much as speed change.",
                "<b>In-out sequencing:</b> Away, away, then in. Inside sets up away. Never live in one lane "
                "for a whole at-bat unless they're helpless there.",
                "<b>Tempo change:</b> Work quick when they're uncomfortable. Slow down when they're locked in "
                "and swinging early. Own the rhythm of the at-bat.",
                "<b>Confidence sells strikes:</b> Hesitation tells a hitter you're scared of contact. Pick a "
                "spot, nod, and throw. Batters swing differently against a pitcher who looks sure.",
            ],
            styles,
        )
    )
    story.append(
        callout_box(
            "New-player secret: You don't need five pitches. You need two locations you trust and the "
            "discipline to sequence them. Aim + plan beats fancy grips you can't control yet.",
            styles,
        )
    )

    # Section 6
    story.append(Paragraph("6. Ready-Made Pitch Plans (Steal These)", styles["h1"]))
    story.append(Paragraph("Plan A — The Outside Artist", styles["h2"]))
    story.append(
        bullets(
            [
                "Pitch 1: Low and away strike",
                "Pitch 2: Farther away (chase) or up and away",
                "Pitch 3: Back to the outside corner, or one quick inside pitch if they lean out",
                "Best for: Patient or pull-happy hitters",
            ],
            styles,
        )
    )
    story.append(Paragraph("Plan B — Climb the Ladder", styles["h2"]))
    story.append(
        bullets(
            [
                "Pitch 1: Strike at the thighs",
                "Pitch 2: Higher, near the letters",
                "Pitch 3: Above the zone (chase) once they start swinging up",
                "Best for: Hitters who love low balls and uppercut",
            ],
            styles,
        )
    )
    story.append(Paragraph("Plan C — Soft Then Firm", styles["h2"]))
    story.append(
        bullets(
            [
                "Pitch 1: Slower / more floating strike on the edge",
                "Pitch 2: Quicker pitch, same tunnel, different height",
                "Pitch 3: Back to soft, just off the plate",
                "Best for: Timing-dependent mashers",
            ],
            styles,
        )
    )

    story.append(PageBreak())

    # Section 7
    story.append(Paragraph("7. Turning Good Aim Into a Real Advantage", styles["h1"]))
    story.append(
        Paragraph(
            "A lot of newer pitchers with good aim accidentally throw too many \"pretty\" strikes down the "
            "middle because they can. Don't. Your accuracy should buy you <b>smaller targets</b>, not safer ones.",
            styles["body"],
        )
    )
    story.append(
        bullets(
            [
                "Warm up by hitting a glove corner 10 times in a row before you care about speed.",
                "In games, call the spot out loud in your head before every pitch: \"low glove-side.\"",
                "If you miss, miss off the plate—not over the heart. Misses away are competitive; misses middle are gifts.",
                "Keep a simple book: which location got each hitter out? Use it next at-bat.",
                "Practice 0-2 and 3-2 scenarios on purpose. Those are where games are won.",
            ],
            styles,
        )
    )

    # Section 8
    story.append(Paragraph("8. Common Mistakes Newer Pitchers Make", styles["h1"]))
    story.append(
        bullets(
            [
                "<b>Throwing \"get-me-over\" meatballs when behind.</b> Compete with a corner, not the middle.",
                "<b>Falling in love with one pitch that worked once.</b> Hitters adjust fast in Wiffle.",
                "<b>Ignoring the count.</b> Same approach on 0-2 and 3-1 is leaving outs on the table.",
                "<b>Speeding up every pitch.</b> Change of pace is a weapon even with average velocity.",
                "<b>Showing frustration after a hit.</b> Next hitter sees it. Reset and execute the next plan.",
                "<b>Overthinking grips mid-game.</b> Master location first; add movement second.",
            ],
            styles,
        )
    )

    # Section 9
    story.append(Paragraph("9. Your First-Game Checklist", styles["h1"]))
    story.append(
        Paragraph(
            "Use this the next time you pitch. Keep it in your pocket mentally:",
            styles["body"],
        )
    )
    story.append(
        bullets(
            [
                "Before each batter: pick Plan A, B, or C.",
                "First pitch: edge strike. Never middle-middle.",
                "If ahead: expand the zone immediately.",
                "If behind: best strike location you trust.",
                "After two away pitches: change height or come inside once.",
                "Two strikes: tiny target just off the corner.",
                "After the out: remember what worked for next time.",
            ],
            styles,
        )
    )
    story.append(
        callout_box(
            "Bottom line: Batters want a predictable, center-cut pitch they can time. Your aim lets you "
            "deny that pitch. Live on the edges, change the eye level, and always know what the count is "
            "telling both of you to do.",
            styles,
        )
    )

    story.append(Spacer(1, 16))
    story.append(Paragraph("Quick Reference Card", styles["h1"]))
    ref = [
        [
            Paragraph("<b>Situation</b>", styles["table_header"]),
            Paragraph("<b>Throw</b>", styles["table_header"]),
        ],
        [
            Paragraph("First pitch", styles["table_cell"]),
            Paragraph("Low/away or corner strike", styles["table_cell"]),
        ],
        [
            Paragraph("0-2 / 1-2", styles["table_cell"]),
            Paragraph("Chase just off plate; change eye level", styles["table_cell"]),
        ],
        [
            Paragraph("3-1 / 3-2", styles["table_cell"]),
            Paragraph("Confident edge strike—not middle", styles["table_cell"]),
        ],
        [
            Paragraph("Hitter diving out", styles["table_cell"]),
            Paragraph("One inside pitch, then back away", styles["table_cell"]),
        ],
        [
            Paragraph("Hitter late", styles["table_cell"]),
            Paragraph("Soft / higher / farther—don't groove speed", styles["table_cell"]),
        ],
        [
            Paragraph("After a hard hit", styles["table_cell"]),
            Paragraph("Reset; same plan, sharper location", styles["table_cell"]),
        ],
    ]
    ref_table = Table(ref, colWidths=[2.2 * inch, 4.3 * inch])
    ref_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), TEAL),
                ("BACKGROUND", (0, 1), (-1, 1), SAND),
                ("BACKGROUND", (0, 3), (-1, 3), SAND),
                ("BACKGROUND", (0, 5), (-1, 5), SAND),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#C9D5DC")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 7),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.append(ref_table)

    story.append(Spacer(1, 20))
    story.append(
        Paragraph(
            "Practice with purpose. Pitch with a plan. Trust your aim.",
            styles["cover_sub"],
        )
    )

    doc.build(story, onFirstPage=footer, onLaterPages=footer)
    print(f"Wrote {OUTPUT}")
    return OUTPUT


if __name__ == "__main__":
    build_pdf()
