#!/usr/bin/env python3
"""Generate Wizards of Wiffs tournament day PDF for PLW Aug 1 2026."""

from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
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

OUT = Path("/opt/cursor/artifacts/Wizards_of_Wiffs_PLW_Tournament_Aug1_2026.pdf")
OUT.parent.mkdir(parents=True, exist_ok=True)

# Team palette
PURPLE = colors.HexColor("#2D1B4E")
GOLD = colors.HexColor("#C9A227")
LIGHT_PURPLE = colors.HexColor("#F3EEF8")
MID_PURPLE = colors.HexColor("#5B3A8C")
DARK = colors.HexColor("#1A1228")
SOFT_GOLD = colors.HexColor("#F8F1D8")
HIGHLIGHT = colors.HexColor("#E8D5FF")
WHITE = colors.white
GRAY = colors.HexColor("#4A4458")


def make_styles():
    base = getSampleStyleSheet()
    styles = {
        "cover_brand": ParagraphStyle(
            "cover_brand",
            parent=base["Title"],
            fontName="Helvetica-Bold",
            fontSize=28,
            textColor=GOLD,
            alignment=TA_CENTER,
            spaceAfter=6,
            leading=32,
        ),
        "cover_sub": ParagraphStyle(
            "cover_sub",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=13,
            textColor=WHITE,
            alignment=TA_CENTER,
            spaceAfter=4,
            leading=17,
        ),
        "h1": ParagraphStyle(
            "h1",
            parent=base["Heading1"],
            fontName="Helvetica-Bold",
            fontSize=16,
            textColor=PURPLE,
            spaceBefore=14,
            spaceAfter=8,
            leading=20,
        ),
        "h2": ParagraphStyle(
            "h2",
            parent=base["Heading2"],
            fontName="Helvetica-Bold",
            fontSize=12,
            textColor=MID_PURPLE,
            spaceBefore=10,
            spaceAfter=5,
            leading=15,
        ),
        "body": ParagraphStyle(
            "body",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            textColor=DARK,
            alignment=TA_JUSTIFY,
            spaceAfter=5,
            leading=13,
        ),
        "bullet": ParagraphStyle(
            "bullet",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            textColor=DARK,
            leftIndent=12,
            spaceAfter=3,
            leading=12.5,
        ),
        "tip": ParagraphStyle(
            "tip",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=9.5,
            textColor=DARK,
            leftIndent=8,
            spaceAfter=4,
            leading=12.5,
        ),
        "callout": ParagraphStyle(
            "callout",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=10,
            textColor=PURPLE,
            alignment=TA_CENTER,
            spaceBefore=4,
            spaceAfter=4,
            leading=13,
        ),
        "small": ParagraphStyle(
            "small",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            textColor=GRAY,
            alignment=TA_CENTER,
            spaceAfter=2,
            leading=10,
        ),
        "table_cell": ParagraphStyle(
            "table_cell",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=8,
            textColor=DARK,
            leading=10,
            alignment=TA_LEFT,
        ),
        "table_cell_bold": ParagraphStyle(
            "table_cell_bold",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            textColor=PURPLE,
            leading=10,
            alignment=TA_LEFT,
        ),
        "table_head": ParagraphStyle(
            "table_head",
            parent=base["Normal"],
            fontName="Helvetica-Bold",
            fontSize=8,
            textColor=WHITE,
            leading=10,
            alignment=TA_CENTER,
        ),
        "footer": ParagraphStyle(
            "footer",
            parent=base["Normal"],
            fontName="Helvetica",
            fontSize=7.5,
            textColor=GRAY,
            alignment=TA_CENTER,
        ),
    }
    return styles


def bullets(items, style):
    return [
        Paragraph(f"• {item}", style) for item in items
    ]


def section_bar(title, styles):
    data = [[Paragraph(title, ParagraphStyle(
        "bar",
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=WHITE,
        alignment=TA_LEFT,
        leading=14,
    ))]]
    t = Table(data, colWidths=[7.0 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PURPLE),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def gold_callout(text, styles):
    data = [[Paragraph(text, styles["callout"])]]
    t = Table(data, colWidths=[7.0 * inch])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), SOFT_GOLD),
        ("BOX", (0, 0), (-1, -1), 1.5, GOLD),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    return t


