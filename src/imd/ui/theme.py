"""Design tokens + runtime dark/light theming.

Single source of truth for colors, mirroring docs/design-system.md and the
prototype. Changing a brand color happens here, once.
"""

from __future__ import annotations

# Semantic + surface tokens per theme. Keys are shared across both themes.
DARK: dict[str, str] = {
    "bull": "#3fb950", "bear": "#f85149", "neutral": "#d29922",
    "info": "#2f81f7", "accent": "#2f81f7",
    "bg": "#0d1117", "panel": "#161b22", "panel2": "#1c2330",
    "border": "#30363d", "text": "#e6edf3", "muted": "#9aa7b4",
}

LIGHT: dict[str, str] = {
    "bull": "#137333", "bear": "#c5221f", "neutral": "#b06f00",
    "info": "#1a73e8", "accent": "#1a73e8",
    "bg": "#ffffff", "panel": "#f6f8fa", "panel2": "#eef1f4",
    "border": "#d0d7de", "text": "#1f2328", "muted": "#636c76",
}

# Colorblind-aware categorical palette for charts.
CHART_PALETTE: list[str] = [
    "#1a73e8", "#d29922", "#3fb950", "#a371f7", "#f85149", "#00a3a3", "#e8710a",
]


def tokens(theme: str) -> dict[str, str]:
    return LIGHT if theme == "light" else DARK


def css_variables(theme: str) -> str:
    """Return a <style> block exposing tokens as CSS vars + a few base overrides."""
    t = tokens(theme)
    vars_block = "".join(f"--{k}:{v};" for k, v in t.items())
    return f"""
    <style>
      :root {{ {vars_block} }}
      .stApp {{ background:{t['bg']}; color:{t['text']}; }}
      .imd-up {{ color:{t['bull']}; }}
      .imd-down {{ color:{t['bear']}; }}
      .imd-flat {{ color:{t['neutral']}; }}
    </style>
    """
