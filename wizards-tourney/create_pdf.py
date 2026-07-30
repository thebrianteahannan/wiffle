#!/usr/bin/env python3
"""Generate Wizards of Wiffs tournament day PDF for PLW Aug 1 2026."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from manager_info import (
    BROADCAST,
    CAFE,
    CHECK_IN,
    FIELDS,
    MANAGER_CHECKLIST,
    REMINDERS,
    WEATHER,
)
from plw_season6_rules import SECTIONS as RULE_SECTIONS
from strategy_tips import (
    DEFENSE,
    EDGES,
    INTRO,
    OFFENSE,
    PITCHING,
    SCRIPT,
    TOURNAMENT,
)

OUT = Path("/opt/cursor/artifacts/Wizards_of_Wiffs_PLW_Tournament_Aug1_2026.pdf")
OUT.parent.mkdir(parents=True, exist_ok=True)

PURPLE = colors.HexColor("#2D1B4E")
GOLD = colors.HexColor("#C9A227")
LIGHT_PURPLE = colors.HexColor("#F3EEF8")
MID_PURPLE = colors.HexColor("#5B3A8C")
DARK = colors.HexColor("#1A1228")
SOFT_GOLD = colors.HexColor("#F8F1D8")
HIGHLIGHT = colors.HexColor("#E8D5FF")
WHITE = colors.white
GRAY = colors.HexColor("#4A4458")

ROSTER = (
    "Tony Kurtanick  •  Brian Hannan  •  Ben Zysek  •  "
    "Jose Gonzalez  •  Jakob Lafirst  •  Cam Dupe"
)


def make_styles():
    base = getSampleStyleSheet()
    return {
        "cover_brand": ParagraphStyle(
            "cover_brand", fontName="Helvetica-Bold", fontSize=28,
            textColor=GOLD, alignment=TA_CENTER, spaceAfter=6, leading=32,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub", fontName="Helvetica", fontSize=13, textColor=WHITE,
            alignment=TA_CENTER, spaceAfter=4, leading=17,
        ),
        "h2": ParagraphStyle(
            "h2", fontName="Helvetica-Bold", fontSize=11, textColor=MID_PURPLE,
            spaceBefore=8, spaceAfter=4, leading=14,
        ),
        "body": ParagraphStyle(
            "body", fontName="Helvetica", fontSize=9, textColor=DARK,
            alignment=TA_JUSTIFY, spaceAfter=4, leading=12,
        ),
        "bullet": ParagraphStyle(
            "bullet", fontName="Helvetica", fontSize=8.5, textColor=DARK,
            leftIndent=10, spaceAfter=2, leading=11,
        ),
        "tip": ParagraphStyle(
            "tip", fontName="Helvetica", fontSize=9, textColor=DARK,
            leftIndent=6, spaceAfter=3, leading=12,
        ),
        "callout": ParagraphStyle(
            "callout", fontName="Helvetica-Bold", fontSize=9.5, textColor=PURPLE,
            alignment=TA_CENTER, spaceBefore=3, spaceAfter=3, leading=12,
        ),
        "small": ParagraphStyle(
            "small", fontName="Helvetica", fontSize=7.5, textColor=GRAY,
            alignment=TA_CENTER, spaceAfter=2, leading=9.5,
        ),
        "table_cell": ParagraphStyle(
            "table_cell", fontName="Helvetica", fontSize=8, textColor=DARK, leading=10,
        ),
    }


def bullets(items, style):
    return [Paragraph(f"• {item}", style) for item in items]


def section_bar(title):
    data = [[Paragraph(title, ParagraphStyle(
        "bar", fontName="Helvetica-Bold", fontSize=11, textColor=WHITE,
        alignment=TA_LEFT, leading=14,
    ))]]
    t = Table(data, colWidths=[7.0 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PURPLE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def gold_callout(text, styles):
    t = Table([[Paragraph(text, styles["callout"])]], colWidths=[7.0 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SOFT_GOLD),
        ("BOX", (0, 0), (-1, -1), 1.5, GOLD),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def styled_table(headers, rows, col_widths, highlight_rows=None):
    highlight_rows = highlight_rows or set()
    head = [Paragraph(h, ParagraphStyle(
        "th", fontName="Helvetica-Bold", fontSize=8, textColor=WHITE,
        leading=10, alignment=TA_CENTER,
    )) for h in headers]
    body = []
    for i, row in enumerate(rows):
        cells = []
        for j, cell in enumerate(row):
            cells.append(Paragraph(str(cell), ParagraphStyle(
                f"td{i}{j}",
                fontName="Helvetica-Bold" if i in highlight_rows else "Helvetica",
                fontSize=8,
                textColor=PURPLE if i in highlight_rows else DARK,
                leading=10,
                alignment=TA_LEFT if j == 0 else TA_CENTER,
            )))
        body.append(cells)
    t = Table([head] + body, colWidths=col_widths, repeatRows=1)
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), PURPLE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_PURPLE]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C8B8D8")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for r in highlight_rows:
        cmds.append(("BACKGROUND", (0, r + 1), (-1, r + 1), HIGHLIGHT))
    t.setStyle(TableStyle(cmds))
    return t


def add_page_decor(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(2)
    canvas.line(0.6 * inch, letter[1] - 0.45 * inch, letter[0] - 0.6 * inch, letter[1] - 0.45 * inch)
    canvas.setFillColor(PURPLE)
    canvas.rect(0, 0, letter[0], 0.45 * inch, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawCentredString(
        letter[0] / 2, 0.2 * inch,
        "Wizards of Wiffs  •  PLW Brooksville  •  Aug 1, 2026  •  Play Hard. Have Fun. Respect All.",
    )
    canvas.setFillColor(GRAY)
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(letter[0] - 0.6 * inch, letter[1] - 0.38 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build():
    styles = make_styles()
    doc = SimpleDocTemplate(
        str(OUT), pagesize=letter,
        leftMargin=0.65 * inch, rightMargin=0.65 * inch,
        topMargin=0.65 * inch, bottomMargin=0.7 * inch,
        title="Wizards of Wiffs — PLW Tournament Packet (Aug 1, 2026)",
        author="Wizards of Wiffs",
    )
    story = []

    roster_style = ParagraphStyle(
        "rc", fontName="Helvetica", fontSize=8.5, textColor=SOFT_GOLD,
        alignment=TA_CENTER, leading=11,
    )
    banner = Table([
        [Paragraph("WIZARDS OF WIFFS", styles["cover_brand"])],
        [Paragraph("Premier League WIFFLE® Tournament Packet", styles["cover_sub"])],
        [Paragraph("Saturday, August 1, 2026  •  Brooksville, Florida", styles["cover_sub"])],
        [Paragraph("Gates 9:00 AM  •  First Pitch 10:00 AM  •  21+ Event", styles["cover_sub"])],
        [Spacer(1, 6)],
        [Paragraph(ROSTER, roster_style)],
    ], colWidths=[7.0 * inch])
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PURPLE),
        ("TOPPADDING", (0, 0), (-1, 0), 16),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 14),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("BOX", (0, 0), (-1, -1), 3, GOLD),
    ]))
    story.append(banner)
    story.append(Spacer(1, 10))
    story.append(gold_callout(
        "YOUR MISSION: Win Pool C (or earn 1 win → Swing-Off Wildcard) → Playoffs → Championship",
        styles,
    ))
    story.append(Spacer(1, 8))

    story.append(section_bar("1. QUICK FACTS"))
    story.append(Spacer(1, 5))
    facts = [
        ["Date", "Saturday, August 1, 2026"],
        ["Location", "Private ranch — Brooksville, FL (address sent to registered teams only)"],
        ["Format", "12 teams • 3 pools of 4 • 3 guaranteed pool games • Single-elim playoffs"],
        ["Fields", "Main Turf Field • Grass Field 1 • Grass Field 2"],
        ["Game length", "6 innings (extras if tied; runner starts on 2nd)"],
        ["Prize pool*", "1st: $1,500  •  2nd: $400  (*based on 12 teams)"],
        ["Your pool", "Pool C — with Savages, Cloud Seeders, Sandvipers"],
        ["Entry / age", "$200/team • 21+ only • No kids • No pets"],
        ["Footwear", "No spikes/cleats — turf shoes or sneakers only"],
        ["Bring", "Water, snacks, chairs, shade, official yellow Wiffle bats"],
        ["Roster", ROSTER],
    ]
    fact_rows = [
        [Paragraph(f"<b>{a}</b>", styles["table_cell"]), Paragraph(b, styles["table_cell"])]
        for a, b in facts
    ]
    ft = Table(fact_rows, colWidths=[1.3 * inch, 5.7 * inch])
    ft.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_PURPLE),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C8B8D8")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(ft)
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Sources: PLW Tournament Manager Information (Updated), premierleaguewiffle.com, "
        "Official Rule Book (Season 6), Basic Rules, Code of Conduct, pool/schedule sheets.",
        styles["small"],
    ))

    story.append(Spacer(1, 8))
    story.append(section_bar("2. MANAGER INFO — CHECK-IN, FIELDS, WEATHER, CAFE"))
    story.append(Spacer(1, 5))
    story.append(gold_callout(
        "CHECK IN at First Pitch Cafe (Green Building by RF) — Thu/Fri 5–7 PM or Sat 8:30–10:30 AM. Bring ID.",
        styles,
    ))
    story.append(Paragraph("Player check-in", styles["h2"]))
    story.extend(bullets(CHECK_IN, styles["bullet"]))
    story.append(Paragraph("Field locations & conditions", styles["h2"]))
    story.extend(bullets(FIELDS, styles["bullet"]))
    story.append(Paragraph("Weather & rain plan", styles["h2"]))
    story.extend(bullets(WEATHER, styles["bullet"]))
    story.append(Paragraph("First Pitch Cafe (Green Building)", styles["h2"]))
    story.extend(bullets(CAFE, styles["bullet"]))
    story.append(Paragraph("Streamed / featured games", styles["h2"]))
    story.extend(bullets(BROADCAST, styles["bullet"]))
    story.append(Paragraph("Important reminders", styles["h2"]))
    story.extend(bullets(REMINDERS, styles["bullet"]))
    story.append(Paragraph("Manager checklist", styles["h2"]))
    story.extend(bullets(MANAGER_CHECKLIST, styles["bullet"]))

    story.append(PageBreak())
    story.append(section_bar("3. WIZARDS OF WIFFS — YOUR POOL GAMES"))
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        "You play every field once. Check in Sat morning (or Thu/Fri). Gates open 9:00 AM; first pitch 10:00 AM.",
        styles["body"],
    ))
    story.append(styled_table(
        ["Round", "Time", "Opponent", "Field"],
        [
            ["Round 1", "10:00 AM", "vs Savages", "Field 2 (Grass 2)"],
            ["Round 4", "1:00 PM", "vs Sandvipers", "Field 1 (Grass 1)"],
            ["Round 6", "3:00 PM", "vs Cloud Seeders", "Field 3 (Main Turf)"],
        ],
        [1.2 * inch, 1.2 * inch, 2.0 * inch, 2.6 * inch],
        highlight_rows={0, 1, 2},
    ))
    story.append(Spacer(1, 5))
    story.append(gold_callout(
        "Between games: hydrate, shade up, talk matchups. Rounds 2–3 & 5 = scout Pool C rivals.",
        styles,
    ))

    story.append(Spacer(1, 8))
    story.append(section_bar("4. FULL POOL PLAY SCHEDULE"))
    story.append(Spacer(1, 5))
    story.append(styled_table(
        ["Pool", "Teams"],
        [
            ["Pool A", "Wiffle Sh*ts, Blitz, Knuckle Up, Get a Whiff of This"],
            ["Pool B", "Marauders, Step Above, Flamingos, Balls Deep"],
            ["Pool C (YOU)", "Savages, Cloud Seeders, Wizards of Wiffs, Sandvipers"],
        ],
        [1.5 * inch, 5.5 * inch],
        highlight_rows={2},
    ))
    story.append(Spacer(1, 6))

    full = [
        ["R1 — 10:00 AM", "Wiffle Sh*ts vs Blitz", "Marauders vs Balls Deep", "Savages vs WIZARDS"],
        ["R2 — 11:00 AM", "Knuckle Up vs Get a Whiff of This", "Step Above vs Flamingos", "Cloud Seeders vs Sandvipers"],
        ["R3 — 12:00 PM", "Marauders vs Flamingos", "Savages vs Cloud Seeders", "Wiffle Sh*ts vs Get a Whiff of This"],
        ["R4 — 1:00 PM", "Step Above vs Balls Deep", "WIZARDS vs Sandvipers", "Blitz vs Knuckle Up"],
        ["R5 — 2:00 PM", "Savages vs Sandvipers", "Wiffle Sh*ts vs Knuckle Up", "Marauders vs Step Above"],
        ["R6 — 3:00 PM", "Cloud Seeders vs WIZARDS", "Blitz vs Get a Whiff of This", "Flamingos vs Balls Deep"],
    ]
    head = [Paragraph(h, ParagraphStyle(
        "th2", fontName="Helvetica-Bold", fontSize=7.5, textColor=WHITE,
        leading=9, alignment=TA_CENTER,
    )) for h in ["Round / Time", "Main Turf Field", "Grass Field 1", "Grass Field 2"]]
    body, wiz_cells = [], set()
    for ri, row in enumerate(full):
        cells = []
        for ci, cell in enumerate(row):
            is_wiz = "WIZARDS" in cell
            if is_wiz:
                wiz_cells.add((ci, ri + 1))
            cells.append(Paragraph(cell, ParagraphStyle(
                f"f{ri}{ci}",
                fontName="Helvetica-Bold" if is_wiz else "Helvetica",
                fontSize=7, textColor=PURPLE if is_wiz else DARK, leading=9,
                alignment=TA_CENTER if ci else TA_LEFT,
            )))
        body.append(cells)
    sched = Table([head] + body, colWidths=[1.25 * inch, 1.95 * inch, 1.95 * inch, 1.85 * inch])
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), PURPLE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_PURPLE]),
        ("GRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#C8B8D8")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 3),
        ("RIGHTPADDING", (0, 0), (-1, -1), 3),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    for c, r in wiz_cells:
        cmds.append(("BACKGROUND", (c, r), (c, r), HIGHLIGHT))
    sched.setStyle(TableStyle(cmds))
    story.append(sched)

    story.append(Spacer(1, 4))
    story.append(Paragraph(
        "Headers map to manager fields: Main Turf = Field 3 • Grass Field 1 = Field 1 • Grass Field 2 = Field 2.",
        styles["small"],
    ))

    story.append(Spacer(1, 8))
    story.append(section_bar("5. FORMAT, TIEBREAKERS & PLAYOFFS"))
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        "3 pools of 4. Each pool winner advances. 4th playoff spot = <b>Wildcard</b> via Swing-Off. "
        "Any team with <b>≥1 win</b> is eligible. Single-elim final four.",
        styles["body"],
    ))
    story.append(Paragraph("<b>Pool 1st-place tiebreakers (in order)</b>", styles["h2"]))
    story.extend(bullets([
        "Head-to-head record",
        "Fewest runs allowed  ← defense/pitching is huge",
        "Run differential",
        "Most runs scored",
        "Coin flip",
    ], styles["bullet"]))
    story.append(Paragraph("<b>Playoff bracket</b>", styles["h2"]))
    story.extend(bullets([
        "Semi-Final 1: Pool 1 Winner vs Pool 2 Winner",
        "Semi-Final 2: Pool 3 Winner vs Wildcard",
        "Championship: Semi winners → CHAMPION",
    ], styles["bullet"]))
    story.append(Spacer(1, 4))
    story.append(gold_callout(
        "UNDERDOG PATH: Steal 1 pool win (Wildcard) + keep runs allowed low (tiebreakers).",
        styles,
    ))

    # ===== FULL SEASON 6 RULES =====
    story.append(PageBreak())
    story.append(section_bar("6. COMPLETE PLW SEASON 6 RULE BOOK (CHEAT SHEET)"))
    story.append(Spacer(1, 5))
    story.append(Paragraph(
        "Full coverage of every rule from "
        "<link href='https://premierleaguewiffle.com/rules/' color='#5B3A8C'>"
        "<u>premierleaguewiffle.com/rules/</u></link> "
        "(Season 6). Bring this. Argue from the book.",
        styles["body"],
    ))
    for title, items in RULE_SECTIONS:
        story.append(Paragraph(title, styles["h2"]))
        story.extend(bullets(items, styles["bullet"]))

    story.append(Spacer(1, 8))
    story.append(section_bar("7. CODE OF CONDUCT (DON'T GET TOSSED)"))
    story.append(Spacer(1, 5))
    story.extend(bullets([
        "Respect players, umpires, staff, fans, and the ranch property. Clean dugouts.",
        "Only managers speak to umps about calls.",
        "Stay in dugout unless on deck / batting / on defense (HR celebration exception).",
        "No taunting, personal insults, or profanity; zero tolerance for racism, violence, weapons.",
        "Don't throw bats in anger. Handle gear safely.",
        "Motto: <b>Play Hard. Have Fun. Respect All.</b>",
    ], styles["bullet"]))

    story.append(PageBreak())
    story.append(section_bar("8. UNDERDOG TIPS & TRICKS — STEAL GAMES FROM BETTER TEAMS"))
    story.append(Spacer(1, 5))
    story.append(Paragraph(INTRO, styles["body"]))
    story.append(Paragraph("A. Pitching game plan", styles["h2"]))
    story.extend(bullets(PITCHING, styles["bullet"]))
    story.append(Paragraph("B. Defense & runs-allowed obsession", styles["h2"]))
    story.extend(bullets(DEFENSE, styles["bullet"]))
    story.append(Paragraph("C. Offense against better pitching", styles["h2"]))
    story.extend(bullets(OFFENSE, styles["bullet"]))
    story.append(Paragraph("D. Tournament math & mind games", styles["h2"]))
    story.extend(bullets(TOURNAMENT, styles["bullet"]))
    story.append(Paragraph("E. Small-rules edges", styles["h2"]))
    story.extend(bullets(EDGES, styles["bullet"]))
    story.append(Spacer(1, 5))
    story.append(gold_callout(SCRIPT, styles))

    story.append(Spacer(1, 8))
    story.append(section_bar("9. GAME-DAY CHECKLIST"))
    story.append(Spacer(1, 5))
    cols = Table([[
        Paragraph(
            "<b>Check-in &amp; gear</b><br/>"
            "• Valid ID + waivers + film release + profile photo<br/>"
            "• Official yellow Wiffle bats (taped legal)<br/>"
            "• Turf shoes / sneakers (no cleats)<br/>"
            "• Matching jerseys (helps for streamed games)<br/>"
            "• Barehand warmup ball",
            styles["tip"],
        ),
        Paragraph(
            "<b>Body &amp; camp</b><br/>"
            "• Water + electrolytes (Cafe also has water/snacks)<br/>"
            "• Chairs + canopy/shade (storms possible)<br/>"
            "• Sunscreen, towels<br/>"
            "• Thu/Fri check-in 5–7 PM <b>or</b> Sat 8:30 AM<br/>"
            "• No kids • No pets • No visible alcohol on stream",
            styles["tip"],
        ),
    ]], colWidths=[3.5 * inch, 3.5 * inch])
    cols.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_PURPLE),
        ("BOX", (0, 0), (-1, -1), 1, GOLD),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    story.append(cols)

    story.append(Spacer(1, 8))
    story.append(section_bar("10. LINKS"))
    story.append(Spacer(1, 5))
    story.extend(bullets([
        "Full rule book: https://premierleaguewiffle.com/rules/",
        "Basic rules: https://premierleaguewiffle.com/basic-rules/",
        "Tournament page: https://premierleaguewiffle.com/2026/07/01/august-1st-tourney-sign-ups-open/",
        "Code of conduct: https://premierleaguewiffle.com/player-code-of-conduct/",
        "Volunteer (cameras / scorekeeping / umpiring): Adam Tanic or Tom Gannon",
    ], styles["bullet"]))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "Go get a win, Wizards. Cast some outs. Steal a Wildcard.",
        ParagraphStyle(
            "end", fontName="Helvetica-Bold", fontSize=12, textColor=PURPLE,
            alignment=TA_CENTER, spaceBefore=4,
        ),
    ))
    story.append(Paragraph(
        "Compiled from PLW Tournament Manager Information (Updated), Season 6 rules, "
        "and provided schedule/pool sheets. On-site umpires / PLW updates control final interpretation.",
        styles["small"],
    ))

    doc.build(story, onFirstPage=add_page_decor, onLaterPages=add_page_decor)
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")
    return OUT


if __name__ == "__main__":
    build()