def styled_table(headers, rows, col_widths, highlight_rows=None):
    highlight_rows = highlight_rows or set()
    head = [Paragraph(h, ParagraphStyle(
        "th", fontName="Helvetica-Bold", fontSize=8, textColor=WHITE, leading=10, alignment=TA_CENTER
    )) for h in headers]
    body = []
    for i, row in enumerate(rows):
        cells = []
        for j, cell in enumerate(row):
            st = ParagraphStyle(
                f"td{i}{j}",
                fontName="Helvetica-Bold" if i in highlight_rows else "Helvetica",
                fontSize=8,
                textColor=PURPLE if i in highlight_rows else DARK,
                leading=10,
                alignment=TA_LEFT if j == 0 else TA_CENTER,
            )
            cells.append(Paragraph(str(cell), st))
        body.append(cells)
    data = [head] + body
    t = Table(data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), PURPLE),
        ("BACKGROUND", (0, 1), (-1, -1), LIGHT_PURPLE),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_PURPLE]),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C8B8D8")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]
    for r in highlight_rows:
        style_cmds.append(("BACKGROUND", (0, r + 1), (-1, r + 1), HIGHLIGHT))
    t.setStyle(TableStyle(style_cmds))
    return t


def add_page_decor(canvas, doc):
    canvas.saveState()
    # Top gold line
    canvas.setStrokeColor(GOLD)
    canvas.setLineWidth(2)
    canvas.line(0.6 * inch, letter[1] - 0.45 * inch, letter[0] - 0.6 * inch, letter[1] - 0.45 * inch)
    # Footer
    canvas.setFillColor(PURPLE)
    canvas.rect(0, 0, letter[0], 0.45 * inch, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.drawCentredString(letter[0] / 2, 0.2 * inch, "Wizards of Wiffs  •  PLW Brooksville  •  Aug 1, 2026  •  Play Hard. Have Fun. Respect All.")
    canvas.setFillColor(GRAY)
    canvas.setFont("Helvetica", 8)
    canvas.drawRightString(letter[0] - 0.6 * inch, letter[1] - 0.38 * inch, f"Page {doc.page}")
    canvas.restoreState()


def build():
    styles = make_styles()
    doc = SimpleDocTemplate(
        str(OUT),
        pagesize=letter,
        leftMargin=0.65 * inch,
        rightMargin=0.65 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.7 * inch,
        title="Wizards of Wiffs — PLW Tournament Packet (Aug 1, 2026)",
        author="Wizards of Wiffs",
    )
    story = []

    # ===== COVER =====
    cover = Table(
        [[
            Paragraph("WIZARDS OF WIFFS", styles["cover_brand"]),
            Paragraph("Premier League WIFFLE® Tournament Packet", styles["cover_sub"]),
            Paragraph("Saturday, August 1, 2026  •  Brooksville, Florida", styles["cover_sub"]),
            Paragraph("Gates 9:00 AM  •  First Pitch 10:00 AM  •  21+ Event", styles["cover_sub"]),
            Spacer(1, 8),
            Paragraph(
                "Roster: Tony Kurtanick  •  Brian Hannan  •  Ben Zysek  •  Jose Gonzalez  •  Jakob Lafirst",
                ParagraphStyle("roster_c", fontName="Helvetica", fontSize=9, textColor=SOFT_GOLD, alignment=TA_CENTER, leading=12),
            ),
        ]],
        colWidths=[7.0 * inch],
    )
    # Flatten into purple banner via nested table
    banner_content = [
        [Paragraph("WIZARDS OF WIFFS", styles["cover_brand"])],
        [Paragraph("Premier League WIFFLE® Tournament Packet", styles["cover_sub"])],
        [Paragraph("Saturday, August 1, 2026  •  Brooksville, Florida", styles["cover_sub"])],
        [Paragraph("Gates 9:00 AM  •  First Pitch 10:00 AM  •  21+ Event", styles["cover_sub"])],
        [Spacer(1, 6)],
        [Paragraph(
            "Tony Kurtanick  •  Brian Hannan  •  Ben Zysek  •  Jose Gonzalez  •  Jakob Lafirst",
            ParagraphStyle("rc", fontName="Helvetica", fontSize=9, textColor=SOFT_GOLD, alignment=TA_CENTER, leading=12),
        )],
    ]
    banner = Table(banner_content, colWidths=[7.0 * inch])
    banner.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PURPLE),
        ("TOPPADDING", (0, 0), (-1, 0), 18),
        ("BOTTOMPADDING", (0, -1), (-1, -1), 16),
        ("LEFTPADDING", (0, 0), (-1, -1), 12),
        ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("BOX", (0, 0), (-1, -1), 3, GOLD),
    ]))
    story.append(banner)
    story.append(Spacer(1, 12))
    story.append(gold_callout(
        "YOUR MISSION: Win Pool C (or earn 1 win → Swing-Off Wildcard) → Playoffs → Championship",
        styles,
    ))
    story.append(Spacer(1, 10))

    # Quick facts
    story.append(section_bar("1. QUICK FACTS", styles))
    story.append(Spacer(1, 6))
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
    ]
    fact_rows = [[Paragraph(f"<b>{a}</b>", styles["table_cell"]), Paragraph(b, styles["table_cell"])] for a, b in facts]
    ft = Table(fact_rows, colWidths=[1.4 * inch, 5.6 * inch])
    ft.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_PURPLE),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#C8B8D8")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    story.append(ft)
    story.append(Spacer(1, 8))
    story.append(Paragraph(
        "Sources: premierleaguewiffle.com tournament page, Basic Rules, Official Rule Book (Season 6), Player Code of Conduct, and your pool/schedule sheets.",
        styles["small"],
    ))

    # ===== YOUR SCHEDULE =====
    story.append(Spacer(1, 8))
    story.append(section_bar("2. WIZARDS OF WIFFS — YOUR POOL GAMES (HIGHLIGHTED)", styles))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "You play every field once. Arrive early for check-in and warmups. Gates open 9:00 AM.",
        styles["body"],
    ))
    wiz_games = [
        ["Round 1", "10:00 AM", "vs Savages", "Grass Field 2"],
        ["Round 4", "1:00 PM", "vs Sandvipers", "Grass Field 1"],
        ["Round 6", "3:00 PM", "vs Cloud Seeders", "Main Turf Field"],
    ]
    story.append(styled_table(
        ["Round", "Time", "Opponent", "Field"],
        wiz_games,
        [1.3 * inch, 1.3 * inch, 2.2 * inch, 2.2 * inch],
        highlight_rows={0, 1, 2},
    ))
    story.append(Spacer(1, 6))
    story.append(gold_callout(
        "Between games: hydrate, shade up, talk matchups. Round 2–3 & 5 are scout/watch time for Pool C rivals.",
        styles,
    ))

    # ===== FULL SCHEDULE =====
    story.append(Spacer(1, 10))
    story.append(section_bar("3. FULL POOL PLAY SCHEDULE", styles))
    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Pools</b>", styles["h2"]))
    pools = [
        ["Pool A", "Wiffle Sh*ts, Blitz, Knuckle Up, Get a Whiff of This"],
        ["Pool B", "Marauders, Step Above, Flamingos, Balls Deep"],
        ["Pool C (YOU)", "Savages, Cloud Seeders, Wizards of Wiffs, Sandvipers"],
    ]
    story.append(styled_table(["Pool", "Teams"], pools, [1.5 * inch, 5.5 * inch], highlight_rows={2}))
    story.append(Spacer(1, 8))

    # Highlight wizard rows: R1 grass2, R4 grass1, R6 turf
    full = [
        ["R1 — 10:00 AM", "Wiffle Sh*ts vs Blitz", "Marauders vs Balls Deep", "Savages vs WIZARDS"],
        ["R2 — 11:00 AM", "Knuckle Up vs Get a Whiff of This", "Step Above vs Flamingos", "Cloud Seeders vs Sandvipers"],
        ["R3 — 12:00 PM", "Marauders vs Flamingos", "Savages vs Cloud Seeders", "Wiffle Sh*ts vs Get a Whiff of This"],
        ["R4 — 1:00 PM", "Step Above vs Balls Deep", "WIZARDS vs Sandvipers", "Blitz vs Knuckle Up"],
        ["R5 — 2:00 PM", "Savages vs Sandvipers", "Wiffle Sh*ts vs Knuckle Up", "Marauders vs Step Above"],
        ["R6 — 3:00 PM", "Cloud Seeders vs WIZARDS", "Blitz vs Get a Whiff of This", "Flamingos vs Balls Deep"],
    ]
    # Custom highlight for cells containing WIZARDS
    head = [Paragraph(h, ParagraphStyle("th2", fontName="Helvetica-Bold", fontSize=7.5, textColor=WHITE, leading=9, alignment=TA_CENTER))
            for h in ["Round / Time", "Main Turf Field", "Grass Field 1", "Grass Field 2"]]
    body = []
    wiz_cells = set()
    for ri, row in enumerate(full):
        cells = []
        for ci, cell in enumerate(row):
            is_wiz = "WIZARDS" in cell
            if is_wiz:
                wiz_cells.add((ci, ri + 1))
            cells.append(Paragraph(cell, ParagraphStyle(
                f"f{ri}{ci}",
                fontName="Helvetica-Bold" if is_wiz else "Helvetica",
                fontSize=7.2,
                textColor=PURPLE if is_wiz else DARK,
                leading=9,
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
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    for c, r in wiz_cells:
        cmds.append(("BACKGROUND", (c, r), (c, r), HIGHLIGHT))
    sched.setStyle(TableStyle(cmds))
    story.append(sched)

    # ===== FORMAT =====
    story.append(Spacer(1, 10))
    story.append(section_bar("4. FORMAT, TIEBREAKERS & PLAYOFFS", styles))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "3 pools of 4. Each pool winner advances. The 4th playoff spot is a <b>Wildcard</b> via Swing-Off Challenge. "
        "Any team with <b>at least 1 win</b> in pool play is eligible. Playoffs are single elimination (4 teams).",
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
        "UNDERDOG PATH: Steal 1 pool win (Wildcard eligibility) + keep runs allowed low (tiebreakers / Swing-Off odds).",
        styles,
    ))

    # ===== RULES ESSENTIALS =====
    story.append(PageBreak())
    story.append(section_bar("5. RULES THAT WIN (AND LOSE) GAMES", styles))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Condensed from PLW Basic Rules + Official Season 6 Rule Book. Know these cold.",
        styles["body"],
    ))

    story.append(Paragraph("Hitting & outcomes (no baserunning except tag-ups)", styles["h2"]))
    story.extend(bullets([
        "Every at-bat starts <b>0–1</b> (one strike already).",
        "<b>Single:</b> grounder through infield played by OF, or fly that lands in OF (not wall / not out of play).",
        "<b>Double:</b> ball that bounces before hitting the back wall.",
        "<b>Triple:</b> fly ball that hits the back wall in the air.",
        "<b>HR:</b> fly ball clears the back wall in the air.",
        "Cheap/front foul line between 1B and 3B — behind it (toward plate) is foul.",
    ], styles["bullet"]))

    story.append(Paragraph("Pitching (huge leverage for underdogs) — Rules 3.05–3.09", styles["h2"]))
    story.extend(bullets([
        "Any speed allowed — but a <b>called strike</b> must read <b>≤55 mph</b> on radar AND hit the K-zone in the air.",
        "Back foot stays on rubber until release; front foot must land on pitching mat. No pump fakes / fluid delivery only.",
        "Illegal pitch progression <b>(3.05, per pitcher per series)</b>: 1st = warning/no-pitch → 2nd = automatic ball → additional = automatic walk (counts toward walk total).",
        "HBP = ball (unless hands-on-bat, or face ≥65 mph). HBP counts toward walk total.",
        "<b>3.06 — Walk 2 batters → pitcher is ineligible for the rest of that game.</b> The <b>last eligible pitcher</b> on a team has <b>no walk limit</b>.",
        "<b>3.07 — In a 3-game series, a different pitcher must start each game.</b> Plan 3 starters (you have 3 pool games).",
        "<b>3.08 — In a 3-game series, a pitcher may appear (throw a pitch) in up to 9 innings total.</b> A pitch in a 10th inning: all outs become walks; if the inning completes → forfeit.",
        "<b>3.09 — Exception:</b> if a pitcher starts a game with 0 IP and throws every pitch in that game, they may continue past the 9th until they walk 2 batters.",
        "Pitchers must face ≥3 batters (or finish inning) when entering — MLB-style appendix rule.",
        "No white/gray/distracting sleeves for pitchers. No quick-pitch (auto ball).",
    ], styles["bullet"]))

    story.append(Paragraph("Fielding / 5-second outs (practice this)", styles["h2"]))
    story.extend(bullets([
        "No gloves — bare hands only.",
        "Force out at 1B/home: throw ball into backstop / K-zone / batter <b>in the air</b> within <b>5 seconds</b> of contact.",
        "Can tag 2B/3B within 5 seconds for force outs when applicable.",
        "Holding runners on singles: throw to 3B (&lt;5s) holds at 2B; throw to backstop in air (&lt;5s) holds at 3B.",
        "Infield ball with no out recorded → runners +1 base, batter to 1B.",
        "Fielders may not be closer to the plate than the pitcher.",
    ], styles["bullet"]))

    story.append(Paragraph("Tag-up / sac fly (the only real baserunning)", styles["h2"]))
    story.extend(bullets([
        "With &lt;2 outs, runner on 3rd may tag up after a caught fly and run home.",
        "Out if ball hits backstop / K-zone / runner before they touch home (throw may bounce).",
        "18-ft commit line on 3B line — touch/cross it and you cannot return to 3B.",
        "Cannot cross commit line after pitcher has the ball on the mat.",
    ], styles["bullet"]))

    story.append(Paragraph("Game structure & equipment", styles["h2"]))
    story.extend(bullets([
        "Games are 6 innings. Extras: runner placed on 2B to start.",
        "Mercy: 10-run lead after 3 complete innings; also ends when a team scores their 15th and leads by ≥2.",
        "Min 6 players; up to 12 on roster. 6 fielders incl. pitcher; lineup 6–12 batters.",
        "Only official original yellow Wiffle bats. Tape: max 12\" barrel section; both ends uncovered; barrel fits 2\" Sch.40 PVC.",
        "Game balls: new/like-new official Wiffle balls — remove deformed/dirty/scuffed balls.",
        "K-zone: 24\" × 28.5\", stands 10\" off ground. Mound ~43.5' to zone. Lines ~90–105', CF ~115–125'.",
    ], styles["bullet"]))

    # ===== CONDUCT =====
    story.append(Spacer(1, 8))
    story.append(section_bar("6. CODE OF CONDUCT (DON'T GET TOSSED)", styles))
    story.append(Spacer(1, 6))
    story.extend(bullets([
        "Respect players, umpires, staff, fans, and the ranch property. Clean dugouts.",
        "Only managers speak to umps about calls.",
        "Stay in dugout unless on deck / batting / on defense (HR celebration exception).",
        "No taunting, personal insults, or profanity; zero tolerance for racism, violence, weapons.",
        "Don't throw bats in anger. Handle gear safely.",
        "Motto: <b>Play Hard. Have Fun. Respect All.</b>",
    ], styles["bullet"]))

    # ===== STRATEGY =====
    story.append(Spacer(1, 10))
    story.append(section_bar("7. UNDERDOG TIPS & TRICKS — STEAL GAMES FROM BETTER TEAMS", styles))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "You're probably the least experienced team — that's fine. PLW rules create specific leverage points. "
        "Use them. Goal: <b>1 quality win</b>, low runs allowed, and stay alive for Wildcard / Pool C chaos.",
        styles["body"],
    ))

    story.append(Paragraph("A. Pitching game plan (your #1 equalizer)", styles["h2"]))
    story.extend(bullets([
        "<b>Live under 55 mph with movement.</b> Called strikes only count ≤55 into the K-zone. Practice a repeatable under-55 strike and a harder “looks like a strike” ball that charts over 55 (reads as ball even if it hits the zone).",
        "<b>Attack the zone early.</b> Batters start 0–1. Get ahead; make them chase. Don't nibble yourself into walks.",
        "<b>Protect your 2-walk limit (3.06).</b> Two free passes = that pitcher is scratched for the game. Near walk #2: challenge the zone. Pre-assign your emergency <b>last eligible pitcher</b> (no walk limit) before first pitch.",
        "<b>Footwork legality.</b> Back foot on rubber, front foot on mat. Illegal pitches escalate to free bases — don't gift better teams walks.",
        "<b>Mix locations / speeds / spin.</b> Experienced hitters crush predictable yellow-ball heaters. Change eye levels and timing every at-bat.",
        "<b>Use intentional walks wisely</b> (no pitches required). Walk the middle-of-order killer to face a weaker bat — but remember walks count and can burn your pitcher.",
    ], styles["bullet"]))

    story.append(Paragraph("B. Defense & runs-allowed obsession", styles["h2"]))
    story.extend(bullets([
        "<b>Fewest runs allowed is tiebreaker #2</b> (after H2H). Even a 1–0 or 2–1 loss helps more than a 12–10 “fun” slugfest if you're fighting for pool rank / strength of schedule optics into Swing-Off.",
        "<b>Drill the 5-second throw to the backstop/K-zone.</b> Most outs are “throw it home in the air, fast.” Practice scoop → throw accuracy barehanded. Missed 5-second windows = free singles.",
        "<b>Hold runners.</b> On singles, a clean &lt;5s throw to 3B or backstop stops traffic. Experienced teams advance aggressively if you panic.",
        "<b>Positioning:</b> no one closer than the pitcher. Shade pull-side for dead-pull hitters; protect the cheap line (short foul in front of the bases).",
        "<b>Communication:</b> call flies early. Collisions / drops with no gloves are free outs for the other team.",
        "<b>Avoid mercy.</b> Don't quit after 3 — keep competing for runs allowed and pride, but also don't gift 15-run mercies that inflate their stats and crush yours.",
    ], styles["bullet"]))

    story.append(Paragraph("C. Offense against better pitching", styles["h2"]))
    story.extend(bullets([
        "<b>Hunt walks to burn their ace (Rule 3.06).</b> Two walks and their best pitcher is DONE for the game. Be patient — take borderline pitches. HBP counts as a walk toward their limit. Force them onto a worse arm; that is how underdogs steal games.",
        "<b>Track their pitcher usage across the day (3.07–3.09).</b> Different starter each game; 9-inning appearance cap in a 3-game series. If their stud already ate innings, attack the backup later.",
        "<b>Start every AB down 0–1 — shorten up.</b> Put the ball in play. Whiffing looking for a perfect pitch plays into good pitchers.",
        "<b>Aim for doubles/triples geometry.</b> Balls that bounce before the wall = doubles; air to the wall = triples. Line drives into gaps beat pop-ups to short OF.",
        "<b>Don't gift outs on the cheap line.</b> Choppers that die in front of the bases are outs/fouls — swing with intent to get it past the infield line.",
        "<b>Two-strike approach:</b> foul tips into the K-zone twice with 2 strikes = K. Protect; soft contact over hero swings.",
        "<b>Tag-up IQ:</b> with &lt;2 outs and a runner on 3rd, a medium fly can score if you commit correctly. Practice the commit line — hesitate and die; overcommit and get doubled off.",
        "<b>Lineup length:</b> you can bat 6–12 and add to the bottom, never shorten. Put your best contact guys where they see the most ABs; hide weaker hitters if needed.",
    ], styles["bullet"]))

    story.append(Paragraph("D. Tournament math & mind games", styles["h2"]))
    story.extend(bullets([
        "<b>Get 1 win at all costs.</b> Wildcard requires ≥1 pool win + Swing-Off. A 1–2 record with a gutsy win beats 0–3 every time.",
        "<b>Target the winnable game.</b> Scout R2/R3/R5 Pool C games. Identify who looks beatable. Peak your best pitcher for that matchup (likely Sandvipers at 1 PM or whoever looks shaky).",
        "<b>Opening game vs Savages (10 AM):</b> set the tone with clean defense and strike-throwing. Even a close loss with low RA helps tiebreakers.",
        "<b>Swing-Off prep:</b> if you're 1–2, treat Swing-Off like Game 7. Know the challenge format from PLW (practice timed swings / accuracy if that's the event style) and stay loose after Round 6.",
        "<b>Energy management:</b> Florida August heat. Shade, water, electrolytes between rounds. Fresh arms & hands beat talent that cramps in Round 6.",
        "<b>Uniforms:</b> photographer prioritizes polished-looking teams. Matching purple/gold kits won't win innings — but they help morale and photos if you make a run.",
    ], styles["bullet"]))

    story.append(Paragraph("E. Small-rules edges most casual teams miss", styles["h2"]))
    story.extend(bullets([
        "Force opponents into illegal-pitch / foot faults with a patient eye — free balls add up.",
        "Know when a ball that hits fence on bounce = everyone scores / batter to 2B (special cases for runner from 1st). Don't stop running the placeholders mentally.",
        "If defense holds the ball against the fence, extra bases are NOT awarded — keep pressure only when the ball is truly past them.",
        "Only managers argue. Keep the dugout calm so umps don't tilt against the “new” team.",
        "Legal bat tape only. An illegal bat = automatic out. Check PVC ring rule before first pitch.",
        "Wild pitch out of play advances runners 1 base — be ready; don't sleep on WP/HBP sequences.",
    ], styles["bullet"]))

    story.append(Spacer(1, 6))
    story.append(gold_callout(
        "SIMPLE SCRIPT: Throw strikes under 55 • Catch + hit the K-zone in 5 seconds • Scratch 1 win • Keep RA low • Survive to Swing-Off.",
        styles,
    ))

    # ===== CHECKLIST =====
    story.append(Spacer(1, 10))
    story.append(section_bar("8. GAME-DAY CHECKLIST", styles))
    story.append(Spacer(1, 6))
    cols = Table(
        [[
            Paragraph(
                "<b>Gear</b><br/>• Official yellow Wiffle bats (taped legal)<br/>"
                "• Extra official Wiffle balls if allowed/needed<br/>"
                "• Turf shoes / sneakers (no cleats)<br/>"
                "• Matching jerseys / team shirts<br/>"
                "• Catching practice ball for barehand warmups",
                styles["tip"],
            ),
            Paragraph(
                "<b>Body & camp</b><br/>• Lots of water + electrolytes<br/>"
                "• Snacks / lunch for a full day<br/>"
                "• Chairs + canopy/shade<br/>"
                "• Sunscreen, towels, change of shirt<br/>"
                "• Arrive by ~9:00–9:15 for gates/check-in",
                styles["tip"],
            ),
        ]],
        colWidths=[3.5 * inch, 3.5 * inch],
    )
    cols.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), LIGHT_PURPLE),
        ("BOX", (0, 0), (-1, -1), 1, GOLD),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(cols)

    story.append(Spacer(1, 10))
    story.append(section_bar("9. LINKS", styles))
    story.append(Spacer(1, 6))
    story.extend(bullets([
        "Tournament page: https://premierleaguewiffle.com/2026/07/01/august-1st-tourney-sign-ups-open/",
        "Basic rules: https://premierleaguewiffle.com/basic-rules/",
        "Full rule book: https://premierleaguewiffle.com/rules/",
        "Code of conduct: https://premierleaguewiffle.com/player-code-of-conduct/",
    ], styles["bullet"]))

    story.append(Spacer(1, 14))
    story.append(Paragraph(
        "Go get a win, Wizards. Cast some outs. Steal a Wildcard.",
        ParagraphStyle("end", fontName="Helvetica-Bold", fontSize=12, textColor=PURPLE, alignment=TA_CENTER, spaceBefore=6),
    ))
    story.append(Paragraph(
        "Compiled for team use from official PLW pages + provided schedule/pool sheets. Rules subject to on-site umpires / PLW updates.",
        styles["small"],
    ))

    doc.build(story, onFirstPage=add_page_decor, onLaterPages=add_page_decor)
    print(f"Wrote {OUT} ({OUT.stat().st_size} bytes)")
    return OUT


if __name__ == "__main__":
    build()
