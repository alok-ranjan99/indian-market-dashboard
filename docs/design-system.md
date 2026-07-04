# Design System — Color & Theme Tokens

Decided 2026-07-04: **standard finance palette**, with **both dark & light** themes (user-toggleable).

## Semantic colors (same meaning across both themes)
| Token | Meaning | Light | Dark |
|---|---|---|---|
| `--bull` | up / bullish / greed / positive | `#137333` (deep green) | `#3fb950` |
| `--bear` | down / bearish / fear / negative | `#c5221f` (deep red) | `#f85149` |
| `--neutral` | flat / caution / neutral | `#b06f00` (amber) | `#d29922` |
| `--info` | links / selected / info | `#1a73e8` | `#2f81f7` |
| `--accent` | primary brand accent | `#1a73e8` | `#2f81f7` |

## Fear→Greed gauge scale (0–100, continuous)
`0 ────────── 50 ────────── 100`
`bear/red  →  amber  →  bull/green`  (extreme fear = red, extreme greed = green)

## Surfaces
| Token | Light | Dark |
|---|---|---|
| `--bg` | `#ffffff` | `#0d1117` |
| `--panel` | `#f6f8fa` | `#161b22` |
| `--panel-2` | `#eef1f4` | `#1c2330` |
| `--border` | `#d0d7de` | `#30363d` |
| `--text` | `#1f2328` | `#e6edf3` |
| `--muted` | `#636c76` | `#9aa7b4` |

## Chart palette (categorical, colorblind-aware)
`#1a73e8`, `#d29922`, `#3fb950`, `#a371f7`, `#f85149`, `#00a3a3`, `#e8710a`

## Rules
- Green = up, Red = down — never invert (Indian/US convention; note: some Indian TV channels invert, but we follow the global standard for clarity).
- Fear/Greed and Bias use the same semantic tokens so the whole app reads consistently.
- Streamlit theme set in `.streamlit/config.toml`; app exposes a dark/light toggle that swaps token sets.
