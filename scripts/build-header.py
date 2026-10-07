"""Generate assets/header-{light,dark}.svg. Edit NAME/SUBTITLE and rerun: python3 scripts/build-header.py"""

import base64
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

NAME = "Jonas S. Büchi"
SUBTITLE = "Fullstack Software Engineer · Bern, Switzerland"

THEMES = {
    "light": {"bg": "#ffffff", "border": "#e5e7eb", "title": "#111827", "muted": "#6b7280", "accent": "#dc2626"},
    "dark": {"bg": "#161b22", "border": "#30363d", "title": "#f0f6fc", "muted": "#8b949e", "accent": "#ef4444"},
}

FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
WIDTH = 820
HEIGHT = 168
CX = WIDTH / 2
ARMS_H = 26
ARMS_W = ARMS_H * 406.505 / 492.818


def arms_uri():
    data = base64.b64encode((ROOT / "assets" / "logos" / "bern.svg").read_bytes()).decode()
    return f"data:image/svg+xml;base64,{data}"


def build(theme):
    c = THEMES[theme]
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="{escape(NAME)} — {escape(SUBTITLE)}" font-family="{FONT}">',
        f'  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{HEIGHT - 1}" rx="14" fill="{c["bg"]}" stroke="{c["border"]}"/>',
        f'  <text x="{CX}" y="72" text-anchor="middle" font-size="34" font-weight="700" letter-spacing="-0.5" fill="{c["title"]}">{escape(NAME)}</text>',
        f'  <rect x="{CX - ARMS_W / 2 - 46}" y="99.5" width="34" height="3" rx="1.5" fill="{c["accent"]}"/>',
        f'  <image href="{arms_uri()}" x="{CX - ARMS_W / 2}" y="88" width="{ARMS_W}" height="{ARMS_H}"/>',
        f'  <rect x="{CX + ARMS_W / 2 + 12}" y="99.5" width="34" height="3" rx="1.5" fill="{c["accent"]}"/>',
        f'  <text x="{CX}" y="136" text-anchor="middle" font-size="14" fill="{c["muted"]}">{escape(SUBTITLE)}</text>',
        "</svg>",
        "",
    ])


for theme in THEMES:
    (ROOT / "assets" / f"header-{theme}.svg").write_text(build(theme))
