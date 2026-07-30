"""Official PLW Season 6 rule digests for the tournament packet PDF."""

# Every numbered rule from https://premierleaguewiffle.com/rules/ plus hit-result cheat sheet.

HIT_RESULTS = [
    "<b>Hit-result cheat sheet</b> (how hits are scored — placeholders, not live baserunning):",
    "<b>Single:</b> grounder through infield played by OF, or fly that lands in OF (not wall / not out of play).",
    "<b>Double:</b> ball that bounces before hitting the back wall/fence.",
    "<b>Triple:</b> fly ball that hits the back wall/fence in the air.",
    "<b>HR:</b> fly ball clears the back wall/fence in the air (foul pole above fence = HR).",
]

GENERAL = [
    "<b>1.01</b> Max 12 players on roster.",
    "<b>1.02</b> 6 fielders including pitcher; lineup bats 6–12.",
    "<b>1.03</b> Up to 6 designated hitters. Batters may be added to the bottom of the lineup; lineup can never be shortened.",
    "<b>1.04</b> Fielders may sub freely (even if removed from lineup). A batter removed from the lineup may not hit or pinch-run the rest of the game.",
    "<b>1.05</b> No pitching/defensive changes mid at-bat except injury forcing a player out.",
    "<b>1.06</b> No gloves — bare hands only. Bandages/casts for injury OK.",
]

GAME_STRUCTURE = [
    "<b>2.01</b> Games are 6 innings. Extras until a winner; runner placed on 2B to start extras.",
    "<b>2.02</b> New/like-new official Wiffle® balls only. Remove deformed, dirty, or scuffed balls.",
    "<b>2.03</b> Official original yellow Wiffle® bats only. Tape OK on a max 12\" barrel section; both ends uncovered. Stickers OK if not overlapping. Barrel must fit a 2\" Sch.40 PVC tee.",
    "<b>2.04</b> 10-run mercy after 3 complete innings.",
    "<b>2.05</b> Game ends in mercy when a team scores their 15th+ run and leads by ≥2 (even if away).",
    "<b>2.06</b> Walk-off multi-run hit: all runners advance; batter credited with the hit result (e.g. walk-off bases-loaded double in 0–0 = 3–0).",
]

GAMEPLAY = [
    "<b>3.01</b> Every at-bat starts <b>0–1</b>.",
    "<b>3.02</b> Called strike: ≤55 mph on PocketRadar™ AND hits K-zone in the air. No radar read in a called-strike situation = “no-pitch,” unless umps agree clearly &lt;50 (strike) or &gt;60 (ball).",
    "<b>3.03</b> HBP = ball, unless face + ≥65 mph, or hands while holding the bat (hands = part of bat). HBP counts toward pitcher’s walk total.",
    "<b>3.04</b> Batter must try to avoid HBP. If batter interferes with a pitch that may have been a ≤55 K-zone strike, pitcher may appeal → strike or no-pitch at umpire discretion.",
    "<b>3.05</b> No balks, but delivery must be fluid (no pump fakes). Illegal if: (a) back/pivot foot leaves rubber before release (no hop/jump/lunge/slide), or (b) entire front foot lands off the pitching mat. Per pitcher/series: 1st = warn/no-pitch; 2nd = auto ball; more = auto walk (counts toward walks).",
    "<b>3.06</b> Walk 2 batters → pitcher ineligible rest of game. <b>Last eligible pitcher has no walk limit.</b>",
    "<b>3.07</b> In a 3-game series, a different pitcher must start each game.",
    "<b>3.08</b> In a 3-game series, a pitcher may appear (throw a pitch) in up to 9 innings. Pitch in a 10th inning: outs become walks; if inning completes → forfeit.",
    "<b>3.09</b> If a pitcher starts with 0 IP and throws every pitch in that game, they may continue past the 9th until they walk 2.",
    "<b>3.10</b> Foul tip into K-zone twice with 2 strikes = strikeout.",
    "<b>3.11</b> Wild pitch: out of play without touching K-zone, backstop, or batter. Over top of backstop = out of play; sides of backstop are NOT. Runners +1 base (no extra base if ball 4).",
    "<b>3.12</b> Bat hitting K-zone on swing/check-swing = swing; ball put in play stays live.",
    "<b>3.13</b> Front foul / “cheap line” between 1B and 3B lines — behind it (toward plate) is foul.",
    "<b>3.14</b> Pylons one ball-length off 1B/3B for fair/foul. Ball hitting pylon before OF = foul. Fielder deflection into pylon = live.",
    "<b>3.15</b> No intentionally using feet to stop the ball (except sliding in OF). Pitcher may foot-deflect a ball directly back to themselves.",
    "<b>3.16</b> Runners are placeholders except tag-up from 3B. Stand within 10 ft of base; avoid fielders. Interference → batter out, no advances.",
    "<b>3.17</b> Fielders may not be closer to home than the pitcher.",
    "<b>3.18</b> Batter must start in the box; may step out while swinging.",
]

