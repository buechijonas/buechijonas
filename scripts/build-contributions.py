"""Generate assets/contributions-{light,dark}.svg from the GitHub contribution calendar.
Needs the gh CLI (authenticated, or GH_TOKEN set): python3 scripts/build-contributions.py"""

import json
import subprocess
from datetime import date
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
USER = "buechijonas"

QUERY = """
query($login: String!) {
  user(login: $login) {
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount contributionLevel } }
      }
    }
  }
}
"""

LEVELS = ["NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"]

THEMES = {
    "light": {
        "bg": "#ffffff", "border": "#e5e7eb", "title": "#111827", "muted": "#6b7280",
        "levels": ["#f3f4f6", "#fecaca", "#f87171", "#dc2626", "#991b1b"],
    },
    "dark": {
        "bg": "#161b22", "border": "#30363d", "title": "#f0f6fc", "muted": "#8b949e",
        "levels": ["#21262d", "#5f1d1d", "#991b1b", "#dc2626", "#f87171"],
    },
}

FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
WIDTH = 820
PAD = 24
CELL = 11
GAP = 3
STEP = CELL + GAP
GRID_X = PAD + 30
GRID_Y = 92
MONTHS = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()


def fetch():
    out = subprocess.run(
        ["gh", "api", "graphql", "-f", f"query={QUERY}", "-f", f"login={USER}"],
        check=True, capture_output=True, text=True,
    ).stdout
    return json.loads(out)["data"]["user"]["contributionsCollection"]["contributionCalendar"]


def streaks(days):
    longest = run = 0
    for d in days:
        run = run + 1 if d["contributionCount"] else 0
        longest = max(longest, run)
    # Today without contributions yet shouldn't break the current streak.
    current = 0
    for i, d in enumerate(reversed(days)):
        if d["contributionCount"]:
            current += 1
        elif i > 0:
            break
    return current, longest


def build(theme, cal):
    c = THEMES[theme]
    weeks = cal["weeks"]
    days = [d for w in weeks for d in w["contributionDays"]]
    current, longest = streaks(days)
    out = []

    out.append(f'<text x="{PAD}" y="{PAD + 12}" font-size="11" font-weight="600" letter-spacing="0.8" fill="{c["muted"]}">GITHUB CONTRIBUTIONS</text>')
    out.append(
        f'<text x="{PAD}" y="{PAD + 38}" font-size="19" font-weight="600" fill="{c["title"]}">{cal["totalContributions"]:,}'
        f'<tspan dx="6" font-size="13.5" font-weight="400" fill="{c["muted"]}">in the last year</tspan></text>'
    )
    stats = f"Current streak {current} {'day' if current == 1 else 'days'}<tspan dx='10' fill='{c['border']}'>|</tspan><tspan dx='10'>Longest streak {longest} days</tspan>"
    out.append(f'<text x="{WIDTH - PAD}" y="{PAD + 38}" text-anchor="end" font-size="12" fill="{c["muted"]}">{stats}</text>')

    last_month = None
    for wi, w in enumerate(weeks):
        first = date.fromisoformat(w["contributionDays"][0]["date"])
        if first.month != last_month and wi < len(weeks) - 2:
            if last_month is not None or first.day <= 7:
                out.append(f'<text x="{GRID_X + wi * STEP}" y="{GRID_Y - 8}" font-size="10.5" fill="{c["muted"]}">{MONTHS[first.month - 1]}</text>')
            last_month = first.month
        for d in w["contributionDays"]:
            wd = (date.fromisoformat(d["date"]).weekday() + 1) % 7  # Sunday = 0, like GitHub
            n = d["contributionCount"]
            title = f'{n} contribution{"" if n == 1 else "s"} on {d["date"]}'
            out.append(
                f'<rect x="{GRID_X + wi * STEP}" y="{GRID_Y + wd * STEP}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{c["levels"][LEVELS.index(d["contributionLevel"])]}"><title>{title}</title></rect>'
            )

    for wd, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        out.append(f'<text x="{PAD}" y="{GRID_Y + wd * STEP + 9}" font-size="10.5" fill="{c["muted"]}">{label}</text>')

    legend_y = GRID_Y + 7 * STEP + 14
    lx = WIDTH - PAD - 5 * STEP - 30
    out.append(f'<text x="{lx - 6}" y="{legend_y + 9}" text-anchor="end" font-size="10.5" fill="{c["muted"]}">Less</text>')
    for i, color in enumerate(c["levels"]):
        out.append(f'<rect x="{lx + i * STEP}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2.5" fill="{color}"/>')
    out.append(f'<text x="{lx + 5 * STEP + 3}" y="{legend_y + 9}" font-size="10.5" fill="{c["muted"]}">More</text>')

    height = legend_y + CELL + PAD
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" role="img" '
        f'aria-label="{cal["totalContributions"]} GitHub contributions in the last year" font-family="{FONT}">',
        f'  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="14" fill="{c["bg"]}" stroke="{c["border"]}"/>',
        *(f"  {o}" for o in out),
        "</svg>",
        "",
    ])


cal = fetch()
for theme in THEMES:
    (ROOT / "assets" / f"contributions-{theme}.svg").write_text(build(theme, cal))
