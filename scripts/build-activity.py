"""Generate assets/activity-{light,dark}.svg: contributions per weekday and commits per weekday/hour.
Needs the gh CLI (authenticated, or GH_TOKEN set): python3 scripts/build-activity.py"""

import json
import subprocess
from datetime import date, datetime, timedelta, timezone
from html import escape
from math import sqrt
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
USER = "buechijonas"
TZ = ZoneInfo("Europe/Zurich")

CALENDAR_QUERY = """
query($login: String!) {
  user(login: $login) {
    id
    contributionsCollection {
      contributionCalendar { weeks { contributionDays { date contributionCount } } }
      commitContributionsByRepository(maxRepositories: 100) { repository { name owner { login } } }
    }
  }
}
"""

HISTORY_QUERY = """
query($owner: String!, $name: String!, $author: ID!, $since: GitTimestamp!, $cursor: String) {
  repository(owner: $owner, name: $name) {
    defaultBranchRef {
      target {
        ... on Commit {
          history(first: 100, after: $cursor, since: $since, author: {id: $author}) {
            pageInfo { hasNextPage endCursor }
            nodes { authoredDate }
          }
        }
      }
    }
  }
}
"""

THEMES = {
    "light": {"bg": "#ffffff", "border": "#e5e7eb", "title": "#111827", "muted": "#6b7280", "empty": "#e5e7eb", "bar": "#fca5a5", "accent": "#dc2626"},
    "dark": {"bg": "#161b22", "border": "#30363d", "title": "#f0f6fc", "muted": "#8b949e", "empty": "#30363d", "bar": "#7f1d1d", "accent": "#ef4444"},
}

FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
WIDTH = 820
PAD = 24
BOX_PAD = 16
BOX_GAP = 16
LEFT_W = 230
RIGHT_W = WIDTH - 2 * PAD - BOX_GAP - LEFT_W
BOX_H = 222
CHART_Y = 64  # relative to box top
BAR_H = 112
ROW_STEP = 18
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
DAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def gql(query, **variables):
    args = ["gh", "api", "graphql", "-f", f"query={query}"]
    for key, value in variables.items():
        if value is not None:
            args += ["-f", f"{key}={value}"]
    return json.loads(subprocess.run(args, check=True, capture_output=True, text=True).stdout)["data"]


def fetch():
    user = gql(CALENDAR_QUERY, login=USER)["user"]
    collection = user["contributionsCollection"]
    per_weekday = [0] * 7
    for week in collection["contributionCalendar"]["weeks"]:
        for d in week["contributionDays"]:
            per_weekday[date.fromisoformat(d["date"]).weekday()] += d["contributionCount"]

    since = (datetime.now(timezone.utc) - timedelta(days=365)).strftime("%Y-%m-%dT%H:%M:%SZ")
    punch = [[0] * 24 for _ in range(7)]
    for entry in collection["commitContributionsByRepository"]:
        repo, cursor = entry["repository"], None
        while True:
            data = gql(HISTORY_QUERY, owner=repo["owner"]["login"], name=repo["name"], author=user["id"], since=since, cursor=cursor)
            ref = (data["repository"] or {}).get("defaultBranchRef")
            if not ref:
                break
            history = ref["target"]["history"]
            for node in history["nodes"]:
                t = datetime.fromisoformat(node["authoredDate"].replace("Z", "+00:00")).astimezone(TZ)
                punch[t.weekday()][t.hour] += 1
            if not history["pageInfo"]["hasNextPage"]:
                break
            cursor = history["pageInfo"]["endCursor"]
    return per_weekday, punch


def box(out, c, x, y, w, label, subtitle):
    out.append(f'<rect x="{x + 0.5}" y="{y + 0.5}" width="{w - 1}" height="{BOX_H - 1}" rx="10" fill="none" stroke="{c["border"]}"/>')
    out.append(f'<text x="{x + BOX_PAD}" y="{y + BOX_PAD + 12}" font-size="11" font-weight="600" letter-spacing="0.8" fill="{c["muted"]}">{escape(label)}</text>')
    out.append(f'<text x="{x + BOX_PAD}" y="{y + BOX_PAD + 32}" font-size="12.5" fill="{c["muted"]}">{subtitle}</text>')