FIELDING = [
    "<b>4.01</b> Force at 1B/home: hit backstop or K-zone with ball <b>in the air</b> within <b>5 seconds</b> of contact. Batter in front of backstop = part of K-zone. Bottom pole of K-zone / balls near backstop = ground. Ball rolls behind batting mat → dead; no further outs.",
    "<b>4.02</b> Tag 2B/3B within 5 seconds for force outs when applicable. Bases loaded, 0 outs: DP throw that hits K-zone gets runner at home (tag play). Fielders may not run toward the backstop with the ball.",
    "<b>4.03</b> Forced runners +1 base on a ground out. Unforced runners hold unless a DP is attempted.",
    "<b>4.04</b> Ball stays in infield with no outs recorded → runners +1, batter to 1B.",
    "<b>4.05</b> Fair ball bounces out of play before OF fence, untouched → no further outs; runners +2; batter to 1B.",
    "<b>4.06</b> Fair ball out of play without hitting K-zone/backstop/batter → runners +2; batter to 2B. No extra bases for throw OOP if no play left.",
    "<b>4.07</b> Fair ball hits ground then fence → all runners score; batter to 2B (except GRD case: runner from 1B holds at 3B).",
    "<b>4.08</b> Ball hits fence in the air → all runners score; batter to 3B.",
    "<b>4.09</b> Ball over fence in the air → all runners + batter score (HR).",
    "<b>4.10</b> Fielder holding ball against fence/OF grass → no extra bases awarded; ball still live.",
    "<b>4.11</b> Tag-up from 3B after fly out: if runner crosses commit line, fielder may hit backstop/K-zone/runner before home for DP (need not be in air). No crossing commit line after pitcher has ball on mat.",
    "<b>4.12</b> On tag-up, throw/deflection OOP without hitting K-zone/backstop/batter/runner → runners +1.",
    "<b>4.13 Holding runners:</b> throw to 3B &lt;5s → runner stops at 2B; throw to backstop in air &lt;5s → runner stops at 3B. With 1st+2nd: backstop hold keeps both at 2B &amp; 3B; throw to 3B only holds the trail at 2B (lead from 2B still scores).",
]

APPENDIX = [
    "Unlisted situations → 2021 MLB rulebook when applicable.",
    "Pitchers must face ≥3 batters or finish the inning when entering.",
    "Intentional walk: no pitches required.",
    "Fair/foul behind the bases = where the ball lands. If fielder touches before fair/foul determined, rule by ball location at contact (any fraction on/above foul line = fair).",
    "No white/gray/distracting pitcher sleeves. Wait until batter is set &amp; looking — illegal quick pitch = auto ball.",
    "All fielders on the ground in fair territory. No intentionally distracting the batter.",
    "To record an out, secure the ball before any body part touches ground/structure that is out of play.",
    "Batting team must vacate space for fielders. Interfere with a batted ball that could roll fair → batter out, no advances. Wait for fouls to stop or hit foul territory before picking up.",
    "Batting out of order: during AB → correct batter assumes count. After AB → proper batter out, next up. If wrong batter becomes runner/out and a pitch is thrown before appeal → result stands.",
    "No legal sub for exited player → out every time that lineup spot comes up.",
    "Deliberately touching fair ball with detached cap/jersey/uniform → batter + all runners awarded 3 bases.",
    "Runner hit by fair batted ball before fielder touch → runner out; batter awarded single; others advance only if forced.",
    "Batter may switch boxes once per AB, not after pitcher starts motion.",
    "Illegal bat → batter out; no advances; outs on the play stand.",
    "No switching pitching hands mid-AB. Injury switch → may not use injured hand rest of series; no warm-ups.",
    "Bounce over fence/OOP = ground-rule double (all +2 bases). Foul tip must be sharp &amp; direct. Pitcher may only have 1 ball. 3 strikes / 4 balls. Catch before ground/backstop/K-zone/fence/chair = out. 3 outs per half-inning.",
]

FIELD = [
    "Home → 1B/3B: 50 ft. Home → 2B: 55 ft.",
    "Pitcher’s mound → K-zone: 43.5 ft. Infield line: 5 ft behind the bases.",
    "LF/RF: 90–105 down the lines; CF: 115–125.",
    "Backstop: 10 ft wide × 8 ft tall. K-zone (basic rules): 24\" × 28.5\", stands 10\" off ground.",
]

SECTIONS = [
    ("Hit results (quick reference)", HIT_RESULTS),
    ("1.00 General", GENERAL),
    ("2.00 Game structure", GAME_STRUCTURE),
    ("3.00 Gameplay", GAMEPLAY),
    ("4.00 Fielding / advancing runners", FIELDING),
    ("Appendix — MLB rules that apply", APPENDIX),
    ("The PLW field", FIELD),
]
