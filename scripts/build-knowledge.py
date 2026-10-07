"""Generate assets/knowledge-{light,dark}.svg. Edit ROWS and rerun: python3 scripts/build-knowledge.py"""

import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Each row is a list of clusters: (label, items[, width weight]); items are (label, icon file in assets/icons, brand color).
ROWS = [
    [
        ("Languages", [
            ("Python", "python", "#3776AB"),
            ("JavaScript", "javascript", "#F7DF1E"),
            ("HTML5", "html5", "#E34F26"),
            ("CSS3", "css3", "#1572B6"),
        ]),
        ("Frameworks & Libraries", [
            ("Django", "django", "#092E20"),
            ("Vue.js", "vuedotjs", "#4FC08D"),
            ("Vuetify", "vuetify", "#1867C0"),
            ("Tailwind CSS", "tailwindcss", "#06B6D4"),
        ], 1.25),
    ],
    [
        ("Build & Testing", [
            ("Vite", "vite", "#646CFF"),
            ("Playwright", "playwright", "#2EAD33"),
        ]),
        ("Databases", [
            ("PostgreSQL", "postgresql", "#336791"),
            ("MySQL", "mysql", "#4479A1"),
        ]),
        ("Operating Systems", [
            ("macOS", "apple", "#000000"),
            ("Linux", "linux", "#FCC624"),
        ]),
    ],
    [
        ("Infrastructure", [
            ("Docker", "docker", "#2496ED"),
            ("Kubernetes", "kubernetes", "#326CE5"),
            ("Nginx", "nginx", "#009639"),
            ("Caddy", "caddy", "#1F88C0"),
            ("Authentik", "authentik", "#FD4B2D"),
        ]),
        ("Tools", [
            ("Git", "git", "#F05032"),
            ("Jira", "jira", "#0052CC"),
            ("Confluence", "confluence", "#172B4D"),
            ("Figma", "figma", "#F24E1E"),
            ("VS Code", "vscode", "#007ACC"),
        ]),
    ],
]

THEMES = {
    "light": {"bg": "#ffffff", "border": "#e5e7eb", "chip": "#f9fafb", "title": "#111827", "muted": "#6b7280", "text": "#374151"},
    "dark": {"bg": "#161b22", "border": "#30363d", "chip": "#0d1117", "title": "#f0f6fc", "muted": "#8b949e", "text": "#c9d1d9"},
}

FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"
WIDTH = 820
PAD = 24
COL_GAP = 16
ROW_GAP = 16
BOX_PAD = 14
LABEL_H = 30
CHIP_H = 28
CHIP_GAP = 6
ICON = 14
FONT_SIZE = 12.5


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


def icon_path(name):
    return re.search(r' d="([^"]+)"', (ROOT / "assets" / "icons" / f"{name}.svg").read_text()).group(1)


def luminance(hex_color):
    r, g, b = (int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def icon_color(hex_color, theme, c):
    # Keep brand colors readable: near-black icons vanish on dark, bright yellow ones on white.
    lum = luminance(hex_color)
    if theme == "dark" and lum < 0.25:
        return c["title"]
    if theme == "light" and lum > 0.7:
        r, g, b = (int(int(hex_color[i:i + 2], 16) * 0.8) for i in (1, 3, 5))
        return f"#{r:02x}{g:02x}{b:02x}"
    return hex_color


def layout_chips(items, col_w):
    rows, x, row = [], 0, []
    max_w = col_w - 2 * BOX_PAD
    for item in items:
        w = 9 + ICON + 6 + text_width(item[0]) + 10
        if row and x + w > max_w:
            rows.append(row)
            row, x = [], 0
        row.append((x, w, item))
        x += w + CHIP_GAP
    rows.append(row)
    return rows


def build(theme):
    c = THEMES[theme]
    out = []
    y = PAD
    for clusters in ROWS:
        weights = [cl[2] if len(cl) > 2 else 1 for cl in clusters]
        unit = (WIDTH - 2 * PAD - (len(clusters) - 1) * COL_GAP) / sum(weights)
        laid = [(cl[0], unit * wt, layout_chips(cl[1], unit * wt)) for cl, wt in zip(clusters, weights)]
        box_h = max(BOX_PAD + LABEL_H + len(rows) * CHIP_H + (len(rows) - 1) * CHIP_GAP + BOX_PAD for _, _, rows in laid)
        bx = PAD
        for label, col_w, rows in laid:
            out.append(f'<rect x="{bx + 0.5:.1f}" y="{y + 0.5}" width="{col_w - 1:.1f}" height="{box_h - 1}" rx="10" fill="none" stroke="{c["border"]}"/>')
            out.append(f'<text x="{bx + BOX_PAD:.1f}" y="{y + BOX_PAD + 12}" font-size="11" font-weight="600" letter-spacing="0.8" fill="{c["muted"]}">{escape(label.upper())}</text>')
            for i, row in enumerate(rows):
                cy = y + BOX_PAD + LABEL_H + i * (CHIP_H + CHIP_GAP)
                for x, w, (name, icon, color) in row:
                    cx = bx + BOX_PAD + x
                    scale = ICON / 24
                    out.append(
                        f'<rect x="{cx + 0.5:.1f}" y="{cy + 0.5}" width="{w - 1:.1f}" height="{CHIP_H - 1}" rx="7" fill="{c["chip"]}" stroke="{c["border"]}"/>'
                        f'<path transform="translate({cx + 9:.1f} {cy + (CHIP_H - ICON) / 2}) scale({scale:.4f})" fill="{icon_color(color, theme, c)}" d="{icon_path(icon)}"/>'
                        f'<text x="{cx + 9 + ICON + 6:.1f}" y="{cy + 18.5}" font-size="{FONT_SIZE}" fill="{c["text"]}">{escape(name)}</text>'
                    )
            bx += col_w + COL_GAP
        y += box_h + ROW_GAP
    height = y - ROW_GAP + PAD
    names = ", ".join(n for clusters in ROWS for cl in clusters for n, _, _ in cl[1])
    return "\n".join([
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height:.0f}" viewBox="0 0 {WIDTH} {height:.0f}" role="img" aria-label="Knowledge: {escape(names)}" font-family="{FONT}">',
        f'  <rect x="0.5" y="0.5" width="{WIDTH - 1}" height="{height - 1:.0f}" rx="14" fill="{c["bg"]}" stroke="{c["border"]}"/>',
        *(f"  {o}" for o in out),
        "</svg>",
        "",
    ])


for theme in THEMES:
    (ROOT / "assets" / f"knowledge-{theme}.svg").write_text(build(theme))
