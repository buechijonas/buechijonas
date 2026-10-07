"""Generate assets/timeline-{light,dark}.svg. Edit ENTRIES and rerun: python3 scripts/build-timeline.py"""

import base64
import textwrap
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ENTRIES = [
    {
        "title": "Jr. Software Engineer",
        "country": "ch",
        "company": "histify AG",
        "handle": "@histifyAG",
        "period": "2025 – Present",
        "logo": "histify.jpg",
        "current": True,
        "text": "Fullstack software development (oikos, agora, charon & chronos) with a gradual expansion of responsibilities into the DevOps area (Official position: Jr. DevOps Engineer).",
    },
    {
        "title": "Computer Scientist VET",
        "country": "ch",
        "company": "histify AG",
        "handle": "@histifyAG",
        "period": "2024 – 2025",
        "logo": "histify.jpg",
        "text": "Fullstack software development since the company’s founding (oikos, agora & charon).",
    },
    {
        "title": "Computer Scientist VET",
        "country": "ch",
        "company": "Fabasoft 4teamwork AG",
        "handle": "@4teamwork",
        "period": "2022 – 2024",
        "logo": "4teamwork.jpg",
        "text": "Frontend development of OneGov GEVER for public authorities & governments, later working as a Fullstack Software Developer in the GLAM sector.",
    },
    {
        "title": "Computer Scientist VET",
        "country": "ch",
        "company": "Berufsbildungscenter AG",
        "handle": "@BbcAG",
        "period": "2021 – 2022",
        "logo": "bbc.jpg",
        "text": "Completed the basic apprenticeship year, including all inter-company courses (üK) and individual projects for basic IT training.",
    },
]

THEMES = {
    "light": {"bg": "#ffffff", "border": "#e5e7eb", "title": "#111827", "muted": "#6b7280", "text": "#4b5563", "accent": "#dc2626"},
    "dark": {"bg": "#161b22", "border": "#30363d", "title": "#f0f6fc", "muted": "#8b949e", "text": "#9ca3af", "accent": "#ef4444"},
}

FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
WIDTH = 820
LINE_X = 40
LOGO_X = 68
TEXT_X = 124
PAD_TOP = 28
LINE_HEIGHT = 19
WRAP = 100
GAP = 30
CURRENT = "#22c55e"
FLAG_SIZE = 12


def flag_ch(x, y, s=FLAG_SIZE):
    bar, arm = s * 6 / 32, s * 20 / 32
    return (
        f'<rect x="{x}" y="{y}" width="{s}" height="{s}" rx="2" fill="#da291c"/>'
        f'<rect x="{x + (s - bar) / 2}" y="{y + (s - arm) / 2}" width="{bar}" height="{arm}" fill="#fff"/>'
        f'<rect x="{x + (s - arm) / 2}" y="{y + (s - bar) / 2}" width="{arm}" height="{bar}" fill="#fff"/>'
    )


FLAGS = {"ch": flag_ch}


def logo_uri(name):
    data = base64.b64encode((ROOT / "assets" / "logos" / name).read_bytes()).decode()
    return f"data:image/jpeg;base64,{data}"


def build(theme):
    c = THEMES[theme]
    body, dots = [], []
    y = PAD_TOP
    for i, e in enumerate(ENTRIES):
        lines = textwrap.wrap(e["text"], WRAP)
        dot_y = y + 14
        if e.get("current"):
            dots.append(f'<circle cx="{LINE_X}" cy="{dot_y}" r="9" fill="{CURRENT}" fill-opacity="0.2"/>')
            dots.append(f'<circle cx="{LINE_X}" cy="{dot_y}" r="5" fill="{CURRENT}"/>')
        else:
            dots.append(f'<circle cx="{LINE_X}" cy="{dot_y}" r="5" fill="{c["bg"]}" stroke="{c["muted"]}" stroke-width="2"/>')
        body.append(
            f'<clipPath id="logo{i}"><rect x="{LOGO_X}" y="{y}" width="40" height="40" rx="8"/></clipPath>'
            f'<image href="{logo_uri(e["logo"])}" x="{LOGO_X}" y="{y}" width="40" height="40" clip-path="url(#logo{i})"/>'
            f'<rect x="{LOGO_X + 0.5}" y="{y + 0.5}" width="39" height="39" rx="8" fill="none" stroke="{c["border"]}"/>'
        )
        body.append(f'<text x="{TEXT_X}" y="{y + 15}" font-size="15" font-weight="600" fill="{c["title"]}">{escape(e["title"])}</text>')
        period_fill = CURRENT if e.get("current") else c["muted"]
        handle = f'<tspan dx="6" fill="{c["title"]}">{escape(e["handle"])}</tspan>' if e.get("handle") else ""
        body.append(
            FLAGS[e["country"]](TEXT_X, y + 25) +
            f'<text x="{TEXT_X + FLAG_SIZE + 6}" y="{y + 35}" font-size="12" fill="{c["muted"]}">{escape(e["company"])}{handle}'
            f'<tspan dx="8" fill="{c["border"]}">·</tspan><tspan dx="8" fill="{period_fill}">{escape(e["period"])}</tspan></text>'
        )
        for j, line in enumerate(lines):
            body.append(f'<text x="{TEXT_X}" y="{y + 60 + j * LINE_HEIGHT}" font-size="13.5" fill="{c["text"]}">{escape(line)}</text>')
        if i == 0:
            first_dot = dot_y
        last_dot = dot_y
        y += 60 + (len(lines) - 1) * LINE_HEIGHT + GAP
    height = y - GAP + PAD_TOP - 6
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" viewBox="0 0 {WIDTH} {height}" role="img" aria-label="Timeline" font-family="{FONT}">',
        f'  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1}" rx="14" fill="{c["bg"]}" stroke="{c["border"]}"/>',
        f'  <line x1="{LINE_X}" y1="{first_dot}" x2="{LINE_X}" y2="{last_dot}" stroke="{c["border"]}" stroke-width="2"/>',
        *(f"  {d}" for d in dots),
        *(f"  {b}" for b in body),
        "</svg>",
        "",
    ])


for theme in THEMES:
    (ROOT / "assets" / f"timeline-{theme}.svg").write_text(build(theme))