def weekdays(out, c, per_weekday):
    x, y = PAD, PAD
    top = max(per_weekday) or 1
    best = per_weekday.index(max(per_weekday))
    box(out, c, x, y, LEFT_W, "WEEKDAYS", f'Most active on <tspan fill="{c["title"]}" font-weight="600">{DAY_NAMES[best]}</tspan>')
    slot = (LEFT_W - 2 * BOX_PAD) / 7
    bar_w = 18
    base = y + CHART_Y + 16 + BAR_H
    for i, n in enumerate(per_weekday):
        cx = x + BOX_PAD + slot * i + slot / 2
        h = max(2, BAR_H * n / top)
        fill = c["accent"] if i == best else c["bar"]
        out.append(f'<rect x="{cx - bar_w / 2:.1f}" y="{base - h:.1f}" width="{bar_w}" height="{h:.1f}" rx="3" fill="{fill}"><title>{n} contributions on {DAY_NAMES[i]}s</title></rect>')
        out.append(f'<text x="{cx:.1f}" y="{base - h - 5:.1f}" text-anchor="middle" font-size="10" fill="{c["muted"]}">{n}</text>')
        out.append(f'<text x="{cx:.1f}" y="{base + 16}" text-anchor="middle" font-size="10.5" fill="{c["muted"]}">{DAYS[i]}</text>')


def punch_card(out, c, punch):
    x, y = PAD + LEFT_W + BOX_GAP, PAD
    flat = [n for row in punch for n in row]
    top = max(flat) or 1
    hourly = [sum(punch[d][h] for d in range(7)) for h in range(24)]
    best = hourly.index(max(hourly))
    box(out, c, x, y, RIGHT_W, "TIME OF DAY", f'Most commits between <tspan fill="{c["title"]}" font-weight="600">{best:02d}:00 – {(best + 1) % 24:02d}:00</tspan><tspan dx="6">(Swiss time)</tspan>')
    gx = x + BOX_PAD + 30
    step = (RIGHT_W - 2 * BOX_PAD - 30) / 24
    gy = y + CHART_Y + 14
    for d in range(7):
        cy = gy + d * ROW_STEP
        out.append(f'<text x="{x + BOX_PAD}" y="{cy + 3.5}" font-size="10.5" fill="{c["muted"]}">{DAYS[d]}</text>')
        for h in range(24):
            cx = gx + h * step + step / 2
            n = punch[d][h]
            if n:
                ratio = n / top
                out.append(
                    f'<circle cx="{cx:.1f}" cy="{cy}" r="{2.5 + 5.5 * sqrt(ratio):.1f}" fill="{c["accent"]}" fill-opacity="{0.35 + 0.65 * ratio:.2f}">'
                    f'<title>{n} commit{"" if n == 1 else "s"} on {DAY_NAMES[d]}s, {h:02d}:00 – {(h + 1) % 24:02d}:00</title></circle>'
                )
            else:
                out.append(f'<circle cx="{cx:.1f}" cy="{cy}" r="1.5" fill="{c["empty"]}"/>')
    label_y = gy + 6 * ROW_STEP + 24
    for h in range(0, 24, 3):
        out.append(f'<text x="{gx + h * step + step / 2:.1f}" y="{label_y}" text-anchor="middle" font-size="10.5" fill="{c["muted"]}">{h:02d}</text>')


def build(theme, per_weekday, punch):
    c = THEMES[theme]
    out = []
    weekdays(out, c, per_weekday)
    punch_card(out, c, punch)
    height = PAD + BOX_H + PAD
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" role="img" '
        f'aria-label="GitHub activity by weekday and time of day" font-family="{FONT}">',
        f'  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="14" fill="{c["bg"]}" stroke="{c["border"]}"/>',
        *(f"  {o}" for o in out),
        "</svg>",
        "",
    ])


per_weekday, punch = fetch()
for theme in THEMES:
    (ROOT / "assets" / f"activity-{theme}.svg").write_text(build(theme, per_weekday, punch))
