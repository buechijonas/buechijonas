"""Generate assets/button-{light,dark}.svg. Edit LABEL and rerun: python3 scripts/build-button.py"""

from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

LABEL = "Mehr erfahren"

THEMES = {
    "light": {"bg": "#dc2626", "text": "#ffffff"},
    "dark": {"bg": "#ef4444", "text": "#ffffff"},
}

FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
WIDTH = 200
HEIGHT = 44
ARROW = 12
GAP = 10
FONT_SIZE = 14


def text_width(s):
    w = 0
    for ch in s:
        if ch in "ijlt.,:'| ":
            w += 0.3
        elif ch in "fr":
            w += 0.38
        elif ch in "mwMW":
            w += 0.85
        elif ch.isupper() or ch.isdigit():
            w += 0.66
        else:
            w += 0.56
    return w * FONT_SIZE


def build(theme):
    c = THEMES[theme]
    tx = (WIDTH - text_width(LABEL) - GAP - ARROW) / 2
    ax = tx + text_width(LABEL) + GAP
    ay = HEIGHT / 2
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="{escape(LABEL)}" font-family="{FONT}">',
        f'  <rect width="{WIDTH}" height="{HEIGHT}" rx="{HEIGHT / 2:.0f}" fill="{c["bg"]}"/>',
        f'  <text x="{tx:.1f}" y="{ay + 5:.1f}" font-size="{FONT_SIZE}" font-weight="600" fill="{c["text"]}">{escape(LABEL)}</text>',
        f'  <path d="M{ax:.1f} {ay} H{ax + ARROW:.1f} M{ax + ARROW - 5:.1f} {ay - 5} L{ax + ARROW:.1f} {ay} L{ax + ARROW - 5:.1f} {ay + 5}" fill="none" stroke="{c["text"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>',
        "</svg>",
        "",
    ])


for theme in THEMES:
    (ROOT / "assets" / f"button-{theme}.svg").write_text(build(theme))
